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
# standard modules
import os
import os.path

# maya modules
import maya.mel
import maya.cmds as cmds
import maya.OpenMayaUI as mui


try:
    from PySide import QtCore, QtGui as widgets
    import shiboken

    def getMayaWindow():
        ptr = mui.MQtUtil.mainWindow()
        return shiboken.wrapInstance(long(ptr), widgets.QWidget)

except ImportError:
    from PySide2 import QtCore, QtWidgets as widgets
    import shiboken2

    def getMayaWindow():
        ptr = mui.MQtUtil.mainWindow()
        return shiboken2.wrapInstance(long(ptr), widgets.QWidget)




# change this path to the location of your plugin:
#

cur_path = os.path.dirname(os.path.abspath(__file__))
edgeFlowMirrorPluginFile = '{}/edgeFlowMirror.py'.format(cur_path)


def edgeFlowMirror_loadPlugin():
    if not cmds.pluginInfo('edgeFlowMirror', query=True,loaded=True):
        if os.path.isfile(edgeFlowMirrorPluginFile):
            cmds.loadPlugin(edgeFlowMirrorPluginFile)
        else:
            cmds.error('cant find plugin, change %s to match your file (including path)' % edgeFlowMirrorPluginFile)

edgeFlowMirror_loadPlugin()

mainWin = None


def showUI():
    global mainWin

    if mainWin != None:
        print("reloading UI...")
        mainWin.close()

    mainWin = edgeFlowMirrorUI()
    mainWin.show()


