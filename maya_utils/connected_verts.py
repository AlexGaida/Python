# import maya modules
import maya.api.OpenMaya as om
import maya.cmds as cmds


class OmEdgeObject(object):
    def __init__(self, edgeIterator):
        self.id = int(edgeIterator.index())
        self.vtx0_id = int(edgeIterator.vertexId(0))
        self.vtx0_pos = edgeIterator.point(0)
        self.vtx1_id = int(edgeIterator.vertexId(1))
        self.vtx1_pos = edgeIterator.point(1)
        self.vtx_list = [self.vtx0_id, self.vtx1_id]
        self.connectedEdges = list(edgeIterator.getConnectedEdges())
        self.edgePos = edgeIterator.center()
    
    def reverseVertData(self):
        old_vtx0_id = int(self.vtx0_id)
        old_vtx0_pos = om.MPoint(self.vtx0_pos)
        old_vtx1_id = int(self.vtx1_id)
        old_vtx1_pos = om.MPoint(self.vtx1_pos)
        self.vtx0_id = old_vtx1_id
        self.vtx0_pos = old_vtx1_pos
        self.vtx1_id = old_vtx0_id
        self.vtx1_pos = old_vtx0_pos
        self.vtx_list.reverse()


def array_rotate(array, step):
    """reorder the array by the length
    :param array:
    :param step:
    :return:
    """
    length = len(array)
    if step < 0:
        # left rotate by one
        for i in range(abs(step)):
            temp = array[0]
            for idx in range(length-1):
                array[idx] = array[idx + 1]
            array[length-1] = temp
    else:
        # right rotate by one
        for i in range(step):
            temp = array[-1]
            for idx in range(length-1, 0, -1):
                array[idx] = array[idx - 1]
            array[0] = temp


def query_edge_chain(startEdgeID, edges_data, desiredCount, attempts):
    """Find the depth of the edges. I don't know what this does.
    """
    loopList = list()
    chainCount = 0
    startEdgeObj = edges_data[startEdgeID]
    connectedEdgeObj = None
    connectedVert = startEdgeObj.vtx_list[1]
    if attempts > 4:
        connectedVert = startEdgeObj.vtx_list[0]
        startEdgeObj.reverseVertData()
    loopList.append(startEdgeObj)

    while chainCount != desiredCount:
        chainCount += 1
        reversed = False
        foundEdgeId = None
        for edgeID, edgeObj in edges_data.iteritems():
            if edgeObj.vtx_list[0] == connectedVert and edgeObj not in loopList:
                foundEdgeId = edgeID
                break
            if attempts > 2:
                if edgeObj.vtx_list[1] == connectedVert and edgeObj not in loopList:
                    foundEdgeId = edgeID
                    reversed = True
                    break
        if foundEdgeId == None:
            if chainCount == desiredCount - 1 and attempts > 0:
                if not connectedEdgeObj:
                    connectedEdgeObj = startEdgeObj
                for edgeID, edgeObj in edges_data.iteritems():
                    if edgeObj.vtx_list[1] == connectedVert and edgeObj != connectedEdgeObj:
                        foundEdgeId = edgeID
                        break
                    if attempts > 2 and edgeObj.vtx_list[0] == connectedVert and edgeObj != connectedEdgeObj:
                        foundEdgeId = edgeID
                        reversed = True
                        break
                if foundEdgeId != None:
                    lastEdgeObj = edges_data[foundEdgeId]
                    if not reversed:
                        lastEdgeObj.reverseVertData()
                    loopList.append(lastEdgeObj)
                continue
            else:
                break
        if len(loopList) == desiredCount:
            break
        connectedEdgeObj = edges_data[foundEdgeId]
        if reversed:
            connectedEdgeObj.reverseVertData()
        loopList.append(connectedEdgeObj)
        connectedVert = connectedEdgeObj.vtx_list[1]
    return loopList


