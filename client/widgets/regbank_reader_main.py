# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './regbank_reader_main.ui'
#
# Created: Mon Jul 13 16:42:17 2015
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_regbank_reader_main(object):
    def setupUi(self, regbank_reader_main):
        regbank_reader_main.setObjectName(_fromUtf8("regbank_reader_main"))
        regbank_reader_main.resize(1054, 823)
        self.centralwidget = QtGui.QWidget(regbank_reader_main)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.mainTabWidget = QtGui.QTabWidget(self.centralwidget)
        self.mainTabWidget.setObjectName(_fromUtf8("mainTabWidget"))
        self.initializationTab = QtGui.QWidget()
        self.initializationTab.setObjectName(_fromUtf8("initializationTab"))
        self.gridLayout_3 = QtGui.QGridLayout(self.initializationTab)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.groupBox = QtGui.QGroupBox(self.initializationTab)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 171))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.targetButton = QtGui.QPushButton(self.groupBox)
        self.targetButton.setMinimumSize(QtCore.QSize(261, 61))
        self.targetButton.setMaximumSize(QtCore.QSize(261, 61))
        self.targetButton.setObjectName(_fromUtf8("targetButton"))
        self.gridLayout.addWidget(self.targetButton, 0, 0, 1, 1)
        self.targetsList = QtGui.QComboBox(self.groupBox)
        self.targetsList.setMinimumSize(QtCore.QSize(381, 61))
        self.targetsList.setObjectName(_fromUtf8("targetsList"))
        self.gridLayout.addWidget(self.targetsList, 0, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(349, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem, 0, 1, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(self.initializationTab)
        self.groupBox_2.setEnabled(True)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.loadRegbankButton = QtGui.QPushButton(self.groupBox_2)
        self.loadRegbankButton.setEnabled(False)
        self.loadRegbankButton.setMinimumSize(QtCore.QSize(261, 61))
        self.loadRegbankButton.setObjectName(_fromUtf8("loadRegbankButton"))
        self.gridLayout_2.addWidget(self.loadRegbankButton, 0, 0, 1, 1)
        self.regbankPathDisp = QtGui.QLineEdit(self.groupBox_2)
        self.regbankPathDisp.setMinimumSize(QtCore.QSize(381, 61))
        self.regbankPathDisp.setReadOnly(True)
        self.regbankPathDisp.setObjectName(_fromUtf8("regbankPathDisp"))
        self.gridLayout_2.addWidget(self.regbankPathDisp, 0, 1, 1, 1)
        self.loadTIBButton = QtGui.QPushButton(self.groupBox_2)
        self.loadTIBButton.setMinimumSize(QtCore.QSize(261, 61))
        self.loadTIBButton.setObjectName(_fromUtf8("loadTIBButton"))
        self.gridLayout_2.addWidget(self.loadTIBButton, 1, 0, 1, 1)
        self.tibPathDisp = QtGui.QLineEdit(self.groupBox_2)
        self.tibPathDisp.setMinimumSize(QtCore.QSize(381, 61))
        self.tibPathDisp.setReadOnly(True)
        self.tibPathDisp.setObjectName(_fromUtf8("tibPathDisp"))
        self.gridLayout_2.addWidget(self.tibPathDisp, 1, 1, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(349, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_3.addItem(spacerItem1, 1, 1, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(20, 449, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout_3.addItem(spacerItem2, 2, 0, 1, 1)
        self.mainTabWidget.addTab(self.initializationTab, _fromUtf8(""))
        self.regbankTab = QtGui.QWidget()
        self.regbankTab.setObjectName(_fromUtf8("regbankTab"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.regbankTab)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.groupBox_3 = QtGui.QGroupBox(self.regbankTab)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 171))
        self.groupBox_3.setTitle(_fromUtf8(""))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem3 = QtGui.QSpacerItem(57, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.label = QtGui.QLabel(self.groupBox_3)
        self.label.setMinimumSize(QtCore.QSize(131, 41))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_4.addWidget(self.label)
        self.label_2 = QtGui.QLabel(self.groupBox_3)
        self.label_2.setMinimumSize(QtCore.QSize(131, 41))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout_4.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(self.groupBox_3)
        self.label_3.setMinimumSize(QtCore.QSize(131, 41))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_4.addWidget(self.label_3)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.regbankSelect = QtGui.QComboBox(self.groupBox_3)
        self.regbankSelect.setMinimumSize(QtCore.QSize(211, 40))
        self.regbankSelect.setObjectName(_fromUtf8("regbankSelect"))
        self.verticalLayout_3.addWidget(self.regbankSelect)
        self.sheetSelect = QtGui.QComboBox(self.groupBox_3)
        self.sheetSelect.setMinimumSize(QtCore.QSize(211, 40))
        self.sheetSelect.setObjectName(_fromUtf8("sheetSelect"))
        self.verticalLayout_3.addWidget(self.sheetSelect)
        self.registerSelect = QtGui.QComboBox(self.groupBox_3)
        self.registerSelect.setMinimumSize(QtCore.QSize(211, 40))
        self.registerSelect.setObjectName(_fromUtf8("registerSelect"))
        self.verticalLayout_3.addWidget(self.registerSelect)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.horizontalLayout_3.addLayout(self.horizontalLayout)
        spacerItem4 = QtGui.QSpacerItem(58, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem4)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.verticalLayout_5 = QtGui.QVBoxLayout()
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_6 = QtGui.QLabel(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setMinimumSize(QtCore.QSize(57, 40))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout_5.addWidget(self.label_6)
        self.label_4 = QtGui.QLabel(self.groupBox_3)
        self.label_4.setMinimumSize(QtCore.QSize(121, 41))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout_5.addWidget(self.label_4)
        self.label_5 = QtGui.QLabel(self.groupBox_3)
        self.label_5.setMinimumSize(QtCore.QSize(91, 41))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout_5.addWidget(self.label_5)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.verticalLayout_6 = QtGui.QVBoxLayout()
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.selectedDisp = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.selectedDisp.sizePolicy().hasHeightForWidth())
        self.selectedDisp.setSizePolicy(sizePolicy)
        self.selectedDisp.setMinimumSize(QtCore.QSize(201, 41))
        self.selectedDisp.setObjectName(_fromUtf8("selectedDisp"))
        self.verticalLayout_6.addWidget(self.selectedDisp)
        self.baseAddressInput = QtGui.QLineEdit(self.groupBox_3)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.baseAddressInput.sizePolicy().hasHeightForWidth())
        self.baseAddressInput.setSizePolicy(sizePolicy)
        self.baseAddressInput.setMinimumSize(QtCore.QSize(201, 41))
        self.baseAddressInput.setObjectName(_fromUtf8("baseAddressInput"))
        self.verticalLayout_6.addWidget(self.baseAddressInput)
        self.sheetOffsetsSelect = QtGui.QComboBox(self.groupBox_3)
        self.sheetOffsetsSelect.setMinimumSize(QtCore.QSize(201, 41))
        self.sheetOffsetsSelect.setObjectName(_fromUtf8("sheetOffsetsSelect"))
        self.verticalLayout_6.addWidget(self.sheetOffsetsSelect)
        self.horizontalLayout_2.addLayout(self.verticalLayout_6)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        spacerItem5 = QtGui.QSpacerItem(57, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem5)
        self.verticalLayout_7.addWidget(self.groupBox_3)
        self.registersTabFrame = QtGui.QFrame(self.regbankTab)
        self.registersTabFrame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.registersTabFrame.setFrameShadow(QtGui.QFrame.Raised)
        self.registersTabFrame.setObjectName(_fromUtf8("registersTabFrame"))
        self.verticalLayout_7.addWidget(self.registersTabFrame)
        self.mainTabWidget.addTab(self.regbankTab, _fromUtf8(""))
        self.tibProcessorTab = QtGui.QWidget()
        self.tibProcessorTab.setObjectName(_fromUtf8("tibProcessorTab"))
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.tibProcessorTab)
        self.verticalLayout_8.setObjectName(_fromUtf8("verticalLayout_8"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label_8 = QtGui.QLabel(self.tibProcessorTab)
        self.label_8.setMinimumSize(QtCore.QSize(121, 40))
        self.label_8.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_8.setAlignment(QtCore.Qt.AlignCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.horizontalLayout_6.addWidget(self.label_8)
        spacerItem6 = QtGui.QSpacerItem(505, 37, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem6)
        self.verticalLayout_8.addLayout(self.horizontalLayout_6)
        self.tibCommandsInput = QtGui.QPlainTextEdit(self.tibProcessorTab)
        self.tibCommandsInput.setMinimumSize(QtCore.QSize(891, 141))
        self.tibCommandsInput.setMaximumSize(QtCore.QSize(16777215, 251))
        self.tibCommandsInput.setObjectName(_fromUtf8("tibCommandsInput"))
        self.verticalLayout_8.addWidget(self.tibCommandsInput)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.runTibCommandsButton = QtGui.QPushButton(self.tibProcessorTab)
        self.runTibCommandsButton.setMinimumSize(QtCore.QSize(131, 40))
        self.runTibCommandsButton.setMaximumSize(QtCore.QSize(16777215, 40))
        self.runTibCommandsButton.setObjectName(_fromUtf8("runTibCommandsButton"))
        self.horizontalLayout_5.addWidget(self.runTibCommandsButton)
        self.clearTbCommandsButton = QtGui.QPushButton(self.tibProcessorTab)
        self.clearTbCommandsButton.setMinimumSize(QtCore.QSize(141, 40))
        self.clearTbCommandsButton.setMaximumSize(QtCore.QSize(16777215, 40))
        self.clearTbCommandsButton.setObjectName(_fromUtf8("clearTbCommandsButton"))
        self.horizontalLayout_5.addWidget(self.clearTbCommandsButton)
        spacerItem7 = QtGui.QSpacerItem(508, 40, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem7)
        self.verticalLayout_8.addLayout(self.horizontalLayout_5)
        self.line = QtGui.QFrame(self.tibProcessorTab)
        self.line.setFrameShadow(QtGui.QFrame.Raised)
        self.line.setLineWidth(10)
        self.line.setMidLineWidth(15)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_8.addWidget(self.line)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName(_fromUtf8("horizontalLayout_7"))
        self.label_9 = QtGui.QLabel(self.tibProcessorTab)
        self.label_9.setMinimumSize(QtCore.QSize(171, 40))
        self.label_9.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_9.setAlignment(QtCore.Qt.AlignCenter)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.horizontalLayout_7.addWidget(self.label_9)
        spacerItem8 = QtGui.QSpacerItem(505, 37, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem8)
        self.verticalLayout_8.addLayout(self.horizontalLayout_7)
        self.tibCommandsOutput = QtGui.QPlainTextEdit(self.tibProcessorTab)
        self.tibCommandsOutput.setMinimumSize(QtCore.QSize(921, 251))
        self.tibCommandsOutput.setObjectName(_fromUtf8("tibCommandsOutput"))
        self.verticalLayout_8.addWidget(self.tibCommandsOutput)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.clearTibsOutputButton = QtGui.QPushButton(self.tibProcessorTab)
        self.clearTibsOutputButton.setMinimumSize(QtCore.QSize(121, 40))
        self.clearTibsOutputButton.setMaximumSize(QtCore.QSize(16777215, 40))
        self.clearTibsOutputButton.setObjectName(_fromUtf8("clearTibsOutputButton"))
        self.horizontalLayout_4.addWidget(self.clearTibsOutputButton)
        spacerItem9 = QtGui.QSpacerItem(505, 37, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem9)
        self.verticalLayout_8.addLayout(self.horizontalLayout_4)
        self.mainTabWidget.addTab(self.tibProcessorTab, _fromUtf8(""))
        self.verticalLayout_2.addWidget(self.mainTabWidget)
        regbank_reader_main.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(regbank_reader_main)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1054, 29))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName(_fromUtf8("menuHelp"))
        regbank_reader_main.setMenuBar(self.menubar)
        self.actionLoad_Regbank = QtGui.QAction(regbank_reader_main)
        self.actionLoad_Regbank.setObjectName(_fromUtf8("actionLoad_Regbank"))
        self.actionExit = QtGui.QAction(regbank_reader_main)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionAbout = QtGui.QAction(regbank_reader_main)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuFile.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(regbank_reader_main)
        self.mainTabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(regbank_reader_main)

    def retranslateUi(self, regbank_reader_main):
        regbank_reader_main.setWindowTitle(QtGui.QApplication.translate("regbank_reader_main", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("regbank_reader_main", "Target Initialization", None, QtGui.QApplication.UnicodeUTF8))
        self.targetButton.setText(QtGui.QApplication.translate("regbank_reader_main", "Connect", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("regbank_reader_main", "Regbank Initialization", None, QtGui.QApplication.UnicodeUTF8))
        self.loadRegbankButton.setText(QtGui.QApplication.translate("regbank_reader_main", "Load regbank excel", None, QtGui.QApplication.UnicodeUTF8))
        self.loadTIBButton.setText(QtGui.QApplication.translate("regbank_reader_main", "Load TIB file", None, QtGui.QApplication.UnicodeUTF8))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.initializationTab), QtGui.QApplication.translate("regbank_reader_main", "Initialization", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("regbank_reader_main", "Select Regbank", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("regbank_reader_main", "Select Sheet", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("regbank_reader_main", "Select Register", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("regbank_reader_main", "Selected", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("regbank_reader_main", "Sheet Base Address", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("regbank_reader_main", "Sheet Offsets", None, QtGui.QApplication.UnicodeUTF8))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.regbankTab), QtGui.QApplication.translate("regbank_reader_main", "Regbank", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("regbank_reader_main", "Enter TIB\'s", None, QtGui.QApplication.UnicodeUTF8))
        self.runTibCommandsButton.setText(QtGui.QApplication.translate("regbank_reader_main", "Run TIB\'s", None, QtGui.QApplication.UnicodeUTF8))
        self.clearTbCommandsButton.setText(QtGui.QApplication.translate("regbank_reader_main", "Clear TIB\'s", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("regbank_reader_main", "TIB Processor Output", None, QtGui.QApplication.UnicodeUTF8))
        self.clearTibsOutputButton.setText(QtGui.QApplication.translate("regbank_reader_main", "Clear Outputs", None, QtGui.QApplication.UnicodeUTF8))
        self.mainTabWidget.setTabText(self.mainTabWidget.indexOf(self.tibProcessorTab), QtGui.QApplication.translate("regbank_reader_main", "TIB Processor", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("regbank_reader_main", "Fi&le", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("regbank_reader_main", "Help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_Regbank.setText(QtGui.QApplication.translate("regbank_reader_main", "Load Regbank", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExit.setText(QtGui.QApplication.translate("regbank_reader_main", "Exit", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout.setText(QtGui.QApplication.translate("regbank_reader_main", "About", None, QtGui.QApplication.UnicodeUTF8))