class edgeFlowMirrorUI(widgets.QDialog):
    def createFixedLabel(self, caption, width=100):
        label = widgets.QLabel(caption, parent=self)
        label.setFixedSize(width,10)
        return label

    def __init__(self, parent=getMayaWindow()):
        super(edgeFlowMirrorUI, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)

        middleEdgeLayout =  widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        middleEdgeLabel = widgets.QLabel('Middle Edge:', parent=self)
        self.middleEdgeLine = widgets.QLineEdit('', parent=self)
        self.middleEdgeLine.setDisabled(True)
        self.middleEdgeButton = widgets.QPushButton("Set Middle Edge", parent=self)
        self.middleEdgeRecomputeButton = widgets.QPushButton("Recompute", parent=self)
        self.middleEdgeDoOptimize = widgets.QCheckBox("Optimize", parent=self)
        self.middleEdgeDoOptimize.setChecked(True)
        middleEdgeLayout.addWidget(middleEdgeLabel)
        middleEdgeLayout.addWidget(self.middleEdgeLine)
        middleEdgeLayout.addWidget(self.middleEdgeButton)
        middleEdgeLayout.addWidget(self.middleEdgeRecomputeButton)
        middleEdgeLayout.addWidget(self.middleEdgeDoOptimize)



        tab_widget = widgets.QTabWidget()
        skinClusterTab = widgets.QWidget()
        geometryTab = widgets.QWidget()
        selectionTab = widgets.QWidget()
        deformersTab = widgets.QWidget()
        blendShapeTab = widgets.QWidget()


        tab_widget.addTab(skinClusterTab, "SkinCluster")
        tab_widget.addTab(geometryTab, "Geometry")
        tab_widget.addTab(selectionTab, "Component Selection")
        tab_widget.addTab(deformersTab, "Deformer Weights")
        tab_widget.addTab(blendShapeTab, "BlendShape Targets")
        self.descLabel = widgets.QLabel("(C) 2007 - 2016 by Thomas Bittner", parent=self)
        self.setWindowTitle('edgeFlowMirror 3.4')

        # skinCluster
        #
        skinClusterLayout = widgets.QVBoxLayout(skinClusterTab)
        skinClusterLayout.setAlignment(QtCore.Qt.AlignTop)
        skinClusterLayout.setSpacing(3)

        self.mirrorSkinClusterLeftToRightButton = widgets.QPushButton("left>right", parent=self)
        self.mirrorSkinClusterRightToLeftButton = widgets.QPushButton("right>left", parent=self)


        MirrorWeightsLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        MirrorWeightsLayout.addWidget(self.createFixedLabel('Mirror Weights:', width = 120))
        MirrorWeightsLayout.addWidget(self.mirrorSkinClusterLeftToRightButton)
        MirrorWeightsLayout.addWidget(self.mirrorSkinClusterRightToLeftButton)
        skinClusterLayout.addLayout(MirrorWeightsLayout)

        leftJointsPrefixLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        leftJointsPrefixLayout.addWidget(self.createFixedLabel('left joints prefix', width = 120))
        self.leftJointsPrefixLine = widgets.QLineEdit('l_', parent=self)
        leftJointsPrefixLayout.addWidget(self.leftJointsPrefixLine)
        skinClusterLayout.addLayout(leftJointsPrefixLayout)

        rightJointsPrefixLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        rightJointsPrefixLayout.addWidget(self.createFixedLabel('right joints prefix', width = 120))
        self.rightJointsPrefixLine = widgets.QLineEdit('r_', parent=self)
        rightJointsPrefixLayout.addWidget(self.rightJointsPrefixLine)
        skinClusterLayout.addLayout(rightJointsPrefixLayout)

        self.mirrorSkinClusterBlendWeightsLeftToRightButton = widgets.QPushButton("left>right", parent=self)
        self.mirrorSkinClusterBlendWeightsRightToLeftButton = widgets.QPushButton("right>left", parent=self)


        MirrorBlendWeightsLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        MirrorBlendWeightsLayout.addWidget(self.createFixedLabel('Mirror Blend Weights:', width = 120))
        MirrorBlendWeightsLayout.addWidget(self.mirrorSkinClusterBlendWeightsLeftToRightButton)
        MirrorBlendWeightsLayout.addWidget(self.mirrorSkinClusterBlendWeightsRightToLeftButton)
        skinClusterLayout.addLayout(MirrorBlendWeightsLayout)




        # geometry
        #
        geometryLayout = widgets.QVBoxLayout(geometryTab)
        geometryLayout.setAlignment(QtCore.Qt.AlignTop)
        geometryLayout.setSpacing(3)

        self.baseMeshLine = widgets.QLineEdit('', parent=self)
        self.selectBaseMeshButton = widgets.QPushButton("selected", parent=self)
        baseMeshLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        baseMeshLayout.addWidget(self.createFixedLabel('Base Mesh:'))
        baseMeshLayout.addWidget(self.baseMeshLine)
        baseMeshLayout.addWidget(self.selectBaseMeshButton)
        geometryLayout.addLayout(baseMeshLayout)

        self.doGeometryVertexSpace = widgets.QCheckBox("calculate offset in Space of surrounding faces of Base Mesh", parent=self)
        geometryLayout.addWidget(self.doGeometryVertexSpace)



        MirrorMeshLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        MirrorMeshLayout.addWidget(self.createFixedLabel('Mirror Mesh:'))
        self.mirrorMeshLeftToRightButton = widgets.QPushButton("left>right", parent=self)
        self.mirrorMeshRightToLeftButton = widgets.QPushButton("right>left", parent=self)
        MirrorMeshLayout.addWidget(self.mirrorMeshLeftToRightButton)
        MirrorMeshLayout.addWidget(self.mirrorMeshRightToLeftButton)
        geometryLayout.addLayout(MirrorMeshLayout)

        FlipMeshButtonLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        FlipMeshButtonLayout.addWidget(self.createFixedLabel('Flip Mesh:'))
        self.FlipMeshButton = widgets.QPushButton("right<>left", parent=self)
        FlipMeshButtonLayout.addWidget(self.FlipMeshButton)
        geometryLayout.addLayout(FlipMeshButtonLayout)


        symmetrySeparator = widgets.QFrame()
        symmetrySeparator.setFrameShape(widgets.QFrame.HLine)
        symmetrySeparator.setFrameShadow(widgets.QFrame.Sunken)
        geometryLayout.addWidget(symmetrySeparator)

        SymmetryMeshButtonLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        SymmetryMeshButtonLayout.addWidget(self.createFixedLabel('Symmetry Mesh:'))
        self.SymmetryMeshButton = widgets.QPushButton("right<>left", parent=self)
        SymmetryMeshButtonLayout.addWidget(self.SymmetryMeshButton)
        geometryLayout.addLayout(SymmetryMeshButtonLayout)

        # selection
        #
        selectionLayout = widgets.QVBoxLayout(selectionTab)
        selectionLayout.setAlignment(QtCore.Qt.AlignTop)
        selectionLayout.setSpacing(3)

        self.flipSelectionButton = widgets.QPushButton("left<>right", parent=self)
        selectionFlipLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        selectionFlipLayout.addWidget(self.createFixedLabel('flip:'))
        selectionFlipLayout.addWidget(self.flipSelectionButton)
        selectionLayout.addLayout(selectionFlipLayout)

        self.mirrorSelectionButton = widgets.QPushButton("left<>right", parent=self)
        selectionmirrorLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        selectionmirrorLayout.addWidget(self.createFixedLabel('add other sides:'))
        selectionmirrorLayout.addWidget(self.mirrorSelectionButton)
        selectionLayout.addLayout(selectionmirrorLayout)


        Mirror2SelectionLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        Mirror2SelectionLayout.addWidget(self.createFixedLabel('Mirror Selection:'))
        self.mirrorSelectionLeftToRightButton = widgets.QPushButton("left>right", parent=self)
        self.mirrorSelectionRightToLeftButton = widgets.QPushButton("right>left", parent=self)
        Mirror2SelectionLayout.addWidget(self.mirrorSelectionLeftToRightButton)
        Mirror2SelectionLayout.addWidget(self.mirrorSelectionRightToLeftButton)
        selectionLayout.addLayout(Mirror2SelectionLayout)



        self.layout = widgets.QBoxLayout(widgets.QBoxLayout.TopToBottom, self)
        self.layout.addLayout(middleEdgeLayout)
        self.layout.addWidget(tab_widget)
        self.layout.addWidget(self.descLabel)
        self.resize(600, 10)



        # blendShape
        #
        blendShapeLayout = widgets.QVBoxLayout(blendShapeTab)
        blendShapeLayout.setAlignment(QtCore.Qt.AlignTop)
        blendShapeLayout.setSpacing(3)

        self.blendShapeLine = widgets.QLineEdit('', parent=self)
        self.selectBlendShapeButton = widgets.QPushButton("selected", parent=self)
        blendShapeNodeLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        blendShapeNodeLayout.addWidget(widgets.QLabel('blendShape:', parent=self))
        blendShapeNodeLayout.addWidget(self.blendShapeLine)
        blendShapeNodeLayout.addWidget(self.selectBlendShapeButton)
        blendShapeLayout.addLayout(blendShapeNodeLayout)

        self.targetList = widgets.QListWidget(parent=self)
        self.targetList.setSelectionMode(widgets.QAbstractItemView.ExtendedSelection)
        blendShapeLayout.addWidget(self.targetList)


        MirrorBlendShapeTargetLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        MirrorBlendShapeTargetLayout.addWidget(self.createFixedLabel('Mirror Marked Targets', width=130))
        self.MirrorBlendShapeTargetLeftToRightButton = widgets.QPushButton("left>right", parent=self)
        self.MirrorBlendShapeTargetRightToLeftButton = widgets.QPushButton("right>left", parent=self)
        MirrorBlendShapeTargetLayout.addWidget(self.MirrorBlendShapeTargetLeftToRightButton)
        MirrorBlendShapeTargetLayout.addWidget(self.MirrorBlendShapeTargetRightToLeftButton)
        blendShapeLayout.addLayout(MirrorBlendShapeTargetLayout)

        FlipBlendShapeTargetButtonLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        FlipBlendShapeTargetButtonLayout.addWidget(self.createFixedLabel('Flip Marked Targets:',  width=130))
        self.FlipBlendShapeTargetButton = widgets.QPushButton("right<>left", parent=self)
        FlipBlendShapeTargetButtonLayout.addWidget(self.FlipBlendShapeTargetButton)
        blendShapeLayout.addLayout(FlipBlendShapeTargetButtonLayout)

        # deformers
        #
        deformersLayout = widgets.QVBoxLayout(deformersTab)
        deformersLayout.setAlignment(QtCore.Qt.AlignTop)
        deformersLayout.setSpacing(3)

        MirrorBlendShapeNodeLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        MirrorBlendShapeNodeLayout.addWidget(self.createFixedLabel('Mirror Selected Deformer Weights', width=180))
        self.MirrorDeformerLeftToRightButton = widgets.QPushButton("left>right", parent=self)
        self.MirrorDeformerRightToLeftButton = widgets.QPushButton("right>left", parent=self)
        MirrorBlendShapeNodeLayout.addWidget(self.MirrorDeformerLeftToRightButton)
        MirrorBlendShapeNodeLayout.addWidget(self.MirrorDeformerRightToLeftButton)
        deformersLayout.addLayout(MirrorBlendShapeNodeLayout)

        FlipBlendShapeNodeButtonLayout = widgets.QBoxLayout(widgets.QBoxLayout.LeftToRight)
        FlipBlendShapeNodeButtonLayout.addWidget(self.createFixedLabel('Flip Selected Deformer Weights:', width=180))
        self.FlipBlendShapeNodeButton = widgets.QPushButton("right<>left", parent=self)
        FlipBlendShapeNodeButtonLayout.addWidget(self.FlipBlendShapeNodeButton)    
        deformersLayout.addLayout(FlipBlendShapeNodeButtonLayout)


        
        #connect buttons
        self.connect(self.middleEdgeButton, QtCore.SIGNAL("clicked()"), self.middleEdgeButtonClicked)        
        self.connect(self.middleEdgeRecomputeButton, QtCore.SIGNAL("clicked()"), self.middleEdgeButtonRecomputeClicked)        
        self.connect(self.selectBaseMeshButton, QtCore.SIGNAL("clicked()"), self.selectBaseMeshButtonClicked)        
        self.connect(self.middleEdgeDoOptimize, QtCore.SIGNAL("clicked(bool)"), self.middleEdgeOptimizeToggled)        




        self.connect(self.mirrorSkinClusterLeftToRightButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorSkinCluster(1))
        self.connect(self.mirrorSkinClusterRightToLeftButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorSkinCluster(2))
        self.connect(self.mirrorSkinClusterBlendWeightsLeftToRightButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorSkinClusterBlend(1))
        self.connect(self.mirrorSkinClusterBlendWeightsRightToLeftButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorSkinClusterBlend(2))

        self.connect(self.mirrorMeshLeftToRightButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorMesh("geometryMirror", 1))
        self.connect(self.mirrorMeshRightToLeftButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorMesh("geometryMirror", 2))
        self.connect(self.FlipMeshButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorMesh("geometryFlip", 1))
        self.connect(self.SymmetryMeshButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorMesh("geometrySymmetry", 0))
        
        self.connect(self.flipSelectionButton, QtCore.SIGNAL("clicked()"), lambda: self.selectMirroredComponents(1, self.middleEdgeDoOptimize.isChecked()))
        self.connect(self.mirrorSelectionButton, QtCore.SIGNAL("clicked()"), lambda: self.selectMirroredComponents(0, self.middleEdgeDoOptimize.isChecked()))

        self.connect(self.mirrorSelectionLeftToRightButton, QtCore.SIGNAL("clicked()"), lambda: self.selectMirroredComponents(2, self.middleEdgeDoOptimize.isChecked(), 2))
        self.connect(self.mirrorSelectionRightToLeftButton, QtCore.SIGNAL("clicked()"), lambda: self.selectMirroredComponents(2, self.middleEdgeDoOptimize.isChecked(), 1))

        
        self.connect(self.selectBlendShapeButton, QtCore.SIGNAL("clicked()"), self.updateBlendShapeNode)
        self.connect(self.FlipBlendShapeTargetButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorWeightMap(self.blendShapeLine.text(), "flip", 0, self.listItemsToTexts(self.targetList.selectedItems()), self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked()))
        self.connect(self.MirrorBlendShapeTargetLeftToRightButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorWeightMap(self.blendShapeLine.text(), "mirror", 1, self.listItemsToTexts(self.targetList.selectedItems()), self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked()))
        self.connect(self.MirrorBlendShapeTargetRightToLeftButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorWeightMap(self.blendShapeLine.text(), "mirror", 2, self.listItemsToTexts(self.targetList.selectedItems()), self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked()))

        self.connect(self.FlipBlendShapeNodeButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorWeightMap(self.getSelectedDeformer(), "flip", 0, None, self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked()))
        self.connect(self.MirrorDeformerLeftToRightButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorWeightMap(self.getSelectedDeformer(), "mirror", 1, None, self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked()))
        self.connect(self.MirrorDeformerRightToLeftButton, QtCore.SIGNAL("clicked()"), lambda: self.mirrorWeightMap(self.getSelectedDeformer(), "mirror", 2, None, self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked()))


    def getSelectedDeformer(self):
        sel = cmds.ls(sl=True)
        for obj in sel:
            if cmds.attributeQuery('weightList', node = obj, exists = True):
                return obj

            #typ = cmds.objectType(obj) 
            #if typ == 'cluster' or typ == 'jiggle' or typ == 'blendShape' or typ == 'shrinkWrap':
            #    return obj
            


    def listItemsToTexts(self, items):
        length = len(items)
        newList = [''] * length
        for i in range(length):
            newList[i] = items[i].text()
            
        print 'getting the list: ', newList
        return newList

    def middleEdgeButtonClicked(self):
        sel = cmds.ls(sl=True, flatten=True)

        if not sel or not len(sel) or '.e[' not in sel[0]:
            raise RuntimeError ('select one of the middle edges of the model')
            return

        edge = str(sel[0])
        
        
        self.middleEdgeLine.setText(edge)
        
        if self.middleEdgeDoOptimize.isChecked():
            cmds.select(self.getComponentTokens(edge)[0])
            cmds.edgeFlowMirror(task = 'compute', middleEdge = edge)

    def middleEdgeButtonRecomputeClicked(self):
        edge = self.middleEdgeLine.text()
        cmds.select(self.getComponentTokens(edge)[0])
        cmds.edgeFlowMirror(task = 'compute', middleEdge = edge)


    def middleEdgeOptimizeToggled(self, isOn):
        edge = self.middleEdgeLine.text()
        
        if isOn and len(edge):
            cmds.select(self.getComponentTokens(edge)[0])    
            cmds.edgeFlowMirror(task = 'compute', middleEdge = edge)
        
    def selectBaseMeshButtonClicked(self):
        sel = cmds.ls(sl=True)
        self.baseMeshLine.setText(sel[0])

    def mirrorSkinCluster(self, inDirection):
        cmds.edgeFlowMirror(task = "skinCluster", direction = inDirection, middleEdge = self.middleEdgeLine.text(), rightJointsPrefix = self.leftJointsPrefixLine.text(), leftJointsPrefix = self.rightJointsPrefixLine.text(), optimize = self.middleEdgeDoOptimize.isChecked())

    def mirrorMesh(self, inTask, inDirection):
        cmds.edgeFlowMirror(task = inTask, direction = inDirection, middleEdge = self.middleEdgeLine.text(), baseObject = self.baseMeshLine.text(), optimize = self.middleEdgeDoOptimize.isChecked(), baseVertexSpace = self.doGeometryVertexSpace.isChecked())


    def updateBlendShapeNode(self):
        print 'update blendshapeNode'
        sel = cmds.ls(sl=True)
        
        for obj in sel:
            if cmds.objectType(obj) == 'blendShape':
                self.blendShapeLine.setText(obj)
                
                self.targetList.clear()
                
                attrs = cmds.aliasAttr(obj, q=True)
                print attrs
                attrCount = len(attrs)/2

                self.targetList.insertItem(0, '_Baseweights')
                for i in range(attrCount):
                    self.targetList.insertItem(i + 1, attrs[i*2])
                    weightAttr = attrs[i*2 + 1]
                
                return
        raise RuntimeError('no blendshape selected')



    def mirrorSkinClusterBlend(self, inDirection):
        sel = cmds.ls(sl=True)
        skinCluster = maya.mel.eval('findRelatedSkinCluster %s' % sel[0])
        self.mirrorWeightMap(skinCluster, 'mirror', inDirection, '', self.middleEdgeLine.text(), self.middleEdgeDoOptimize.isChecked(), overwriteWeightmap = 'blendWeights')
        

    def mirrorWeightMap(self, node, inTask, inDirection, blendshapeTargets, inMiddleEdge, doOptimize, overwriteWeightmap = ''):
        print 'node: ', node
        if not inMiddleEdge:
            raise RuntimeError ('no middle edge selected')
                        
        typ = cmds.objectType(node)
        #obj = cmds.listConnections ('%s.outputGeometry[0]' % node)[0]
        obj = inMiddleEdge.split('.')[0]
        vertexCount = cmds.polyEvaluate(obj, vertex=True)
        
        oldSelection = cmds.ls(sl=True)
        
        cmds.select(obj)


        if inTask != 'mirror':
            mapArray = cmds.edgeFlowMirror(task = 'getMapArray', middleEdge = inMiddleEdge, optimize = doOptimize)
        else:
            mapArray = cmds.edgeFlowMirror(task = 'getMapSideArray', middleEdge = inMiddleEdge, optimize = doOptimize)

        if not blendshapeTargets:
            blendshapeTargets = ['']
            
        for target in blendshapeTargets:
            if target == '':
                if len(overwriteWeightmap):
                    attr = '%s.%s[0:%d]' % (node, overwriteWeightmap, vertexCount-1)
                elif typ == 'blendShape':
                    attr = '%s.inputTarget[0].baseWeights[0:%d]' % (node, vertexCount-1)
                else:
                    attr = '%s.weightList[0].weights[0:%d]' % (node, vertexCount-1)
            elif target == '_Baseweights': 
                attr = '%s.inputTarget[0].baseWeights[0:%d]' % (node, vertexCount-1)
            else: # we are dealing with blendShape targets
                aliases = cmds.aliasAttr(node, q=True)                
                for i in range(len(aliases)/2):
                    if aliases[i*2] == target:
                        targetIndex = int(aliases[i*2+1].split('[')[1].split(']')[0])

                attr = '%s.inputTarget[0].inputTargetGroup[%d].targetWeights[0:%d]' % (node, targetIndex, vertexCount-1)
                
            originWeights = cmds.getAttr(attr)

            newWeights = [0] * vertexCount

            if inTask == 'flip':
                for i in range(len(newWeights)):    
                    newWeights[i] = originWeights[mapArray[i]]
            elif inTask == 'mirror':
                if inDirection == 2:
                    for i in range(len(newWeights)):    
                        if mapArray[vertexCount + i] == 1:
                            newWeights[i] = originWeights[mapArray[i]]
                        else:
                            newWeights[i] = originWeights[i]
                elif inDirection == 1:
                    for i in range(len(newWeights)):    
                        if mapArray[vertexCount + i] == 2:
                            newWeights[i] = originWeights[mapArray[i]]
                        else:
                            newWeights[i] = originWeights[i]

            cmds.setAttr(attr, *newWeights)
            cmds.select(oldSelection)



    def getComponentTokens(self, component):
        toks = component.split('.')
        toks1 = toks[1].split('[')
        toks2 = toks1[-1].split(']')
        return toks[0], toks[1], int(toks2[0])
        

    def selectMirroredComponents(self, flip, doOptimize, direction=0):
    
        print 'mirror component selection: ', flip, ', direction: ', direction
    
        sel = cmds.ls(sl=True, flatten=True)

        polyListConverted = cmds.polyListComponentConversion(sel, tv=True)
        cmds.select(polyListConverted)

        middleEdge = self.middleEdgeLine.text()
        mapArray = cmds.edgeFlowMirror(task = 'getMapSideArray', middleEdge = self.middleEdgeLine.text(), optimize = doOptimize )
        vertexCount = len(mapArray) / 2

        
        cmds.select(sel)


        selArray = []

        if flip is 0: #simply add them to the other side
            selArray = sel
        selArray = []

        for i in range(len(sel)):
            if '.vtx' in sel[i]:
                componentTokens = self.getComponentTokens(sel[i])
                index = int(componentTokens[2])
                doThis = False
                
                if flip != 2:
                    doThis = True
                elif mapArray[vertexCount + index] == 2 and direction == 1:
                    doThis = True
                elif mapArray[vertexCount + index] == 1 and direction == 2:
                    doThis = True
                
                if doThis:
                    selArray.append('%s.vtx[%s]' % (componentTokens[0], mapArray[index]))
                    if flip != 1:
                        selArray.append('%s.vtx[%s]' % (componentTokens[0], index))
                elif flip == 2 and mapArray[vertexCount + index] == 0:
                    selArray.append('%s.vtx[%s]' % (componentTokens[0], index))
                    
            
            else: #edge or face
                if '.e' in sel[i]:
                    isEdge = True
                elif '.f' in sel[i]:
                    isEdge = False
                else:
                    continue
                
                verts = cmds.polyListComponentConversion(sel[i], fe = isEdge, ff = (isEdge==False), tv=True)
                verts = cmds.ls(verts, flatten=True)

                mirrorVerts = []
                    
                for k in range(len(verts)):
                    componentTokens = self.getComponentTokens(verts[k])
                    index = componentTokens[2]
                    if flip == 2:
                        if mapArray[vertexCount + index] == 2 and direction == 2:
                            continue
                        elif mapArray[vertexCount + index] == 1 and direction == 1:
                            continue
                            
                    mirrorVerts.append('%s.vtx[%d]' % (componentTokens[0], mapArray[index]))
                    if flip != 1:
                        mirrorVerts.append('%s.vtx[%d]' % (componentTokens[0], index))
                
                for obj in cmds.polyListComponentConversion(mirrorVerts, fv = True, te = isEdge, tf = (isEdge==False), internal=True):
                    selArray.append(obj)


        cmds.select(selArray)

