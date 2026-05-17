"""
Utilities for building nurbs curves in maya 
"""
from maya.api import OpenMaya

from dragger_tools.utilities import math_utils


class TwoPointDisplayCurve(object):
    """
    Curve with 2 points, intended for displaying information to the user.
    """

    def __init__(self):
        self.dag_path = None
        self.curve = None

    def create(self, vector_a, vector_b, thickness=1, color=18):
        """
        Create a curve node with 2 points
        """
        points = OpenMaya.MPointArray()
        points.append(OpenMaya.MPoint(*vector_a))
        points.append(OpenMaya.MPoint(*vector_b))

        knots = OpenMaya.MDoubleArray([0.0, 1.0])
        degree = 1
        form = OpenMaya.MFnNurbsCurve.kOpen
        rational = False

        curve_fn = OpenMaya.MFnNurbsCurve()
        transform_mobj = curve_fn.create(points, knots, degree, form, rational, False)

        fn_dag_node = OpenMaya.MFnDagNode(transform_mobj)
        self.dag_path = fn_dag_node.getPath()
        self.dag_path.extendToShape()

        self.curve = OpenMaya.MFnNurbsCurve(self.dag_path)
        self.set_curve_display(thickness=thickness, color=color)

    def set_curve_display(self, thickness=1, color=18):
        """
        Set the curve's thickness and viewport color override
        """
        if self.dag_path is None or not self.dag_path.isValid():
            return

        curve_obj = self.dag_path.node()
        dep_fn = OpenMaya.MFnDependencyNode(curve_obj)

        hidden_plug = dep_fn.findPlug("hiddenInOutliner", False)
        hidden_plug.setBool(True)

        line_width_plug = dep_fn.findPlug("lineWidth", False)
        line_width_plug.setFloat(float(thickness))

        override_enabled_plug = dep_fn.findPlug("overrideEnabled", False)
        override_enabled_plug.setInt(1)

        override_rgb_plug = dep_fn.findPlug("overrideRGBColors", False)
        override_rgb_plug.setInt(0)  # 0 = Index colors, 1 = RGB colors

        override_color_plug = dep_fn.findPlug("overrideColor", False)
        override_color_plug.setInt(color)

    def move_points(self, vector_a, vector_b):
        """
        Dynamically update positions of start and end points.
        """
        if self.curve is None or not self.dag_path.isValid():
            return

        points = self.curve.cvPositions(OpenMaya.MSpace.kWorld)

        if vector_a is not None:
            points[0] = OpenMaya.MPoint(*vector_a)
        if vector_b is not None:
            points[1] = OpenMaya.MPoint(*vector_b)

        self.curve.setCVPositions(points, OpenMaya.MSpace.kWorld)
        self.curve.updateCurve()

    def delete(self):
        """
        Cleans up the curve nodes from the scene dependency graph.
        """
        if self.dag_path is None or not self.dag_path.isValid():
            return

        fn_dag_node = OpenMaya.MFnDagNode(self.dag_path)
        transform_mobj = fn_dag_node.parent(0)

        # Clear references
        self.curve = None
        self.dag_path = None

        # Delete the transform node via DAG modifier
        dag_mod = OpenMaya.MDagModifier()
        dag_mod.deleteNode(transform_mobj)
        dag_mod.doIt()


class LerpVectorDisplayCurves(object):
    """
    comprised of 2 curves
    This is a way to display the 2 lerp vectors and the current lerp offset from the default position
    I am passing full matrices and retrieving the translation vectors for the curve
    """
    def __init__(self, vector_curve_matrix_a, vector_curve_matrix_b, lerp_curve_default_matrix):
        self.vector_curve = None
        self.lerp_curve = None
        self.create_vector_curve(vector_curve_matrix_a, vector_curve_matrix_b)
        self.create_lerp_curve(lerp_curve_default_matrix)

    def create_vector_curve(self, vector_curve_matrix_a, vector_curve_matrix_b):
        a_decomposed_matrix = math_utils.decompose_position_matrix(vector_curve_matrix_a)
        b_decomposed_matrix = math_utils.decompose_position_matrix(vector_curve_matrix_b)
        vector_a = a_decomposed_matrix[0]
        vector_b = b_decomposed_matrix[0]
        self.vector_curve = TwoPointDisplayCurve()
        self.vector_curve.create(vector_a, vector_b)

    def create_lerp_curve(self, lerp_curve_default_matrix):
        a_decomposed_matrix = math_utils.decompose_position_matrix(lerp_curve_default_matrix)
        b_decomposed_matrix = math_utils.decompose_position_matrix(lerp_curve_default_matrix)
        vector_a = a_decomposed_matrix[0]
        vector_b = b_decomposed_matrix[0]
        self.lerp_curve = TwoPointDisplayCurve()
        self.lerp_curve.create(vector_a, vector_b, thickness=4, color=9)

    def update_lerp_curve(self, matrix):
        decomposed_matrix = math_utils.decompose_position_matrix(matrix)
        vector = decomposed_matrix[0]
        self.lerp_curve.move_points(None, vector)

    def delete_curves(self):
        try:
            self.vector_curve.delete()
            self.lerp_curve.delete()
        except Exception as e:
            return e
