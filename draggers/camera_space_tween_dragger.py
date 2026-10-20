
"""
Camera space dragger
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


class CameraSpaceDragger(dragger_utils.Dragger):
    """
    Lerp object positions between previous and next world-space
    positions relative to the camera.
    """

    NAME = "Camera Space Dragger"
    TITLE = "Camera Space Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = os.path.join(ICONS, "cameraspacedragger.png")
    TRANSFORM_ATTRIBUTES = [
        "tx", "ty", "tz",
        "rx", "ry", "rz",
        "sx", "sy", "sz"
    ]

    def __init__(self, *args, **kwargs):
        super(CameraSpaceDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        Initialize the dragger tool data.
        """
        # Get the camera we're looking through.
        self.camera = maya_utils.get_current_camera()

        if self.camera is None or self.camera is False:
            maya_utils.message(
                "Unable to find camera",
                record_warning=False
            )
            raise ValueError("Unable to find camera")

        # Get the camera matrix.
        self.camera_current_position = OpenMaya.MMatrix(
            cmds.getAttr(
                "{0}.worldMatrix[0]".format(self.camera)
            )
        )

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

            if not cmds.findKeyframe(node, curve=True):
                continue

            previous_keyframe = cmds.findKeyframe(
                node,
                which="previous"
            )
            next_keyframe = cmds.findKeyframe(
                node,
                which="next"
            )

            # Get the world matrices at the previous and next keyframes.
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

            # Get the camera matrices at the previous and next keyframes.
            camera_pre_frame_matrix = OpenMaya.MMatrix(
                cmds.getAttr(
                    "{0}.worldMatrix[0]".format(self.camera),
                    time=previous_keyframe
                )
            )
            camera_next_frame_matrix = OpenMaya.MMatrix(
                cmds.getAttr(
                    "{0}.worldMatrix[0]".format(self.camera),
                    time=next_keyframe
                )
            )

            # Calculate positions relative to the camera.
            pre_offset_matrix = math_utils.calculate_matrix_difference(
                camera_pre_frame_matrix,
                pre_frame_matrix
            )
            next_offset_matrix = math_utils.calculate_matrix_difference(
                camera_next_frame_matrix,
                next_frame_matrix
            )

            # Calculate offsets relative to the current camera matrix.
            relative_pre_matrix = (
                pre_offset_matrix * self.camera_current_position
            )
            relative_next_position = (
                next_offset_matrix * self.camera_current_position
            )

            lerped_matrix = math_utils.lerp_matrix(
                relative_pre_matrix,
                relative_next_position,
                self.DEFAULT_VALUE,
                *args,
                **kwargs
            )

            display_curves = curve_utils.LerpVectorDisplayCurves(
                relative_pre_matrix,
                relative_next_position,
                lerped_matrix
            )

            data = {
                "relative_pre_matrix": relative_pre_matrix,
                "relative_next_position": relative_next_position,
                "display_curves": display_curves
            }

            self.node_data[node] = data

        if not self.node_data:
            maya_utils.message(
                "No nodes found to tween",
                record_warning=False
            )
            raise ValueError(
                "No nodes found to tween. Make sure there are keyframes "
                "to tween and transform attributes are keyable."
            )

    def drag(self, *args, **kwargs):
        """
        Perform the drag operation.
        """
        for node in self.node_data:
            # Calculate the interpolated matrix.
            lerped_matrix = math_utils.lerp_matrix(
                self.node_data[node]["relative_pre_matrix"],
                self.node_data[node]["relative_next_position"],
                self.x,
                *args,
                **kwargs
            )

            cmds.xform(node, matrix=lerped_matrix, worldSpace=True)

            # Update the curve display after updating the object.
            display_curves = self.node_data[node]["display_curves"]
            display_curves.update_lerp_curve(lerped_matrix)

    def release(self, *args, **kwargs):
        """
        Remove display curves when the drag operation ends.
        """
        try:
            for node in self.node_data:
                display_curves = self.node_data[node]["display_curves"]
                display_curves.delete_curves()
        except Exception:
            pass


def drag(*args, **kwargs):
    """
    Main drag function. Creates the drag tool.
    """
    CameraSpaceDragger(*args, **kwargs)
