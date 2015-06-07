import sys;
import re;
from hashlib import md5
from os.path import basename, splitext
from PyQt4.QtCore import pyqtRemoveInputHook, QThread, Qt, qDebug
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDialog, QWidget, QHeaderView, QVBoxLayout, QTableWidgetItem
from regbank_reader_main import *
from regbank_reader_model import *
from regbank_address_dialog import *
from register_tab import *

view_field_t = namedtuple("view_field_t", ["col_name", "col_num"]);
field_info_t = namedtuple("field_info_t", ["row_idx", "col_idx", "bit_mask", "bit_shift"]);
class register_table_t (QWidget, Ui_register_tab, QObject) :

    # To store the columns and their spacing details
    view_fields = [view_field_t("Subfield Name", 0), view_field_t("Field desc", 1),
                   view_field_t("Value", 2), view_field_t("Default value", 3),
                   view_field_t("General Description", 4)];

    def __init__(self, register, parent, model):
        super(register_table_t, self).__init__(parent);
        qDebug("register_table_t with register "+str(id(register)));
        self.register = register;
        self.setupUi(self);
        self.show();
        self.model = model;
        self.field_infos = [];
        self.register_subfields_view.setRowCount(len(self.register.element.sub_elements));
        self.register_subfields_view.setColumnCount(len(self.view_fields));
        self.register_name_disp.setText(self.register.element.register_name);
        self.register_subfields_view.horizontalHeader().setResizeMode(QHeaderView.Stretch);
        self.register_subfields_view.verticalHeader().setResizeMode(QHeaderView.Stretch);
        self.register_subfields_view.verticalHeader().setVisible(False);
        headerLabels = [];
        qDebug("register_subfields_view items are set now");
        for row, sub_element in enumerate(self.register.element.sub_elements):
            view_field = self.view_fields[0];
            headerLabels.append(view_field.col_name);
            text = sub_element.name;
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter);
            self.register_subfields_view.setItem(row, view_field.col_num, item);

            view_field = self.view_fields[1];
            headerLabels.append(view_field.col_name);
            positions = re.findall("[0-9]+", sub_element.bit_position);
            if len(positions)==1:
                start_bit = end_bit = positions[0];
            else:
                [end_bit, start_bit] = positions;
            start_bit = int(start_bit, 0);
            end_bit   = int(end_bit, 0);
            field_info = field_info_t(row_idx=row, col_idx=2, bit_mask=(pow(2, end_bit+1)-1)-(pow(2, start_bit)-1), bit_shift=start_bit);
            self.field_infos.append(field_info);
            text = str(sub_element.bit_width) + " bits in " + sub_element.bit_position + " SW_ATTR[" + sub_element.sw_attr + "]";
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter);
            self.register_subfields_view.setItem(row, view_field.col_num, item);

            view_field = self.view_fields[2];
            headerLabels.append(view_field.col_name);
            text = "--";
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter);
            self.register_subfields_view.setItem(row, view_field.col_num, item);

            view_field = self.view_fields[3];
            headerLabels.append(view_field.col_name);
            text = str(sub_element.default_val);
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter);
            self.register_subfields_view.setItem(row, view_field.col_num, item);

            view_field = self.view_fields[4];
            headerLabels.append(view_field.col_name);
            text = sub_element.description;
            item = QTableWidgetItem(text); item.setTextAlignment(Qt.AlignCenter);
            self.register_subfields_view.setItem(row, view_field.col_num, item);
        self.register_subfields_view.setHorizontalHeaderLabels(headerLabels);
        self.register_subfields_view.cellChanged.connect(self.write_register_from_subfields_value);
        self.register_update_button.clicked.connect(self.slot_register_update_clicked);
        self.register_value_edit.editingFinished.connect(self.slot_register_update_write);
        # Initial register update
        self.slot_register_update_clicked();

    def slot_register_set_value(self, value):
        self.register_subfields_view.cellChanged.disconnect(self.write_register_from_subfields_value);
        text = hex(value).upper().replace("X", "x");
        self.register_value_edit.setText(text);
        for field_info in self.field_infos:
            sub_value = (value & field_info.bit_mask) >> field_info.bit_shift;
            item = self.register_subfields_view.item(field_info.row_idx, field_info.col_idx);
            if item==None:
                set_trace();
                pass;
            text = hex(sub_value).upper().replace("X", "x");
            item.setText(text);
        self.register_subfields_view.cellChanged.connect(self.write_register_from_subfields_value);

    def slot_register_update_clicked(self):
        value = self.model.read_register(self.register);
        if value:
            self.slot_register_set_value(value);

    def slot_register_update_write(self):
        text = self.register_value_edit.text();
        value = self.model.write_register(self.register, int(text, 0));
        if value:
            self.slot_register_set_value(value);

    def write_register_from_subfields_value(self):
        self.register_subfields_view.cellChanged.disconnect(self.write_register_from_subfields_value);
        old_read_value = int(self.register_value_edit.text(), 0);
        new_write_value = 0x00;
        new_read_value  = 0x00;
        valid_value = True;
        for field_info in self.field_infos:
            try:
                sub_value = int(self.register_subfields_view.item(field_info.row_idx, field_info.col_idx).text(), 0);
            except:
                valid_value = False;
                break;
            max_value = field_info.bit_mask >> field_info.bit_shift;
            if sub_value > max_value:
                # Value greater than bit field for item;
                valid_value = False;
                break;
            new_write_value = new_write_value | sub_value << field_info.bit_shift;
        if valid_value:
            new_read_value = self.model.write_register(self.register, new_write_value);
        else:
            new_read_value = old_read_value;
        self.register_subfields_view.cellChanged.connect(self.write_register_from_subfields_value);
        self.slot_register_set_value(new_read_value);

