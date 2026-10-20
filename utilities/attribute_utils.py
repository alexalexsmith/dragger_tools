
"""
Utilities for managing attributes
"""
from maya import cmds
from maya.api import OpenMaya


class Attribute(object):
    """
    Represents a single attribute on a node.
    """

    def __init__(self, attribute_path):
        self.attribute_path = attribute_path
        self.node, self.attribute = attribute_path.split(".", 1)
        self.type = cmds.getAttr(attribute_path, type=True)
        self.value = cmds.getAttr(attribute_path)
        self.fn_node = None
        self.m_attr_plug = None
        self.m_attribute = None
        self._init_m_attribute()

    def _init_m_attribute(self):
        """Initialize the OpenMaya attribute object."""
        sel = OpenMaya.MSelectionList()
        sel.add(self.node)
        mobj = sel.getDependNode(0)
        self.fn_node = OpenMaya.MFnDependencyNode(mobj)
        self.m_attr_plug = self.fn_node.findPlug(self.attribute, False)
        self.m_attribute = self.m_attr_plug.attribute()

    def node_name(self):
        """Return the node name."""
        return self.fn_node.name()

    def attribute_name(self):
        """Return the attribute name."""
        return self.m_attribute.name()

    def attribute_path(self):
        """Return the attribute path."""
        path = "{0}.{1}".format(
            self.node_name(),
            self.attribute_name()
        )
        return path

    def is_selected(self):
        """
        Get whether the attribute is selected in the main Channel Box.

        NOTE: If the node that owns the attribute is not selected at
        execution time, this method may not work as expected.
        """
        selected_attributes = cmds.channelBox(
            'mainChannelBox',
            query=True,
            selectedMainAttributes=True
        )

        if not selected_attributes:
            return False

        return self.attribute in selected_attributes

    def is_keyable(self):
        return cmds.getAttr(self.attribute_path, keyable=True)

    def is_locked(self):
        return cmds.getAttr(self.attribute_path, lock=True)

    def get_source_connection(self):
        """Get the source connection, if any."""
        m_plug_source = self.m_attr_plug.source()

        if m_plug_source.isNull:
            return None

        m_object_source_node = m_plug_source.node()
        fn_source_node = OpenMaya.MFnDependencyNode(
            m_object_source_node
        )
        return fn_source_node.name()

    def get_default_value(self):
        """Return the default value."""
        if self.m_attribute.hasFn(OpenMaya.MFn.kNumericAttribute):
            return OpenMaya.MFnNumericAttribute(
                self.m_attribute
            ).default

        elif self.m_attribute.hasFn(OpenMaya.MFn.kEnumAttribute):
            return OpenMaya.MFnEnumAttribute(
                self.m_attribute
            ).default

        elif self.m_attribute.hasFn(OpenMaya.MFn.kTypedAttribute):
            return OpenMaya.MFnTypedAttribute(
                self.m_attribute
            ).default

        else:
            return 0

    def get_value(self, time=None):
        """
        Get the current value.

        :param float time: Optional time at which to get the value.
        """
        if time is not None:
            return cmds.getAttr(self.attribute_path(), time=time)

        return cmds.getAttr(self.attribute_path())

    def get_keyframes(self):
        """Get any keyframes on the attribute."""
        return cmds.keyframe(
            self.attribute_path(),
            query=True,
            timeChange=True
        )

    def get_enum_values(self):
        """Get all available enum values."""
        if self.type != "enum":
            cmds.warning(
                "{0} is not an enum attribute".format(
                    self.attribute_path
                )
            )
            return None

        enum_data = cmds.attributeQuery(
            self.attribute,
            node=self.node,
            listEnum=True
        )

        if not enum_data:
            return []

        return enum_data[0].split(":")

    def get_minimum(self):
        """Return the minimum value."""
        if cmds.attributeQuery(
            self.attribute,
            node=self.node,
            minExists=True
        ):
            return cmds.attributeQuery(
                self.attribute,
                node=self.node,
                minimum=True
            )[0]

        if self.type == "double":
            return -99999.99

        return -99999

    def get_maximum(self):
        """Return the maximum value."""
        if cmds.attributeQuery(
            self.attribute,
            node=self.node,
            maxExists=True
        ):
            return cmds.attributeQuery(
                self.attribute,
                node=self.node,
                maximum=True
            )[0]

        if self.type == "double":
            return 99999.99

        return 99999

    def set_value(self, value):
        """Set the attribute value."""
        try:
            cmds.setAttr(self.attribute_path, value)
        except Exception as e:
            cmds.warning(
                "Attempt to set attribute was aborted: {0}".format(e)
            )
