"""
Tween dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, attribute_utils
from dragger_tools import ICONS


class TweenDragger(dragger_utils.Dragger):
    """
    Drag context tool to lerp attribute value between previous and next keyframe value
    """
    NAME = "Tween Dragger"
    TITLE = "Tween Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/tweendragger.png"

    def __init__(self, *args, **kwargs):
        super(TweenDragger, self).__init__(*args, **kwargs)

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

                previous_keyframe_data = cmds.getAttr(f"{node}.{attribute}", time=previous_keyframe)
                next_keyframe_data = cmds.getAttr(f"{node}.{attribute}", time=next_keyframe)
                data = {"previous_keyframe_value": previous_keyframe_data, "next_keyframe_value": next_keyframe_data}
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
                    self.attribute_data[attribute]["previous_keyframe_value"],
                    self.attribute_data[attribute]["next_keyframe_value"],
                    self.x)
            )


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs:
    :return:
    """
    TweenDragger(*args, **kwargs)
