# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './regbank_address_dialog.ui'
#
# Created: Tue Jun  9 00:11:54 2015
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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(600, 174)
        Dialog.setMinimumSize(QtCore.QSize(600, 174))
        Dialog.setMaximumSize(QtCore.QSize(600, 174))
        self.verticalLayout_4 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.main_label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.main_label.setFont(font)
        self.main_label.setObjectName(_fromUtf8("main_label"))
        self.horizontalLayout_2.addWidget(self.main_label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.base_addr = QtGui.QLineEdit(Dialog)
        self.base_addr.setMaximumSize(QtCore.QSize(180, 36))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.base_addr.setFont(font)
        self.base_addr.setAlignment(QtCore.Qt.AlignCenter)
        self.base_addr.setObjectName(_fromUtf8("base_addr"))
        self.verticalLayout_2.addWidget(self.base_addr)
        self.addr_offset_type = QtGui.QComboBox(Dialog)
        self.addr_offset_type.setObjectName(_fromUtf8("addr_offset_type"))
        self.addr_offset_type.addItem(_fromUtf8(""))
        self.addr_offset_type.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.addr_offset_type)
        self.horizontalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem4 = QtGui.QSpacerItem(208, 17, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.accept_button = QtGui.QPushButton(Dialog)
        self.accept_button.setMinimumSize(QtCore.QSize(94, 31))
        self.accept_button.setMaximumSize(QtCore.QSize(94, 31))
        self.accept_button.setObjectName(_fromUtf8("accept_button"))
        self.horizontalLayout.addWidget(self.accept_button)
        spacerItem5 = QtGui.QSpacerItem(211, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem5)
        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.main_label.setText(_translate("Dialog", "Enter base address and offset type for *", None))
        self.label.setText(_translate("Dialog", "Base Address (Absolute)", None))
        self.label_2.setText(_translate("Dialog", "Address Offset Type", None))
        self.base_addr.setText(_translate("Dialog", "0", None))
        self.addr_offset_type.setItemText(0, _translate("Dialog", "Byte offsets", None))
        self.addr_offset_type.setItemText(1, _translate("Dialog", "Word offsets", None))
        self.accept_button.setText(_translate("Dialog", "OK", None))