def get_loop_list(edges_data, input_edges, remove_edges=None):
    """Retrieve a valid edge loop list
    :param edges_data:
    :param input_edges:
    :param remove_edges:
    :return: loopList (list) array of edge chains found.
    """
    if remove_edges:
        remove_edges = list()
        for e in remove_edges:
            if e.id in input_edges:
                remove_edges.append(e.id)
        for e in remove_edges:
            input_edges.remove(e)
    desiredCount = len(edges_data.keys()) / 2
    loopFound = False
    attempts = 0
    while not loopFound:
        for index, startEdgeID in enumerate(input_edges):
            loopList = query_edge_chain(startEdgeID, edges_data, desiredCount, attempts)
            if len(loopList) == desiredCount:
                loopFound = True
                break
        attempts += 1
    return loopList


def assess_components():
    """Verify the selection of edges or vertexes before proceeding with merge.
    :return:
        edges_data: (dict)
        dag: (OpenMaya.MDag)
    """
    edges_data = {}
    sel = om.MGlobal.getActiveSelectionList()
    dag, component = sel.getComponent(0)
    selected_verts = ()

    # if the component selected is a vertex
    if component.apiType() == om.MFn.kMeshVertComponent:
        sel2 = om.MSelectionList()
        vert_itr = om.MItMeshVertex(dag, component)
        if vert_itr.count() % 2 != 0:
            raise ValueError('Please select matching number of vertices/edges')
        while not vert_itr.isDone():
            vertID = int(vert_itr.index())
            selected_verts += vertID,
            for vertEdge_id in list(vert_itr.getConnectedEdges()):
                sel2.add('%s.e[%s]' % (dag.fullPathName(), vertEdge_id))
            vert_itr.next()
        dag, vertEdge_component = sel2.getComponent(0)
        vertEdge_itr = om.MItMeshEdge(dag, vertEdge_component)
        while not vertEdge_itr.isDone():
            connectedVertices = [vertEdge_itr.vertexId(0), vertEdge_itr.vertexId(1)]
            if all(x in selected_verts for x in connectedVertices):
                edges_data[int(vertEdge_itr.index())] = OmEdgeObject(vertEdge_itr)
            vertEdge_itr.next()

    # else if the component selected is edge
    elif component.apiType() == om.MFn.kMeshEdgeComponent:
        edge_itr = om.MItMeshEdge(dag, component)
        if edge_itr.count() % 2 != 0:
            raise ValueError('Please select matching number of vertices/edges')
        while not edge_itr.isDone():
            edges_data[int(edge_itr.index())] = OmEdgeObject(edge_itr)
            edge_itr.next()
    else:
        raise ValueError('Select either vertices or edges')
    return edges_data, dag


def trim_data(edges_data, selected_edges):
    """removes edges we do not need from the dictionary data.
    :param edges_data:
    :param selected_edges:
    :return:
    """
    for edge in edges_data:
        edgeObj = edges_data[edge]
        remove_edges = ()
        for connectedEdge in edgeObj.connectedEdges:
            if connectedEdge not in selected_edges:
                remove_edges += connectedEdge,
        for y in remove_edges:
            edgeObj.connectedEdges.remove(y)
    return edges_data


def build_distance_data(edges_1, edges_2):
    """Build a dictionary of distances between two edges.
    :param edges_1:
    :param edges_2:
    :return:
    """
    edge_distance = {}
    for edgeObj1 in edges_1:
        edge1_pos = edgeObj1.edgePos
        for edgeObj2 in edges_2:
            edge2_pos = edgeObj2.edgePos
            distance = edge1_pos.distanceTo(edge2_pos)
            edge_distance[distance] = (edgeObj1, edgeObj2)
    return edge_distance


def assess_distance(edge_distance={}):
    """Calculate distances between two vertices.    
    :param edge_distance: (dict) dictionary data of edges.
    :return: 
    """
    edge_obj_1 = edge_distance[min(edge_distance)][0]
    edge_obj_2 = edge_distance[min(edge_distance)][1]
    vertex_pairs = [(0, 0), (0, 1), (1, 0), (1, 1)]

    # calculated distances array
    distances = [edge_obj_1.vtx0_pos.distanceTo(edge_obj_2.vtx0_pos),
                 edge_obj_1.vtx0_pos.distanceTo(edge_obj_2.vtx1_pos),
                 edge_obj_1.vtx1_pos.distanceTo(edge_obj_2.vtx0_pos),
                 edge_obj_1.vtx1_pos.distanceTo(edge_obj_2.vtx1_pos)]
    return vertex_pairs[distances.index(min(distances))], edge_obj_1, edge_obj_2


