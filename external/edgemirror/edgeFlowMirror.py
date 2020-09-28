"""
=====================================================================

edgeFlowMirror 3.4 (c) 2007 - 2016 by Thomas Bittner

(c) 2007 - 2016 by Thomas Bittner
thomasbittner@hotmail.de

This tool mirrors mainly skinweights, geometry and component selection.
Opposite Mirror-points are found per edgeflow, and NOT via position.
This means, that only the way the edges are connected together is relevant,
and the actual positions of the vertices does not matter.
one of the inputs the tool requires, is one of the middleedges
The character can even be in a different pose and most parts of the tool will
still work.

=====================================================================
    
"""


import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds
import sys
import math


 
# name our command
kPluginCmdName="edgeFlowMirror"
  
kTaskFlag = "-t"
kTaskFlagLong = "-task"
kDirectionFlag = "-d"
kDirectionFlagLong = "-direction"
kMiddleEdgeFlag = "-me"
kMiddleEdgeFlagLong = "-middleEdge"
kBaseObjectFlag = "-bo"
kBaseObjectFlagLong = "-baseObject"
kBaseVertexSpaceFlag = "-bv"
kBaseVertexSpaceFlagLong = "-baseVertexSpace"
kLeftJointsPrefixFlag = "-ljp"
kLeftJointsPrefixFlagLong = "-leftJointsPrefix"
kRightJointsPrefixFlag = "-rjp"
kRightJointsPrefixFlagLong = "-rightJointsPrefix"
kOptimizeFlag = "-o"
kOptimizeFlagLong = "-optimize"

