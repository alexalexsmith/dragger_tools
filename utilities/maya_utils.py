"""
Functions that replace maya functions for speed
Common maya functions to reduce redundancies or forcing everything to be included in an object
"""
import inspect
import sys

import maya.api.OpenMaya as OpenMaya
from maya import cmds, mel


def record_error(function, error, *args, **kwargs):
    """
    records a clean error message in the maya terminal with details for troubleshooting
    :param function: function that caused issue
    :param error: error message
    """
    error_message = str(error)
    try:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        module = inspect.getmodule(function)
        file_name = inspect.getframeinfo(exc_tb.tb_next).filename
        line = exc_tb.tb_next.tb_lineno
        error_message = f"module '{module.__name__}' {error}\nTraceback:\n{file_name}, line {line} in {function.__name__}"
    except Exception as e:
        OpenMaya.MGlobal.displayError(str(e))
    OpenMaya.MGlobal.displayError(error_message)
    return


def message(msg, position='midCenterTop', record_warning=True, drag_kill=False, *args, **kwargs):
    """
    A nicer way to display messages to the user
    :param str msg: text to display to user
    :param str position: The position that the message will appear at relative to the active viewport. The supported positions are:
                            "topLeft"
                            "topCenter"
                            "topRight"
                            "midLeft"
                            "midCenter"
                            "midCenterTop"
                            "midCenterBot"
                            "midRight"
                            "botLeft"
                            "botCenter"
                            "botRight"
    :param bool record_warning: Option to record the warning in the script output
    :param bool drag_kill: Option to have drag kill the warning
    """
    if record_warning:
        OpenMaya.MGlobal.displayWarning(msg)
    else:
        OpenMaya.MGlobal.displayInfo(msg)
    fade_time = min(len(msg) * 100, 2000)
    cmds.inViewMessage(amg=msg, pos=position, fade=True, fadeStayTime=fade_time, dragKill=drag_kill)


def get_current_camera():
    """
    Returns the camera that you're currently looking through.
    If the current highlighted panel isn't a modelPanel,
    """

    panel = cmds.getPanel(withFocus=True)

    if cmds.getPanel(typeOf=panel) != 'modelPanel':
        # just get the first visible model panel we find, hopefully the correct one.
        for p in cmds.getPanel(visiblePanels=True):
            if cmds.getPanel(typeOf=p) == 'modelPanel':
                panel = p
                cmds.setFocus(panel)
                break

    if cmds.getPanel(typeOf=panel) != 'modelPanel':
        OpenMaya.MGlobal.displayWarning('Please highlight a camera viewport.')
        return False

    cam_shape = cmds.modelEditor(panel, query=True, camera=True)
    if not cam_shape:
        return False

    cam_node_type = cmds.nodeType(cam_shape)
    if cmds.nodeType(cam_shape) == 'transform':
        return cam_shape
    elif cmds.nodeType(cam_shape) in ['camera', 'stereoRigCamera']:
        return cmds.listRelatives(cam_shape, parent=True, path=True)[0]