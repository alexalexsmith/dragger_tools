"""
Utilities for building nurbs curves in maya 
"""
import maya.OpenMaya as om
import maya.OpenMayaAnim as oma  # not strictly needed here, but often used
import maya.cmds as cmds

def create_two_point_curve(vector_a, vector_b):
    # 1. Define the control points (CVs)
    # Using om.MPointArray for API 2.0
    points = om.MPointArray()
    points.append(om.MPoint(*vector_a))
    points.append(om.MPoint(*vector_b))

    # 2. Define Knots
    # For a degree 1 curve with 2 points, we need 2 knots
    # Formula: knots = points + degree - 1
    knots = om.MDoubleArray()
    knots.append(0.0)
    knots.append(1.0)

    # 3. Curve Parameters
    degree = 1
    form = om.MFnNurbsCurve.kOpen
    rational = False

    # 4. Create the function set
    curve_fn = om.MFnNurbsCurve()

    # 5. Create the curve
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