edgeFlowMirrorSavedMapArray = []
edgeFlowMirrorSavedSideArray = []
edgeFlowMirrorNewBaseObjectName = ''

 
class EdgeFlowMirrorCommand(OpenMayaMPx.MPxCommand):
 
    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)
        self.oldTargetPoints = OpenMaya.MFloatVectorArray()
        self.newTargetPoints = OpenMaya.MFloatVectorArray()
        self.targetObj = OpenMaya.MDagPath()
   
        self.WeightArray = OpenMaya.MDoubleArray()
        self.oldWeightArray = OpenMaya.MDoubleArray()
        self.infCount = int(0)
        self.vtxComponents = OpenMaya.MObject()
        self.skinCluster = OpenMaya.MObject()


    def manipulateObject(self, redo):
        if self.task.startswith('geometry'):

            targetPointArray = OpenMaya.MPointArray()
            targetObjectDagPath = OpenMaya.MDagPath()

            fnTargetMesh = OpenMaya.MFnMesh(self.targetObj)
            OpenMaya.MFnDagNode(self.targetObj).getPath(targetObjectDagPath);
            fnTargetMesh.getPoints(targetPointArray);
            pointIndex = int(0)
            if redo:
                for i in range(targetPointArray.length()):
                    targetPointArray.set(i, self.newTargetPoints[pointIndex].x, self.newTargetPoints[pointIndex].y, self.newTargetPoints[pointIndex].z)                    
                    pointIndex += 1

            else:
                for i in range(targetPointArray.length()):
                    targetPointArray.set(i, self.oldTargetPoints[pointIndex].x, self.oldTargetPoints[pointIndex].y, self.oldTargetPoints[pointIndex].z)
                    pointIndex += 1


            fnTargetMesh.setPoints(targetPointArray, OpenMaya.MSpace.kObject)
            fnTargetMesh.updateSurface()           


        if self.task == "skinCluster":

            fnSkinCluster = OpenMayaAnim.MFnSkinCluster(self.skinCluster)
            skinPath = OpenMaya.MDagPath() 
            fnSkinCluster.getPathAtIndex(0,skinPath)

            influenceIndices = OpenMaya.MIntArray() 
            for i in range(self.infCount):
                influenceIndices.append(i)

            if redo:
                fnSkinCluster.setWeights(skinPath, self.vtxComponents,influenceIndices,self.WeightArray,0)
            else:
                fnSkinCluster.setWeights(skinPath,self.vtxComponents,influenceIndices,self.oldWeightArray,0)
       


 

    def doIt(self, args):
        direction = 1
        searchString = 'l_'
        replaceString = 'r_'
        middleEdge = ''
        self.task = ''
        baseObject = ''
        
        #skinCluster
        system = "old"
	    
	    #geometry
        baseObjectName = "";
        #baseObj = OpenMaya.MObject()
        
        syntax = OpenMaya.MSyntax()
        syntax.addFlag( kTaskFlag, kTaskFlagLong, OpenMaya.MSyntax.kString )
        syntax.addFlag( kDirectionFlag, kDirectionFlagLong, OpenMaya.MSyntax.kDouble )
        syntax.addFlag( kMiddleEdgeFlag, kMiddleEdgeFlagLong, OpenMaya.MSyntax.kString )
        syntax.addFlag( kBaseObjectFlag, kBaseObjectFlagLong, OpenMaya.MSyntax.kString )
        syntax.addFlag( kBaseVertexSpaceFlag, kBaseVertexSpaceFlagLong, OpenMaya.MSyntax.kBoolean )
        syntax.addFlag( kLeftJointsPrefixFlag, kLeftJointsPrefixFlagLong, OpenMaya.MSyntax.kString )
        syntax.addFlag( kRightJointsPrefixFlag, kRightJointsPrefixFlagLong, OpenMaya.MSyntax.kString )
        syntax.addFlag( kOptimizeFlag, kOptimizeFlagLong, OpenMaya.MSyntax.kBoolean )
        argData = OpenMaya.MArgDatabase( syntax, args )

        doVertexSpace = False
                
        if argData.isFlagSet( kTaskFlag ):
            self.task = argData.flagArgumentString( kTaskFlag, 0 )
            
        if argData.isFlagSet( kDirectionFlag ):
            direction  = argData.flagArgumentDouble( kDirectionFlag, 0 )  
            
        if argData.isFlagSet( kMiddleEdgeFlag ):
            middleEdge = argData.flagArgumentString( kMiddleEdgeFlag, 0 )
            
        if argData.isFlagSet( kBaseObjectFlag ):
            baseObjectName = argData.flagArgumentString( kBaseObjectFlag, 0 )
        
        if argData.isFlagSet( kBaseVertexSpaceFlag ):
            doVertexSpace = argData.flagArgumentBool( kBaseVertexSpaceFlag, 0 )
            
        if argData.isFlagSet( kLeftJointsPrefixFlag ):
            searchString = argData.flagArgumentString( kLeftJointsPrefixFlag, 0 )

        if argData.isFlagSet( kRightJointsPrefixFlag ):
            replaceString = argData.flagArgumentString( kRightJointsPrefixFlag, 0 )

        if argData.isFlagSet( kOptimizeFlag ):
            doOptimize = argData.flagArgumentString( kOptimizeFlag, 0 )
        else:
            doOptimize = False
                      
        selection = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(selection)
        dagPathSelShape = OpenMaya.MDagPath()
        component = OpenMaya.MObject()

        iterate = OpenMaya.MItSelectionList(selection)
        if iterate.isDone():
            print 'nothing selected - need to select vertices'
            return 
        
        iterate.getDagPath (dagPathSelShape, component)
        selectedPoints = OpenMaya.MItMeshVertex ( dagPathSelShape, component) # problem
        pointCount = OpenMaya.MFnMesh(dagPathSelShape).numVertices()
        objectName = OpenMaya.MFnMesh(dagPathSelShape).partialPathName()
        if (pointCount == 0):
            print "point count is 0"
            return

        if not len(middleEdge):
            print 'you need to specify Middle Edge'
            return
            
        global edgeFlowMirrorSavedMapArray
        global edgeFlowMirrorSavedSideArray
        global edgeFlowMirrorNewBaseObjectName

        if doOptimize and len(edgeFlowMirrorSavedMapArray) and self.task != 'compute':
            mapArray = edgeFlowMirrorSavedMapArray
            sideArray = edgeFlowMirrorSavedSideArray
            newBaseObjectName = edgeFlowMirrorNewBaseObjectName
        else:
            mapArray, sideArray, newBaseObjectName = self.analizeTopology(middleEdge)               
            edgeFlowMirrorSavedMapArray = mapArray
            edgeFlowMirrorSavedSideArray = sideArray
            edgeFlowMirrorNewBaseObjectName = newBaseObjectName
        
        
        
        if self.task == 'getMapArray':            
            self.setResult(mapArray)
            return
        
        if self.task == 'getSideArray':
            self.setResult(sideArray)
            return
            
        if self.task == 'getMapSideArray':
            self.setResult(mapArray+sideArray)
            return

        if self.task == 'compute':
            return

        if self.task == "geometrySymmetry" and len(newBaseObjectName):
            baseObjectName = newBaseObjectName;

        bothIndexes = OpenMaya.MIntArray()
        allPointsArray = OpenMaya.MIntArray()
        for i in range(pointCount):
            allPointsArray.append(-1)
        
        counter = int(0)            
        selectedPoints.reset()
        
        while not selectedPoints.isDone():
            index = selectedPoints.index();
            if mapArray[index] != -1:
                bothIndexes.append( index )
                
            allPointsArray[index] = counter;
            counter += 1;
            if sideArray[index] != 0 and sideArray[index] != -1:
                bothIndexes.append( mapArray[index] )
                allPointsArray[ mapArray[index] ] = counter
                counter += 1
            
            selectedPoints.next()

        #reorder bothIndexes
        bothIndexes.clear()
        for i in xrange(pointCount):
            if (allPointsArray[i] != -1):
                bothIndexes.append(i);

        #reorder allPointsArray
        allPointsArray.clear();
        for i in range(pointCount):          
            allPointsArray.append(-1)
        for i in range(bothIndexes.length()):          
            allPointsArray[bothIndexes[i]] = i
        
        fnVtxComp = OpenMaya.MFnSingleIndexedComponent() ;
        self.vtxComponents = fnVtxComp.create( OpenMaya.MFn.kMeshVertComponent )
        vertexIndices = []
        skinPath = OpenMaya.MDagPath()
        
        for i in xrange(len(bothIndexes)):
            fnVtxComp.addElement(bothIndexes[i]);
            vertexIndices.append(bothIndexes[i]);

        if self.task == "skinCluster":
            foundSkin = False;

            it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kSkinClusterFilter)
            while not it.isDone():
                fnSkinCluster = OpenMayaAnim.MFnSkinCluster(it.item())
                fnSkinCluster.getPathAtIndex(0,skinPath)
                if OpenMaya.MFnDagNode(skinPath.node()).partialPathName() == objectName:
                    self.skinCluster = it.item()
                it.next()
            
            

            if self.skinCluster.hasFn(OpenMaya.MFn.kSkinClusterFilter):
                foundSkin = True;


            if foundSkin:
                skinPath = OpenMaya.MDagPath();
                influenceArray = OpenMaya.MDagPathArray();
                jointNames = [] #OpenMaya.MStringArray() ;
                searchJointNames = [] #OpenMaya.MStringArray() ;
                replaceJointNames = [] #OpenMaya.MStringArray() ;
                middleJointNames = [] #OpenMaya.MStringArray() ;
                jointMapArray = OpenMaya.MIntArray();
                
                fnSkinCluster = OpenMayaAnim.MFnSkinCluster(self.skinCluster);
                
                fnSkinCluster.getPathAtIndex(fnSkinCluster.indexForOutputConnection(0),skinPath)
                #fnSkinCluster.influenceObjects(influenceArray, &status) # status ?!
                fnSkinCluster.influenceObjects(influenceArray)
                
                for i in range(influenceArray.length()):
                    jointNames.append(OpenMaya.MFnDagNode(influenceArray[i]).name())
                
                self.infCount = len(jointNames)
                for i in range(self.infCount):
                    jointMapArray.append(i)
                    

                searchJointIndexes = OpenMaya.MIntArray() 
                replaceJointIndexes = OpenMaya.MIntArray() 
                for i in range(self.infCount):
                    nameSpace = ''
                    if ':' in jointNames[i]:
                        nameSpace = (jointNames[i].split(':')[0]+":")
                    if jointNames[i].split(":")[-1].startswith(searchString):                        
                        searchJointNames.append(nameSpace+jointNames[i].split(':')[-1][len(searchString):len(jointNames[i])])
                        searchJointIndexes.append(i)
                    elif jointNames[i].split(":")[-1].startswith(replaceString):
                        replaceJointNames.append(nameSpace+jointNames[i].split(':')[-1][len(replaceString):len(jointNames[i])]);
                        replaceJointIndexes.append(i);
                    else:
                        middleJointNames.append(nameSpace+jointNames[i]);
                
                for i in range(len(searchJointNames)):
                    for k in range(len(replaceJointNames)):
                        if searchJointNames[i] == replaceJointNames[k]:
                            jointMapArray[searchJointIndexes[i]] = replaceJointIndexes[k];
                            jointMapArray[replaceJointIndexes[k]] = searchJointIndexes[i];
                
                

                print '\n'
                print '==============='
                print 'joints without mirrorJoints (points of the other side will be assigned to the same joint)'
                for i in range(len(jointNames)):
                    if jointMapArray[i] == i:
                        print jointNames[i]
                print '==============='
                print '\n'


                self.WeightArray.clear()
                scriptUtil = OpenMaya.MScriptUtil()
                infCountPtr = scriptUtil.asUintPtr()
                fnSkinCluster.getWeights(skinPath,self.vtxComponents, self.WeightArray, infCountPtr)
                               
                self.oldWeightArray.copy(self.WeightArray);

                # mirroring WeightArray 
                averageWeights = OpenMaya.MDoubleArray()
                for l in range(self.infCount):
                    averageWeights.append(0)

                oppositeIndex = int(0)
                
                import time
                t = time.time() 
                for i in range(bothIndexes.length()):
                    index = bothIndexes[i]
                    startIndexB = i * self.infCount


                    # not middle
                    #
                    if sideArray[index] == direction and mapArray[index] != index:
                        oppositeIndex = allPointsArray[ mapArray[bothIndexes[i]] ]
                        startIndexA = oppositeIndex * self.infCount
                        
                        for k in range(self.infCount):
                            self.WeightArray[startIndexA + k] = self.WeightArray[ startIndexB + jointMapArray[k]]         

                    # middle one
                    #
                    elif (mapArray[index] == index):   
                        for k in range(self.infCount):
                            averageWeights[k] = (self.WeightArray[startIndexB + k] + self.WeightArray[startIndexB + jointMapArray[k]]) * 0.5;
                        for k in range(self.infCount):
                            self.WeightArray[startIndexB + k] = averageWeights[k]
                            
                #print 'creating the new array took: ', (time.time()-t), 'seconds'


                """
                t = time.time() 
                for i in range(bothIndexes.length()):
                    index = bothIndexes[i]


                    # not middle
                    #
                    if sideArray[index] == direction and mapArray[index] != index:
                        oppositeIndex = allPointsArray[ mapArray[bothIndexes[i]] ]
                        
                        for k in range(self.infCount):
                            self.WeightArray[oppositeIndex * self.infCount + k] = self.WeightArray[ i * self.infCount + jointMapArray[k]]         

                    # middle one
                    #
                    elif (mapArray[index] == index):   
                        for k in range(self.infCount):
                            averageWeights[k] = (self.WeightArray[i * self.infCount + k] + self.WeightArray[i * self.infCount + jointMapArray[k]]) * 0.5;
                        for k in range(self.infCount):
                            self.WeightArray[i * self.infCount + k] = averageWeights[k]
                            
                print 'creating the new array again took: ', (time.time()-t), 'seconds'
                """

        

        if self.task == "geometryFlip" or self.task == "geometryMirror" or self.task == "geometrySymmetry":    # geometry mirror

            mirrorInt = int(0)
            if self.task == "geometryMirror":
                mirrorInt = 1
            if self.task == "geometrySymmetry":
                mirrorInt = 2

            baseSel = OpenMaya.MSelectionList()
            baseSel.add(baseObjectName);
            baseObj = OpenMaya.MDagPath()

            baseSel.getDagPath (0, baseObj, component )
            vertexCount = OpenMaya.MFnMesh(baseObj).numVertices()
            if vertexCount == 0:
                print "something's wrong with the baseObject"
                return OpenMaya.MStatus.kFailure        


            objectName = OpenMaya.MFnMesh(baseObj).partialPathName()
            self.targetObj = dagPathSelShape

            fnBaseMesh = OpenMaya.MFnMesh(baseObj)
            basePoints = OpenMaya.MPointArray()
            fnBaseMesh.getPoints(basePoints)            

            offset = [0, 0, 0]


            self.oldTargetPoints.clear()
            self.newTargetPoints.clear()

            fnTargetMesh = OpenMaya.MFnMesh(self.targetObj)
            targetObjectDagPath = OpenMaya.MDagPath()
            
            targetObjectDagPath = OpenMaya.MDagPath()
            OpenMaya.MFnDagNode(self.targetObj).getPath(targetObjectDagPath);
            
            targetPoints = OpenMaya.MPointArray()            
            fnTargetMesh.getPoints(targetPoints,OpenMaya.MSpace.kObject)
            
            for i in range(targetPoints.length()):
                self.oldTargetPoints.append( OpenMaya.MFloatVector(targetPoints[i].x, targetPoints[i].y, targetPoints[i].z) )
                self.newTargetPoints.append( OpenMaya.MFloatVector(targetPoints[i].x, targetPoints[i].y, targetPoints[i].z) )


            if mirrorInt != 2:        # if it's not create symmetryshape
                if not doVertexSpace:
                    import time
                    t = time.time()
                    pointOffset = OpenMaya.MPoint()
                    for i in range(len(bothIndexes)):
                        if mirrorInt == 0 or direction == sideArray[bothIndexes[i]]:

                            pointOffset = (targetPoints[bothIndexes[i]] - basePoints[bothIndexes[i]])
                            self.newTargetPoints.set(OpenMaya.MFloatVector(basePoints[mapArray[bothIndexes[i]]].x - pointOffset.x, basePoints[mapArray[bothIndexes[i]]].y + pointOffset.y, basePoints[mapArray[bothIndexes[i]]].z + pointOffset.z), mapArray[bothIndexes[i]])


                            """
                            offset[0] = targetPoints[bothIndexes[i]].x - basePoints[bothIndexes[i]].x
                            offset[1] = targetPoints[bothIndexes[i]].y - basePoints[bothIndexes[i]].y
                            offset[2] = targetPoints[bothIndexes[i]].z - basePoints[bothIndexes[i]].z
                            
                            x = basePoints[mapArray[bothIndexes[i]]].x + offset[0] * -1 # basePoints' index is -1
                            y = basePoints[mapArray[bothIndexes[i]]].y + offset[1]
                            z = basePoints[mapArray[bothIndexes[i]]].z + offset[2]
                            
                            self.newTargetPoints.set(OpenMaya.MFloatVector(x, y, z), mapArray[bothIndexes[i]])
                            """




                                        
                elif doVertexSpace:
                    import time
                    t = time.time()
                    
                    
                    vertCount = fnBaseMesh.numVertices()
                    faceCount = fnBaseMesh.numPolygons()
                    connectedVertices = OpenMaya.MIntArray()
                    connectedFaces = OpenMaya.MIntArray()
                    scriptUtil = OpenMaya.MScriptUtil()                                
                    ptr = scriptUtil.asIntPtr()

                    conVerts = [None] * vertCount
                    conFaces = [None] * vertCount
                    baseNormals = [None] * vertCount
                    targetNormals = [None] * vertCount


                    vertexIter = OpenMaya.MItMeshVertex(baseObj)
                    for i in range(vertCount):
                        vertexIter.setIndex(i, ptr)
                        vertexIter.getConnectedVertices(connectedVertices)   
                        vertexIter.getConnectedFaces(connectedFaces)
                        conVerts[i] = intArrayToList(connectedVertices)
                        conFaces[i] = intArrayToList(connectedFaces)
                        vec = OpenMaya.MVector()

                        vertexIter.getNormal(vec)
                        vec.normalize()
                        baseNormals[i] = OpenMaya.MVector(vec)



                    targetVertexIter = OpenMaya.MItMeshVertex(self.targetObj)
                    for i in range(vertCount):
                        vec = OpenMaya.MVector()
                        targetVertexIter.getNormal(vec)
                        vec.normalize()
                        targetNormals[i] = OpenMaya.MVector(vec)



                    faceIter = OpenMaya.MItMeshPolygon(baseObj)
                    vertsOnFaces = [None] * faceCount
                    for i in range(faceCount):
                        faceIter.setIndex(i, ptr)
                        faceIter.getVertices(connectedVertices)
                        vertsOnFaces[i] = intArrayToList(connectedVertices)

                    #print 'getting all the infos: ', (time.time()-t)
                    t = time.time()


                    #changeLocals = [None] * vertCount
                    skips = [False] * vertCount
                    xIds = [None] * vertCount
                    zIds = [None] * vertCount
                    xNegs = [None] * vertCount
                    zNegs = [None] * vertCount

                    skipsCounter = 0
                    # create matrices for one side
                    #print 'create matrices for one side'
                    time0 = 0
                    timeA = 0
                    timeB = 0
                    timeC = 0
                    #print 'created large arrays: ', (time.time()-t)
                    
                    
                    timeD = 0
                    timeDinc = 0 
                    timeE = 0
                    matrixCreateStartTime = time.time()
                    timeF = 0
                    for i in range(len(bothIndexes)):
                        bIndex = bothIndexes[i]
                
                        if sideArray[bIndex] == 1: #dont do the right ones yet, they'll get mirrored
                            continue
            

                        doSkipThisOne = False
                        
                        t = time.time()
                        
                        #if i not in bothIndexes:
                        #    doSkipThisOne = True
                        
                        
                        if (basePoints[bIndex]-targetPoints[bIndex]).length() < 0.00001 and (basePoints[mapArray[bIndex]]-targetPoints[mapArray[bIndex]]).length() < 0.00001:
                            doSkipThisOne = True
                            
                        timeE += (time.time()-t)
                            
                        if doSkipThisOne:
                            skips[bIndex] = True
                            skipsCounter += 1
                            continue


                        xId = []
                        zId = []
                        xNeg = []
                        zNeg = []


                        # get the avarage
                        #
                        averagePos = OpenMaya.MPoint(0,0,0)
                        for vertId in conVerts[bIndex]:
                            averagePos.x += basePoints[vertId].x
                            averagePos.y += basePoints[vertId].y
                            averagePos.z += basePoints[vertId].z
                            
                        averagePos /= len(conVerts[bIndex])
                        
                        #averagePos = basePoints[bIndex]
                        timeDinc = time.time()
                        for f, face in enumerate(conFaces[bIndex]):
                            t = time.time()
                            twoDots = [-1, -1]
                            twoVecs = [None, None]

                           
                            for vert in vertsOnFaces[face]:
                                if vert != bIndex and vert in conVerts[bIndex]:
                                    for d in range(2):
                                        if twoDots[d] == -1:
                                            twoDots[d] = vert
                                            twoVecs[d] = OpenMaya.MVector(basePoints[vert] - averagePos)
                                            break

                            timeA += time.time() - t
                            t = time.time()
                            # skip face if it's from middle vertex and not along middle edges
                            #
                            if sideArray[bIndex] == 0 and sideArray[twoDots[0]] != 0 and sideArray[twoDots[1]] != 0:
                                continue
                                

                            if f == 0:
                                firstVecs = list(twoVecs)

                                xId.append(twoDots[0])
                                zId.append(twoDots[1])
                                xNeg.append(False)
                                zNeg.append(False)
                                
                            timeB += time.time() - t
                            t = time.time()

                            # reshuffle them to match the first one as close as possible
                            # 
                            """
                            def distanceSqr(a):
                                return a.x*a.x + a.y*a.y + a.z*a.z

                            if f > 0:

                                negs = [False, False]

                                # compare current 2 dots with first dot from first face
                                dist0 = distanceSqr(twoVecs[0] - firstVecs[0])
                                dist1 = distanceSqr(twoVecs[1] - firstVecs[0])

                                dist0n = distanceSqr(-twoVecs[0] - firstVecs[0])
                                dist1n = distanceSqr(-twoVecs[1] - firstVecs[0])


                                dist0negated = False
                                dist1negated = False

                                if dist0 > dist0n:
                                    dist0 = dist0n
                                    dist0negated = True
                                if dist1 > dist1n:
                                    dist1 = dist1n
                                    dist1negated = True


                                if dist0 > dist1:    
                                    swap(0,1,twoDots)
                                    swap(0,1,twoVecs)

                                xId.append(twoDots[0])
                                zId.append(twoDots[1])

                                xNeg.append(dist0negated)
                                zNeg.append(distanceSqr(twoVecs[1]-firstVecs[1]) > distanceSqr(-twoVecs[1]-firstVecs[1]))
                                    
                            """
                            if f > 0:

                                negs = [False, False]

                                # compare current 2 dots with first dot from first face
                                angle0 = twoVecs[0].angle(firstVecs[0])
                                angle1 = twoVecs[1].angle(firstVecs[0])                
                                angle0neg = False
                                angle1neg = False

                                if angle0 > math.pi*0.5:
                                    angle0 = math.pi - angle0
                                    angle0neg = True
                                if angle1 > math.pi*0.5:
                                    angle1 = math.pi - angle1
                                    angle1neg = True


                                if angle0 < angle1:                    
                                    xId.append(twoDots[0])
                                    zId.append(twoDots[1])
                                    xNeg.append(angle0neg)
                                    zNeg.append(twoVecs[1].angle(firstVecs[1]) > math.pi*0.5)

                                else:
                                    xId.append(twoDots[1])
                                    zId.append(twoDots[0])
                                    xNeg.append(angle1neg)
                                    zNeg.append(twoVecs[0].angle(firstVecs[1]) > math.pi*0.5)
                                
                                
                            timeC += time.time() - t
                        timeD += (time.time() - timeDinc)
                                    
                        xIds[bIndex] = xId
                        zIds[bIndex] = zId

                        xNegs[bIndex] = xNeg
                        zNegs[bIndex] = zNeg
                    
                        
                    
                    #print 'got all the matrices: timeA:', timeA, 'timeB:', timeB, 'timeC:', timeC
                    #print 'timeD:', timeD, 'timeE:', timeE
                    #print 'complete time: ', (time.time() - matrixCreateStartTime)
                    
                    dv = 74
                    #print xIds[dv], xNegs[dv]
                    #print zIds[dv], zNegs[dv]
                    
                    # now create the other ones by mirroring
                    #
                    #print 'now create the other ones by mirroring'
                    for i in range(len(bothIndexes)):
                        bIndex = bothIndexes[i]
                        
                        if sideArray[bIndex] != 1:
                            continue


                        if skips[mapArray[bIndex]]:
                            skipsCounter += 1
                            skips[bIndex] = True
                            continue

                        xId = list(xIds[mapArray[bIndex]]) # [None] * vertCount
                        zId = list(zIds[mapArray[bIndex]]) # [None] * vertCount

                        for k in range(len(xId)):
                            xId[k] = mapArray[xId[k]]
                            zId[k] = mapArray[zId[k]]

                        xIds[bIndex] = xId
                        zIds[bIndex] = zId

                        xNegs[bIndex] = xNegs[mapArray[bIndex]]
                        zNegs[bIndex] = zNegs[mapArray[bIndex]]


                    #print 'skipping ', skipsCounter, 'vertices'

                    #print 'now mirror them'
                    t = time.time()
                    for i in range(bothIndexes.length()):
                        
                        
                        if mapArray[bothIndexes[i]] != -2:

                            bIndex = bothIndexes[i]

                            if (skips[bIndex]):
                                continue

                            if mirrorInt == 0 or direction == sideArray[bIndex] or sideArray[bIndex] == 0:
                                
                                idsCount = len(xIds[bIndex])
                                baseX = OpenMaya.MVector(0, 0, 0)
                                baseZ = OpenMaya.MVector(0, 0, 0)


                                for k in range(idsCount):
                                    if xNegs[bIndex][k]: xMult = -1
                                    else: xMult = 1
                                    if zNegs[bIndex][k]: zMult = -1
                                    else: zMult = 1

                                    baseX += (OpenMaya.MVector(basePoints[xIds[bIndex][k]] - basePoints[bIndex])) * xMult
                                    baseZ += (OpenMaya.MVector(basePoints[zIds[bIndex][k]] - basePoints[bIndex])) * zMult

                                baseX /= idsCount
                                baseZ /= idsCount
                                baseX.normalize()
                                baseZ.normalize()

                                baseMat = createMatrixFromList([baseX.x, baseX.y, baseX.z, 0, baseNormals[bIndex].x, baseNormals[bIndex].y, baseNormals[bIndex].z, 0, baseZ.x, baseZ.y, baseZ.z, 0, basePoints[bIndex].x, basePoints[bIndex].y, basePoints[bIndex].z, 1])    
                                changeWorld = createMatrixFromPos(targetPoints[bIndex])    
                                changeLocal = changeWorld * baseMat.inverse()

                                if sideArray[bIndex] == 0: # middle vertex

                                    middleId = -1
                                    for nId in xIds[bIndex] + zIds[bIndex]:
                                        if sideArray[nId] == 0:
                                            middleId = nId
                                            continue

                                    # check which angle is closer
                                    #
                                    middleIdVect = OpenMaya.MVector(basePoints[middleId]-basePoints[bIndex])
                                    angleX = middleIdVect.angle(baseX)
                                    angleZ = middleIdVect.angle(baseZ)
                                    if angleX > math.pi*0.5: angleX = math.pi - angleX
                                    if angleZ > math.pi*0.5: angleZ = math.pi - angleZ
                                    
                                    if angleX < angleZ:
                                        centeredLocal = createMatrixFromPos(OpenMaya.MPoint(changeLocal(3,0), changeLocal(3,1), -changeLocal(3,2)))
                                    else:
                                        centeredLocal = createMatrixFromPos(OpenMaya.MPoint(-changeLocal(3,0), changeLocal(3,1), changeLocal(3,2)))


                                    changetarget = centeredLocal * baseMat
                                    mappedBIndex = bIndex

                                elif sideArray[bIndex] != 0: # not middle vertex
                                    mappedBIndex = mapArray[bIndex]

                                    targetX = OpenMaya.MVector(0, 0, 0)
                                    targetZ = OpenMaya.MVector(0, 0, 0)

                                    idsCount = len(xIds[mappedBIndex])

                                    for k in range(idsCount):
                                        if xNegs[mappedBIndex][k]: xMult = -1
                                        else: xMult = 1
                                        if zNegs[mappedBIndex][k]: zMult = -1
                                        else: zMult = 1

                                        targetX += (OpenMaya.MVector(basePoints[xIds[mappedBIndex][k]] - basePoints[mappedBIndex])) * xMult
                                        targetZ += (OpenMaya.MVector(basePoints[zIds[mappedBIndex][k]] - basePoints[mappedBIndex])) * zMult

                                    targetX /= idsCount
                                    targetZ /= idsCount

                                    targetX.normalize()
                                    targetZ.normalize()
                    
                                    targetMat = createMatrixFromList([targetX.x, targetX.y, targetX.z, 0, baseNormals[mappedBIndex].x, baseNormals[mappedBIndex].y, baseNormals[mappedBIndex].z, 0, targetZ.x, targetZ.y, targetZ.z, 0, basePoints[mappedBIndex].x, basePoints[mappedBIndex].y, basePoints[mappedBIndex].z, 1])    

                                    changetarget = changeLocal * targetMat
                        
                    

                                self.newTargetPoints.set(OpenMaya.MFloatVector(changetarget(3,0), changetarget(3,1), changetarget(3,2)), mappedBIndex)
                    #print 'mirrored them .. ', (time.time()-t)


                    
            elif mirrorInt == 2:  # create symmetryshape

                for i in range(bothIndexes.length()):   
                    if sideArray[bothIndexes[i]] == 1 and mapArray[bothIndexes[i]] != -1:
                        targetPoints[bothIndexes[i]].x = targetPoints[bothIndexes[i]].x * -1

                for i in range(bothIndexes.length()):   
                    if mapArray[bothIndexes[i]] != -1:

                        x = (targetPoints[bothIndexes[i]].x + targetPoints[mapArray[bothIndexes[i]]].x) * 0.5; 
                        y = (targetPoints[bothIndexes[i]].y + targetPoints[mapArray[bothIndexes[i]]].y) * 0.5;
                        z = (targetPoints[bothIndexes[i]].z + targetPoints[mapArray[bothIndexes[i]]].z) * 0.5;
                        targetPoints[bothIndexes[i]].x = x; 
                        targetPoints[bothIndexes[i]].y = y;
                        targetPoints[bothIndexes[i]].z = z;
                        targetPoints[mapArray[bothIndexes[i]]].x = x; 
                        targetPoints[mapArray[bothIndexes[i]]].y = y;
                        targetPoints[mapArray[bothIndexes[i]]].z = z;

                        if mapArray[bothIndexes[i]] == bothIndexes[i]:        # middlePoint
                            targetPoints[bothIndexes[i]].x = 0;

                for i in range(bothIndexes.length()):
                    if mapArray[bothIndexes[i]] != -1:
                        if sideArray[bothIndexes[i]] == 1:    # middle
                            targetPoints[bothIndexes[i]].x = targetPoints[bothIndexes[i]].x * -1;

                        self.newTargetPoints.set( OpenMaya.MFloatVector( targetPoints[bothIndexes[i]].x, targetPoints[bothIndexes[i]].y,  targetPoints[bothIndexes[i]].z), bothIndexes[i] )


                #selecting wrong points:
                fnVtxComp = OpenMaya.MFnSingleIndexedComponent()
                vtxComponent = OpenMaya.MObject();
                self.vtxComponents = fnVtxComp.create( OpenMaya.MFn.kMeshVertComponent );
                selectPoints = OpenMaya.MSelectionList()


                missingPoints = False;
                selectedPoints.reset();
                while not selectedPoints.isDone():      # for (; !selectedPoints.isDone(); selectedPoints.next())
                    index = selectedPoints.index()
                    if mapArray[index] == -1:           # if no mirrorPoint found
                        fnVtxComp.addElement(index)
                        missingPoints = True;

                    selectedPoints.next()


                if missingPoints:
                    selectPoints.clear()
                    selectPoints.add(dagPathSelShape,self.vtxComponents)
                    print "some points couldn't be mirrored (see selection)"
                    OpenMaya.MGlobal.setActiveSelectionList(selectPoints)

                else:
                    print "found mirrorPoint for each selected point"


        return self.redoIt()


    def redoIt(self):
        self.manipulateObject(True)
 
 
    def undoIt(self):
        self.manipulateObject(False)
 
    def isUndoable(self):
        return True


    

    def analizeTopology(self, edge):
        selection = OpenMaya.MSelectionList()
        selection.add(edge)
        dagPathSelShape = OpenMaya.MDagPath()
        component = OpenMaya.MObject()
        iter = OpenMaya.MItSelectionList(selection)
        iter.getDagPath(dagPathSelShape, component)
        selectedEdges = OpenMaya.MItMeshEdge( dagPathSelShape, component)

        fnMesh = OpenMaya.MFnMesh(dagPathSelShape)
        pointCount = fnMesh.numVertices()
        edgeCount = fnMesh.numEdges()
        polyCount = fnMesh.numPolygons()

        baseObjectName = fnMesh.name()

        selectedEdges.reset()
        firstEdge = selectedEdges.index()
        prevIndex = 0
        mapArray = OpenMaya.MIntArray()
        sideArray = OpenMaya.MIntArray()


        checkedV = OpenMaya.MIntArray()
        sideV = OpenMaya.MIntArray()
        checkedP = OpenMaya.MIntArray()
        checkedE = OpenMaya.MIntArray()
        for x in range(pointCount):
            checkedV.append(-1)
            sideV.append(-1)

        for x in range(edgeCount):
            checkedE.append(-1)

        for x in range(polyCount):
            checkedP.append(-1)

        l_faceList = OpenMaya.MIntArray()
        r_faceList = OpenMaya.MIntArray()

        l_currentP = int(0)
        l_currentE = int(0)
        r_currentP = int(0)
        r_currentE = int(0)
        vertexIter = OpenMaya.MItMeshVertex(dagPathSelShape)
        polyIter = OpenMaya.MItMeshPolygon(dagPathSelShape)
        edgeIter = OpenMaya.MItMeshEdge(dagPathSelShape)

        l_edgeQueue = OpenMaya.MIntArray()
        r_edgeQueue = OpenMaya.MIntArray()


        l_edgeQueue.append(firstEdge)
        r_edgeQueue.append(firstEdge)

        scriptUtil = OpenMaya.MScriptUtil()
        ptr = scriptUtil.asIntPtr()
        l_edgeVertices = scriptUtil.asInt2Ptr() 
        r_edgeVertices = scriptUtil.asInt2Ptr() 
        l_ifCheckedVertices = scriptUtil.asInt2Ptr()
        r_faceEdgeVertices = scriptUtil.asInt2Ptr()
        
        l_faceEdges = []
        r_faceEdges = []
        l_faceEdgesCount = 0
        r_faceEdgesCount = 0

        faceEdgeComponent = OpenMaya.MObject()
        faceEdgeVtxComp = OpenMaya.MFnSingleIndexedComponent() 



        # create statusbar
        #
        statusWindow = cmds.window(title='Finding Opposite Vertices')
        cmds.columnLayout()

        progressControl = cmds.progressBar(maxValue=10, width=300)

        cmds.showWindow( statusWindow )
        stepsCount = 100
        cmds.progressBar( progressControl,
				        edit=True,
				        beginProgress=True,
				        isInterruptable=True,
				        status='Finding Mirrored Vertices',
				        maxValue=stepsCount )

        
        stepSize = (edgeCount/2) / 100
        stepIncrement = 0

        time0 = 0
        timeA = 0
        timeB = 0
        timeC = 0
        timeD = 0
        timeE = 0
        
        import time
        
        t = time.time()

        
        # get connected Edges from Faces
        #faceEdgeVtxComp = OpenMaya.MFnSingleIndexedComponent() 
        
        numPolys = fnMesh.numPolygons()
        connectedEdgesPerFaces = [None] * numPolys
        edges = OpenMaya.MIntArray()

        for i in range(numPolys):
            polyIter.setIndex(i, ptr)
            polyIter.getEdges(edges)
            connectedEdgesPerFaces[i] = list(edges)
            #print 'faces edges', i, edges

            """
            connectedEdgesPerFaces[i] = []
            
            faceEdgeComponent = faceEdgeVtxComp.create( OpenMaya.MFn.kMeshPolygonComponent ) #crash
            faceEdgeVtxComp.addElement(i)
            edgeIter = OpenMaya.MItMeshEdge(dagPathSelShape, faceEdgeComponent)
            connectedEdgesPerFaces[i] = []

            while not edgeIter.isDone(): 
                connectedEdgesPerFaces[i].append(edgeIter.index())
                edgeIter.next()
            """
        
        #print 'edge faces', connectedEdgesPerFaces
        #print 'getting edges per faces took this long:', (time.time() - t)


        
        while True:
            
            t = time.time()
            
            if l_edgeQueue.length() == 0:
                cmds.progressBar(progressControl, edit=True, endProgress=True)
                cmds.deleteUI(statusWindow, window = True)
                break

            # progressbar
            #
            stepIncrement += 1
            if stepIncrement >= stepSize:            
                cmds.progressBar(progressControl, edit=True, step=1)
                stepIncrement = 0


            l_currentE = l_edgeQueue[0]
            r_currentE = r_edgeQueue[0]

            l_edgeQueue.remove(0)
            r_edgeQueue.remove(0)

            checkedE[l_currentE] = r_currentE
            checkedE[r_currentE] = l_currentE        



            timeA += time.time() - t
            t = time.time()
            
            
            if l_currentE == r_currentE and l_currentE != firstEdge:
                continue

            # get the left face
            edgeIter.setIndex(l_currentE, ptr)
            edgeIter.getConnectedFaces(l_faceList)
            if len(l_faceList) == 1:
                l_currentP = l_faceList[0]
            elif checkedP[l_faceList[0]] == -1 and checkedP[l_faceList[1]] != -1: 
                l_currentP = l_faceList[0]
            elif checkedP[l_faceList[1]] == -1 and checkedP[l_faceList[0]] != -1:    
                l_currentP = l_faceList[1]
            elif checkedP[l_faceList[0]] == -1 and checkedP[l_faceList[1]] == -1:
                l_currentP = l_faceList[0]
                checkedP[l_currentP] = -2

            #get the right face
            edgeIter.setIndex(r_currentE, ptr)
            edgeIter.getConnectedFaces(r_faceList)
            if len(r_faceList) == 1:
                r_currentP = r_faceList[0]
            elif checkedP[r_faceList[0]] == -1 and checkedP[r_faceList[1]] != -1:
                r_currentP = r_faceList[0]
            elif checkedP[r_faceList[1]] == -1 and checkedP[r_faceList[0]] != -1:
                r_currentP = r_faceList[1]
            elif checkedP[r_faceList[1]] == -1 and checkedP[r_faceList[0]] == -1:
                return OpenMaya.MStatus.kFailure
            elif checkedP[r_faceList[1]] != -1 and checkedP[r_faceList[0]] != -1:
                continue

            checkedP[r_currentP] = l_currentP
            checkedP[l_currentP] = r_currentP                

            fnMesh.getEdgeVertices(l_currentE, l_edgeVertices) 
            l_edgeVertices0 = scriptUtil.getInt2ArrayItem(l_edgeVertices, 0, 0)
            l_edgeVertices1 = scriptUtil.getInt2ArrayItem(l_edgeVertices, 0, 1)

            fnMesh.getEdgeVertices(r_currentE, r_edgeVertices)
            r_edgeVertices0 = scriptUtil.getInt2ArrayItem(r_edgeVertices, 0, 0)
            r_edgeVertices1 = scriptUtil.getInt2ArrayItem(r_edgeVertices, 0, 1)

            timeB += time.time() - t
            t = time.time()

            if l_currentE == firstEdge:
                r_edgeVertices0 = scriptUtil.getInt2ArrayItem(r_edgeVertices, 0, 0)
                r_edgeVertices1 = scriptUtil.getInt2ArrayItem(r_edgeVertices, 0, 1)
                l_edgeVertices0 = scriptUtil.getInt2ArrayItem(l_edgeVertices, 0, 0)
                l_edgeVertices1 = scriptUtil.getInt2ArrayItem(l_edgeVertices, 0, 1)

                checkedV[l_edgeVertices0] = r_edgeVertices0  
                checkedV[l_edgeVertices1] = r_edgeVertices1  
                checkedV[r_edgeVertices0] = l_edgeVertices0  
                checkedV[r_edgeVertices1] = l_edgeVertices1  
            else:
                if checkedV[l_edgeVertices0] == -1 and checkedV[r_edgeVertices0] == -1:
                    checkedV[l_edgeVertices0] = r_edgeVertices0
                    checkedV[r_edgeVertices0] = l_edgeVertices0
                if checkedV[l_edgeVertices1] == -1 and checkedV[r_edgeVertices1] == -1:
                    checkedV[l_edgeVertices1] = r_edgeVertices1
                    checkedV[r_edgeVertices1] = l_edgeVertices1
                if checkedV[l_edgeVertices0] == -1 and checkedV[r_edgeVertices1] == -1:
                    checkedV[l_edgeVertices0] = r_edgeVertices1
                    checkedV[r_edgeVertices1] = l_edgeVertices0
                if checkedV[l_edgeVertices1] == -1 and checkedV[r_edgeVertices0] == -1:
                    checkedV[l_edgeVertices1] = r_edgeVertices0
                    checkedV[r_edgeVertices0] = l_edgeVertices1


            sideV[l_edgeVertices0] = 2
            sideV[l_edgeVertices1] = 2
            sideV[r_edgeVertices0] = 1 
            sideV[r_edgeVertices1] = 1
            
            
            
            timeC += time.time() - t
            t = time.time()

            r_faceEdgesCount = 0
            for edge in connectedEdgesPerFaces[r_currentP]:
                if len(r_faceEdges) > r_faceEdgesCount:
                    r_faceEdges[r_faceEdgesCount] = edge
                else:
                    r_faceEdges.append(edge)
                r_faceEdgesCount += 1   

            l_faceEdgesCount = 0
            for edge in connectedEdgesPerFaces[l_currentP]:
                if len(l_faceEdges) > l_faceEdgesCount:
                    l_faceEdges[l_faceEdgesCount] = edge
                else:
                    l_faceEdges.append(edge)
                l_faceEdgesCount += 1   
            

            l_checkedVertex = 0
            l_nonCheckedVertex = 0
            
            
            timeD += time.time() - t
            t = time.time()

            for i in range(l_faceEdgesCount):

                if checkedE[l_faceEdges[i]] == -1:

                    edgeIter.setIndex(l_currentE, ptr)

                    if edgeIter.connectedToEdge(l_faceEdges[i]) and l_currentE != l_faceEdges[i]:

                        fnMesh.getEdgeVertices(l_faceEdges[i], l_ifCheckedVertices)
                        l_ifCheckedVertice0 = scriptUtil.getInt2ArrayItem(l_ifCheckedVertices, 0, 0)
                        l_ifCheckedVertice1 = scriptUtil.getInt2ArrayItem(l_ifCheckedVertices, 0, 1)
                        if l_ifCheckedVertice0 == l_edgeVertices0 or l_ifCheckedVertice0 == l_edgeVertices1:
                            l_checkedVertex = l_ifCheckedVertice0
                            l_nonCheckedVertex = l_ifCheckedVertice1 
                        elif l_ifCheckedVertice1 == l_edgeVertices0 or l_ifCheckedVertice1 == l_edgeVertices1:
                            l_checkedVertex = l_ifCheckedVertice1
                            l_nonCheckedVertex = l_ifCheckedVertice0
                        else:
                            continue

                        for k in range(r_faceEdgesCount):
                            edgeIter.setIndex(r_currentE, ptr)  
                            if edgeIter.connectedToEdge(r_faceEdges[k]) and r_currentE != r_faceEdges[k]:
                                fnMesh.getEdgeVertices(r_faceEdges[k], r_faceEdgeVertices)
                                r_faceEdgeVertice0 = scriptUtil.getInt2ArrayItem(r_faceEdgeVertices, 0, 0)
                                r_faceEdgeVertice1 = scriptUtil.getInt2ArrayItem(r_faceEdgeVertices, 0, 1)

                                if r_faceEdgeVertice0 == checkedV[l_checkedVertex]: 
                                    checkedV[l_nonCheckedVertex] = r_faceEdgeVertice1
                                    checkedV[r_faceEdgeVertice1] = l_nonCheckedVertex
                                    sideV[l_nonCheckedVertex] = 2
                                    sideV[r_faceEdgeVertice1] = 1
                                    l_edgeQueue.append(l_faceEdges[i])
                                    r_edgeQueue.append(r_faceEdges[k])    


                                if r_faceEdgeVertice1 == checkedV[l_checkedVertex]: 
                                    checkedV[l_nonCheckedVertex] = r_faceEdgeVertice0
                                    checkedV[r_faceEdgeVertice0] = l_nonCheckedVertex
                                    sideV[l_nonCheckedVertex] = 2
                                    sideV[r_faceEdgeVertice0] = 1
                                    l_edgeQueue.append(l_faceEdges[i])
                                    r_edgeQueue.append(r_faceEdges[k])
                                    

            timeE += time.time() - t
            t = time.time()


        #print 'timeA:', timeA, 'timeB:', timeB, 'timeC:', timeC, 'timeD:', timeD, 'timeE:', timeE, 

        xAverage2 = 0
        xAverage1 = 0
        checkPosPoint = OpenMaya.MPoint() 
        for i in range(pointCount):
            if checkedV[i] != i and checkedV[i] != -1:
                fnMesh.getPoint ( checkedV[i], checkPosPoint)
                if sideV[i] == 2:
                    xAverage2 += checkPosPoint.x
                if sideV[i] == 1:
                    xAverage1 += checkPosPoint.x


        switchSide =  xAverage2 < xAverage1 

        for i in range(pointCount):
            mapArray.append(checkedV[i])
            if checkedV[i] != i:
                if not switchSide:
                    sideArray.append(sideV[i])
                else:
                    if sideV[i] == 2:
                        sideArray.append(1)
                    else:
                        sideArray.append(2)
            else:
                sideArray.append(0)



        for i in range(len(mapArray)):
            if mapArray[i] == -1:
                mapArray[i] = i

        return mapArray, sideArray, baseObjectName


 
 
