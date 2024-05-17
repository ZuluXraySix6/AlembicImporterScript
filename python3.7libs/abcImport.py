from PySide2 import QtWidgets
from hutil.Qt import QtCore
from hutil.Qt import QtGui
from hutil.Qt import QtWidgets
from hutil.Qt.QtCore import Qt
from PySide2 import QtCore, QtGui
from PySide2.QtWidgets import QApplication, QWidget, QAbstractItemView
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
import hou
import os
import sys
import datetime as datetime
from hou import SopNode, Node

abc_list = []
abc_date_modified = []
root = hou.node("/obj/")


##### Main Class
class MainWindow(QtWidgets.QDialog):
    def __init__(self, parm=None, parent=hou.qt.mainWindow()):
        super(MainWindow, self).__init__(parent)
        self.mainWindow()

        self.abcPath = ""
        self.listABC = []
        self.abc_select = []
        self.abc_deselect = []
        self.subDir = []
        self.totalFiles = 0
        self.selectedNodes = []
        self.layoutNodes = []
        ##### Set columns widths
        self.tableWidget.setColumnWidth(0, 200)
        self.tableWidget.setColumnWidth(1, 250)

        ##### Call all Buttons
        self.ALL_BUTTONS()

    ##### All mutton call method
    def ALL_BUTTONS(self):
        self.selectABCBtn.clicked.connect(self.SET_PATH)
        self.refreshBtn.clicked.connect(self.REFRESH)
        self.executeBtn.clicked.connect(self.EXECUTE)

    ##### Get total no of files.
    def TOTAL_FILES(self):
        self.fileCount = 0
        for files in os.listdir(self.abcPath):
            if files.endswith(".abc") or files.endswith(".ABC"):
                self.fileCount = self.fileCount + 1
        return self.fileCount

    ##### Select and Set Path
    def SET_PATH(self):
        self.abcPath = ""
        ##### Clear Rows
        self.tableWidget.setRowCount(0)
        self.abcPath = hou.ui.selectFile(start_directory=None, title="Select ABC Folder path",
                                         file_type=hou.fileType.Directory)
        self.pathEdit.setText(self.abcPath)

        if self.abcPath:
            ##### Get Subdirectory NAMES #####
            if self.includeSubChkBx.isChecked():
                self.subDir = next(os.walk(self.abcPath))[1]

            self.tableWidget.setRowCount(0)

            self.REFRESH()

    def CANCEL(self):
        pass

    ##### Display Data on TableWidget
    def REFRESH(self):
        abc_list.clear()
        self.abc_select.clear()
        for files in os.listdir(self.abcPath):
            if files.endswith(".abc") or files.endswith(".ABC"):
                fullPath = self.abcPath + files
                m_time = os.path.getmtime(fullPath)
                # convert timestamp into DateTime object
                self.date_modified = str(datetime.datetime.fromtimestamp(m_time))
                self.date_modified = self.date_modified[0:18]
                abc_list.append(files)
                abc_date_modified.append(self.date_modified)

                self.totalFiles = len(abc_list)

        self.INCLUDE_SUB()

    ##### Include the SubDirectories Function Call
    def INCLUDE_SUB(self):
        if self.includeSubChkBx.isChecked():
            for path in self.subDir:
                for files in os.listdir(self.abcPath + path):
                    if files.endswith(".abc") or files.endswith(".ABC"):
                        fullPath = self.abcPath + path + "/" + files
                        m_time = os.path.getmtime(fullPath)
                        # convert timestamp into DateTime object
                        self.date_modified = str(datetime.datetime.fromtimestamp(m_time))
                        self.date_modified = self.date_modified[0:18]
                        abc_list.append(files)
                        abc_date_modified.append(self.date_modified)
            self.totalFiles = len(abc_list)

            self.DISPLAY_DATA()
        else:
            self.DISPLAY_DATA()

    ##### Display Data
    def DISPLAY_DATA(self):
        self.tableWidget.setRowCount(0)
        row1 = 0
        self.tableWidget.setRowCount(self.totalFiles)
        for items in abc_list:
            self.tableWidget.setItem(row1, 0, QtWidgets.QTableWidgetItem(items))
            row1 = row1 + 1

        row2 = 0
        for items in abc_date_modified:
            self.tableWidget.setItem(row2, 1, QtWidgets.QTableWidgetItem(items))
            row2 = row2 + 1

        self.tableWidget.setShowGrid(False)

    ##### Click the EXECUTE button
    def EXECUTE(self):
        self.abc_select.clear()
        for i in self.tableWidget.selectedIndexes():
            self.abc_select.append(abc_list[i.row()])

        for file in self.abc_select:
            sizeofFile = len(file)
            fileNames = file[:sizeofFile - 4]
            geoNode = hou.node("/obj/").createNode("geo", "ABC_" + fileNames)
            geoNode.setColor(hou.Color(0, 0, 0))
            geoNode.setDisplayFlag(False)
            geoNode.setSelectableInViewport(False)

            abcNode = geoNode.createNode("alembic", "ABC_" + fileNames)
            abcNode.parm("fileName").set(self.abcPath + fileNames + ".abc")

            if self.createTransformChkBx.isChecked():
                transformNode = geoNode.createNode("xform")
                transformNode.setInput(0, abcNode)

            if self.createConvertChkBx.isChecked():
                convertNode = geoNode.createNode("convert")
                if self.createTransformChkBx.isChecked():
                    convertNode.setInput(0, transformNode)
                else:
                    convertNode.setInput(0, abcNode)

            if self.createNormalChkBx.isChecked():
                normalNode = geoNode.createNode("normal")
                if self.createConvertChkBx.isChecked():
                    normalNode.setInput(0, convertNode)
                if self.createConvertChkBx.isChecked() == False and self.createTransformChkBx.isChecked():
                    normalNode.setInput(0, transformNode)
                if self.createConvertChkBx.isChecked() == False and self.createTransformChkBx.isChecked() == False:
                    normalNode.setInput(0, abcNode)

            if self.addFileCacheChkBx.isChecked():
                fileNode = geoNode.createNode("filecache", "GEO_" + fileNames)
                fileNode.parm("file").set("$JOB/$HIPNAME/geo/ABC_cache/$OS/$OS.$F4.bgeo.sc")
                fileNode.parm("loadfromdisk").set(0)

                if self.createNormalChkBx.isChecked():
                    fileNode.setInput(0, normalNode)
                if self.createNormalChkBx.isChecked() == False:
                    if self.createConvertChkBx.isChecked():
                        fileNode.setInput(0, convertNode)
                    elif self.createConvertChkBx.isChecked() == False:
                        if self.createTransformChkBx.isChecked():
                            fileNode.setInput(0, transformNode)
                        else:
                            fileNode.setInput(0, abcNode)

            nullNode = geoNode.createNode("null", "OUT_" + fileNames.upper())
            nullNode.setColor(hou.Color(0, 0, 0))
            nullNode.setGenericFlag(hou.nodeFlag.Render, 1)
            nullNode.setGenericFlag(hou.nodeFlag.Visible, 1)

            if self.addFileCacheChkBx.isChecked():
                nullNode.setInput(0, fileNode)
            elif self.addFileCacheChkBx.isChecked() == False:
                if self.createNormalChkBx.isChecked():
                    nullNode.setInput(0, normalNode)
                elif self.createNormalChkBx.isChecked() == False:
                    if self.createConvertChkBx.isChecked():
                        nullNode.setInput(0, convertNode)
                    elif self.createConvertChkBx.isChecked() == False:
                        if self.createTransformChkBx.isChecked():
                            nullNode.setInput(0, transformNode)
                        elif self.createTransformChkBx.isChecked() == False:
                            nullNode.setInput(0, abcNode)
            hou.node("/obj/" + "ABC_" + fileNames).layoutChildren()

        self.NETWORKBOX()

    ##### Create Network Box for all ABC geo nodes and Layout Selected
    def NETWORKBOX(self):
        for nodes in self.abc_select:
            self.len_of_nodes = len(nodes)
            # self.selectedNodes.append("/obj/" + "ABC_" + nodes[:self.len_of_nodes - 4])
            self.layoutNodes.append("ABC_" + nodes[:self.len_of_nodes - 4])
            print(self.layoutNodes)

        ##### Networkbox Code
        n_box = root.createNetworkBox()
        for nodes in self.layoutNodes:
            n_box.addItem(nodes)
        n_box.fitAroundContents()

        # root.layoutChildren(items = n_box, horizontal_spacing=1.7, vertical_spacing=1.7 )

        self.selectedNodes.clear()
        self.abc_select.clear()
        self.layoutNodes.clear()
        self.subDir.clear()

    ##### MAIN UI Function and CALL############################
    def mainWindow(self):
        self.setWindowTitle("Alembic Importer")
        self.setMinimumSize(QSize(550, 650))
        # self.setMaximumSize(QSize(550, 650))
        self.setStyleSheet(u"QPushButton"
                           u"{\n"
                           "		background-color: rgb(102, 102, 102);\n"
                           "		border : 1px solid #000;\n"
                           "		font: bold 11pt \"Calibri\";\n"
                           "		color:rgba(255, 255, 255, 255);\n"
                           "		padding-left : 8px;\n"
                           "		padding-right : 8px;\n"
                           "		padding-top : 4px;\n"
                           "		padding-bottom : 6px;\n"
                           "		margin:3px;\n"
                           "}\n"
                           "QPushButton:hover{\n"
                           "		background-color: rgba(99, 99, 99, 200);\n"
                           "		border-radius:3px;\n"
                           "		font: 11pt \"Calibri\";\n"
                           "}\n"
                           "QPushButton:pressed{\n"
                           "		background-color: rgba(50, 50, 50, 200);\n"
                           "		padding-left : 4px;\n"
                           "		padding-top : 4px;\n"
                           "}\n"
                           "QHeaderView::section{\n"
                           "	    font-size: 8pt;\n"
                           "        border: 0px;\n"
                           "        text-align: left;\n"
                           "}\n"
                           "QTableView::item{\n"
                           "	    font-size: 8pt;\n"
                           "        border: 0px;\n"
                           "}")
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(0, 0, -1, 0)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.selectAllBtn = QPushButton()
        self.selectAllBtn.setObjectName(u"selectAllBtn")
        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 220))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        gradient = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient.setSpread(QGradient.PadSpread)
        gradient.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient.setColorAt(0, QColor(114, 129, 239, 219))
        gradient.setColorAt(1, QColor(114, 239, 152, 226))
        brush1 = QBrush(gradient)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        gradient1 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient1.setSpread(QGradient.PadSpread)
        gradient1.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient1.setColorAt(0, QColor(114, 129, 239, 219))
        gradient1.setColorAt(1, QColor(114, 239, 152, 226))
        brush2 = QBrush(gradient1)
        palette.setBrush(QPalette.Active, QPalette.Base, brush2)
        gradient2 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient2.setSpread(QGradient.PadSpread)
        gradient2.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient2.setColorAt(0, QColor(114, 129, 239, 219))
        gradient2.setColorAt(1, QColor(114, 239, 152, 226))
        brush3 = QBrush(gradient2)
        palette.setBrush(QPalette.Active, QPalette.Window, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        gradient3 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient3.setSpread(QGradient.PadSpread)
        gradient3.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient3.setColorAt(0, QColor(114, 129, 239, 219))
        gradient3.setColorAt(1, QColor(114, 239, 152, 226))
        brush4 = QBrush(gradient3)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        gradient4 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient4.setSpread(QGradient.PadSpread)
        gradient4.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient4.setColorAt(0, QColor(114, 129, 239, 219))
        gradient4.setColorAt(1, QColor(114, 239, 152, 226))
        brush5 = QBrush(gradient4)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush5)
        gradient5 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient5.setSpread(QGradient.PadSpread)
        gradient5.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient5.setColorAt(0, QColor(114, 129, 239, 219))
        gradient5.setColorAt(1, QColor(114, 239, 152, 226))
        brush6 = QBrush(gradient5)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.WindowText, brush)
        gradient6 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient6.setSpread(QGradient.PadSpread)
        gradient6.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient6.setColorAt(0, QColor(114, 129, 239, 219))
        gradient6.setColorAt(1, QColor(114, 239, 152, 226))
        brush7 = QBrush(gradient6)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush7)
        palette.setBrush(QPalette.Disabled, QPalette.Text, brush)
        palette.setBrush(QPalette.Disabled, QPalette.ButtonText, brush)
        gradient7 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient7.setSpread(QGradient.PadSpread)
        gradient7.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient7.setColorAt(0, QColor(114, 129, 239, 219))
        gradient7.setColorAt(1, QColor(114, 239, 152, 226))
        brush8 = QBrush(gradient7)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush8)
        gradient8 = QLinearGradient(0, 0.505682, 1, 0.477)
        gradient8.setSpread(QGradient.PadSpread)
        gradient8.setCoordinateMode(QGradient.ObjectBoundingMode)
        gradient8.setColorAt(0, QColor(114, 129, 239, 219))
        gradient8.setColorAt(1, QColor(114, 239, 152, 226))
        brush9 = QBrush(gradient8)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush9)
        font = QFont()
        font.setFamily(u"Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.mainLabel = QLabel()
        self.mainLabel.setObjectName(u"mainLabel")
        font1 = QFont()
        font1.setFamily(u"Calibri")
        font1.setPointSize(20)
        font1.setBold(True)
        font1.setWeight(75)
        self.mainLabel.setFont(font1)
        self.mainLabel.setStyleSheet(u"font: bold 20pt \"Calibri\";\n"
                                     "color: rgba(255, 255, 255, 255);")
        self.mainLabel.setFrameShape(QFrame.NoFrame)
        self.mainLabel.setAlignment(Qt.AlignCenter)
        self.verticalLayout_2.addWidget(self.mainLabel)
        self.refreshBtn = QPushButton()
        self.refreshBtn.setObjectName(u"refreshBtn")
        self.refreshBtn.setFont(font)
        self.refreshBtn.setStyleSheet(u"")
        self.verticalLayout_2.addWidget(self.refreshBtn)
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.selectABCBtn = QPushButton()
        self.selectABCBtn.setObjectName(u"selectABCBtn")
        self.horizontalLayout_4.addWidget(self.selectABCBtn)
        self.pathEdit = QLineEdit()
        self.pathEdit.setObjectName(u"pathEdit")
        self.horizontalLayout_4.addWidget(self.pathEdit)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.tableWidget = QTableWidget()
        if (self.tableWidget.columnCount() < 2):
            self.tableWidget.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableWidget.setStyleSheet(u"font-size : 12px;\n")
        self.tableWidget.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableWidget.setObjectName(u"tableWidget")
        self.tableWidget.setMaximumSize(QSize(530, 500))
        font3 = QFont()
        font3.setStyleStrategy(QFont.PreferAntialias)
        self.tableWidget.setFont(font3)
        self.tableWidget.setFrameShape(QFrame.Panel)
        self.tableWidget.horizontalHeader().setMinimumSectionSize(20)
        self.tableWidget.horizontalHeader().setDefaultSectionSize(90)
        self.verticalLayout.addWidget(self.tableWidget)
        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, -1, 0, -1)
        self.includeSubChkBx = QCheckBox()
        self.includeSubChkBx.setObjectName(u"includeSubChkBx")
        self.horizontalLayout_6.addWidget(self.includeSubChkBx)
        self.createTransformChkBx = QCheckBox()
        self.createTransformChkBx.setObjectName(u"createTransformChkBx")
        self.horizontalLayout_6.addWidget(self.createTransformChkBx)
        self.createConvertChkBx = QCheckBox()
        self.createConvertChkBx.setObjectName(u"createConvertChkBx")
        self.createConvertChkBx.setLayoutDirection(Qt.LeftToRight)
        self.horizontalLayout_6.addWidget(self.createConvertChkBx)
        self.createNormalChkBx = QCheckBox()
        self.createNormalChkBx.setObjectName(u"createConvertChkBx")
        self.createNormalChkBx.setLayoutDirection(Qt.LeftToRight)
        self.horizontalLayout_6.addWidget(self.createNormalChkBx)
        self.addFileCacheChkBx = QCheckBox()
        self.addFileCacheChkBx.setObjectName(u"addFileCacheChkBx")
        self.horizontalLayout_6.addWidget(self.addFileCacheChkBx)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.verticalLayout.addItem(self.horizontalSpacer)
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.executeBtn = QPushButton()
        self.executeBtn.setObjectName(u"executeBtn")
        self.horizontalLayout_3.addWidget(self.executeBtn)
        self.cancelBtn = QPushButton()
        self.cancelBtn.setObjectName(u"cancelBtn")
        self.horizontalLayout_3.addWidget(self.cancelBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.retranslateUi()

    def retranslateUi(self):
        self.setWindowTitle(QCoreApplication.translate("abcImporter", u"ABC Importer : Houdini Extension", None))
        self.mainLabel.setText(QCoreApplication.translate("abcImporter", u"MultiAlembic Importer v1.0", None))
        self.refreshBtn.setText(QCoreApplication.translate("abcImporter", u"R e f r e s h U I ", None))
        self.selectABCBtn.setText(QCoreApplication.translate("abcImporter", u"Select Folder", None))
        # if QT_CONFIG(tooltip)
        self.pathEdit.setToolTip("")
        # endif // QT_CONFIG(tooltip)
        self.pathEdit.setInputMask("")
        self.pathEdit.setText("")
        ___qtablewidgetitem = self.tableWidget.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("widget", u"ABC Files", None));
        ___qtablewidgetitem1 = self.tableWidget.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("widget", u"Date Modified", None));
        self.includeSubChkBx.setText(QCoreApplication.translate("widget", u"Include SubFold", None))
        self.createTransformChkBx.setText(QCoreApplication.translate("widget", u"Add Transform", None))
        self.createConvertChkBx.setText(QCoreApplication.translate("widget", u"Add Convert", None))
        self.addFileCacheChkBx.setText(QCoreApplication.translate("widget", u"Add FileCache", None))
        self.createNormalChkBx.setText(QCoreApplication.translate("widget", u"Add Normal", None))
        self.executeBtn.setText(QCoreApplication.translate("widget", u"Execute", None))
        self.cancelBtn.setText(QCoreApplication.translate("widget", u"Cancel", None))


dialog = MainWindow()
dialog.show()

