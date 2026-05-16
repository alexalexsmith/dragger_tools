"""
Utilities for building nurbs curves in maya 
"""
import maya.api.OpenMaya as om

from dragger_tools.utilities import math_utils


class TwoPointDisplayCurve(object):
    """
    Curve with 2 points, intended for displaying information to the user.
    Fully converted to OpenMaya 2.0.
    """

    def __init__(self):
        self.dag_path = None
        self.curve = None

    def create(self, vector_a, vector_b, thickness=1, color=18):
        # 1. Build points array
        points = om.MPointArray()
        points.append(om.MPoint(*vector_a))
        points.append(om.MPoint(*vector_b))

        # 2. OpenMaya 2.0 list initialization for arrays
        knots = om.MDoubleArray([0.0, 1.0])
        degree = 1
        form = om.MFnNurbsCurve.kOpen
        rational = False

        # 3. Create the curve
        curve_fn = om.MFnNurbsCurve()
        transform_mobj = curve_fn.create(points, knots, degree, form, rational, False)

        # 4. Correctly extract and assign the DAG Path in 2.0
        fn_dag_node = om.MFnDagNode(transform_mobj)
        self.dag_path = fn_dag_node.getPath()
        self.dag_path.extendToShape()

        # 5. Initialize the curve function set on the shape path
        self.curve = om.MFnNurbsCurve(self.dag_path)
        self.set_curve_display(thickness=thickness, color=color)

    def set_curve_display(self, thickness=1, color=18):
        """
        Set the curve's thickness and viewport color override using pure OpenMaya 2.0.
        """
        if self.dag_path is None or not self.dag_path.isValid():
            return

        curve_obj = self.dag_path.node()
        dep_fn = om.MFnDependencyNode(curve_obj)

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

        points = self.curve.cvPositions(om.MSpace.kWorld)

        if vector_a is not None:
            points[0] = om.MPoint(*vector_a)
        if vector_b is not None:
            points[1] = om.MPoint(*vector_b)

        self.curve.setCVPositions(points, om.MSpace.kWorld)
        self.curve.updateCurve()

    def delete(self):
        """
        Cleans up the curve nodes from the scene dependency graph.
        """
        if self.dag_path is None or not self.dag_path.isValid():
            return

        fn_dag_node = om.MFnDagNode(self.dag_path)
        transform_mobj = fn_dag_node.parent(0)

        # Clear references
        self.curve = None
        self.dag_path = None

        # Delete the transform node via DAG modifier
        dag_mod = om.MDagModifier()
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
