from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui

import sys
import hou


class AlembicImporter(QtWidgets.QDialog):
    def __int__(self):
        super(AlembicImporter, self).__init__(hou.qt.mainWindow())
        self.configure_dialog()

    def configure_dialog(self):
        self.setWindowTitle("Main Win")
        self.setMinimumWidth(240)
        self.setMinimimHeight(320)


dialog = AlembicImporter()
dialog.show()
