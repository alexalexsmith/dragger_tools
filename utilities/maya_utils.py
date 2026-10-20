
"""
Functions that replace Maya functions for speed
Common Maya functions to reduce redundancies or forcing everything to be included in an object
"""
import inspect
import sys

from maya.api import OpenMaya
from maya import cmds


def record_error(function, error, *args, **kwargs):
    """
    Records a clean error message in the Maya terminal with details for troubleshooting.
    :param function: function that caused issue
    :param error: error message
    """
    error_message = str(error)

    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        module = inspect.getmodule(function)

        if exc_tb and exc_tb.tb_next:
            traceback_frame = exc_tb.tb_next
        else:
            traceback_frame = exc_tb

        if traceback_frame:
            file_name = inspect.getframeinfo(traceback_frame).filename
            line = traceback_frame.tb_lineno
        else:
            file_name = "Unknown"
            line = "Unknown"

        module_name = module.__name__ if module else "Unknown"
        function_name = getattr(function, "__name__", str(function))

        error_message = (
            "module '{0}' {1}\nTraceback:\n{2}, line {3} in {4}"
        ).format(
            module_name,
            error,
            file_name,
            line,
            function_name
        )

    except Exception as e:
        OpenMaya.MGlobal.displayError(str(e))

    OpenMaya.MGlobal.displayError(error_message)
    return


def message(msg, position='midCenterTop', record_warning=True,
            drag_kill=False, *args, **kwargs):
    """
    A nicer way to display messages to the user.
    :param str msg: text to display to user
    :param str position: The position that the message will appear at relative to the active viewport.
    :param bool record_warning: Option to record the warning in the script output
    :param bool drag_kill: Option to have drag kill the warning
    """
    if record_warning:
        OpenMaya.MGlobal.displayWarning(msg)
    else:
        OpenMaya.MGlobal.displayInfo(msg)

    fade_time = min(len(msg) * 100, 2000)

    cmds.inViewMessage(
        amg=msg,
        pos=position,
        fade=True,
        fadeStayTime=fade_time,
        dragKill=drag_kill
    )


def get_current_camera():
    """
    Returns the camera that you're currently looking through.
    If the current highlighted panel isn't a modelPanel,
    find the first visible model panel available.
    """
    panel = cmds.getPanel(withFocus=True)

    if cmds.getPanel(typeOf=panel) != 'modelPanel':
        # Get the first visible model panel we find.
        for p in cmds.getPanel(visiblePanels=True):
            if cmds.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                cmds.setFocus(panel)
                break

    if cmds.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning(
            'Please highlight a camera viewport.'
        )
        return False

    cam_shape = cmds.modelEditor(panel, query=True, camera=True)

    if not cam_shape:
        return False

    cam_node_type = cmds.nodeType(cam_shape)

    if cam_node_type == 'transform':
        return cam_shape
    elif cam_node_type in ['camera', 'stereoRigCamera']:
        parents = cmds.listRelatives(
            cam_shape,
            parent=True,
            path=True
        )
        return parents[0] if parents else False


def get_active_animation_layer_cmds():
    """
    Returns the name of the currently active animation layer using maya.cmds.
    """
    node_iter = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kAnimLayer)

    base_layer = None

    while not node_iter.isDone():
        mobject = node_iter.thisNode()
        dep_node = OpenMaya.MFnDependencyNode(mobject)

        layer_name = dep_node.name()

        if layer_name == "BaseAnimation":
            base_layer = layer_name

        if cmds.animLayer(layer_name, query=True, selected=True):
            return layer_name

        node_iter.next()

    return base_layer
