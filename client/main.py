import xlrd
import sys
import re
from hashlib import md5
from os.path import basename, splitext
from PyQt4.QtCore import pyqtRemoveInputHook, QThread, Qt, qDebug, QObject
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDialog, QWidget, QHeaderView, QVBoxLayout, QTableWidgetItem, QMessageBox
from widgets.regbank_reader_main import *
from regbank_reader_model import model, parse_tib_file, target_t, load_sheet, load_regbank
import regbank_reader_model
from widgets.regbank_address_dialog import *
from widgets.register_tab import *
from pdb import set_trace
from os.path import basename, splitext

#class register_table_t (QWidget, Ui_register_tab, QObject) :
#
#    # To store the columns and their spacing details
#    view_fields = [view_field_t("Subfield Name", 0), view_field_t("Field desc", 1),
#                   view_field_t("Value", 2), view_field_t("Default value", 3),
#                   view_field_t("General Description", 4)]
#
#    def __init__(self, register, parent, model):
#        super(register_table_t, self).__init__(parent)
#        self.setupUi(self)
#        self.show()
#
#        qDebug("register_table_t with register "+str(id(register)))
#        self.register = register
#        self.register_addr = self.register.base_addr + self.register.offset_size * self.register.offset_addr
#        self.register_name_disp.setText(self.register.name + "@" + self.toHex(self.register_addr))
#        self.model = model
#        self.field_infos = []
#        self.auto_read_mode.setEditable(True)
#        self.auto_read_mode.lineEdit().setAlignment(Qt.AlignCenter)
#        self.auto_read_mode.lineEdit().setReadOnly(True)
#
#        self.addr_offset_type.setEditable(True)
#        self.addr_offset_type.lineEdit().setAlignment(Qt.AlignCenter)
#        self.addr_offset_type.lineEdit().setReadOnly(True)
#
#        self.register_subfields_view.setRowCount(len(self.register.sub_elements))
#        self.register_subfields_view.setColumnCount(len(self.view_fields))
#        self.register_subfields_view.horizontalHeader().setResizeMode(QHeaderView.Stretch)
#        self.register_subfields_view.verticalHeader().setResizeMode(QHeaderView.Stretch)
#        self.register_subfields_view.verticalHeader().setVisible(False)
#        headerLabels = []
#        qDebug("register_subfields_view items are set now")
#        for row, sub_element in enumerate(self.register.sub_elements):
#            view_field = self.view_fields[0]
#            headerLabels.append(view_field.col_name)
#            text = sub_element.name
#            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
#            self.register_subfields_view.setItem(row, view_field.col_num, item)
#
#            view_field = self.view_fields[1]
#            headerLabels.append(view_field.col_name)
#            positions = re.findall("[0-9]+", sub_element.bit_position)
#            if len(positions)==1:
#                start_bit = end_bit = positions[0]
#            else:
#                [end_bit, start_bit] = positions
#            start_bit = int(start_bit, 0)
#            end_bit   = int(end_bit, 0)
#            field_info = field_info_t(row_idx=row, col_idx=2, bit_mask=(pow(2, end_bit+1)-1)-(pow(2, start_bit)-1), bit_shift=start_bit)
#            self.field_infos.append(field_info)
#            text = str(sub_element.bit_width) + " bits in " + sub_element.bit_position + " SW_ATTR[" + sub_element.sw_attr + "]"
#            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
#            self.register_subfields_view.setItem(row, view_field.col_num, item)
#
#            view_field = self.view_fields[2]
#            headerLabels.append(view_field.col_name)
#            text = "--"
#            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
#            self.register_subfields_view.setItem(row, view_field.col_num, item)
#
#            view_field = self.view_fields[3]
#            headerLabels.append(view_field.col_name)
#            text = str(sub_element.default_val)
#            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
#            self.register_subfields_view.setItem(row, view_field.col_num, item)
#
#            view_field = self.view_fields[4]
#            headerLabels.append(view_field.col_name)
#            text = sub_element.description
#            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter)
#            self.register_subfields_view.setItem(row, view_field.col_num, item)
#        self.register_subfields_view.setHorizontalHeaderLabels(headerLabels)
#        self.register_subfields_view.cellChanged.connect(self.write_register_from_subfields_value)
#        self.register_update_button.clicked.connect(self.slot_register_update_clicked)
#        self.register_value_edit.editingFinished.connect(self.slot_register_update_write)
#
#        self.base_addr_edit.setText(self.toHex(self.register.base_addr))
#        self.offset_addr_edit.setText(self.toHex(self.register.offset_addr))
#        self.addr_offset_type.setCurrentIndex(0 if self.register.offset_size==1 else 1)
#
#        self.base_addr_edit.editingFinished.connect(self.slot_update_register_address)
#        self.addr_offset_type.currentIndexChanged.connect(self.slot_update_register_address)
#        self.offset_addr_edit.editingFinished.connect(self.slot_update_register_address)
#
#    def toHex(self, value):
#        return hex(value).upper().replace("X", "x")
#
#    def slot_base_addr_changed(self):
#        self.register.base_addr = self.toHex(self.base_addr_edit.text())
#
#    def slot_update_register_address(self):
#        base_addr = int(self.base_addr_edit.text(), 0)
#        offset_addr = int(self.offset_addr_edit.text(), 0)
#        offset_size = 1 if self.addr_offset_type.currentIndex()==0 else 4
#        self.register.base_addr = base_addr
#        self.register.offset_addr = offset_addr
#        self.register.offset_size = offset_size
#        self.register_addr = base_addr + offset_addr * offset_size
#        self.register_name_disp.setText(self.register.name + "@" + self.toHex(self.register_addr))
#
#    def slot_offset_addr_changed(self):
#        self.register.offset_addr = self.toHex(self.offset_addr_edit.text())
#
#    def slot_register_set_value(self, value):
#        self.register_subfields_view.cellChanged.disconnect(self.write_register_from_subfields_value)
#        text = hex(value).upper().replace("X", "x")
#        self.register_value_edit.setText(text)
#        for field_info in self.field_infos:
#            sub_value = (value & field_info.bit_mask) >> field_info.bit_shift
#            item = self.register_subfields_view.item(field_info.row_idx, field_info.col_idx)
#            if item==None:
#                set_trace()
#                pass
#            text = hex(sub_value).upper().replace("X", "x")
#            item.setText(text)
#        self.register_subfields_view.cellChanged.connect(self.write_register_from_subfields_value)
#
#    def slot_register_update_clicked(self):
#        value = self.model.read_register(self.register)
#        if value!=None:
#            self.slot_register_set_value(value)
#        else:
#            print("Read failed, investigate")
#
#    def slot_register_update_write(self):
#        text = self.register_value_edit.text()
#        write_value = int(text, 0)
#        write_success = self.model.write_register(self.register, write_value)
#        if not write_success:
#            print("Write failed, investigate")
#        if (write_success and (self.auto_read_mode.currentIndex()==0)):
#            read_value = self.model.read_register(self.register)
#            if read_value!=None:
#                self.slot_register_set_value(read_value)
#        else:
#            # Display the previous write value to all places
#            self.slot_register_set_value(write_value)
#
#    def write_register_from_subfields_value(self):
#        self.register_subfields_view.cellChanged.disconnect(self.write_register_from_subfields_value)
#        old_read_value = int(self.register_value_edit.text(), 0)
#        new_write_value = 0x00
#        new_read_value  = None
#        valid_value = True
#        write_success = None
#        for field_info in self.field_infos:
#            try:
#                sub_value = int(self.register_subfields_view.item(field_info.row_idx, field_info.col_idx).text(), 0)
#            except:
#                valid_value = False
#                break
#            max_value = field_info.bit_mask >> field_info.bit_shift
#            if sub_value > max_value:
#                # Value greater than bit field for item
#                valid_value = False
#                break
#            new_write_value = new_write_value | sub_value << field_info.bit_shift
#        if valid_value:
#            write_success = self.model.write_register(self.register, new_write_value)
#            if write_success:
#                new_read_value = self.model.read_register(self.register)
#            else:
#                print("Write failed, investigate")
#        if new_read_value==None:
#            new_read_value = old_read_value
#        self.register_subfields_view.cellChanged.connect(self.write_register_from_subfields_value)
#        self.slot_register_set_value(new_read_value)
#
class regbank_main_window_t(Ui_regbank_reader_main, QObject):
    def __init__(self, tib_file=None):
        super(regbank_main_window_t, self).__init__()

    def slot_set_regbank_list(self, cur_idx, regbank_list):
        self.regbank_selection.clear()
        for regbank_name in regbank_list:
            self.regbank_selection.addItem(regbank_name)
        self.regbank_selection.setCurrentIndex(cur_idx)

    def slot_set_regbank_info(self, sheets_list, registers_list):
        self.register_sheet_selection.currentIndexChanged.disconnect(self.slot_sheet_changed)
        self.sheets = sheets_list
        self.registers_list = registers_list
        self.register_sheet_selection.clear()
        for sheet in sheets_list:
            self.register_sheet_selection.addItem(sheet)
        self.register_sheet_selection.currentIndexChanged.connect(self.slot_sheet_changed)
        self.slot_sheet_changed(0)

    def slot_sheet_changed(self, sheet_idx):
        self.register_selection.currentIndexChanged.disconnect(self.slot_register_changed)
        if sheet_idx>=0:
            registers = self.registers_list[sheet_idx]
            self.register_selection.clear()
            for register in registers:
                self.register_selection.addItem(register)
        self.register_selection.currentIndexChanged.connect(self.slot_register_changed)
        self.slot_register_changed(0)

    def slot_register_changed(self, idx):
        if idx >=0:
            register = self.model.get_register(self.regbank_selection.currentIndex(),
                    self.register_sheet_selection.currentIndex(), idx)
            qDebug("regbank_selection = {0}, sheet_index = {1}, register_idx = {2}".format( 
                    self.regbank_selection.currentIndex(), self.register_sheet_selection.currentIndex(), 
                    idx))
            self.slot_update_register_tab(register)

    def get_register_id(self, register):
        text = (self.regbank_selection.currentText() + self.register_sheet_selection.currentText()
                + register.name + str(register.offset_addr)
                + str(len(register.sub_elements)))
        return md5(text.encode()).hexdigest()

    def slot_update_register_tab(self, register):
        print("Register bank selected")
        addTabWidget = False
        widget = register_widget = None
        if self.registers_tab_widget.count()==0:
            addTabWidget = True
        else:
            if self.get_register_id(register) in self.register_tabs.keys():
                # Register already exists, put the tab to highlight
                (register_widget, _) = self.register_tabs[self.get_register_id(register)]
                idx = self.registers_tab_widget.indexOf(register_widget)
                self.registers_tab_widget.setCurrentIndex(idx)
            else:
                addTabWidget = True

        if addTabWidget:
            register_widget = register_table_t(register, self.registers_tab_widget, self.model)
            self.registers_tab_widget.addTab(register_widget, register.name)
            self.register_tabs[self.get_register_id(register)] = (register_widget, register)
            idx = self.registers_tab_widget.indexOf(register_widget)
            self.registers_tab_widget.setCurrentIndex(idx)

    def slot_regbank_button_clicked(self):
        if self.model.target_connected==False:
            msgBox = QMessageBox()
            msgBox.setText("Target not connected, please connect")
            msgBox.exec()
            return
        fdialog = QFileDialog(None)
        fname = fdialog.getOpenFileName(None, 'Open file'); 
        regbank_name = splitext(basename(fname))[0]
        additional_info = self.get_regbank_additional_info(regbank_name)
        self.model.load_regbank_file(fname)
        self.model.update_regbank_additional_info(additional_info)
        
    
    def get_regbank_additional_info(self, regbank_name):
        dialog = QDialog(None)
        label_text = "Enter base address and offset size for "+regbank_name
        regbank_dialog = Ui_Dialog()
        regbank_dialog.setupUi(dialog)
        regbank_dialog.accept_button.clicked.connect(dialog.accept)
        regbank_dialog.main_label.setText(label_text)
        base_addr = 0x00
        offset_size = 0x00
        while 1:
            dialog.show()
            dialog.exec()
            base_addr = int(regbank_dialog.base_addr.text(), 0)
            offset_size = 1 if regbank_dialog.addr_offset_type.currentIndex()==0 else 4
            if (base_addr==0 or offset_size==0) :
                continue
            else:
                break
        info = regbank_additional_info_t(regbank_name, base_addr, offset_size)
        return info