def cmdCreator():
    return OpenMayaMPx.asMPxPtr( EdgeFlowMirrorCommand() )
 
 
def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Thomas Bittner", "3.3", "Any")
    try:
        mplugin.registerCommand( kPluginCmdName, cmdCreator)
    except:
        sys.stderr.write( "Failed to register command: %s\n" % kPluginCmdName )
        raise
 
 
def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand( kPluginCmdName )
    except:
        sys.stderr.write( "Failed to unregister command: %s\n" % kPluginCmdName )
        raise
 
def swap(indexA, indexB, inList):
    temp = inList[indexA]
    inList[indexA] = inList[indexB]
    inList[indexB] = temp
    return inList


def getDagPath(name):
    sel = OpenMaya.MSelectionList()
    sel.add(name);
    obj = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    sel.getDagPath (0, obj, component )
    return obj


def intArrayToList(array):
    newList = [0] * len(array)
    for i in range(len(array)):
        newList[i] = array[i]
    return newList


def pointStr(point):
    return point.x, point.y, point.z
    
def printMatrix(matrix):
    print matrix(0,0), matrix(0,1), matrix(0,2), matrix(0,3)
    print matrix(1,0), matrix(1,1), matrix(1,2), matrix(1,3)
    print matrix(2,0), matrix(2,1), matrix(2,2), matrix(2,3)
    print matrix(3,0), matrix(3,1), matrix(3,2), matrix(3,3)


def createMatrixFromPos(pos):
    mat = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList( [1,0,0,0,  0,1,0,0,  0,0,1,0,  pos.x,pos.y,pos.z,1], mat )
    return mat

def createMatrixFromList(matList):
    mat = OpenMaya.MMatrix()
    OpenMaya.MScriptUtil.createMatrixFromList( matList, mat )
    return mat


