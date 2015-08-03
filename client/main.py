import xlrd
import sys
import re
from StructDict import StructDict
from regbank_parser import offsets_enum_t
from hashlib import md5
from os.path import basename, splitext
from PyQt4.QtCore import pyqtRemoveInputHook, pyqtSignal, QThread, Qt, qDebug, QObject
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDialog, QWidget, QHeaderView, QVBoxLayout, QTableWidgetItem, QMessageBox
from widgets.regbank_reader_main import *
from regbank_reader_model import model, parse_tib_file, target_t, load_sheet, load_regbank, exec_tib
import regbank_reader_model
from widgets.register_tab import *
from pdb import set_trace
from collections import namedtuple
from os.path import basename, splitext

view_field_t = namedtuple("view_field_t", ["col_name", "col_num"])
field_info_t = namedtuple("field_info_t", ["row_idx", "col_idx", "bit_mask", "bit_shift"])

class register_table_t (QWidget, Ui_register_tab, QObject) :
    # To store the columns and their spacing details
    view_fields = [view_field_t("Subfield Name", 0), view_field_t("Field desc", 1),
                   view_field_t("Value", 2), view_field_t("Default value", 3),
                   view_field_t("General Description", 4)]

    def __init__(self, register, parent, model):
        super(register_table_t, self).__init__(parent)
        self.setupUi(self)
        self.show()

        qDebug("register_table_t with register "+str(id(register)))
        self.register = register
        self.model = model
        self.field_infos = []
        self.comboBox_registerAutoReadMode.setEditable(True)
        self.comboBox_registerAutoReadMode.lineEdit().setAlignment(Qt.AlignCenter)
        self.comboBox_registerAutoReadMode.lineEdit().setReadOnly(True)

        self.tableWidget_subfieldsView.setRowCount(len(self.register.subfields))
        self.tableWidget_subfieldsView.setColumnCount(len(self.view_fields))
        self.tableWidget_subfieldsView.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.tableWidget_subfieldsView.verticalHeader().setResizeMode(QHeaderView.Stretch)
        self.tableWidget_subfieldsView.verticalHeader().setVisible(False)
        headerLabels = []
        qDebug("tableWidget_subfieldsView items are set now")
        row_idx = 0
        for subfield_name in self.register.subfields.keys():
            subfield = self.register.subfields[subfield_name]
            view_field = self.view_fields[0]
            headerLabels.append(view_field.col_name)
            text = subfield.name
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_subfieldsView.setItem(row_idx, view_field.col_num, item)

            view_field = self.view_fields[1]
            headerLabels.append(view_field.col_name)
            start_bit = subfield.bit_position[0]
            end_bit   = subfield.bit_position[-1]
            field_info = field_info_t(row_idx=row_idx, col_idx=2, bit_mask=(pow(2, end_bit+1)-1)-(pow(2, start_bit)-1), bit_shift=start_bit)
            self.field_infos.append(field_info)
            text = str(subfield.bit_width) + " bits in " + str(subfield.bit_position) + " SW_ATTR[" + subfield.sw_attr + "]"
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_subfieldsView.setItem(row_idx, view_field.col_num, item)

            view_field = self.view_fields[2]
            headerLabels.append(view_field.col_name)
            text = "--"
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_subfieldsView.setItem(row_idx, view_field.col_num, item)

            view_field = self.view_fields[3]
            headerLabels.append(view_field.col_name)
            text = str(subfield.default_val)
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_subfieldsView.setItem(row_idx, view_field.col_num, item)

            view_field = self.view_fields[4]
            headerLabels.append(view_field.col_name)
            text = subfield.description
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
            self.tableWidget_subfieldsView.setItem(row_idx, view_field.col_num, item)
            row_idx += 1 
        self.tableWidget_subfieldsView.setHorizontalHeaderLabels(headerLabels)
        self.tableWidget_subfieldsView.cellChanged.connect(self.write_register_from_subfields_value)
        self.pushButton_readValue.clicked.connect(self.slot_register_update_clicked)
        self.lineEdit_registerValue.editingFinished.connect(self.slot_register_update_write)
        self.slot_update_register_ui()

    def slot_update_register_ui(self):
        sheet = self.model.db[self.register.regbank_name][self.register.sheet_name]
        register_addr = sheet.base_addr + self.register.offset_addr * (1 
                if sheet.offset_type == offsets_enum_t.BYTE_OFFSETS else 4)
        self.lineEdit_registerName.setText("{0} @ {1}".format(self.register.register_name, 
            hex(register_addr)))
        self.lineEdit_sheetBaseAddr.setText(hex(sheet.base_addr))
        self.lineEdit_registerOffsetAddr.setText(str(self.register.offset_addr))
        self.lineEdit_sheetOffsetType.setText("BYTE_OFFSETS" 
                if sheet.offset_type == offsets_enum_t.BYTE_OFFSETS else 
                "WORD_OFFSETS")

    def slot_reset_register_ui(self, regbank_name, sheet_name):
        if (self.register.regbank_name==regbank_name and
                self.register.sheet_name==sheet_name):
            self.lineEdit_registerValue.blockSignals(True)
            self.lineEdit_registerValue.setText("")
            self.lineEdit_registerValue.blockSignals(False)
            row_idx = 0
            self.tableWidget_subfieldsView.blockSignals(True)
            for subfield_name in self.register.subfields.keys():
                view_field = self.view_fields[2]
                text = "--"
                item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
                self.tableWidget_subfieldsView.setItem(row_idx, view_field.col_num, item)
                row_idx += 1
            self.tableWidget_subfieldsView.blockSignals(False)
            self.slot_update_register_ui()



    def toHex(self, value):
        return hex(value).upper().replace("X", "x")

    def slot_register_set_value(self, value):
        self.tableWidget_subfieldsView.cellChanged.disconnect(self.write_register_from_subfields_value)
        text = hex(value).upper().replace("X", "x")
        self.lineEdit_registerValue.setText(text)
        for field_info in self.field_infos:
            sub_value = (value & field_info.bit_mask) >> field_info.bit_shift
            item = self.tableWidget_subfieldsView.item(field_info.row_idx, field_info.col_idx)
            if item==None:
                set_trace()
                pass
            text = hex(sub_value).upper().replace("X", "x")
            item.setText(text)
        self.tableWidget_subfieldsView.cellChanged.connect(self.write_register_from_subfields_value)

    def slot_register_update_clicked(self):
        value = self.model.read_register(self.register.regbank_name, 
                                         self.register.sheet_name, 
                                         self.register.register_name, None)
        if value!=None:
            self.slot_register_set_value(value)
        else:
            print("Read failed, investigate")

    def slot_register_update_write(self):
        text = self.lineEdit_registerValue.text()
        write_value = int(text, 0)
        self.model.write_register(self.register.regbank_name,
                                  self.register.sheet_name,
                                  self.register.register_name, None, write_value)
        if (self.auto_read_mode.currentIndex()==0):
            read_value = self.model.read_register(self.register.regbank_name, 
                                                  self.register.sheet_name, 
                                                  self.register.register_name, None)
            if read_value!=None:
                self.slot_register_set_value(read_value)
        else:
            # Display the previous write value to all places
            self.slot_register_set_value(write_value)

    def write_register_from_subfields_value(self):
        self.tableWidget_subfieldsView.cellChanged.disconnect(self.write_register_from_subfields_value)
        try:
            old_read_value = int(self.lineEdit_registerValue.text(), 0)
        except:
            set_trace()
            pass
        new_write_value = 0x00
        new_read_value  = None
        valid_value = True
        write_success = None
        for field_info in self.field_infos:
            try:
                sub_value = int(self.tableWidget_subfieldsView.item(field_info.row_idx, field_info.col_idx).text(), 0)
            except:
                valid_value = False
                break
            max_value = field_info.bit_mask >> field_info.bit_shift
            if sub_value > max_value:
                # Value greater than bit field for item
                valid_value = False
                break
            new_write_value = new_write_value | sub_value << field_info.bit_shift
        if valid_value:
            write_success = self.model.write_register(self.register, new_write_value)
            if write_success:
                new_read_value = self.model.read_register(self.register)
            else:
                print("Write failed, investigate")
        if new_read_value==None:
            new_read_value = old_read_value
        self.tableWidget_subfieldsView.cellChanged.connect(self.write_register_from_subfields_value)
        self.slot_register_set_value(new_read_value)

