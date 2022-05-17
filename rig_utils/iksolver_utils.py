"""
iksolver_utils.py manipulating and retrieving information from ikSolvers.
"""
from maya import OpenMaya, OpenMayaAnim, cmds
# import local modules
from maya_utils import name_utils, node_utils, object_utils, transform_utils, curve_utils


class IkSolver(node_utils.Node):
    def __init__(self, **kwargs):
        super(IkSolver, self).__init__(**kwargs)
        self.dag_mod = OpenMaya.MDagModifier()
        if not self.suffix_name:
            self.suffix_name = self.naming_convention['ik_handle']
        # get the name with the updated suffix name parameter
        self.name = self.get_name(suffix_name=self.suffix_name)
        # properties
        self.effector = None
        self.__solver = None
        self.__sticky = None
        if not kwargs.get('solver'):
            self.__solver = 'ikRPsolver'
        else:
            self.__solver = kwargs.get('solver')
        self.__first_joint = kwargs.get('first_joint')
        self.__last_joint = kwargs.get('last_joint')
        # create if exists
        if not self.exists:
            self.node = self.name
            self.create()

    def create(self, mfn_dag=False):
        if not self.exists:
            # if mfn_dag:
            #     # The first joint has no parent.
            #     ik_obj = self.dag_mod.createNode('ikHandle')
            #     # rename the joint using OpenMaya
            #     self.dag_mod.renameNode(ik_obj, self.name)
            #     self.dag_mod.doIt()
            # else:
            cmds.select(d=True)  # deselect first before creating any joints
            if self.__solver == 'ikRPsolver':
                self.node, self.effector = cmds.ikHandle(name=self.name, sj=self.__first_joint, ee=self.__last_joint,
                                                         solver='ikRPsolver', setupForRPsolver=True)
            if self.__solver == 'ikSCsolver':
                self.node, self.effector = cmds.ikHandle(name=self.name, sj=self.__first_joint, ee=self.__last_joint,
                                                         solver='ikSCsolver', setupForRPsolver=False)
    @property
    def sticky(self):
        return self.__sticky

    @sticky.setter
    def sticky(self, stickiness):
        """
        accepted arguments: ikRPsolver, ikSCsolver and ikSplineSolver.
        :param stickiness: <bool> stickiness boolean attribute to use.
        """
        self.__sticky = stickiness
        cmds.setAttr(self.node + '.stickiness', stickiness)
        return self.__sticky
# ______________________________________________________________________________________________________________________
# iksolver_utils.py
