# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './register_tab.ui'
#
# Created: Mon Jun  1 01:16:25 2015
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
        register_tab.resize(584, 135)
        register_tab.setMinimumSize(QtCore.QSize(0, 0))
        register_tab.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.verticalLayout = QtGui.QVBoxLayout(register_tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(register_tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.register_name_disp = QtGui.QLineEdit(register_tab)
        self.register_name_disp.setMinimumSize(QtCore.QSize(181, 31))
        self.register_name_disp.setAlignment(QtCore.Qt.AlignCenter)
        self.register_name_disp.setReadOnly(True)
        self.register_name_disp.setObjectName(_fromUtf8("register_name_disp"))
        self.horizontalLayout.addWidget(self.register_name_disp)
        self.register_update_button = QtGui.QPushButton(register_tab)
        self.register_update_button.setObjectName(_fromUtf8("register_update_button"))
        self.horizontalLayout.addWidget(self.register_update_button)
        self.register_value_edit = QtGui.QLineEdit(register_tab)
        self.register_value_edit.setMinimumSize(QtCore.QSize(151, 31))
        self.register_value_edit.setAlignment(QtCore.Qt.AlignCenter)
        self.register_value_edit.setObjectName(_fromUtf8("register_value_edit"))
        self.horizontalLayout.addWidget(self.register_value_edit)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.register_subfields_view = QtGui.QTableWidget(register_tab)
        self.register_subfields_view.setObjectName(_fromUtf8("register_subfields_view"))
        self.register_subfields_view.setColumnCount(0)
        self.register_subfields_view.setRowCount(0)
        self.verticalLayout.addWidget(self.register_subfields_view)

        self.retranslateUi(register_tab)
        QtCore.QMetaObject.connectSlotsByName(register_tab)

    def retranslateUi(self, register_tab):
        register_tab.setWindowTitle(_translate("register_tab", "Register", None))
        self.label.setText(_translate("register_tab", "Register Name :", None))
        self.register_update_button.setText(_translate("register_tab", "Update Value", None))

