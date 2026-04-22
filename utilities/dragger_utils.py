"""
Dragger utilities for creating viewport dragging tools
"""
from functools import partial

from maya import cmds, mel

from dragger_tools.utilities import qt_utils, maya_utils


class Dragger(object):
    """
    Dragger tool abstract. creates a draggerContext in maya
    """
    NAME = None  # name of dragger context
    TITLE = None  # title to display to the user
    CURSOR = None  # cursor to display to user
    DEFAULT_VALUE = None  # the default start value
    ICON = None  # icon file path
    MAX_MULTIPLIER = 0.01  # NOTE: the fastest the drag value will raise or lower
    MIN_MULTIPLIER = 0.001  # NOTE: the slowest the drag value will raise or lower

    def __init__(self, debug=False, *args, **kwargs):

        self.__press_failed = False
        self.debug = debug
        self.y = None
        self.x = None
        self.modifier = None  # NOTE: only 3 options "shift", "ctrl", "other". other is the alt key
        self.drag_point = None
        self.multiplier = self.MAX_MULTIPLIER  # The default drag speed is max
        self.min_value = None
        self.max_value = None
        self.cursor_label = None

        self.dragger_context = self.NAME
        if not cmds.draggerContext(self.dragger_context, exists=True):
            self.dragger_context = cmds.draggerContext(self.dragger_context)

        # Priming functions with arguments
        press_function = partial(self.__press, *args, **kwargs)
        drag_function = partial(self.__drag, *args, **kwargs)
        release_function = partial(self.__release, *args, **kwargs)

        cmds.draggerContext(self.dragger_context, edit=True,
                            pressCommand=press_function,
                            dragCommand=drag_function,
                            releaseCommand=release_function,
                            cursor=self.CURSOR,
                            drawString=self.TITLE,
                            undoMode='all'
                            )
        if self.ICON:
            cmds.draggerContext(self.dragger_context, edit=True, image1=self.ICON)

        self.__set_tool(*args, **kwargs)

    def _init_subclass(self, *args, **kwargs):
        """
        _init_subclass function for all subclasses. Raise an error when checking for failures
        """
        return

    @staticmethod
    def __init_cursor_label(label, *args, **kwargs):
        """
        Initialize the cursor label
        :param label: string label to display
        :return: qt_utils.CursorLabel()
        """
        cursor_label = qt_utils.CursorLabel()
        cursor_label.setText(label)
        cursor_label.show()
        return cursor_label

    def __press(self, *args, **kwargs):
        """
        private press function. Undo chunk is opened here
        :return: None
        """
        # subclass is initialized on press command so that all data is properly gathered inside the dragger context
        # created in maya. This means if your init is heavy there may be some lag on the press
        try:
            self._init_subclass(*args, **kwargs)
            self.__press_failed = False
        except Exception as e:
            self.__press_failed = True
            if self.debug:
                maya_utils.record_error(self._init_subclass, e)
            self.__release()
            return

        self.cursor_label = self.__init_cursor_label(self.TITLE)

        self.anchor_point = cmds.draggerContext(self.dragger_context, query=True, anchorPoint=True)
        self.button = cmds.draggerContext(self.dragger_context, query=True, button=True)
        cmds.undoInfo(openChunk=True, chunkName=self.NAME)

        # Run press command if there are any other functions the user wants to apply before drag begins
        try:
            self.press(*args, **kwargs)
        except Exception as e:
            if self.debug:
                maya_utils.record_error(self.press, e)
            self.__release()
            return

    def press(self, *args, **kwargs):
        """
        Press function to be overwritten by subclass
        """
        return

    def __drag(self, *args, **kwargs):
        """
        private drag function. sets up basic drag parameters and key modifier features before running subclass drag
        :return: None
        """
        if self.__press_failed:
            return

        self.drag_point = cmds.draggerContext(self.dragger_context, query=True, dragPoint=True)
        self.modifier = cmds.draggerContext(self.dragger_context, query=True, modifier=True)

        # set min max value based on control key modifier press state
        if self.modifier == "ctrl":
            self.min_value = 0.0
            self.max_value = 1.0
        if not self.modifier == "ctrl":
            self.min_value = None
            self.max_value = None

        # set drag speed based on alt key modifier press state
        if self.modifier == "other":
            self.multiplier = self.MIN_MULTIPLIER
        if not self.modifier == "other":
            self.multiplier = self.MAX_MULTIPLIER

        self.x = ((self.drag_point[0] - self.anchor_point[0]) * self.multiplier) + self.DEFAULT_VALUE
        self.y = ((self.drag_point[1] - self.anchor_point[1]) * self.multiplier) + self.DEFAULT_VALUE

        if self.min_value is not None and self.x < self.min_value:
            self.x = self.min_value
        if self.max_value is not None and self.x > self.max_value:
            self.x = self.max_value

        try:
            self.drag(*args, **kwargs)
        except Exception as e:
            if self.debug:
                maya_utils.record_error(self.drag, e)
            self.__release()
            return

        self._set_cursor_label_drag_display(*args, **kwargs)
        cmds.refresh()

    def drag(self, *args, **kwargs):
        """
        Drag function to be overwritten by subclass
        """
        return

    def _set_cursor_label_drag_display(self, *args, **kwargs):
        """
        defines what is displayed on the cursor label and how it looks when dragging
        """
        label = f"{int(self.x * 100)}%"
        self.cursor_label.setText(label)
        if int(self.x * 100) > 100 or int(self.x * 100) < 0:
            self.cursor_label.set_color("red")
        else:
            self.cursor_label.set_color("white")

    def __release(self, *args, **kwargs):
        """
        private release function
        """
        try:
            self.release(*args, **kwargs)
        except Exception as e:
            if self.debug:
                maya_utils.record_error(self.drag, e)
        cmds.undoInfo(closeChunk=True, chunkName=self.NAME)
        if self.cursor_label:
            self.cursor_label.close()
        mel.eval('SelectTool')

    def release(self, *args, **kwargs):
        """
        release function to be overwritten by subclass
        """
        return

    def __set_tool(self, *args, **kwargs):
        """
        Sets the active tool
        """
        cmds.setToolTo(self.dragger_context)
