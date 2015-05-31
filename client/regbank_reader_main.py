# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './regbank_reader_main.ui'
#
# Created: Mon Jun  1 01:16:36 2015
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

class Ui_regbank_reader_main(object):
    def setupUi(self, regbank_reader_main):
        regbank_reader_main.setObjectName(_fromUtf8("regbank_reader_main"))
        regbank_reader_main.resize(793, 620)
        self.centralwidget = QtGui.QWidget(regbank_reader_main)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.target_button = QtGui.QPushButton(self.centralwidget)
        self.target_button.setMinimumSize(QtCore.QSize(151, 31))
        self.target_button.setMaximumSize(QtCore.QSize(151, 31))
        self.target_button.setObjectName(_fromUtf8("target_button"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.target_button)
        self.target_selection = QtGui.QComboBox(self.centralwidget)
        self.target_selection.setMinimumSize(QtCore.QSize(251, 31))
        self.target_selection.setMaximumSize(QtCore.QSize(251, 31))
        self.target_selection.setEditable(False)
        self.target_selection.setObjectName(_fromUtf8("target_selection"))
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.target_selection)
        self.regbank_button = QtGui.QPushButton(self.centralwidget)
        self.regbank_button.setMinimumSize(QtCore.QSize(151, 31))
        self.regbank_button.setMaximumSize(QtCore.QSize(151, 31))
        self.regbank_button.setObjectName(_fromUtf8("regbank_button"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.regbank_button)
        self.regbank_selection = QtGui.QComboBox(self.centralwidget)
        self.regbank_selection.setMinimumSize(QtCore.QSize(251, 31))
        self.regbank_selection.setMaximumSize(QtCore.QSize(251, 31))
        self.regbank_selection.setObjectName(_fromUtf8("regbank_selection"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.regbank_selection)
        self.horizontalLayout_2.addLayout(self.formLayout_2)
        self.line_2 = QtGui.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtGui.QFrame.VLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.horizontalLayout_2.addWidget(self.line_2)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.register_sheet_selection = QtGui.QComboBox(self.centralwidget)
        self.register_sheet_selection.setMinimumSize(QtCore.QSize(231, 31))
        self.register_sheet_selection.setMaximumSize(QtCore.QSize(231, 31))
        self.register_sheet_selection.setObjectName(_fromUtf8("register_sheet_selection"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.register_sheet_selection)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_3)
        self.register_selection = QtGui.QComboBox(self.centralwidget)
        self.register_selection.setMinimumSize(QtCore.QSize(231, 31))
        self.register_selection.setMaximumSize(QtCore.QSize(231, 31))
        self.register_selection.setObjectName(_fromUtf8("register_selection"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.register_selection)
        self.horizontalLayout_2.addLayout(self.formLayout)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.line_3 = QtGui.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtGui.QFrame.HLine)
        self.line_3.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_3.setObjectName(_fromUtf8("line_3"))
        self.verticalLayout.addWidget(self.line_3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.formLayout_3 = QtGui.QFormLayout()
        self.formLayout_3.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_3.setObjectName(_fromUtf8("formLayout_3"))
        self.horizontalLayout.addLayout(self.formLayout_3)
        self.formLayout_4 = QtGui.QFormLayout()
        self.formLayout_4.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_4.setObjectName(_fromUtf8("formLayout_4"))
        self.horizontalLayout.addLayout(self.formLayout_4)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.registers_tab_widget = QtGui.QTabWidget(self.centralwidget)
        self.registers_tab_widget.setMinimumSize(QtCore.QSize(773, 304))
        self.registers_tab_widget.setObjectName(_fromUtf8("registers_tab_widget"))
        self.verticalLayout.addWidget(self.registers_tab_widget)
        regbank_reader_main.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(regbank_reader_main)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 793, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        regbank_reader_main.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(regbank_reader_main)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        regbank_reader_main.setStatusBar(self.statusbar)
        self.actionLoad_Regbank = QtGui.QAction(regbank_reader_main)
        self.actionLoad_Regbank.setObjectName(_fromUtf8("actionLoad_Regbank"))
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(regbank_reader_main)
        self.registers_tab_widget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(regbank_reader_main)

    def retranslateUi(self, regbank_reader_main):
        regbank_reader_main.setWindowTitle(_translate("regbank_reader_main", "MainWindow", None))
        self.target_button.setText(_translate("regbank_reader_main", "No target available", None))
        self.regbank_button.setText(_translate("regbank_reader_main", "No regbank loaded", None))
        self.label_2.setText(_translate("regbank_reader_main", "Regbank Sheet ?", None))
        self.label_3.setText(_translate("regbank_reader_main", "Register ?", None))
        self.menuFile.setTitle(_translate("regbank_reader_main", "File", None))
        self.actionLoad_Regbank.setText(_translate("regbank_reader_main", "Load Regbank", None))

