# dragger_tools
dragger tools for maya
place the dragger_tools folder in your scripts folder and run the dragger tool with the below commands

## Tween Dragger
lerp (ease) attributes between previous and next keyframe values
```from dragger_tools.draggers import tween_dragger;tween_dragger.drag()```

## World Space Tween Dragger
lerp (ease) world position between previous and next keyframe time world positions. This function allows you to choose to exclude translation, rotation, and scale
```from dragger_tools.draggers import tween_dragger;world_space_tween_dragger.drag(translation=True, rotation=True, scale=True)```

## Default Tween Dragger
lerp (ease) attributes between current value and default value
```from dragger_tools.draggers import tween_dragger;default_tween_dragger.drag()```

## Curve Value Dragger
change current attribute value to future or past value of the animation curve. Could also be descripbed as slidding the attribute value along the animation curve
```from dragger_tools.draggers import tween_dragger;curve_value_dragger.drag()```

## Lerp Snap Dragger
Lerp objects towards the first selected object. This function allows you to choose to exclude translation, rotation, and scale
```from dragger_tools.draggers import tween_dragger;lerp_snap_dragger.drag(translation=True, rotation=True, scale=True)```

## Camera Depth Dragger
Lerp objects towards the active camera. The active camera is decided based on the active model panel or the first viewport panel available
```from dragger_tools.draggers import tween_dragger;camera_depth_dragger.drag()```
