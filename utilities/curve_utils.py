"""
Utilities for building nurbs curves in maya 
"""
import maya.OpenMaya as om
import maya.cmds as cmds


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


def create_two_point_curve(vector_a, vector_b):
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
    curve_obj = curve_fn.create(points, knots, degree, form, rational, False)
    return curve_obj
    
    
def delete_m_object(m_obj):
    """
    Delete is stored in undo chunch
    """
    dag_mod = om.MDagModifier()
    dag_mod.deleteNode(m_obj)
    dag_mod.doIt()

