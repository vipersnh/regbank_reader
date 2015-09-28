# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './client/widgets/status_bar.ui'
#
# Created: Thu Sep 17 23:50:20 2015
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_statusWidget(object):
    def setupUi(self, statusWidget):
        statusWidget.setObjectName(_fromUtf8("statusWidget"))
        statusWidget.resize(625, 39)
        self.horizontalLayout = QtGui.QHBoxLayout(statusWidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_status = QtGui.QLabel(statusWidget)
        self.label_status.setMinimumSize(QtCore.QSize(441, 16))
        self.label_status.setText(_fromUtf8(""))
        self.label_status.setObjectName(_fromUtf8("label_status"))
        self.horizontalLayout.addWidget(self.label_status)
        self.line = QtGui.QFrame(statusWidget)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.label_record = QtGui.QLabel(statusWidget)
        self.label_record.setMinimumSize(QtCore.QSize(151, 21))
        self.label_record.setMaximumSize(QtCore.QSize(151, 16777215))
        self.label_record.setText(_fromUtf8(""))
        self.label_record.setObjectName(_fromUtf8("label_record"))
        self.horizontalLayout.addWidget(self.label_record)

        self.retranslateUi(statusWidget)
        QtCore.QMetaObject.connectSlotsByName(statusWidget)

    def retranslateUi(self, statusWidget):
        statusWidget.setWindowTitle(QtGui.QApplication.translate("statusWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))

