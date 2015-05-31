# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './regbank_address_dialog.ui'
#
# Created: Sun May 31 17:12:54 2015
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
        Dialog.resize(552, 174)
        Dialog.setMinimumSize(QtCore.QSize(552, 174))
        Dialog.setMaximumSize(QtCore.QSize(552, 174))
        self.gridLayout_2 = QtGui.QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.main_label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(75)
        self.main_label.setFont(font)
        self.main_label.setObjectName(_fromUtf8("main_label"))
        self.gridLayout_2.addWidget(self.main_label, 0, 0, 1, 3)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
        self.base_addr = QtGui.QLineEdit(Dialog)
        self.base_addr.setMaximumSize(QtCore.QSize(180, 36))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.base_addr.setFont(font)
        self.base_addr.setAlignment(QtCore.Qt.AlignCenter)
        self.base_addr.setObjectName(_fromUtf8("base_addr"))
        self.gridLayout.addWidget(self.base_addr, 0, 3, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 1, 1, 2)
        self.offset_size = QtGui.QLineEdit(Dialog)
        self.offset_size.setMaximumSize(QtCore.QSize(180, 36))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.offset_size.setFont(font)
        self.offset_size.setAlignment(QtCore.Qt.AlignCenter)
        self.offset_size.setObjectName(_fromUtf8("offset_size"))
        self.gridLayout.addWidget(self.offset_size, 1, 3, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 1, 0, 1, 3)
        spacerItem2 = QtGui.QSpacerItem(211, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem2, 2, 0, 1, 1)
        self.accept_button = QtGui.QPushButton(Dialog)
        self.accept_button.setMinimumSize(QtCore.QSize(94, 31))
        self.accept_button.setMaximumSize(QtCore.QSize(94, 31))
        self.accept_button.setObjectName(_fromUtf8("accept_button"))
        self.gridLayout_2.addWidget(self.accept_button, 2, 1, 1, 1)
        spacerItem3 = QtGui.QSpacerItem(211, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem3, 2, 2, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.main_label.setText(_translate("Dialog", "Enter base address and offset size for *", None))
        self.label.setText(_translate("Dialog", "Base Address (Absolute)", None))
        self.base_addr.setText(_translate("Dialog", "0", None))
        self.label_2.setText(_translate("Dialog", "Offset Size (Bytes)", None))
        self.offset_size.setText(_translate("Dialog", "0", None))
        self.accept_button.setText(_translate("Dialog", "OK", None))

