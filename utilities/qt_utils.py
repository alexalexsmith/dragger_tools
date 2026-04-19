try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from shiboken2 import wrapInstance
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from shiboken6 import wrapInstance

import maya.OpenMayaUI as omui


def get_maya_main_widget():
    """
    Get pointer to Maya's main window
    """
    maya_main_window_pointer = omui.MQtUtil.mainWindow()
    return wrapInstance(int(maya_main_window_pointer), QtWidgets.QWidget)


class CursorLabel(QtWidgets.QLabel):
    """
    Label that follows the cursor
    """

    STYLE_SHEET = """
                QLabel {{
                    background-color: rgba(0, 0, 0, 180);
                    color: {color_val};
                    padding: 4px 8px;
                    border-radius: 4px;
                }}
                """

    def __init__(self, parent=get_maya_main_widget()):
        super(CursorLabel, self).__init__(parent)

        self.setStyleSheet(self.STYLE_SHEET.format(color_val="white"))
        self.adjustSize()

        # Make it float above everything
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        # Timer to follow cursor
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.follow_mouse)
        self.timer.start(16)  # ~60 FPS

    def setText(self, text):
        super().setText(text)
        self.adjustSize()  # Resize immediately
        self.updateGeometry()

    def follow_mouse(self):
        pos = QtGui.QCursor.pos()
        self.move(pos.x() + 15, pos.y() + 15)  # offset from cursor

    def set_color(self, color):
        """
        set the color of the text
        :param color: qss color
        """
        self.setStyleSheet(self.STYLE_SHEET.format(color_val=color))