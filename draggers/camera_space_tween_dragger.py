"""
Camera depth dragger
"""
from maya import cmds
from maya.api import OpenMaya

from dragger_tools.utilities import maya_utils, math_utils, dragger_utils, curve_utils
from dragger_tools import ICONS


class CameraSpaceDragger(dragger_utils.Dragger):
    """
    Lerp objects position between previosu and next world space position relative to camera
    """
    NAME = "Camera Space Dragger"
    TITLE = "Camera Space Dragger"
    CURSOR = "track"
    DEFAULT_VALUE = 0.5
    ICON = f"{ICONS}/cameraspacedragger.png"
    TRANSFORM_ATTRIBUTES = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    def __init__(self, *args, **kwargs):
        super(CameraSpaceDragger, self).__init__(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        init the dragger tool data
        """
        # get the camera that we're looking through, and the objects selected
        self.camera = maya_utils.get_current_camera()
        if self.camera is None:
            maya_utils.message("Unable to find camera", record_warning=False)
            raise ValueError("Unable to find camera")
        # get camera matrix, this is all we really need
        self.camera_current_position = OpenMaya.MMatrix(cmds.getAttr(f"{self.camera}.worldMatrix"))

        nodes = cmds.ls(selection=True)
        self.attributes = []

        if nodes is None or len(nodes) == 0:
            maya_utils.message("0 nodes selected", position='midCenterTop', record_warning=False)
            raise ValueError("0 transform nodes selected")

        self.node_data = {}
        for node in nodes:
            animatable_attributes = cmds.listAttr(node, keyable=True, unlocked=True, shortNames=True)
            # skipping node if no animatable attributes are available
            if not animatable_attributes or len(animatable_attributes) == 0:
                continue

            for attribute in animatable_attributes:
                if attribute in self.TRANSFORM_ATTRIBUTES:
                    self.attributes.append(f"{node}.{attribute}")

            if not cmds.findKeyframe(node, curve=True):
                continue

            previous_keyframe = cmds.findKeyframe(node, which="previous")  # NOTE: default is current time
            next_keyframe = cmds.findKeyframe(node, which="next")  # NOTE: default is current time

            # get the world matrix values
            pre_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=previous_keyframe))
            next_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{node}.worldMatrix", time=next_keyframe))
            
            # get camera pre and next position
            camera_pre_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{self.camera}.worldMatrix", time=previous_keyframe))
            camera_next_frame_matrix = OpenMaya.MMatrix(cmds.getAttr(f"{self.camera}.worldMatrix", time=next_keyframe))
            
            # calculate the pre/next frame position relative to camera
            pre_offset_matrix = math_utils.calculate_matrix_difference(camera_pre_frame_matrix, pre_frame_matrix)
            next_offset_matrix = math_utils.calculate_matrix_difference(camera_next_frame_matrix, next_frame_matrix)

            # calculate the offset relative to the cameras current position
            relative_pre_matrix = pre_offset_matrix * self.camera_current_position
            relative_next_position = next_offset_matrix * self.camera_current_position
            lerped_matrix = math_utils.lerp_matrix(relative_pre_matrix,
                                                   relative_next_position,
                                                   self.DEFAULT_VALUE,
                                                   *args, **kwargs)

            data = {
                "relative_pre_matrix": relative_pre_matrix,
                "relative_next_position": relative_next_position,
                "key_display_curve": self.draw_key_display_curve(relative_pre_matrix, relative_next_position),
                "lerp_display_curve": self.draw_tween_display_curve(lerped_matrix, lerped_matrix)
            }
            self.node_data[node] = data

            if len(self.node_data) == 0:
                maya_utils.message("No nodes found to tween", record_warning=False)
                raise ValueError("No nodes found to tween. Make sure there are keyframes to tween and transform attributes are keyable")
        
    def drag(self, *args, **kwargs):
        """
        pre_drag normal speed
        """
        for node in self.node_data:
            # get lerped matrix values
            lerped_matrix = math_utils.lerp_matrix(self.node_data[node]["relative_pre_matrix"],
                                                   self.node_data[node]["relative_next_position"],
                                                   self.x,
                                                   *args, **kwargs)
            cmds.xform(node, matrix=lerped_matrix, ws=True)
            # update curve draw after object data is updated
            self.update_tween_display_curve(self.node_data[node]["lerp_display_curve"], lerped_matrix)
            
    def draw_key_display_curve(self, matrix_a, matrix_b):
        """
        Initiate a curve to illustrate tween data
        """
        a_decomposed_matrix = math_utils.decompose_position_matrix(matrix_a)
        b_decomposed_matrix = math_utils.decompose_position_matrix(matrix_b)
        vector_a = a_decomposed_matrix[0]
        vector_b = b_decomposed_matrix[0]
        curve = curve_utils.TwoPointDisplayCurve()
        curve.create(vector_a, vector_b)
        return curve

    def draw_tween_display_curve(self, matrix_a, matrix_b):
        a_decomposed_matrix = math_utils.decompose_position_matrix(matrix_a)
        b_decomposed_matrix = math_utils.decompose_position_matrix(matrix_b)
        vector_a = a_decomposed_matrix[0]
        vector_b = b_decomposed_matrix[0]
        curve = curve_utils.TwoPointDisplayCurve()
        curve.create(vector_a, vector_b, thickness=4, color=9)
        return curve

    def update_tween_display_curve(self, curve, matrix):
        """
        I will only update 1 point
        """
        decomposed_matrix = math_utils.decompose_position_matrix(matrix)
        vector = decomposed_matrix[0]
        curve.move_points(None, vector)
        
    def release(self, *args, **kwargs):
        """
        release function to be overwritten by subclass
        """
        try:
            for node in self.node_data:
                position_curve = self.node_data[node]["key_display_curve"]
                lerp_curve = self.node_data[node]["lerp_display_curve"]
                position_curve.delete()
                lerp_curve.delete()
        except Exception as e:
            return


def drag(*args, **kwargs):
    """
    main drag function. sets the drag tool
    :param args:
    :param kwargs:
    :return:
    """
    CameraSpaceDragger(*args, **kwargs)