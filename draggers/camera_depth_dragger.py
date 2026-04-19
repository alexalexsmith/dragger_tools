"""
Camera depth dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, attribute_utils
from dragger_tools import ICONS


class CameraDepthDragger(dragger_utils.Dragger):
    """
    Lerp objects position towards or away from camera position
    """
    NAME = "Camera Depth Dragger"
    TITLE = "Camera Depth Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    ICON = f"{ICONS}/cameradepthdragger.png"

    def __init__(self, *args, **kwargs):
        super(CameraDepthDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        # get the camera that we're looking through, and the objects selected
        camera = maya_utils.get_current_camera()
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", record_warning=False)
            raise ValueError("0 transform nodes selected")

        # get the position of the camera in space and convert it to a vector
        self.camera_position = cmds.xform(camera, query=True, worldSpace=True, rotatePivot=True)

        self.node_data = {}
        for node in nodes:
            # make sure all translate attributes are settable
            if not cmds.getAttr(f"{node}.translate", settable=True):
                continue

            # get the position of the objects as a vector, and subtract the camera vector from that
            node_position = cmds.xform(node, query=True, worldSpace=True, rotatePivot=True)
            self.node_data[node] = node_position

        if not self.node_data:
            maya_utils.message("No selected objects are translatable", record_warning=False)
            raise ValueError("No selected objects are translatable")

        if len(nodes) != len(self.node_data):
            maya_utils.message("Some selected objects cannot be translated", record_warning=True)

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        self.cursor_label.set_color("white")
        label = f"X:{round(self.lerp_vector[0], 3)} Y:{round(self.lerp_vector[1], 3)} Z:{round(self.lerp_vector[2], 3)}"
        self.cursor_label.setText(label)

    def drag(self, *args, **kwargs):
        """
        pre_drag normal speed
        """
        self.lerp_vector = [0, 0, 0]
        for node in self.node_data:
            self.lerp_vector = math_utils.lerp_vector(self.node_data[node], self.camera_position, self.x)
            cmds.move(self.lerp_vector[0], self.lerp_vector[1], self.lerp_vector[2], node, absolute=True, worldSpace=True)


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs:
    :return:
    """
    CameraDepthDragger(*args, **kwargs)
