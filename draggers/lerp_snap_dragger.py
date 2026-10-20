
"""
Lerp snap dragger
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


class LerpSnapDragger(dragger_utils.Dragger):
    """
    Lerp objects towards first selection.

    Use the translate, rotate, and scale boolean parameters from
    math_utils.lerp_matrix() to define what gets interpolated.
    """
    NAME = "Lerp Snap Dragger"
    TITLE = "Lerp Snap Dragger"
    CURSOR = "hand"
    DEFAULT_VALUE = 0.0
    ICON = os.path.join(ICONS, "lerpsnapdragger.png")

    def __init__(self, *args, **kwargs):
        super(LerpSnapDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        Initialize the dragger tool data.
        """
        nodes = cmds.ls(selection=True)

        if not nodes or len(nodes) < 2:
            maya_utils.message(
                "Not enough nodes selected. Select at least 2 nodes",
                position="midCenterTop",
                record_warning=False
            )
            raise ValueError(
                "Not enough nodes selected. Select at least 2 nodes"
            )

        self.snap_node_matrix = OpenMaya.MMatrix(
            cmds.xform(
                nodes[0],
                query=True,
                matrix=True,
                worldSpace=True
            )
        )

        self.node_data = {}

        for node in nodes:
            node_matrix = OpenMaya.MMatrix(
                cmds.xform(
                    node,
                    query=True,
                    matrix=True,
                    worldSpace=True
                )
            )

            display_curves = curve_utils.LerpVectorDisplayCurves(
                node_matrix,
                self.snap_node_matrix,
                node_matrix
            )

            self.node_data[node] = {
                "matrix": node_matrix,
                "display_curves": display_curves
            }

    def drag(self, *args, **kwargs):
        """
        Actions activated by left drag.
        """
        for node, data in self.node_data.items():
            # Get interpolated matrix values.
            lerped_matrix = math_utils.lerp_matrix(
                data["matrix"],
                self.snap_node_matrix,
                self.x,
                *args,
                **kwargs
            )

            cmds.xform(
                node,
                matrix=lerped_matrix,
                worldSpace=True
            )

            display_curves = data["display_curves"]
            display_curves.update_lerp_curve(lerped_matrix)

    def release(self, *args, **kwargs):
        """
        Delete display curves.
        """
        for data in self.node_data.values():
            try:
                display_curves = data["display_curves"]
                display_curves.delete_curves()
            except Exception:
                # Continue cleaning up the remaining display curves.
                continue


def drag(*args, **kwargs):
    """
    Main drag function.

    Args:
        translate, rotate, scale: Boolean options passed to lerp_matrix().
    """
    LerpSnapDragger(*args, **kwargs)
