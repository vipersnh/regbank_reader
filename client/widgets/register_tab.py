# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './client/widgets/register_tab.ui'
#
# Created: Sun Aug  2 23:26:00 2015
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_register_tab(object):
    def setupUi(self, register_tab):
        register_tab.setObjectName(_fromUtf8("register_tab"))
        register_tab.resize(906, 538)
        register_tab.setMinimumSize(QtCore.QSize(0, 0))
        register_tab.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtGui.QVBoxLayout(register_tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.label = QtGui.QLabel(register_tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_5.addWidget(self.label)
        self.formLayout.setLayout(0, QtGui.QFormLayout.LabelRole, self.horizontalLayout_5)
        self.lineEdit_registerName = QtGui.QLineEdit(register_tab)
        self.lineEdit_registerName.setMinimumSize(QtCore.QSize(181, 31))
        self.lineEdit_registerName.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_registerName.setReadOnly(True)
        self.lineEdit_registerName.setObjectName(_fromUtf8("lineEdit_registerName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEdit_registerName)
        self.pushButton_readValue = QtGui.QPushButton(register_tab)
        self.pushButton_readValue.setMinimumSize(QtCore.QSize(121, 31))
        self.pushButton_readValue.setObjectName(_fromUtf8("pushButton_readValue"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.pushButton_readValue)
        self.lineEdit_registerValue = QtGui.QLineEdit(register_tab)
        self.lineEdit_registerValue.setMinimumSize(QtCore.QSize(181, 31))
        self.lineEdit_registerValue.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_registerValue.setReadOnly(False)
        self.lineEdit_registerValue.setObjectName(_fromUtf8("lineEdit_registerValue"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit_registerValue)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_5 = QtGui.QLabel(register_tab)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout.addWidget(self.label_5)
        self.formLayout.setLayout(2, QtGui.QFormLayout.LabelRole, self.horizontalLayout)
        self.comboBox_registerAutoReadMode = QtGui.QComboBox(register_tab)
        self.comboBox_registerAutoReadMode.setMinimumSize(QtCore.QSize(161, 31))
        self.comboBox_registerAutoReadMode.setObjectName(_fromUtf8("comboBox_registerAutoReadMode"))
        self.comboBox_registerAutoReadMode.addItem(_fromUtf8(""))
        self.comboBox_registerAutoReadMode.addItem(_fromUtf8(""))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.comboBox_registerAutoReadMode)
        self.horizontalLayout_6.addLayout(self.formLayout)
        self.line = QtGui.QFrame(register_tab)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout_6.addWidget(self.line)
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label_2 = QtGui.QLabel(register_tab)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout_2.addWidget(self.label_2)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.LabelRole, self.horizontalLayout_2)
        self.lineEdit_sheetBaseAddr = QtGui.QLineEdit(register_tab)
        self.lineEdit_sheetBaseAddr.setMinimumSize(QtCore.QSize(161, 31))
        self.lineEdit_sheetBaseAddr.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_sheetBaseAddr.setReadOnly(True)
        self.lineEdit_sheetBaseAddr.setObjectName(_fromUtf8("lineEdit_sheetBaseAddr"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEdit_sheetBaseAddr)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label_3 = QtGui.QLabel(register_tab)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.horizontalLayout_3.addWidget(self.label_3)
        self.formLayout_2.setLayout(1, QtGui.QFormLayout.LabelRole, self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label_4 = QtGui.QLabel(register_tab)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.horizontalLayout_4.addWidget(self.label_4)
        self.formLayout_2.setLayout(2, QtGui.QFormLayout.LabelRole, self.horizontalLayout_4)
        self.lineEdit_registerOffsetAddr = QtGui.QLineEdit(register_tab)
        self.lineEdit_registerOffsetAddr.setMinimumSize(QtCore.QSize(161, 31))
        self.lineEdit_registerOffsetAddr.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_registerOffsetAddr.setReadOnly(True)
        self.lineEdit_registerOffsetAddr.setObjectName(_fromUtf8("lineEdit_registerOffsetAddr"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.lineEdit_registerOffsetAddr)
        self.lineEdit_sheetOffsetType = QtGui.QLineEdit(register_tab)
        self.lineEdit_sheetOffsetType.setMinimumSize(QtCore.QSize(161, 31))
        self.lineEdit_sheetOffsetType.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit_sheetOffsetType.setReadOnly(True)
        self.lineEdit_sheetOffsetType.setObjectName(_fromUtf8("lineEdit_sheetOffsetType"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.lineEdit_sheetOffsetType)
        self.horizontalLayout_6.addLayout(self.formLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.line_2 = QtGui.QFrame(register_tab)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout.addWidget(self.line_2)
        self.tableWidget_subfieldsView = QtGui.QTableWidget(register_tab)
        self.tableWidget_subfieldsView.setObjectName(_fromUtf8("tableWidget_subfieldsView"))
        self.tableWidget_subfieldsView.setColumnCount(0)
        self.tableWidget_subfieldsView.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget_subfieldsView)

        self.retranslateUi(register_tab)
        QtCore.QMetaObject.connectSlotsByName(register_tab)

    def retranslateUi(self, register_tab):
        register_tab.setWindowTitle(QtGui.QApplication.translate("register_tab", "Register", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("register_tab", "Register :", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_readValue.setText(QtGui.QApplication.translate("register_tab", "Read Value", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("register_tab", "Auto Read Mode:", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_registerAutoReadMode.setItemText(0, QtGui.QApplication.translate("register_tab", "Autoread on write", None, QtGui.QApplication.UnicodeUTF8))
        self.comboBox_registerAutoReadMode.setItemText(1, QtGui.QApplication.translate("register_tab", "Read only on demand", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("register_tab", "Base Addr :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("register_tab", "Offset Addr :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("register_tab", "Offset Type :", None, QtGui.QApplication.UnicodeUTF8))

