"""
World Space tween dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, attribute_utils
from dragger_tools import ICONS


class WSTweenDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool
    You can use translate, rotate, scale bool parameters from math_utils.lerp_matrix() to define what gets lerped
    """
    NAME = "WorldSpace Tween Dragger"
    TITLE = "WorldSpace Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/wstweendragger.png"
    TRANSFORM_ATTRIBUTES = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    def __init__(self, *args, **kwargs):
        super(WSTweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)
        self.attributes = []

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.node_data = {}
        for node in nodes:
            animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not animatable_attributes or len(animatable_attributes) == 0:
                continue

            for attribute in animatable_attributes:
                if attribute in self.TRANSFORM_ATTRIBUTES:
                    self.attributes.append(f"{node}.{attribute}")

            if not cmds.findKeyframe(node, curve=True):
                continue

            previous_keyframe = cmds.findKeyframe(node, which="previous")  # NOTE: default is current time
            next_keyframe = cmds.findKeyframe(node, which="next")  # NOTE: default is current time

            # get the world matrix values
            pre_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=previous_keyframe))
            next_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=next_keyframe))

            data = {"pre_frame_matrix": pre_frame_matrix, "next_frame_matrix": next_frame_matrix}
            self.node_data[node] = data

            if len(self.node_data) == 0:
                maya_utils.message("No nodes found to tween", record_warning=False)
                raise ValueError("No nodes found to tween. Make sure there are keyframes to tween and transform attributes are keyable")

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframes on transform attributes
        cmds.setKeyframe()

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node]["pre_frame_matrix"],
                                                   self.node_data[node]["next_frame_matrix"],
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
    WSTweenDragger(*args, **kwargs)
