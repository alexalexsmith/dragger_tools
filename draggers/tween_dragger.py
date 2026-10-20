
"""
Tween dragger
"""
import os

from maya import cmds

from dragger_tools.utilities import (
    maya_utils,
    math_utils,
    dragger_utils
)
from dragger_tools import ICONS


class TweenDragger(dragger_utils.Dragger):
    """
    Drag context tool to interpolate attribute values between
    the previous and next keyframes.
    """
    NAME = "Tween Dragger"
    TITLE = "Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = os.path.join(ICONS, "tweendragger.png")

    def __init__(self, *args, **kwargs):
        super(TweenDragger, self).__init__(*args, **kwargs)

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

        self.attributes = []
        self.attribute_data = {}

        selected_attributes = cmds.channelBox(
            "mainChannelBox",
            query=True,
            selectedMainAttributes=True
        )

        for node in nodes:
            attributes = cmds.listAttr(
                node,
                keyable=True,
                unlocked=True,
                shortNames=True
            )

            # Skip nodes with no keyable, unlocked attributes.
            if not attributes:
                continue

            for attribute in attributes:
                if selected_attributes and attribute not in selected_attributes:
                    continue

                attribute_path = "{0}.{1}".format(node, attribute)

                previous_keyframe = cmds.findKeyframe(
                    attribute_path,
                    which="previous"
                )
                next_keyframe = cmds.findKeyframe(
                    attribute_path,
                    which="next"
                )

                if previous_keyframe is None or next_keyframe is None:
                    continue

                previous_keyframe_value = cmds.getAttr(
                    attribute_path,
                    time=previous_keyframe
                )
                next_keyframe_value = cmds.getAttr(
                    attribute_path,
                    time=next_keyframe
                )

                self.attribute_data[attribute_path] = {
                    "previous_keyframe_value": previous_keyframe_value,
                    "next_keyframe_value": next_keyframe_value
                }
                self.attributes.append(attribute_path)

        if not self.attribute_data:
            maya_utils.message(
                "No attributes found to tween",
                position="midCenterTop",
                record_warning=False
            )
            raise ValueError("No attributes found to tween")

    def press(self, *args, **kwargs):
        """
        Set keyframes on the attributes being tweened.
        """
        if self.attribute_data:
            cmds.setKeyframe(list(self.attribute_data.keys()))

    def drag(self, *args, **kwargs):
        """
        Interpolate attribute values during the drag.
        """
        current_time = cmds.currentTime(query=True)

        for attribute, data in self.attribute_data.items():
            value = math_utils.lerp(
                data["previous_keyframe_value"],
                data["next_keyframe_value"],
                self.x
            )

            cmds.keyframe(
                attribute,
                time=(current_time,),
                valueChange=value
            )


def drag(*args, **kwargs):
    """
    Main drag function. Sets the drag tool.
    """
    TweenDragger(*args, **kwargs)
