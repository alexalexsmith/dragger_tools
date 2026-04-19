"""
Utilities for managing attributes
"""
from maya import cmds
import maya.api.OpenMaya as om


class Attribute(object):
    """
    Represents a single attribute on a node
    """

    def __init__(self, attribute_path):
        self.attribute_path = attribute_path
        self.node, self.attribute = attribute_path.split(".")
        self.type = cmds.getAttr(attribute_path, type=True)
        self.value = cmds.getAttr(attribute_path)
        self.m_attr_plug = None
        self.m_attribute = None
        self._init_m_attribute()

    def _init_m_attribute(self):
        """initiate the openMaya attribute object"""
        sel = om.MSelectionList()
        sel.add(self.node)
        mobj = sel.getDependNode(0)
        fn_node = om.MFnDependencyNode(mobj)
        self.m_attr_plug = fn_node.findPlug(self.attribute, False)
        self.m_attribute = self.m_attr_plug.attribute()

    def is_selected(self):
        """
        Get if the attribute is selected in the mainChannelBox
        NOTE: if the node that owns the attribute is not selected at the time of execution, this method not work as expected
        """
        selected_attributes = cmds.channelBox('mainChannelBox', query=True, selectedMainAttributes=True)
        if not selected_attributes:
            return False
        if self.attribute in selected_attributes:
            return True
        return False

    def is_keyable(self):
        return cmds.getAttr(self.attribute_path, keyable=True)

    def is_locked(self):
        return cmds.getAttr(self.attribute_path, lock=True)

    def get_connections(self):
        """
        get a list of incoming connections
        """
        # TODO: may need to filter out self in list
        return cmds.listConnections(self.attribute_path, skipConversionNodes=True)

    def get_default_value(self):
        """
        return the default value.
        """
        if self.m_attribute.hasFn(om.MFn.kNumericAttribute):
            return om.MFnNumericAttribute(self.m_attribute).default
        elif self.m_attribute.hasFn(om.MFn.kEnumAttribute):
            return om.MFnEnumAttribute(self.m_attribute).default
        elif self.m_attribute.hasFn(om.MFn.kTypedAttribute):
            return om.MFnTypedAttribute(self.m_attribute).default
        else:
            return 0  # NOTE: default value for translation and rotation attributes

    def get_value(self, time=None):
        """
        get the current value
        :param float time: option to get the value a specified time
        """
        return cmds.getAttr(self.attribute_path)

    def get_keyframes(self):
        """
        get any keyframes on the attribute
        """
        return cmds.keyframe(self.attribute, query=True, timeChange=True)

    def get_enum_values(self):
        """
        get all available enum values
        """
        if self.type != "enum":
            cmds.warning("{0} is not an enum attribute".format(self.attribute_path))
            return
        return cmds.attributeQuery(self.attribute, node=self.node, listEnum=True)[0].split(":")

    def get_minimum(self):
        """
        Return the minimum value
        """
        if cmds.attributeQuery(self.attribute, node=self.node, minExists=True):
            return cmds.attributeQuery(self.attribute, node=self.node, minimum=True)[0]
        if self.type == "double":
            return -99999.99
        return -99999

    def get_maximum(self):
        """
        Return the maximum value
        """
        if cmds.attributeQuery(self.attribute, node=self.node, maxExists=True):
            return cmds.attributeQuery(self.attribute, node=self.node, maximum=True)[0]
        if self.type == "double":
            return 99999.99
        return 99999

    def set_value(self, value):
        try:
            cmds.setAttr(self.attribute_path, value)
        except Exception as e:
            cmds.warning("Attempt to set attribute was aborted:{0}".format(e))