## Glue logic between UI and Model
class regbank_reader_gui_controller_t(QObject):

    signal_reset_sheet_register = pyqtSignal(str, str)

    def __init__(self, tib_file):
        super(regbank_reader_gui_controller_t, self).__init__()
        self.init_tib_file = tib_file

    def initialize(self, tib_file = None):
        self.regbanks_path_list = dict()
        self.tibs_list = dict()
        self.target_list = list()
        self.register_tabs = dict()

        self.model = model
        self.model.cmd_line = False
        self.model.tib_file = tib_file
        
        self.window = QMainWindow()
        self.gui = Ui_regbank_reader_main()
        self.gui.setupUi(self.window)
        self.window.show()

        # Target Initialization Section
        self.gui.pushButton_targetConnect.setEnabled(False)
        self.gui.pushButton_targetConnect.setText("Waiting for targets")
        self.gui.comboBox_targetsList.setEditable(True)
        self.gui.comboBox_targetsList.lineEdit().setAlignment(Qt.AlignCenter)
        self.gui.comboBox_targetsList.lineEdit().setReadOnly(True)
        self.gui.pushButton_targetConnect.clicked.connect(self.slot_gui_target_button_clicked)

        # Regbank Initialization Section
        self.gui.pushButton_loadRegBank.setEnabled(False)
        self.gui.comboBox_regbankSelect.setEditable(True)
        self.gui.comboBox_regbankSelect.lineEdit().setAlignment(Qt.AlignCenter)
        self.gui.comboBox_regbankSelect.lineEdit().setReadOnly(True)
        self.gui.comboBox_sheetSelect.setEditable(True)
        self.gui.comboBox_sheetSelect.lineEdit().setAlignment(Qt.AlignCenter)
        self.gui.comboBox_sheetSelect.lineEdit().setReadOnly(True)
        self.gui.comboBox_sheetOffsets.setEditable(True)
        self.gui.comboBox_sheetOffsets.lineEdit().setAlignment(Qt.AlignCenter)
        self.gui.comboBox_sheetOffsets.lineEdit().setReadOnly(True)
        self.gui.comboBox_sheetOffsets.addItem("BYTE_OFFSETS")
        self.gui.comboBox_sheetOffsets.addItem("WORD_OFFSETS")
        self.gui.pushButton_loadRegBank.clicked.connect(self.slot_gui_load_regbank)
        self.gui.pushButton_loadSheet.clicked.connect(self.slot_gui_load_sheet)
        self.gui.comboBox_regbankSelect.currentIndexChanged.connect(self.slot_gui_regbank_changed)
        self.gui.comboBox_sheetSelect.currentIndexChanged.connect(self.slot_gui_regbank_sheet_changed)
        self.gui.comboBox_loadedSheetOffsetSel.addItem("BYTE_OFFSETS")
        self.gui.comboBox_loadedSheetOffsetSel.addItem("WORD_OFFSETS")
        self.gui.lineEdit_loadedCalcAddr.setReadOnly(True)
        self.gui.lineEdit_loadedSheetAddr.editingFinished.connect(self.slot_gui_regbank_sheet_base_addr_changed)
        self.gui.comboBox_loadedSheetOffsetSel.currentIndexChanged.connect(self.slot_gui_regbank_sheet_offsets_changed)
        
        # Memory Editor Section
        self.memory_radioButtons = dict()
        self.gui.pushButton_getCurrRegisterAddr.setEnabled(False)
        self.gui.pushButton_memEditorReadValue.setEnabled(False)
        self.gui.pushButton_memEditorWriteValue.setEnabled(False)
        self.gui.comboBox_memEditorMode.setEnabled(False)
        for i in range(32):
            radioButton = getattr(self.gui, "radioButton_" + str(i))
            radioButton.toggled.connect(self.slot_gui_memEditor_memory_radioButton_changed)
            self.memory_radioButtons[i] = radioButton
        self.gui.lineEdit_memEditorAddr.setText("---")
        self.gui.lineEdit_memEditorNextValue.setText("---")
        self.gui.lineEdit_memEditorCurrValue.setText("---")
        self.gui.comboBox_memEditorMode.currentIndexChanged.connect(self.slot_gui_memEditor_modeChanged)
        self.gui.pushButton_getCurrRegisterAddr.clicked.connect(self.slot_gui_memEditor_getCurrRegisterAddr)
        self.gui.pushButton_memEditorReadValue.clicked.connect(self.slot_gui_memEditor_readValue)
        self.gui.pushButton_memEditorWriteValue.clicked.connect(self.slot_gui_memEditor_writeValue)
        self.gui.lineEdit_memEditorAddr.editingFinished.connect(self.slot_gui_memEditor_regAddrChanged)
        self.gui.lineEdit_memEditorNextValue.editingFinished.connect(self.slot_gui_memEditor_nextValueChanged)


        # TIB Initialization Section
        self.gui.pushButton_loadTibFile.setEnabled(False)
        self.gui.pushButton_loadTibFile.clicked.connect(self.slot_gui_load_tib_file)
        self.gui.comboBox_tibList.setEditable(True)
        self.gui.comboBox_tibList.lineEdit().setAlignment(Qt.AlignCenter)
        self.gui.comboBox_tibList.lineEdit().setReadOnly(True)
        self.gui.pushButton_executeTib.setEnabled(False)
        self.gui.pushButton_executeTib.clicked.connect(self.slot_gui_execute_tib)
        self.gui.lineEdit_execTibCommand.cursorPositionChanged.connect(self.slot_gui_execute_tib_command_cursor_changed)
        self.gui.lineEdit_execTibCommand.returnPressed.connect(self.slot_gui_execute_tib_command)

        # Register access Section

        # TIB Processor section
        self.model.signal_tib_exec_op.connect(self.slot_gui_display_tib_op)
        self.gui.plainTextEdit_tibOutput.setCenterOnScroll(True)
        self.gui.pushButton_clearTibOutputs.clicked.connect(self.gui.plainTextEdit_tibOutput.clear)
 
        # Connect slots related to targets
        self.model.signal_target_connected.connect(self.slot_gui_target_connected)
        self.model.signal_target_disconnected.connect(self.slot_gui_target_disconnected)
        self.model.signal_targets_list_updated.connect(self.slot_gui_targets_list_updated)
        
        # Connect slots related to model
        self.model.signal_regbank_updated.connect(self.slot_gui_regbank_updated)

        # Connect slots related to gui updates
        self.gui.comboBox_loadedRegbankSel.currentIndexChanged.connect(self.slot_gui_regbank_selection_changed)
        self.gui.comboBox_loadedSheetSel.currentIndexChanged.connect(self.slot_gui_regbank_selection_changed)
        self.gui.comboBox_loadedRegisterSel.currentIndexChanged.connect(self.slot_gui_regbank_selection_changed)

        # Start the model
        regbank_reader_model.initialize()
        self.model.initialize()

        if self.init_tib_file:
            fname = self.init_tib_file
            tib_name = splitext(basename(fname))[0]
            self.tibs_list[tib_name] = fname
            self.gui.comboBox_tibList.addItem(tib_name)

    # Target related slots
    def slot_gui_target_button_clicked(self):
        target_str = self.gui.comboBox_targetsList.currentText()
        [prot, ip_addr, port] = target_str.replace(" ",'').split(':')
        if self.model.target_connected:
            # Disconnect currently connected target
            target = target_t(ip_addr, port, prot, None)
            self.model.disconnect_from_target()

        else:
            # Connect to target
            target = target_t(ip_addr, port, prot, None)
            self.model.connect_to_target(target)

    def slot_gui_targets_list_updated(self, targets):
        if not self.model.target_connected:
            self.gui.pushButton_targetConnect.setEnabled(True)
            self.gui.pushButton_targetConnect.setText("Click to connect")
            self.gui.comboBox_targetsList.clear()
            for target in targets:
                target_str = target.protocol + " : " + target.ip_addr + " : " + target.port
                self.gui.comboBox_targetsList.addItem(target_str)

    def slot_gui_target_connected(self, target):
        self.gui.pushButton_loadRegBank.setEnabled(True)
        self.gui.pushButton_loadSheet.setEnabled(True)
        self.gui.pushButton_loadTibFile.setEnabled(True)

        self.gui.pushButton_getCurrRegisterAddr.setEnabled(True)
        self.gui.pushButton_memEditorReadValue.setEnabled(True)
        self.gui.pushButton_memEditorWriteValue.setEnabled(True)
        self.gui.comboBox_memEditorMode.setEnabled(True)


        self.gui.pushButton_targetConnect.setText("Click to disconnect")
        self.gui.comboBox_targetsList.setEnabled(False)

    def slot_gui_target_disconnected(self):
        self.gui.pushButton_loadRegBank.setEnabled(False)
        self.gui.pushButton_loadSheet.setEnabled(False)
        self.gui.pushButton_loadTibFile.setEnabled(False)

        self.gui.pushButton_getCurrRegisterAddr.setEnabled(False)
        self.gui.pushButton_memEditorReadValue.setEnabled(False)
        self.gui.pushButton_memEditorWriteValue.setEnabled(False)
        self.gui.comboBox_memEditorMode.setEnabled(False)

        self.gui.pushButton_targetConnect.setText("Click to connect")
        self.gui.comboBox_targetsList.setEnabled(True)

    # Regbank related slots
    def slot_gui_load_regbank(self):
        fdialog = QFileDialog(None)
        fname = fdialog.getOpenFileName(None, 'Open file',
                "./", "All files (*.xlsx)")
        if fname is not'' and re.search(".xlsx$", fname):
            regbank_name = splitext(basename(fname))[0]
            if fname not in self.regbanks_path_list.values():
                self.regbanks_path_list[regbank_name] = fname
                load_regbank(fname)
            self.slot_gui_regbank_changed(regbank_name)

    def slot_gui_regbank_sheet_changed(self):
        name = self.gui.comboBox_sheetSelect.currentText()
        self.gui.lineEdit_asSheetName.setText(name)
        regbank_name = self.gui.comboBox_regbankSelect.currentText()
        try:
            sheet_name   = name
            predicted_offset = self.model.get_sheet_offsets(regbank_name, sheet_name)
            self.gui.comboBox_sheetOffsets.setCurrentIndex(0 if predicted_offset==0 else 1)
        except:
            sheet_name = self.gui.lineEdit_asSheetName.text()
            predicted_offset = self.model.get_sheet_offsets(regbank_name, sheet_name)
            self.gui.comboBox_sheetOffsets.setCurrentIndex(0 if predicted_offset==0 else 1)



    def slot_gui_load_sheet(self):
        regbank_name = self.gui.comboBox_regbankSelect.currentText()
        sheet_name = self.gui.comboBox_sheetSelect.currentText()
        as_sheet_name = self.gui.lineEdit_asSheetName.text()
        base_addr = self.gui.lineEdit_sheetLoadAddress.text()
        if base_addr is not "":
            base_addr = int(base_addr, 0)
            offset_size = 1 if self.gui.comboBox_sheetOffsets.currentIndex()==0 else 4
            if as_sheet_name==sheet_name :
                as_sheet_name = None
            load_sheet(getattr(model.db_dict[regbank_name], sheet_name), base_addr, offset_size, as_sheet_name)
        else:
            # Warn about invalid base_addr
            msgBox = QMessageBox(QMessageBox.Warning, "...",  "Invalid \"At Address\" specified")
            msgBox.setStandardButtons(QMessageBox.Ok);
            msgBox.exec_()

    def slot_gui_regbank_changed(self, regbank_name):
        try:
            fname = self.regbanks_path_list[regbank_name]
        except:
            set_trace()
        workbook = xlrd.open_workbook(fname)
        sheet_names = workbook.sheet_names()
        self.gui.comboBox_regbankSelect.blockSignals(True)
        self.gui.comboBox_regbankSelect.addItem(regbank_name)
        self.gui.comboBox_regbankSelect.blockSignals(False)
        self.gui.comboBox_sheetSelect.clear()
        for sheet_name in sheet_names:
            self.gui.comboBox_sheetSelect.addItem(sheet_name)

    # Memory editor related slots
    def slot_gui_memEditor_update_value(self, value):
        self.gui.lineEdit_memEditorNextValue.blockSignals(True)
        self.gui.lineEdit_memEditorNextValue.setText(hex(value))
        self.gui.lineEdit_memEditorNextValue.blockSignals(False)
        self.slot_gui_memEditor_radioBtnsSetValue(value)

    def slot_gui_memEditor_radioBtnsGetValue(self):
        value = 0
        for i in self.memory_radioButtons.keys():
            if self.memory_radioButtons[i].isChecked():
                value |= (1 << i)
        return value
            
    def slot_gui_memEditor_radioBtnsSetValue(self, value):
        for i in self.memory_radioButtons.keys():
            self.memory_radioButtons[i].blockSignals(True)
            if value & (1 << i):
                self.memory_radioButtons[i].setChecked(True)
            else:
                self.memory_radioButtons[i].setChecked(False)
            self.memory_radioButtons[i].blockSignals(False)

    def slot_gui_memEditor_memory_radioButton_changed(self):
        value = self.slot_gui_memEditor_radioBtnsGetValue()
        self.slot_gui_memEditor_update_value(value)
        if self.gui.comboBox_memEditorMode.currentIndex()==1:
            # Live mode
            self.slot_gui_memEditor_writeValue()
            self.slot_gui_memEditor_readValue()
        else:
            # On demand mode
            pass
 
    def slot_gui_memEditor_modeChanged(self):
        if self.gui.comboBox_memEditorMode.currentIndex()==1:
            # Update current value if Live Mode is selected
            value = self.slot_gui_memEditor_readValue()
    
    def slot_gui_memEditor_nextValueChanged(self):
        value = int(self.gui.lineEdit_memEditorNextValue.text(), 0)
        self.slot_gui_memEditor_update_value(value)
        if self.gui.comboBox_memEditorMode.currentIndex()==1:
            # Write current value and read back in Live Mode
            self.slot_gui_memEditor_writeValue()
            self.slot_gui_memEditor_readValue()
 

    def slot_gui_memEditor_regAddrChanged(self):
        if self.gui.comboBox_memEditorMode.currentIndex()==1:
            # Read and update value in Live Mode
            self.slot_gui_memEditor_readValue()
        else:
            self.slot_gui_memEditor_update_value(0)

    def slot_gui_memEditor_getCurrRegisterAddr(self):
        try:
            regbank_name = self.gui.comboBox_loadedRegbankSel.currentText()
            sheet_name = self.gui.comboBox_loadedSheetSel.currentText()
            register_name = self.gui.comboBox_loadedRegisterSel.currentText()
            sheet = self.model.db[regbank_name][sheet_name]
            register = sheet.registers[register_name]
            addr = sheet.base_addr + (register.offset_addr *
                    (1 if sheet.offset_type==offsets_enum_t.BYTE_OFFSETS else 4))
            self.gui.lineEdit_memEditorAddr.setText(hex(addr))
        except:
            pass

    def slot_gui_memEditor_readValue(self):
        addr = int(self.gui.lineEdit_memEditorAddr.text(), 0)
        value = self.model.read_address(addr)
        self.slot_gui_memEditor_update_value(value)

    def slot_gui_memEditor_writeValue(self):
        addr = int(self.gui.lineEdit_memEditorAddr.text(), 0)
        value = int(self.gui.lineEdit_memEditorNextValue.text(), 0)
        self.model.write_address(addr, value)
        self.gui.lineEdit_memEditorCurrValue.setText(hex(value))

    # TIB related slots
    def slot_gui_load_tib_file(self):
        fdialog = QFileDialog(None)
        fname = fdialog.getOpenFileName(None, 'Open file',
                "./", "All files (*.tib)")
        if fname is not'' and re.search(".tib$", fname):
            self.gui.pushButton_executeTib.setEnabled(True)
            tib_name = splitext(basename(fname))[0]
            if fname not in self.tibs_list.values():
                self.tibs_list[tib_name] = fname
                self.gui.comboBox_tibList.addItem(tib_name)

    def slot_gui_execute_tib(self):
        tib_name = self.gui.comboBox_tibList.currentText()
        tib_file = self.tibs_list[tib_name]
        self.model.tib_file = tib_file
        parse_tib_file(tib_file)

    def slot_gui_execute_tib_command(self):
        tib = self.gui.lineEdit_execTibCommand.text()
        try:
            exec_tib(tib[3:])
            self.gui.lineEdit_execTibCommand.clear()
        except:
            set_trace()
            pass

    def slot_gui_execute_tib_command_cursor_changed(self, old, new):
        if new < 3:
            self.gui.lineEdit_execTibCommand.setText(">>>")

    def slot_gui_display_tib_op(self, ops):
        for op in ops:
            self.gui.plainTextEdit_tibOutput.appendPlainText(op)

    # Regbank related slots

    def slot_gui_regbank_sheet_base_addr_changed(self):
        regbank_name = self.gui.comboBox_loadedRegbankSel.currentText()
        sheet_name   = self.gui.comboBox_loadedSheetSel.currentText()
        orig_base_addr = self.model.db[regbank_name][sheet_name].base_addr
        try:
            base_addr = int(self.gui.lineEdit_loadedSheetAddr.text(), 0)
            if base_addr==orig_base_addr:
                return 
            self.model.db[regbank_name][sheet_name].base_addr = base_addr
        except:
            self.gui.lineEdit_loadedSheetAddr.setText(hex(orig_base_addr))
        self.slot_gui_update_register_ui()
        self.signal_reset_sheet_register.emit(regbank_name, sheet_name)

    def slot_gui_regbank_sheet_offsets_changed(self, offset_idx):
        regbank_name = self.gui.comboBox_loadedRegbankSel.currentText()
        sheet_name   = self.gui.comboBox_loadedSheetSel.currentText()
        cur_idx = self.gui.comboBox_loadedSheetOffsetSel.currentIndex()
        self.model.db[regbank_name][sheet_name].offset_type = (
                offsets_enum_t.BYTE_OFFSETS if cur_idx==0 else 
                offsets_enum_t.WORD_OFFSETS)
        self.slot_gui_update_register_ui()
        self.signal_reset_sheet_register.emit(regbank_name, sheet_name)

    def slot_gui_regbank_updated(self):
        self.gui.comboBox_loadedRegbankSel.blockSignals(True)
        for regbank_name in self.model.db.keys():
            if self.gui.comboBox_loadedRegbankSel.findText(regbank_name) < 0:
                self.gui.comboBox_loadedRegbankSel.addItem(regbank_name)
        self.gui.comboBox_loadedRegbankSel.blockSignals(False)
        self.gui.comboBox_loadedRegbankSel.currentIndexChanged.emit(
                self.gui.comboBox_loadedRegbankSel.currentIndex())
        
    def slot_gui_regbank_selection_changed(self):
        self.gui.comboBox_loadedRegbankSel.blockSignals(True)
        self.gui.comboBox_loadedSheetSel.blockSignals(True)
        self.gui.comboBox_loadedRegisterSel.blockSignals(True)

        regbank_name = self.gui.comboBox_loadedRegbankSel.currentText()
        if self.sender()==self.gui.comboBox_loadedRegbankSel:
            # Regbank selection changed, update sheets and registers
            self.gui.comboBox_loadedSheetSel.clear()
            for sheet_name in self.model.db[regbank_name].keys():
                if self.model.db[regbank_name][sheet_name]:
                    self.gui.comboBox_loadedSheetSel.addItem(sheet_name)
            sheet_name = self.gui.comboBox_loadedSheetSel.currentText()
            self.gui.comboBox_loadedRegisterSel.clear()
            for register_name in self.model.db[regbank_name][sheet_name].registers.keys():
                self.gui.comboBox_loadedRegisterSel.addItem(register_name)
        elif self.sender()==self.gui.comboBox_loadedSheetSel:
            # Sheet selection changed
            sheet_name = self.gui.comboBox_loadedSheetSel.currentText()
            self.gui.comboBox_loadedRegisterSel.clear()
            for register_name in self.model.db[regbank_name][sheet_name].registers.keys():
                self.gui.comboBox_loadedRegisterSel.addItem(register_name)
        elif self.sender()==self.gui.comboBox_loadedRegisterSel:
            # Register selection changed
            pass
        else:
            assert 0, "Invalid condition"
        self.gui.comboBox_loadedRegbankSel.blockSignals(False)
        self.gui.comboBox_loadedSheetSel.blockSignals(False)
        self.gui.comboBox_loadedRegisterSel.blockSignals(False)
        self.slot_gui_update_register_ui()
    
    def slot_get_register_id(self):
        text = (self.gui.comboBox_loadedRegbankSel.currentText() + 
                self.gui.comboBox_loadedSheetSel.currentText() + 
                self.gui.comboBox_loadedRegisterSel.currentText())
        return md5(text.encode()).hexdigest()

    def slot_gui_update_register_ui(self):
        addTabWidget = False
        widget = register_widget = None
        regbank_name  = self.gui.comboBox_loadedRegbankSel.currentText()
        sheet_name    = self.gui.comboBox_loadedSheetSel.currentText()
        register_name = self.gui.comboBox_loadedRegisterSel.currentText()

        sheet = self.model.db[regbank_name][sheet_name]
        self.gui.lineEdit_loadedSheetAddr.setText(hex(sheet.base_addr))
        self.gui.lineEdit_loadedCalcAddr.setText(hex(sheet.base_addr + 
                sheet.registers[register_name].offset_addr * (1 
                    if sheet.offset_type==offsets_enum_t.BYTE_OFFSETS else 4)))
        self.gui.comboBox_loadedSheetOffsetSel.setCurrentIndex(
                0 if sheet.offset_type==offsets_enum_t.BYTE_OFFSETS else 1)

        if self.gui.tabWidget_registers.count()==0:
            addTabWidget = True
        else:
            if self.slot_get_register_id() in self.register_tabs.keys():
                # Register already exists, put the tab to highlight
                register_widget = self.register_tabs[self.slot_get_register_id()]
                idx = self.gui.tabWidget_registers.indexOf(register_widget)
                self.gui.tabWidget_registers.setCurrentIndex(idx)
            else:
                addTabWidget = True

        if addTabWidget:
            register  = sheet.registers[register_name]
            base_addr = sheet.base_addr
            offset_type = sheet.offset_type
            register_widget = register_table_t(register, self.gui.tabWidget_registers, 
                    self.model)
            self.signal_reset_sheet_register.connect(register_widget.slot_reset_register_ui)
            self.gui.tabWidget_registers.addTab(register_widget, 
                    "{0}:{1}".format(sheet_name, register_name))
            self.register_tabs[self.slot_get_register_id()] = register_widget
            idx = self.gui.tabWidget_registers.indexOf(register_widget)
            self.gui.tabWidget_registers.setCurrentIndex(idx)

    def start(self):
        pass

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', nargs=1, help="Process specified tib file")
    parser.add_argument('-gui', action="store_true", help="Start in gui mode")
    parse_res = parser.parse_args()
    gui = parse_res.gui
    tib_file = None
    if parse_res.f:
        tib_file = parse_res.f[0]
    if gui:
        pyqtRemoveInputHook()
        app = QApplication(sys.argv)
        gui_controller = regbank_reader_gui_controller_t(tib_file)
        gui_controller.initialize()
        gui_controller.start()
        app.exec()
    else:
        model.cmd_line = True
        if tib_file:
            model.tib_file = tib_file
            parse_tib_file(tib_file)
        else:
            print("Please pass a tib file to process")