def build_vert_list(edges_1, edges_2):
    """Builds the vertex list against matching component id's
    :param edges_1: (list)
    :param edges_2: (list)
    :return:
    """
    vertices_1 = []
    vertices_2 = []

    for a in range(len(edges_1)):
        e1 = edges_1[a]
        e2 = edges_2[a]
        if e1.vtx0_id not in vertices_1:
            vertices_1.append(e1.vtx0_id)
        if e2.vtx0_id not in vertices_2:
            vertices_2.append(e2.vtx0_id)
        if e1.vtx1_id not in vertices_1:
            vertices_1.append(e1.vtx1_id)
        if e2.vtx1_id not in vertices_2:
            vertices_2.append(e2.vtx1_id)
    return vertices_1, vertices_2


def center_merge_verts(dag, vertices_1, vertices_2):
    """Calculaes the center position of the vertices and snaps them.
    :param dag: (OpenMaya.MDag)
    :param vertices_1: (list)
    :param vertices_2: (list)
    :return:
    """
    selection_verts = ()
    vertices_done = []
    
    for vert_idx in range(len(vertices_1)):
        if vertices_1[vert_idx] in vertices_done:
            continue

        v1_path = '%s.vtx[%s]' % (dag.fullPathName(), vertices_1[vert_idx])
        v2_path = '%s.vtx[%s]' % (dag.fullPathName(), vertices_2[vert_idx])

        # do not perform merge on the same vertex
        if v1_path == v2_path:
            continue

        # add the two vertices to selection
        selection_verts += v1_path, v2_path,

        # assign the verts to list to prevent similar operations on the vertices already merged
        vertices_done.append(vertices_1[vert_idx])

        # push the vertices together
        avg_position = get_average_positons(v1_path, v2_path)
        cmds.xform(v1_path, translation=avg_position, worldSpace=True)
        cmds.xform(v2_path, translation=avg_position, worldSpace=True)

    # perform the mesh merge to change from 2 vertices into one
    do_merge(selection_verts)


def get_average_positons(object_1="", object_2=""):
    """Returns the average position between the two objects.
    :param object_1: (str) the first object.
    :param object_2: (str) the second object.
    :return:
    """
    v1_pos = cmds.xform(object_1, query=True, translation=True, worldSpace=True)
    v2_pos = cmds.xform(object_2, query=True, translation=True, worldSpace=True)
    return (v1_pos[0] + v2_pos[0]) / 2.0, (v1_pos[1] + v2_pos[1]) / 2.0, (v1_pos[2] + v2_pos[2]) / 2.0,


def do_merge(vertices=()):
    """Perform the vertex merge operation.
    :param vertices:
    :return:
    """
    cmds.select(vertices, replace=True)
    cmds.polyMergeVertex()


def run():
    edges_data, dag = assess_components()
    selected_edges = edges_data.keys()

    edges_data = trim_data(edges_data, selected_edges)

    # dealing with edge loops
    edges_1 = get_loop_list(edges_data, selected_edges)
    edges_2 = get_loop_list(edges_data, selected_edges, remove_edges=edges_1)

    if len(edges_1) != len(edges_2):
        raise ValueError('Loop counts do not match')

    edge_distance = build_distance_data(edges_1, edges_2)
    
    pairResult, edge_obj_1, edge_obj_2 = assess_distance(edge_distance)
    
    # determine if the other loop needs to be reversed
    if pairResult[0] != pairResult[1]:
        edges_2.reverse()
        for z in edges_2:
            z.reverseVertData()
    firstListShift = edges_1.index(edge_obj_1) * -1
    secondListShift = edges_2.index(edge_obj_2) * -1

    array_rotate(edges_1, firstListShift)
    array_rotate(edges_2, secondListShift)
    center_merge_verts(dag, *build_vert_list(edges_1, edges_2))
