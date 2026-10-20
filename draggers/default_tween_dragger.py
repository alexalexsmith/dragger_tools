
"""
Default tween dragger
"""
from maya import cmds

from dragger_tools.utilities import (
    maya_utils,
    math_utils,
    dragger_utils,
    attribute_utils
)
from dragger_tools import ICONS
import os


class DefaultTweenDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool
    """
    NAME = "Default Tween Dragger"
    TITLE = "Default Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = os.path.join(ICONS, "defaulttweendragger.png")

    def __init__(self, *args, **kwargs):
        super(DefaultTweenDragger, self).__init__(*args, **kwargs)

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

            # Skip nodes with no animatable attributes.
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

                # TODO: For additive animation layers, retrieve and manipulate
                # the animation curve value rather than the attribute value.
                as_attribute = attribute_utils.Attribute(attribute_path)

                default_value = as_attribute.get_default_value()
                current_value = as_attribute.value

                self.attribute_data[attribute_path] = {
                    "default_value": default_value,
                    "current_value": current_value
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
        Actions taking place on press action.
        """
        # Set a keyframe on the selected attributes.
        if self.attribute_data:
            cmds.setKeyframe(list(self.attribute_data.keys()))

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag.
        """
        current_time = cmds.currentTime(query=True)

        for attribute, data in self.attribute_data.items():
            value = math_utils.lerp(
                data["default_value"],
                data["current_value"],
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
    DefaultTweenDragger(*args, **kwargs)
