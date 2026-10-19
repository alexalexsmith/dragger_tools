
# Maya Dragger Tools
<img width="32" height="32" alt="tweendragger" src="https://github.com/user-attachments/assets/8f7efd50-855d-4f18-a16b-b208b6cf8d7f" />
<img width="32" height="32" alt="wstweendragger" src="https://github.com/user-attachments/assets/86deecf8-595e-44cd-8b41-15406a4a9c78" />
<img width="34" height="34" alt="cameraspacedragger" src="https://github.com/user-attachments/assets/5e14407c-21dc-405a-a97a-4da3682c899b" />
<img width="32" height="32" alt="defaulttweendragger" src="https://github.com/user-attachments/assets/6ef3943e-0b57-47ee-8623-e2a23a21bb89" />
<img width="32" height="32" alt="curvevaluedragger" src="https://github.com/user-attachments/assets/24afacbb-8ee6-4419-9658-f8cfaa7f3c72" />
<img width="32" height="32" alt="lerpsnapdragger" src="https://github.com/user-attachments/assets/e7bdb166-6b5d-4c9a-81ad-cc652923bd61" />
<img width="34" height="34" alt="cameradepthdragger" src="https://github.com/user-attachments/assets/10b14776-decc-41d4-b295-48d47fac1d25" />

dragger tools for maya

place the dragger_tools folder in your scripts folder and run the dragger tool with the below commands. Use the drag_and_drop_install_shelve_buttons.py to add the buttons to your current shelf
The tools work by left mouse click and dragging across the viewport. You can lock the drag value to avoid overshooting using the ctrl key and reduce the drag speed using the alt key.

## Tween Dragger <img width="32" height="32" alt="tweendragger" src="https://github.com/user-attachments/assets/8f7efd50-855d-4f18-a16b-b208b6cf8d7f" />
<img width="720" height="720" alt="tween_dragger" src="https://github.com/user-attachments/assets/26f00c16-f5a1-44eb-9fae-506fecf1a2f2" />

lerp (ease) attributes between previous and next keyframe values

```
from dragger_tools.draggers import tween_dragger;tween_dragger.drag()
```

## World Space Tween Dragger <img width="32" height="32" alt="wstweendragger" src="https://github.com/user-attachments/assets/86deecf8-595e-44cd-8b41-15406a4a9c78" />
<img width="720" height="720" alt="world_space_tween_dragger" src="https://github.com/user-attachments/assets/d0d76191-f061-462b-ae59-5fbc90a03b28" />

lerp (ease) world position between previous and next keyframe time world positions. This function allows you to choose to exclude translation, rotation, and scale

```
from dragger_tools.draggers import world_space_tween_dragger;world_space_tween_dragger.drag(translation=True, rotation=True, scale=True)
```

## Camera Space Tween Dragger <img width="34" height="34" alt="cameraspacedragger" src="https://github.com/user-attachments/assets/5e14407c-21dc-405a-a97a-4da3682c899b" />
<img width="720" height="720" alt="camera_space_dragger" src="https://github.com/user-attachments/assets/9f2b1689-ba46-4141-b776-ad6ba98318f0" />

lerp (ease) position between previous and next keyframe time relative to active camera positions. This function allows you to choose to exclude translation, rotation, and scale

```
from dragger_tools.draggers import camera_space_tween_dragger;camera_space_tween_dragger.drag(translation=True, rotation=True, scale=True)
```


## Default Tween Dragger <img width="32" height="32" alt="defaulttweendragger" src="https://github.com/user-attachments/assets/6ef3943e-0b57-47ee-8623-e2a23a21bb89" />
<img width="720" height="720" alt="default_tween_dragger" src="https://github.com/user-attachments/assets/c931b687-1a00-4782-90da-7814fafd5e93" />

lerp (ease) attributes between current value and default value

```
from dragger_tools.draggers import default_tween_dragger;default_tween_dragger.drag()
```

## Curve Value Dragger <img width="32" height="32" alt="curvevaluedragger" src="https://github.com/user-attachments/assets/24afacbb-8ee6-4419-9658-f8cfaa7f3c72" />
<img width="720" height="720" alt="curve_value_dragger" src="https://github.com/user-attachments/assets/27bd98fe-e8a3-4a8c-9ef8-7671a5520cb9" />

change current attribute value to future or past value of the animation curve. Could also be described as slidding the attribute value along the animation curve

```
from dragger_tools.draggers import curve_value_dragger;curve_value_dragger.drag()
```

## Lerp Snap Dragger <img width="32" height="32" alt="lerpsnapdragger" src="https://github.com/user-attachments/assets/e7bdb166-6b5d-4c9a-81ad-cc652923bd61" />
<img width="720" height="720" alt="lerp_snap_dragger" src="https://github.com/user-attachments/assets/a3b03a79-2879-45bd-9d11-3b7a7d621b51" />

Lerp objects towards the first selected object. This function allows you to choose to exclude translation, rotation, and scale

```
from dragger_tools.draggers import lerp_snap_dragger;lerp_snap_dragger.drag(translation=True, rotation=True, scale=True)
```

## Camera Depth Dragger <img width="34" height="34" alt="cameradepthdragger" src="https://github.com/user-attachments/assets/10b14776-decc-41d4-b295-48d47fac1d25" />
<img width="720" height="720" alt="camera_depth_dragger" src="https://github.com/user-attachments/assets/8f0ad6b1-6e26-4360-b9a2-c82c2ab72b29" />

Lerp objects towards the active camera. The active camera is decided based on the active model panel or the first viewport panel available

```
from dragger_tools.draggers import camera_depth_dragger;camera_depth_dragger.drag()
```
