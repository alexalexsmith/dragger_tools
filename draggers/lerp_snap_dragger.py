"""
Lerp snap dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, curve_utils
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
    position_display_curves = []
    lerp_display_curves = []

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
            node_data = {}
            node_matrix = OpenMaya.MMatrix(cmds.xform(node, query=True, matrix=True, ws=True))
            node_data["matrix"] = node_matrix
            node_data["position_display_curve"] = self.draw_key_display_curve(self.snap_node_matrix, node_matrix)
            node_data["lerp_display_curve"] = self.draw_tween_display_curve(node_matrix, node_matrix)
            self.node_data[node] = node_data

    def draw_key_display_curve(self, matrix_a, matrix_b):
        """
        Initiate a curve to illustrate tween data
        """
        a_decomposed_matrix = math_utils.decompose_position_matrix(matrix_a)
        b_decomposed_matrix = math_utils.decompose_position_matrix(matrix_b)
        vector_a = a_decomposed_matrix[0]
        vector_b = b_decomposed_matrix[0]
        curve = curve_utils.TwoPointDisplayCurve()
        curve.create(vector_a, vector_b)
        return curve

    def draw_tween_display_curve(self, matrix_a, matrix_b):
        a_decomposed_matrix = math_utils.decompose_position_matrix(matrix_a)
        b_decomposed_matrix = math_utils.decompose_position_matrix(matrix_b)
        vector_a = a_decomposed_matrix[0]
        vector_b = b_decomposed_matrix[0]
        curve = curve_utils.TwoPointDisplayCurve()
        curve.create(vector_a, vector_b, thickness=4, color=9)
        return curve

    def update_tween_display_curve(self, curve, matrix):
        """
        I will only update 1 point
        """
        decomposed_matrix = math_utils.decompose_position_matrix(matrix)
        vector = decomposed_matrix[0]
        curve.move_points(None, vector)

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node]["matrix"],
                                                   self.snap_node_matrix,
                                                   self.x,
                                                   *args, **kwargs)
            cmds.xform(node, matrix=lerped_matrix, ws=True)
            self.update_tween_display_curve(self.node_data[node]["lerp_display_curve"], lerped_matrix)

    def release(self, *args, **kwargs):
        """
        delete display curves
        """
        for node in self.node_data:
            try:
                position_curve = self.node_data[node]["position_display_curve"]
                lerp_curve = self.node_data[node]["lerp_display_curve"]
                position_curve.delete()
                lerp_curve.delete()
            except Exception as e:
                return


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs: translate, rotate, scale bool options
    :return:
    """
    LerpSnapDragger(*args, **kwargs)
