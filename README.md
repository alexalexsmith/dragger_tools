# Maya Dragger Tools
dragger tools for maya
place the dragger_tools folder in your scripts folder and run the dragger tool with the below commands

## Tween Dragger
<img width="720" height="720" alt="tween_dragger" src="https://github.com/user-attachments/assets/26f00c16-f5a1-44eb-9fae-506fecf1a2f2" />

lerp (ease) attributes between previous and next keyframe values

```
from dragger_tools.draggers import tween_dragger;tween_dragger.drag()
```

## World Space Tween Dragger
<img width="720" height="720" alt="world_space_tween_dragger" src="https://github.com/user-attachments/assets/d0d76191-f061-462b-ae59-5fbc90a03b28" />

lerp (ease) world position between previous and next keyframe time world positions. This function allows you to choose to exclude translation, rotation, and scale

```
from dragger_tools.draggers import tween_dragger;world_space_tween_dragger.drag(translation=True, rotation=True, scale=True)
```

## Default Tween Dragger
<img width="720" height="720" alt="default_tween_dragger" src="https://github.com/user-attachments/assets/c931b687-1a00-4782-90da-7814fafd5e93" />

lerp (ease) attributes between current value and default value

```
from dragger_tools.draggers import tween_dragger;default_tween_dragger.drag()
```

## Curve Value Dragger
<img width="720" height="720" alt="curve_value_dragger" src="https://github.com/user-attachments/assets/27bd98fe-e8a3-4a8c-9ef8-7671a5520cb9" />

change current attribute value to future or past value of the animation curve. Could also be described as slidding the attribute value along the animation curve

```
from dragger_tools.draggers import tween_dragger;curve_value_dragger.drag()
```

## Lerp Snap Dragger
<img width="720" height="720" alt="lerp_snap_dragger" src="https://github.com/user-attachments/assets/a3b03a79-2879-45bd-9d11-3b7a7d621b51" />

Lerp objects towards the first selected object. This function allows you to choose to exclude translation, rotation, and scale

```
from dragger_tools.draggers import tween_dragger;lerp_snap_dragger.drag(translation=True, rotation=True, scale=True)
```

## Camera Depth Dragger
<img width="720" height="720" alt="camera_depth_dragger" src="https://github.com/user-attachments/assets/8f0ad6b1-6e26-4360-b9a2-c82c2ab72b29" />

Lerp objects towards the active camera. The active camera is decided based on the active model panel or the first viewport panel available

```
from dragger_tools.draggers import tween_dragger;camera_depth_dragger.drag()
```
