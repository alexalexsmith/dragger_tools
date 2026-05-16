"""
Utilities for building nurbs curves in maya 
"""
import maya.OpenMaya as om
import maya.cmds as cmds

from dragger_tools.utilities import math_utils


class TwoPointDisplayCurve(object):
    """
    curve with 2 points, intended for displaying Information to the user
    """
    def __init__(self):
        self.dag_path = om.MDagPath()
        self.curve = None

    def create(self, vector_a, vector_b, thickness=1, color=18):
        points = om.MPointArray()
        points.append(om.MPoint(*vector_a))
        points.append(om.MPoint(*vector_b))

        knots = om.MDoubleArray()
        knots.append(0.0)
        knots.append(1.0)

        degree = 1
        form = om.MFnNurbsCurve.kOpen
        rational = False

        curve_fn = om.MFnNurbsCurve()
        # Returns an MObject for the new curve
        transform = curve_fn.create(points, knots, degree, form, rational, False)
        self.dag_path = om.MDagPath()
        fn_dag_node = om.MFnDagNode(transform)
        fn_dag_node.getPath(self.dag_path)

        self.dag_path.extendToShape()

        self.curve = om.MFnNurbsCurve(self.dag_path)
        self.set_curve_display(thickness=thickness, color=color)

    def set_curve_display(self, thickness=1, color=18):
        """
        Set the curves thickness and color
        """
        if not self.dag_path.isValid():
            return
        curve_name = self.dag_path.fullPathName()
        cmds.setAttr(f"{curve_name}.lineWidth", thickness)

        # 4. Apply Color via Display Overrides
        cmds.setAttr(f"{curve_name}.overrideEnabled", 1)
        cmds.setAttr(f"{curve_name}.overrideRGBColors", 0)  # Use Index colors
        cmds.setAttr(f"{curve_name}.overrideColor", color)

    def move_points(self, vector_a, vector_b):
        if not self.dag_path.isValid():
            return
        # Get existing points
        points = om.MPointArray()
        self.curve.getCVs(points, om.MSpace.kWorld)

        if vector_a is not None:
            points.set(om.MPoint(*vector_a), 0)
        if vector_b is not None:
            points.set(om.MPoint(*vector_b), 1)

        self.curve.setCVs(points, om.MSpace.kWorld)
        # Tell Maya to redraw the curve in the viewport
        self.curve.updateCurve()

    def delete(self):
        if not self.dag_path.isValid():
            return
        transform_path = om.MDagPath(self.dag_path)
        transform_path.pop()  # Step up from shape to transform
        transform_mobj = transform_path.node()

        self.curve = None
        self.dag_path = om.MDagPath()

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
        