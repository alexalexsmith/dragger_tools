"""
Curve value dragger
"""
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, attribute_utils
from dragger_tools import ICONS


ANIM_CURVE_TYPES = ["animCurveTU", "animCurveTA", "animCurveTL"]


class CurveValueDragger(dragger_utils.Dragger):
    """
    Slide the current attribute values along the curve value
    """
    NAME = "Curve Value Dragger"
    TITLE = "Curve Value Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    MAX_MULTIPLIER = 1.0  # NOTE: the fastest the drag value will raise or lower
    MIN_MULTIPLIER = 0.1  # NOTE: the slowest the drag value will raise or lower
    ICON = f"{ICONS}/curvevaluedragger.png"

    def __init__(self, *args, **kwargs):
        super(CurveValueDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        nodes = cmds.ls(selection=True)

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.nodes = {}
        for node in nodes:
            attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not attributes or len(attributes) == 0:
                continue

            self.nodes[node] = {}

            for attribute in attributes:
                attribute_object = attribute_utils.Attribute(f"{node}.{attribute}")
                source_connection = attribute_object.get_source_connection()
                if not source_connection:
                    continue
                if not cmds.nodeType(source_connection) in ANIM_CURVE_TYPES:
                    continue
                buffer_curve = cmds.duplicate(source_connection)[0]
                sel = OpenMaya.MSelectionList()
                sel.add(buffer_curve)
                new_obj = sel.getDependNode(0)
                fn_curve = OpenMayaAnim.MFnAnimCurve(new_obj)

                self.nodes[node][f"{node}.{attribute}"] = fn_curve

    def press(self, *args, **kwargs):
        """
        Actions taking place on press action
        """
        # set keyframe will set a keyframe on all attributes
        cmds.setKeyframe()

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        self.cursor_label.set_color("white")
        label = f"frame:{round(self.time_drag,3)}"
        self.cursor_label.setText(label)

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag
        """

        self.time_drag = cmds.currentTime(query=True) + self.x

        for node in self.nodes:
            for attribute in self.nodes[node]:
                buffer_curve = self.nodes[node][attribute]
                cmds.keyframe(
                    attribute,
                    time=(cmds.currentTime(query=True),),
                    valueChange=buffer_curve.evaluate(OpenMaya.MTime(self.time_drag, OpenMaya.MTime.uiUnit()))
                )

    def release(self):
        """release actions. clean up all data"""
        for node in self.nodes:
            for attribute in self.nodes[node]:
                buffer_curve = self.nodes[node][attribute]
                dg_mod = OpenMaya.MDGModifier()
                dg_mod.deleteNode(buffer_curve.object())
                dg_mod.doIt()  # There is no try


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs:
    :return:
    """
    CurveValueDragger(*args, **kwargs)