class regbank_main_window_t(Ui_regbank_reader_main, QObject):
    def __init__(self):
        super(regbank_main_window_t, self).__init__();
        self.target_list = [];
        self.registers_list = [];
        self.register_tabs = {};
        self.sheet_list = [];
        self.base_addr = None;
        self.offset_size = None;
        self.model = regbank_reader_model_t();
        self.valid_db = False;


    signal_get_register = pyqtSignal(int,int,int);
    signal_load_regbank = pyqtSignal(str);
    signal_connect_target = pyqtSignal(target_t);
    signal_regbank_additional_info = pyqtSignal(regbank_additional_info_t);
    signal_register_selected = pyqtSignal(int, int, int);

    def initialize(self):
        self.target_button.setEnabled(False);
        self.target_selection.setEditable(True);
        self.target_selection.lineEdit().setAlignment(Qt.AlignCenter)
        self.target_selection.lineEdit().setReadOnly(True);
        self.regbank_button.clicked.connect(self.slot_regbank_button_clicked);
        self.signal_load_regbank.connect(self.model.load_regbank_file);
        self.model.signal_regbank_connection.connect(self.regbank_button.setText);
        self.model.signal_regbank_list.connect(self.slot_set_regbank_list);
        self.model.signal_regbank_info.connect(self.slot_set_regbank_info);
        self.model.signal_target_connection.connect(self.target_button.setText);
        self.model.signal_target_info.connect(self.slot_set_target_list);
        self.signal_connect_target.connect(self.model.connect_to_target);
        self.register_sheet_selection.currentIndexChanged.connect(self.slot_sheet_changed);
        self.signal_regbank_additional_info.connect(self.model.update_regbank_additional_info);
        self.signal_register_selected.connect(self.model.get_register);
        self.register_selection.currentIndexChanged.connect(self.slot_register_changed);
        self.target_button.clicked.connect(self.slot_target_button_clicked);
        self.model.initialize();

    def slot_set_target_list(self, targets):
        self.target_button.setEnabled(True);
        self.targets_list = targets;
        self.target_selection.clear();
        for target in targets:
            target_str = target.protocol + " : " + target.ip_addr + " : " + target.port;
            self.target_selection.addItem(target_str);

    def slot_set_regbank_list(self, cur_idx, regbank_list):
        self.regbank_selection.clear();
        for regbank_name in regbank_list:
            self.regbank_selection.addItem(regbank_name);
        self.regbank_selection.setCurrentIndex(cur_idx);

    def slot_set_regbank_info(self, sheets_list, registers_list):
        self.register_sheet_selection.currentIndexChanged.disconnect(self.slot_sheet_changed);
        self.sheets = sheets_list;
        self.registers_list = registers_list;
        self.register_sheet_selection.clear();
        for sheet in sheets_list:
            self.register_sheet_selection.addItem(sheet);
        self.register_sheet_selection.currentIndexChanged.connect(self.slot_sheet_changed);
        self.slot_sheet_changed(0);

    def slot_sheet_changed(self, sheet_idx):
        self.register_selection.currentIndexChanged.disconnect(self.slot_register_changed);
        if sheet_idx>=0:
            registers = self.registers_list[sheet_idx];
            self.register_selection.clear();
            for register in registers:
                self.register_selection.addItem(register);
        self.register_selection.currentIndexChanged.connect(self.slot_register_changed);
        self.slot_register_changed(0);

    def slot_register_changed(self, idx):
        if idx >=0:
            register = self.model.get_register(self.regbank_selection.currentIndex(),
                    self.register_sheet_selection.currentIndex(), idx);
            qDebug("regbank_selection = {0}, sheet_index = {1}, register_idx = {2}".format( 
                    self.regbank_selection.currentIndex(), self.register_sheet_selection.currentIndex(), 
                    idx));
            self.slot_update_register_tab(register);

    def get_register_id(self, register):
        text = (self.regbank_selection.currentText() + self.register_sheet_selection.currentText()
                + register.element.register_name + str(register.element.offset_addr)
                + str(len(register.element.sub_elements)));
        return md5(text.encode()).hexdigest();

    def slot_update_register_tab(self, register):
        print("Register bank selected");
        addTabWidget = False;
        widget = register_widget = None;
        if self.registers_tab_widget.count()==0:
            addTabWidget = True;
        else:
            if self.get_register_id(register) in self.register_tabs.keys():
                # Register already exists, put the tab to highlight
                (register_widget, _) = self.register_tabs[self.get_register_id(register)];
                idx = self.registers_tab_widget.indexOf(register_widget);
                self.registers_tab_widget.setCurrentIndex(idx);
            else:
                addTabWidget = True;

        if addTabWidget:
            register_widget = register_table_t(register, self.registers_tab_widget, self.model);
            self.registers_tab_widget.addTab(register_widget, register.element.register_name);
            self.register_tabs[self.get_register_id(register)] = (register_widget, register);
            idx = self.registers_tab_widget.indexOf(register_widget);
            self.registers_tab_widget.setCurrentIndex(idx);

    def slot_regbank_button_clicked(self):
        if self.model.target_connected==False:
            msgBox = QMessageBox();
            msgBox.setText("Target not connected, please connect");
            msgBox.exec();
            return;
        fdialog = QFileDialog(None);
        fname = fdialog.getOpenFileName(None, 'Open file'); 
        regbank_name = splitext(basename(fname))[0];
        additional_info = self.get_regbank_additional_info(regbank_name);
        self.model.load_regbank_file(fname);
        self.model.update_regbank_additional_info(additional_info);
        
    
    def get_regbank_additional_info(self, regbank_name):
        dialog = QDialog(None);
        label_text = "Enter base address and offset size for "+regbank_name;
        regbank_dialog = Ui_Dialog();
        regbank_dialog.setupUi(dialog);
        regbank_dialog.accept_button.clicked.connect(dialog.accept);
        regbank_dialog.main_label.setText(label_text);
        base_addr = 0x40004000;
        offset_size = 2;
        while 1:
            #dialog.show();
            #dialog.exec();
            #base_addr = int(regbank_dialog.base_addr.text(), 0);
            #offset_size = int(regbank_dialog.offset_size.text(), 0);
            if (base_addr==0 or offset_size==0) :
                continue;
            else:
                break;
    
        info = regbank_additional_info_t(regbank_name, base_addr, offset_size);
        return info;

    def slot_target_button_clicked(self):
        if self.model.target_connected:
            self.model.disconnect_target(self.targets_list[self.target_selection.currentIndex()]);
        else:
            self.model.connect_to_target(self.targets_list[self.target_selection.currentIndex()]);

if __name__ == "__main__":
    pyqtRemoveInputHook();
    app = QApplication(sys.argv)
    window = QMainWindow();
    register_main_window = regbank_main_window_t();
    register_main_window.setupUi(window);
    
    # Setup signals and slots
    register_main_window.initialize();

    # Show the application
    window.show();
    app.exec()