## Glue logic between UI and Model
class regbank_reader_gui_controller_t:
    def __init__(self, tib_file):
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
        self.gui = regbank_main_window_t()
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
        

        # TIB Initialization Section
        self.gui.pushButton_loadTibFile.setEnabled(False)
        self.gui.pushButton_loadTibFile.clicked.connect(self.slot_gui_load_tib_file)
        self.gui.comboBox_tibList.setEditable(True)
        self.gui.comboBox_tibList.lineEdit().setAlignment(Qt.AlignCenter)
        self.gui.comboBox_tibList.lineEdit().setReadOnly(True)
        self.gui.pushButton_executeTib.setEnabled(False)
        self.gui.pushButton_executeTib.clicked.connect(self.slot_gui_execute_tib)

        # Register access Section

        # TIB Processor section
 
        # Connect slots related to targets
        self.model.signal_target_connected.connect(self.slot_gui_target_connected)
        self.model.signal_target_disconnected.connect(self.slot_gui_target_disconnected)
        self.model.signal_targets_list_updated.connect(self.slot_gui_targets_list_updated)

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
        self.gui.pushButton_targetConnect.setText("Click to disconnect")
        self.gui.comboBox_targetsList.setEnabled(False)

    def slot_gui_target_disconnected(self):
        self.gui.pushButton_loadRegBank.setEnabled(False)
        self.gui.pushButton_loadSheet.setEnabled(False)
        self.gui.pushButton_loadTibFile.setEnabled(False)
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
        set_trace()
        tib_name = self.gui.comboBox_tibList.currentText()
        tib_file = self.tibs_list[tib_name]
        self.model.tib_file = tib_file
        parse_tib_file(tib_file)

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

