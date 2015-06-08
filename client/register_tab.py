# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './client/register_tab.ui'
#
# Created: Tue Jun  9 01:26:07 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

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
        self.register_name_disp = QtGui.QLineEdit(register_tab)
        self.register_name_disp.setMinimumSize(QtCore.QSize(181, 31))
        self.register_name_disp.setAlignment(QtCore.Qt.AlignCenter)
        self.register_name_disp.setReadOnly(True)
        self.register_name_disp.setObjectName(_fromUtf8("register_name_disp"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.register_name_disp)
        self.register_update_button = QtGui.QPushButton(register_tab)
        self.register_update_button.setMinimumSize(QtCore.QSize(121, 31))
        self.register_update_button.setObjectName(_fromUtf8("register_update_button"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.register_update_button)
        self.register_value_edit = QtGui.QLineEdit(register_tab)
        self.register_value_edit.setMinimumSize(QtCore.QSize(181, 31))
        self.register_value_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.register_value_edit.setReadOnly(False)
        self.register_value_edit.setObjectName(_fromUtf8("register_value_edit"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.register_value_edit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_5 = QtGui.QLabel(register_tab)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.horizontalLayout.addWidget(self.label_5)
        self.formLayout.setLayout(2, QtGui.QFormLayout.LabelRole, self.horizontalLayout)
        self.auto_read_mode = QtGui.QComboBox(register_tab)
        self.auto_read_mode.setMinimumSize(QtCore.QSize(161, 31))
        self.auto_read_mode.setObjectName(_fromUtf8("auto_read_mode"))
        self.auto_read_mode.addItem(_fromUtf8(""))
        self.auto_read_mode.addItem(_fromUtf8(""))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.auto_read_mode)
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
        self.base_addr_edit = QtGui.QLineEdit(register_tab)
        self.base_addr_edit.setMinimumSize(QtCore.QSize(161, 31))
        self.base_addr_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.base_addr_edit.setObjectName(_fromUtf8("base_addr_edit"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.base_addr_edit)
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
        self.addr_offset_type = QtGui.QComboBox(register_tab)
        self.addr_offset_type.setMinimumSize(QtCore.QSize(161, 31))
        self.addr_offset_type.setObjectName(_fromUtf8("addr_offset_type"))
        self.addr_offset_type.addItem(_fromUtf8(""))
        self.addr_offset_type.addItem(_fromUtf8(""))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.FieldRole, self.addr_offset_type)
        self.offset_addr_edit = QtGui.QLineEdit(register_tab)
        self.offset_addr_edit.setMinimumSize(QtCore.QSize(161, 31))
        self.offset_addr_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.offset_addr_edit.setObjectName(_fromUtf8("offset_addr_edit"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.offset_addr_edit)
        self.horizontalLayout_6.addLayout(self.formLayout_2)
        self.verticalLayout.addLayout(self.horizontalLayout_6)
        self.line_2 = QtGui.QFrame(register_tab)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.verticalLayout.addWidget(self.line_2)
        self.register_subfields_view = QtGui.QTableWidget(register_tab)
        self.register_subfields_view.setObjectName(_fromUtf8("register_subfields_view"))
        self.register_subfields_view.setColumnCount(0)
        self.register_subfields_view.setRowCount(0)
        self.verticalLayout.addWidget(self.register_subfields_view)

        self.retranslateUi(register_tab)
        QtCore.QMetaObject.connectSlotsByName(register_tab)

    def retranslateUi(self, register_tab):
        register_tab.setWindowTitle(_translate("register_tab", "Register", None))
        self.label.setText(_translate("register_tab", "Register :", None))
        self.register_update_button.setText(_translate("register_tab", "Read Value", None))
        self.label_5.setText(_translate("register_tab", "Auto Read Mode:", None))
        self.auto_read_mode.setItemText(0, _translate("register_tab", "Autoread on write", None))
        self.auto_read_mode.setItemText(1, _translate("register_tab", "Read only on demand", None))
        self.label_2.setText(_translate("register_tab", "Base Addr :", None))
        self.label_3.setText(_translate("register_tab", "Offset Addr :", None))
        self.label_4.setText(_translate("register_tab", "Offset Type :", None))
        self.addr_offset_type.setItemText(0, _translate("register_tab", "Byte Offset", None))
        self.addr_offset_type.setItemText(1, _translate("register_tab", "Word Offset", None))

