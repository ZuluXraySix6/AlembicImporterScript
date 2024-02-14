import time
from PySide2 import QtCore
from PySide2 import QtWidgets
import hou
import os
import sys
import datetime as datetime
import toolutils
from PySide2.QtWidgets import *

global myWindow


class MainWindow(QtWidgets.QDialog):
    def __init__(self, parm=None, parent=hou.qt.mainWindow()):
        super(MainWindow, self).__init__(parent)
        self.abcPath = ""
        self.abcFilePath = ""
        self.abcFileList = []
        self.fileDateModified = []
        self.selectedFiles = []
        self.node_for_network_box = []
        self.camera_for_networkbox = []
        self.camera_files = []
        self.mainWindow()
        # Set columns widths
        self.abcTableWidget.setColumnWidth(0, 180)
        self.abcTableWidget.setColumnWidth(1, 100)
        self.abcTableWidget.setColumnWidth(2, 150)
        self.ALL_BUTTONS()

    def ALL_BUTTONS(self):
        self.selectFolderBtn.clicked.connect(self.SET_ABC_PATH)
        self.executeBtn.clicked.connect(self.EXECUTE)
        self.cancelBtn.clicked.connect(self.close)

    def SET_ABC_PATH(self):
        self.abcPath = hou.ui.selectFile(title="Select folder containing alembic files",
                                         file_type=hou.fileType.Directory)
        if self.abcPath:
            self.abcFileList.clear()
            self.fileDateModified.clear()
            self.selectedFiles.clear()
            self.node_for_network_box.clear()
            self.camera_for_networkbox.clear()
            self.camera_files.clear()
            self.abcpathField.setText(self.abcPath)
            fileList = os.listdir(self.abcPath)
            for x in fileList:
                if x.endswith(".abc") or x.endswith(".ABC"):
                    fileDate = os.path.getmtime(self.abcPath + x)
                    fileDate = time.ctime(fileDate)
                    x = x[:-4]
                    self.abcFileList.append(x)
                    self.fileDateModified.append(fileDate)
            self.abcTableWidget.setRowCount(len(self.abcFileList))
            row0 = 0
            row2 = 0
            for y in self.abcFileList:
                self.abcTableWidget.setItem(row0, 0, QTableWidgetItem(y))
                # Look for camera files among the alembic files
                file_name = y.lower()
                if "cam" in file_name:
                    self.camera_files.append(y)
                    item = QtWidgets.QTableWidgetItem("Archive Camera")
                    item.setFlags(QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    self.abcTableWidget.setItem(row0, 1, item)
                else:
                    item = QtWidgets.QTableWidgetItem("File")
                    item.setFlags(QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    self.abcTableWidget.setItem(row0, 1, item)
                row0 += 1
            for z in self.fileDateModified:
                item = QtWidgets.QTableWidgetItem(z)
                item.setFlags(QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                self.abcTableWidget.setItem(row2, 2, item)
                row2 += 1
            self.abcTableWidget.setShowGrid(False)
        else:
            self.abcPath = ""
            self.abcFilePath = ""
            self.abcFileList.clear()
            self.fileDateModified.clear()
            self.selectedFiles.clear()
            self.node_for_network_box.clear()
            self.camera_for_networkbox.clear()
            self.camera_files.clear()
            self.abcTableWidget.setRowCount(0)
            self.abcpathField.setText("Select a folder with ABCs....")
            print("Path needs to pe specified")
        # Make all rows and columns non-Editable
        self.abcTableWidget.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        total_cam_files = len(self.camera_files)
        if total_cam_files > 0:
            hou.ui.displayMessage("Seems like we found some camera/cameras in the folder." + "\nTotal : " + str(
                total_cam_files) + "." + "\nIf imported, will be imported as Alembic Archives. So Chill.")
        # self.camera_files.clear()

    def EXECUTE(self):
        cam_netbox_size = 0
        self.selectedFiles = self.abcTableWidget.selectedIndexes()
        for x in self.selectedFiles:
            camFile = self.abcFileList[x.row()]
            file_name = camFile.lower()
            if "cam" in file_name:
                camNode = hou.node("/obj/").createNode("alembicarchive", "ABC_CAM_" + file_name)
                camPath = self.abcPath + file_name + ".abc"
                camNode.parm("fileName").set(camPath)
                # Build or Update Hierarchy on the Camera Node
                camNode.parm("buildHierarchy").pressButton()
                camNode.setColor(hou.Color(1, 0, 0))
                camNode.setGenericFlag(hou.nodeFlag.Visible, 0)
                camNode.setGenericFlag(hou.nodeFlag.Selectable, 0)
                self.camera_for_networkbox.append(camNode)
        if len(self.camera_for_networkbox) > 0:
            # Create a Network Box and add camera into it...
            camLayout = hou.node("/obj/").layoutChildren(items=self.node_for_network_box, horizontal_spacing=1.5,
                                                         vertical_spacing=1)
            cam_box = hou.node("/obj").createNetworkBox("Camera")
            cam_box.setComment("ABC Camera")
            for cam in self.camera_for_networkbox:
                cam_box.addItem(cam)
            cam_box.fitAroundContents()
            cam_box.setColor(hou.Color(0, 0, 0))
            # Camera Network Box Size
            cam_netbox_size = cam_box.size()[0]

        for current_file in self.selectedFiles:
            checkedNodes = []
            file_name = self.abcFileList[current_file.row()]
            if "cam" not in file_name:
                # We are calling the index values from the List "selectedFiles" and then using those
                # for ABC files that are selected.
                geoNode = hou.node("/obj/").createNode("geo", "ABC_" + file_name)
                geoNode.setColor(hou.Color(0, 0, 0))
                geoNode.setSelectableInViewport(False)
                self.node_for_network_box.append(geoNode)
                abcNode = geoNode.createNode("alembic", "ABC_" + file_name)
                self.abcFilePath = self.abcPath + file_name + ".abc"
                abcNode.parm("fileName").set(self.abcFilePath)
                if self.chkBxAddTransform.isChecked():
                    transformNode = geoNode.createNode("xform")
                    checkedNodes.append(transformNode)
                if self.chkBxAddConvert.isChecked():
                    convertNode = geoNode.createNode("convert")
                    checkedNodes.append(convertNode)
                if self.chkBxAddNormal.isChecked():
                    normalNode = geoNode.createNode("normal")
                    checkedNodes.append(normalNode)
                if self.chkBxAddFileCache.isChecked():
                    fileNode = geoNode.createNode("filecache", "GEO_" + file_name)
                    fileNode.parm("basename").set("$OS")
                    checkedNodes.append(fileNode)
                # Just connect one node to another after they are created.
                if len(checkedNodes) > 0:
                    for item in checkedNodes:
                        if item == checkedNodes[0]:
                            item.setInput(0, abcNode)
                            continue
                        item.setInput(0, checkedNodes[checkedNodes.index(item) - 1])
                        if item == checkedNodes[(len(checkedNodes) - 1)]:
                            nullNode = geoNode.createNode("null", "OUT_" + file_name.upper())
                            nullNode.setColor(hou.Color(0, 0, 0))
                            nullNode.setGenericFlag(hou.nodeFlag.Render, 1)
                            nullNode.setGenericFlag(hou.nodeFlag.Visible, 1)
                            nullNode.setInput(0, item)
                    hou.node("/obj/" + "ABC_" + file_name).layoutChildren()
                else:
                    nullNode = geoNode.createNode("null", "OUT_" + file_name.upper())
                    nullNode.setColor(hou.Color(0, 0, 0))
                    nullNode.setGenericFlag(hou.nodeFlag.Render, 1)
                    nullNode.setGenericFlag(hou.nodeFlag.Visible, 1)
                    nullNode.setInput(0, abcNode)
                    hou.node("/obj/" + "ABC_" + file_name).layoutChildren()
        if len(self.node_for_network_box) > 0:
            nodeLayout = hou.node("/obj/").layoutChildren(items=self.node_for_network_box, horizontal_spacing=3,
                                                          vertical_spacing=.5)
            # Create a Network Box and add geo nodes into it...
            box = hou.node("/obj").createNetworkBox("Nodes")
            box.setComment("ABC Files")
            for node in self.node_for_network_box:
                box.addItem(node)
            box.fitAroundContents()
            box.setColor(hou.Color(0, 0, 0))
            # Move the networkbox below the CAMERA networkbox
            cam_netbox_size = box.position()[0] + cam_netbox_size
            box.move(hou.Vector2(cam_netbox_size * 2.5, 0))
            box_size = box.size()
            box.resize(hou.Vector2(0.5, 0.5))

        # Set the camera view of the imported Camera
        cameras = hou.nodeType(hou.objNodeTypeCategory(), "cam").instances()
        if len(cameras) > 0:
            desktop = hou.ui.curDesktop()
            sceneViewer = desktop.paneTabOfType(hou.paneTabType.SceneViewer)
            viewPort = sceneViewer.curViewport()
            viewPort.setCamera(cameras[0].path())
        self.close()
    def mainWindow(self):
        self.setWindowTitle("Alembic Importer")
        self.setMinimumSize(QSize(550, 650))
        self.setStyleSheet(u"QPushButton"
                           u"{\n"
                           "		background-color: rgb(102, 102, 102);\n"
                           "		border : 1px solid #000;\n"
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
                           "		font: 9pt \"Calibri\";\n"
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
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.main = QtWidgets.QVBoxLayout()
        self.main.setSpacing(0)
        self.main.setObjectName("main")
        self.widgetNameWidget = QtWidgets.QWidget(self)
        self.widgetNameWidget.setMaximumSize(QtCore.QSize(16777215, 55))
        self.widgetNameWidget.setObjectName("widgetNameWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widgetNameWidget)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widgetNameWidget)
        self.label.setMaximumSize(QtCore.QSize(16777215, 70))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.main.addWidget(self.widgetNameWidget, 0, QtCore.Qt.AlignHCenter)
        self.pathWidget = QtWidgets.QWidget(self)
        self.pathWidget.setMaximumSize(QtCore.QSize(16777215, 50))
        self.pathWidget.setObjectName("pathWidget")
        self.horizontalLayout_17 = QtWidgets.QHBoxLayout(self.pathWidget)
        self.horizontalLayout_17.setContentsMargins(-1, 6, 9, 6)
        self.horizontalLayout_17.setSpacing(0)
        self.horizontalLayout_17.setObjectName("horizontalLayout_17")
        self.widget_10 = QtWidgets.QWidget(self.pathWidget)
        self.widget_10.setObjectName("widget_10")
        self.horizontalLayout_18 = QtWidgets.QHBoxLayout(self.widget_10)
        self.horizontalLayout_18.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_18.setSpacing(0)
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.selectFolderBtn = QtWidgets.QPushButton(self.widget_10)
        self.selectFolderBtn.setObjectName("selectFolderBtn")
        self.horizontalLayout_18.addWidget(self.selectFolderBtn)
        self.horizontalLayout_17.addWidget(self.widget_10)
        self.widget_14 = QtWidgets.QWidget(self.pathWidget)
        self.widget_14.setObjectName("widget_14")
        self.horizontalLayout_19 = QtWidgets.QHBoxLayout(self.widget_14)
        self.horizontalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_19.setSpacing(0)
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.abcpathField = QtWidgets.QLineEdit(self.widget_14)
        self.abcpathField.setObjectName("abcpathField")
        self.horizontalLayout_19.addWidget(self.abcpathField)
        self.horizontalLayout_17.addWidget(self.widget_14)
        self.main.addWidget(self.pathWidget)
        self.tableWidget = QtWidgets.QWidget(self)
        self.tableWidget.setObjectName("tableWidget")
        self.horizontalLayout_20 = QtWidgets.QHBoxLayout(self.tableWidget)
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.abcTableWidget = QtWidgets.QTableWidget(self.tableWidget)
        self.abcTableWidget.setObjectName("abcTableWidget")
        self.abcTableWidget.setColumnCount(3)
        self.abcTableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.abcTableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.abcTableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.abcTableWidget.setHorizontalHeaderItem(2, item)
        self.horizontalLayout_20.addWidget(self.abcTableWidget)
        self.main.addWidget(self.tableWidget)
        self.sopsWidget = QtWidgets.QWidget(self)
        self.sopsWidget.setMaximumSize(QtCore.QSize(16777215, 50))
        self.sopsWidget.setObjectName("sopsWidget")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.sopsWidget)
        self.horizontalLayout_5.setContentsMargins(12, 0, 12, 0)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.widget_3 = QtWidgets.QWidget(self.sopsWidget)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_9 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.widget_7 = QtWidgets.QWidget(self.widget_3)
        self.widget_7.setObjectName("widget_7")
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout(self.widget_7)
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.chkBxIncludeSubfolders = QtWidgets.QCheckBox(self.widget_7)
        self.chkBxIncludeSubfolders.setObjectName("chkBxIncludeSubfolders")
        self.horizontalLayout_10.addWidget(self.chkBxIncludeSubfolders)
        self.horizontalLayout_9.addWidget(self.widget_7)
        self.horizontalLayout_5.addWidget(self.widget_3)
        self.widget_4 = QtWidgets.QWidget(self.sopsWidget)
        self.widget_4.setObjectName("widget_4")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout(self.widget_4)
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.widget_9 = QtWidgets.QWidget(self.widget_4)
        self.widget_9.setObjectName("widget_9")
        self.horizontalLayout_11 = QtWidgets.QHBoxLayout(self.widget_9)
        self.horizontalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_11.setSpacing(0)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.chkBxAddTransform = QtWidgets.QCheckBox(self.widget_9)
        self.chkBxAddTransform.setObjectName("chkBxAddTransform")
        self.horizontalLayout_11.addWidget(self.chkBxAddTransform)
        self.horizontalLayout_8.addWidget(self.widget_9)
        self.horizontalLayout_5.addWidget(self.widget_4)
        self.widget_5 = QtWidgets.QWidget(self.sopsWidget)
        self.widget_5.setObjectName("widget_5")
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout(self.widget_5)
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_7.setSpacing(0)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.widget_11 = QtWidgets.QWidget(self.widget_5)
        self.widget_11.setObjectName("widget_11")
        self.horizontalLayout_12 = QtWidgets.QHBoxLayout(self.widget_11)
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_12.setSpacing(0)
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.chkBxAddConvert = QtWidgets.QCheckBox(self.widget_11)
        self.chkBxAddConvert.setObjectName("chkBxAddConvert")
        self.horizontalLayout_12.addWidget(self.chkBxAddConvert)
        self.horizontalLayout_7.addWidget(self.widget_11)
        self.horizontalLayout_5.addWidget(self.widget_5)
        self.widget_6 = QtWidgets.QWidget(self.sopsWidget)
        self.widget_6.setObjectName("widget_6")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout(self.widget_6)
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.widget_13 = QtWidgets.QWidget(self.widget_6)
        self.widget_13.setObjectName("widget_13")
        self.horizontalLayout_13 = QtWidgets.QHBoxLayout(self.widget_13)
        self.horizontalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_13.setSpacing(0)
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.chkBxAddNormal = QtWidgets.QCheckBox(self.widget_13)
        self.chkBxAddNormal.setObjectName("chkBxAddNormal")
        self.horizontalLayout_13.addWidget(self.chkBxAddNormal)
        self.horizontalLayout_6.addWidget(self.widget_13)
        self.horizontalLayout_5.addWidget(self.widget_6)
        self.widget_8 = QtWidgets.QWidget(self.sopsWidget)
        self.widget_8.setObjectName("widget_8")
        self.horizontalLayout_14 = QtWidgets.QHBoxLayout(self.widget_8)
        self.horizontalLayout_14.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_14.setSpacing(0)
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.widget_12 = QtWidgets.QWidget(self.widget_8)
        self.widget_12.setObjectName("widget_12")
        self.horizontalLayout_15 = QtWidgets.QHBoxLayout(self.widget_12)
        self.horizontalLayout_15.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_15.setSpacing(0)
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.chkBxAddFileCache = QtWidgets.QCheckBox(self.widget_12)
        self.chkBxAddFileCache.setObjectName("chkBxAddFileCache")
        self.horizontalLayout_15.addWidget(self.chkBxAddFileCache)
        self.horizontalLayout_14.addWidget(self.widget_12)
        self.horizontalLayout_5.addWidget(self.widget_8)
        self.main.addWidget(self.sopsWidget)
        self.buttonsWidget = QtWidgets.QWidget(self)
        self.buttonsWidget.setMaximumSize(QtCore.QSize(16777215, 45))
        self.buttonsWidget.setObjectName("buttonsWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.buttonsWidget)
        self.horizontalLayout_2.setContentsMargins(-1, 7, -1, 7)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.widget = QtWidgets.QWidget(self.buttonsWidget)
        self.widget.setObjectName("widget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.executeBtn = QtWidgets.QPushButton(self.widget)
        self.executeBtn.setObjectName("executeBtn")
        self.horizontalLayout_3.addWidget(self.executeBtn)
        self.horizontalLayout_2.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.buttonsWidget)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.cancelBtn = QtWidgets.QPushButton(self.widget_2)
        self.cancelBtn.setObjectName("cancelBtn")
        self.horizontalLayout_4.addWidget(self.cancelBtn)
        self.horizontalLayout_2.addWidget(self.widget_2)
        self.main.addWidget(self.buttonsWidget)
        self.verticalLayout_2.addLayout(self.main)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "Bulk Alembic Importer v1.1.0"))
        self.label.setText(_translate("Form", "Bulk Alembic Importer v1.1.0"))
        self.selectFolderBtn.setText(_translate("Form", "Select Folder"))
        self.abcpathField.setPlaceholderText(_translate("Form", "ABC path.............."))
        item = self.abcTableWidget.horizontalHeaderItem(0)
        item.setText(_translate("Form", "ABC Files"))
        item = self.abcTableWidget.horizontalHeaderItem(1)
        item.setText(_translate("Form", "File Type"))
        item = self.abcTableWidget.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Date Modified"))
        self.chkBxIncludeSubfolders.setText(_translate("Form", "Include SubFolders"))
        self.chkBxAddTransform.setText(_translate("Form", "Add Transform"))
        self.chkBxAddConvert.setText(_translate("Form", "Add Convert"))
        self.chkBxAddNormal.setText(_translate("Form", "Add Normal"))
        self.chkBxAddFileCache.setText(_translate("Form", "Add File Cache"))
        self.executeBtn.setText(_translate("Form", "Execute"))
        self.cancelBtn.setText(_translate("Form", "Cancel"))


try:
    myWindow.close()
except:
    pass
myWindow = MainWindow()
myWindow.show()
