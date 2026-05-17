"""
Drag and drop file to add dragger tools to current shelf
"""
import os

from maya import cmds, mel

REPO_DATA_PATH = os.path.dirname(os.path.abspath(__file__))
ICONS = f"{REPO_DATA_PATH}/icons"
shelf_buttons = {
    "TweenDrag": {
        "imageOverlayLabel": "TD",
        "command": "from dragger_tools.draggers import tween_dragger;tween_dragger.drag()",
        "icon": f"{ICONS}/tweendragger.png",
        "annotation": "lerp (ease) attributes between previous and next keyframe values"
    },
    "WorldSpaceTweenDrag": {
        "imageOverlayLabel": "WSTD",
        "command": "from dragger_tools.draggers import world_space_tween_dragger;world_space_tween_dragger.drag(translation=True, rotation=True, scale=True)",
        "icon": f"{ICONS}/wstweendragger.png",
        "annotation": "lerp (ease) world position between previous and next keyframe time world positions. This function allows you to choose to exclude translation, rotation, and scale"
    },
    "CameraSpaceTweenDrag": {
        "imageOverlayLabel": "CSTD",
        "command": "from dragger_tools.draggers import camera_space_tween_dragger;camera_space_tween_dragger.drag(translation=True, rotation=True, scale=True)",
        "icon": f"{ICONS}/cameraspacedragger.png",
        "annotation": "lerp (ease) position between previous and next keyframe time relative to active camera positions. This function allows you to choose to exclude translation, rotation, and scale"
    },
    "DefaultTweenDrag": {
        "imageOverlayLabel": "DTD",
        "command": "from dragger_tools.draggers import default_tween_dragger;default_tween_dragger.drag()",
        "icon": f"{ICONS}/defaulttweendragger.png",
        "annotation": "lerp (ease) attributes between current value and default value"
    },
    "CurveValueDrag": {
        "imageOverlayLabel": "CVD",
        "command": "from dragger_tools.draggers import curve_value_dragger;curve_value_dragger.drag()",
        "icon": f"{ICONS}/curvevaluedragger.png",
        "annotation": "change current attribute value to future or past value of the animation curve. Could also be described as slidding the attribute value along the animation curve"
    },
    "LerpSnapDrag": {
        "imageOverlayLabel": "LSD",
        "command": "from dragger_tools.draggers import lerp_snap_dragger;lerp_snap_dragger.drag(translation=True, rotation=True, scale=True)",
        "icon": f"{ICONS}/lerpsnapdragger.png",
        "annotation": "Lerp objects towards the first selected object. This function allows you to choose to exclude translation, rotation, and scale"
    },
    "CameraDepthDrag": {
        "imageOverlayLabel": "CDD",
        "command": "from dragger_tools.draggers import camera_depth_dragger;camera_depth_dragger.drag()",
        "icon": f"{ICONS}/cameradepthdragger.png",
        "annotation": "Lerp objects towards the active camera. The active camera is decided based on the active model panel or the first viewport panel available"
    },
}


def install_shelve_buttons():
    """
    install shelf buttons
    """
    shelf = mel.eval("$shelf = $gShelfTopLevel;")
    if cmds.tabLayout(shelf, exists=True):
        parent = cmds.tabLayout(shelf, query=True, selectTab=True)
        for tool in shelf_buttons:
            cmds.shelfButton(
                parent=parent,
                label=tool,
                imageOverlayLabel=shelf_buttons[tool]["imageOverlayLabel"],
                command=shelf_buttons[tool]["command"],
                image=shelf_buttons[tool]["icon"],
                annotation=shelf_buttons[tool]["annotation"]
            )
    else:
        cmds.error("You need a shelf for this Install to complete!  Show your shelf, man!")


def onMayaDroppedPythonFile(*args, **kwargs):
    install_shelve_buttons()
    