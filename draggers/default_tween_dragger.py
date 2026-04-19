"""
default tween dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, attribute_utils
from dragger_tools import ICONS


class DefaultTweenDragger(dragger_utils.Dragger):
    """
    World space tween dragger tool
    """
    NAME = "Default Tween Dragger"
    TITLE = "Default Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/defaulttweendragger.png"

    def __init__(self, *args, **kwargs):
        super(DefaultTweenDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.attributes = None
        self.attribute_data = {}
        for node in nodes:
            self.attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not self.attributes or len(self.attributes) == 0:
                continue

            for attribute in self.attributes:

                previous_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="previous")
                next_keyframe = cmds.findKeyframe(f"{node}.{attribute}", which="next")
                if not previous_keyframe:
                    continue
                if not next_keyframe:
                    continue

                as_attribute = attribute_utils.Attribute(f"{node}.{attribute}")
                default_value = as_attribute.get_default_value()
                current_value = as_attribute.value

                data = {"default_value": default_value, "current_value": current_value}
                self.attribute_data[f"{node}.{attribute}"] = data

        if not self.attributes or len(self.attributes) == 0:
            maya_utils.message("No attributes found to tween", position='midCenterTop', record_warning=False)
            raise ValueError("No attributes found to tween")

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """
        for attribute in self.attribute_data:
            cmds.keyframe(
                attribute,
                time=(cmds.currentTime(query=True),),
                valueChange=math_utils.lerp(
                    self.attribute_data[attribute]["default_value"],
                    self.attribute_data[attribute]["current_value"],
                    self.x)
            )


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs:
    :return:
    """
    DefaultTweenDragger(*args, **kwargs)
