
"""
Camera depth dragger
"""
import os

from maya import cmds

from dragger_tools.utilities import (
    maya_utils,
    math_utils,
    dragger_utils,
    attribute_utils
)
from dragger_tools import ICONS


class CameraDepthDragger(dragger_utils.Dragger):
    """
    Lerp objects position towards or away from camera position.
    """

    NAME = "Camera Depth Dragger"
    TITLE = "Camera Depth Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    ICON = os.path.join(ICONS, "cameradepthdragger.png")

    def __init__(self, *args, **kwargs):
        super(CameraDepthDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        Initialize the dragger tool data.
        """
        # Get the camera that we're looking through and the selected objects.
        camera = maya_utils.get_current_camera()
        nodes = cmds.ls(selection=True)

        if not nodes:
            maya_utils.message(
                "0 nodes selected",
                record_warning=False
            )
            raise ValueError("0 transform nodes selected")

        if not camera:
            raise ValueError("No active camera found")

        # Get the camera position in world space.
        self.camera_position = cmds.xform(
            camera,
            query=True,
            worldSpace=True,
            rotatePivot=True
        )

        self.node_data = {}

        for node in nodes:
            # Make sure all translate attributes are settable.
            if not cmds.getAttr(
                "{0}.translate".format(node),
                settable=True
            ):
                continue

            # Store each object's world-space pivot position.
            node_position = cmds.xform(
                node,
                query=True,
                worldSpace=True,
                rotatePivot=True
            )
            self.node_data[node] = node_position

        if not self.node_data:
            maya_utils.message(
                "No selected objects are translatable",
                record_warning=False
            )
            raise ValueError(
                "No selected objects are translatable"
            )

        if len(nodes) != len(self.node_data):
            maya_utils.message(
                "Some selected objects cannot be translated",
                record_warning=True
            )

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        Define what is displayed on the cursor label while dragging.
        """
        self.cursor_label.set_color("white")

        label = "X:{0} Y:{1} Z:{2}".format(
            round(self.lerp_vector[0], 3),
            round(self.lerp_vector[1], 3),
            round(self.lerp_vector[2], 3)
        )

        self.cursor_label.setText(label)

    def drag(self, *args, **kwargs):
        """
        Perform the drag operation.
        """
        self.lerp_vector = [0, 0, 0]

        for node in self.node_data:
            self.lerp_vector = math_utils.lerp_vector(
                self.node_data[node],
                self.camera_position,
                self.x
            )

            cmds.move(
                self.lerp_vector[0],
                self.lerp_vector[1],
                self.lerp_vector[2],
                node,
                absolute=True,
                worldSpace=True
            )


def drag(*args, **kwargs):
    """
    Main drag function. Sets the drag tool.
    """
    CameraDepthDragger(*args, **kwargs)
