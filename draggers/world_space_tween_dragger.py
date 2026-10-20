
"""
World Space Tween Dragger
"""
import os

from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import (
    maya_utils,
    math_utils,
    dragger_utils,
    curve_utils
)
from dragger_tools import ICONS


class WSTweenDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool.

    Translate, rotate, and scale boolean options can be passed to
    math_utils.lerp_matrix() to define which components are interpolated.
    """
    NAME = "WorldSpace Tween Dragger"
    TITLE = "WorldSpace Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = os.path.join(ICONS, "wstweendragger.png")

    TRANSFORM_ATTRIBUTES = [
        "tx", "ty", "tz",
        "rx", "ry", "rz",
        "sx", "sy", "sz"
    ]

    def __init__(self, *args, **kwargs):
        super(WSTweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        Initialize the dragger tool data.
        """
        nodes = cmds.ls(selection=True)

        self.attributes = []

        if not nodes:
            maya_utils.message(
                "0 nodes selected",
                position="midCenterTop",
                record_warning=False
            )
            raise ValueError("0 transform nodes selected")

        self.node_data = {}

        for node in nodes:
            animatable_attributes = cmds.listAttr(
                node,
                keyable=True,
                unlocked=True,
                shortNames=True
            )

            # Skip nodes without animatable attributes.
            if not animatable_attributes:
                continue

            for attribute in animatable_attributes:
                if attribute in self.TRANSFORM_ATTRIBUTES:
                    self.attributes.append(
                        "{0}.{1}".format(node, attribute)
                    )

            # Skip nodes without animation curves.
            if not cmds.findKeyframe(node, curve=True):
                continue

            # Find surrounding keyframe times.
            previous_keyframe = cmds.findKeyframe(
                node,
                which="previous"
            )
            next_keyframe = cmds.findKeyframe(
                node,
                which="next"
            )

            # Get world matrices at the surrounding keyframes.
            pre_frame_matrix = OpenMaya.MMatrix(
                cmds.getAttr(
                    "{0}.worldMatrix[0]".format(node),
                    time=previous_keyframe
                )
            )

            next_frame_matrix = OpenMaya.MMatrix(
                cmds.getAttr(
                    "{0}.worldMatrix[0]".format(node),
                    time=next_keyframe
                )
            )

            lerped_matrix = math_utils.lerp_matrix(
                pre_frame_matrix,
                next_frame_matrix,
                self.DEFAULT_VALUE,
                *args,
                **kwargs
            )

            display_curves = curve_utils.LerpVectorDisplayCurves(
                pre_frame_matrix,
                next_frame_matrix,
                lerped_matrix
            )

            self.node_data[node] = {
                "pre_frame_matrix": pre_frame_matrix,
                "next_frame_matrix": next_frame_matrix,
                "display_curves": display_curves
            }

        if not self.node_data:
            maya_utils.message(
                "No nodes found to tween",
                record_warning=False
            )
            raise ValueError(
                "No nodes found to tween. Make sure there are keyframes "
                "to tween and transform attributes are keyable."
            )

    def press(self, *args, **kwargs):
        """
        Set keyframes on the transform attributes being tweened.
        """
        if self.attributes:
            cmds.setKeyframe(self.attributes)

    def drag(self, *args, **kwargs):
        """
        Interpolate world-space transforms during the drag.
        """
        for node, data in self.node_data.items():
            lerped_matrix = math_utils.lerp_matrix(
                data["pre_frame_matrix"],
                data["next_frame_matrix"],
                self.x,
                *args,
                **kwargs
            )

            cmds.xform(
                node,
                matrix=lerped_matrix,
                worldSpace=True
            )

            data["display_curves"].update_lerp_curve(lerped_matrix)

    def release(self, *args, **kwargs):
        """
        Delete display curves.
        """
        for data in self.node_data.values():
            try:
                data["display_curves"].delete_curves()
            except Exception:
                # Continue cleaning up any remaining display curves.
                continue


def drag(*args, **kwargs):
    """
    Main drag function.

    Args:
        translate, rotate, scale: Boolean options passed to lerp_matrix().
    """
    WSTweenDragger(*args, **kwargs)
