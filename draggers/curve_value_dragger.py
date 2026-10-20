
"""
Curve value dragger
"""
import os

from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim

from dragger_tools.utilities import (
    maya_utils,
    math_utils,
    dragger_utils,
    attribute_utils
)
from dragger_tools import ICONS


ANIM_CURVE_TYPES = ["animCurveTU", "animCurveTA", "animCurveTL"]


class CurveValueDragger(dragger_utils.Dragger):
    """
    Slide the current attribute values along the curve value.
    """

    NAME = "Curve Value Dragger"
    TITLE = "Curve Value Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    MAX_MULTIPLIER = 1.0
    MIN_MULTIPLIER = 0.1
    ICON = os.path.join(ICONS, "curvevaluedragger.png")

    def __init__(self, *args, **kwargs):
        super(CurveValueDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        Initialize the dragger tool data.
        """
        nodes = cmds.ls(selection=True)

        if not nodes:
            maya_utils.message(
                "0 nodes selected",
                position="midCenterTop",
                record_warning=False
            )
            raise ValueError("0 transform nodes selected")

        self.nodes = {}

        for node in nodes:
            attributes = cmds.listAttr(
                node,
                keyable=True,
                unlocked=True,
                shortNames=True
            )

            # Skip nodes without animatable attributes.
            if not attributes:
                continue

            self.nodes[node] = {}

            for attribute in attributes:
                attribute_path = "{0}.{1}".format(node, attribute)
                attribute_object = attribute_utils.Attribute(
                    attribute_path
                )

                source_connection = (
                    attribute_object.get_source_connection()
                )

                if not source_connection:
                    continue

                if cmds.nodeType(source_connection) not in ANIM_CURVE_TYPES:
                    continue

                buffer_curve = cmds.duplicate(source_connection)[0]

                self.nodes[node][attribute_path] = buffer_curve

    def press(self, *args, **kwargs):
        """
        Actions taking place on press.
        """
        # Set a keyframe on the current attributes.
        cmds.setKeyframe()

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        Define the cursor label displayed while dragging.
        """
        self.cursor_label.set_color("white")

        label = "frame:{0}".format(round(self.time_drag, 3))
        self.cursor_label.setText(label)

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag.
        """
        self.time_drag = cmds.currentTime(query=True) + self.x
        current_time = cmds.currentTime(query=True)

        for node in self.nodes:
            for attribute in self.nodes[node]:
                buffer_curve = self.nodes[node][attribute]

                values = cmds.keyframe(
                    buffer_curve,
                    query=True,
                    eval=True,
                    time=(self.time_drag, self.time_drag)
                )

                if not values:
                    continue

                value = values[0]

                cmds.keyframe(
                    attribute,
                    time=(current_time,),
                    valueChange=value
                )

    def release(self, *args, **kwargs):
        """
        Release actions. Clean up temporary curves.
        """
        for node in self.nodes:
            for attribute in self.nodes[node]:
                buffer_curve = self.nodes[node][attribute]

                if cmds.objExists(buffer_curve):
                    cmds.delete(buffer_curve)


def drag(*args, **kwargs):
    """
    Main drag function. Creates the drag tool.
    """
    CurveValueDragger(*args, **kwargs)
