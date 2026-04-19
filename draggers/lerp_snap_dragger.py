"""
Lerp snap dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, attribute_utils
from dragger_tools import ICONS


class LerpSnapDragger(dragger_utils.Dragger):
    """
    Lerp objects towards first selection
    You can use translate, rotate, scale bool parameters from math_utils.lerp_matrix() to define what gets lerped
    """
    NAME = "Lerp Snap Dragger"
    TITLE = "Lerp Snap Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    ICON = f"{ICONS}/lerpsnapdragger.png"

    def __init__(self, *args, **kwargs):
        super(LerpSnapDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) < 2:
            maya_utils.message("Not enough nodes selected. Select at least 2 nodes", position='midCenterTop', record_warning=False)
            raise ValueError("Not enough nodes selected. Select at least 2 nodes")

        self.snap_node_matrix = OpenMaya.MMatrix(cmds.xform(nodes[0], query=True, matrix=True, ws=True))
        self.node_data = {}
        for node in nodes:
            node_matrix = OpenMaya.MMatrix(cmds.xform(node, query=True, matrix=True, ws=True))
            self.node_data[node] = node_matrix

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node],
                                                   self.snap_node_matrix,
                                                   self.x,
                                                   *args, **kwargs)
            cmds.xform(node, matrix=lerped_matrix, ws=True)


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs: translate, rotate, scale bool options
    :return:
    """
    LerpSnapDragger(*args, **kwargs)
