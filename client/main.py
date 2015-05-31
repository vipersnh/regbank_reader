import sys
from os.path import basename, splitext
from PyQt4.QtCore import pyqtRemoveInputHook, QThread, Qt
from PyQt4.QtGui import QApplication, QMainWindow, QFileDialog, QDialog, QWidget, QHeaderView, QVBoxLayout
from regbank_reader_main import *
from regbank_reader_model import *
from regbank_address_dialog import *
from register_tab import *

class regbank_main_window_t(Ui_regbank_reader_main, QObject):
    def __init__(self):
        super(regbank_main_window_t, self).__init__();

    target_list = [];
    registers_list = [];
    register_tabs = {};
    sheet_list = [];
    base_addr = None;
    offset_size = None;
    model = regbank_reader_model_t();
    valid_db = False;


    signal_get_register = pyqtSignal(int,int,int);
    signal_load_regbank = pyqtSignal(str);
    signal_connect_target = pyqtSignal(target_t);
    signal_regbank_additional_info = pyqtSignal(regbank_additional_info_t);
    signal_register_selected = pyqtSignal(int, int, int);

    def initialize(self):
        self.target_selection.setEditable(True);
        self.target_selection.lineEdit().setAlignment(Qt.AlignCenter)
        self.target_selection.lineEdit().setReadOnly(True);
        self.regbank_button.clicked.connect(self.slot_regbank_button_clicked);
        self.signal_load_regbank.connect(self.model.load_regbank_file);
        self.model.signal_regbank_connection.connect(self.regbank_button.setText);
        self.model.signal_regbank_list.connect(self.slot_set_regbank_list);
        self.model.signal_regbank_info.connect(self.slot_set_regbank_info);
        self.model.signal_register_info.connect(self.slot_update_register_tab);
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
            self.signal_register_selected.emit(self.regbank_selection.currentIndex(),
                    self.register_sheet_selection.currentIndex(), idx);

    def slot_update_register_tab(self, register):
        print("Register bank selected");
        addTabWidget = False;
        widget = register_tab = None;
        if self.registers_tab_widget.count()==0:
            addTabWidget = True;
        else:
            if register.element.register_name in self.register_tabs.keys():
                # Register already exists, put the tab to highlight
                (parent_widget, register_tab, _) = self.register_tabs[register.element.register_name];
                idx = self.registers_tab_widget.indexOf(parent_widget);
                self.registers_tab_widget.setCurrentIndex(idx);
            else:
                addTabWidget = True;

        if addTabWidget:
            parent_widget = QWidget(None);
            widget = QWidget(None);
            register_tab = Ui_register_tab();
            register_tab.setupUi(widget);
            register_tab.register_name_disp.setText(register.element.register_name);
            register_tab.register_subfields_view.horizontalHeader().setVisible(False);
            register_tab.register_subfields_view.horizontalHeader().setResizeMode(QHeaderView.Stretch);
            register_tab.register_subfields_view.verticalHeader().setVisible(False);
            register_tab.register_subfields_view.verticalHeader().setResizeMode(QHeaderView.Stretch);
            vlayout = QVBoxLayout();
            vlayout.addWidget(widget);
            parent_widget.setLayout(vlayout);
            self.registers_tab_widget.addTab(parent_widget, register.element.register_name);
            self.register_tabs[register.element.register_name] = (parent_widget, register_tab, register);
            idx = self.registers_tab_widget.indexOf(parent_widget);
            self.registers_tab_widget.setCurrentIndex(idx);

        register_tab.register_subfields_view.setRowCount(len(register.element.sub_elements));
        register_tab.register_subfields_view.setColumnCount(5);


    def slot_regbank_button_clicked(self):
        fdialog = QFileDialog(None);
        fname = fdialog.getOpenFileName(None, 'Open file'); 
        self.signal_load_regbank.emit(fname);
        regbank_name = splitext(basename(fname))[0];
        additional_info = self.get_regbank_additional_info(regbank_name);
        self.signal_regbank_additional_info.emit(additional_info);
        
    
    def get_regbank_additional_info(self, regbank_name):
        dialog = QDialog(None);
        label_text = "Enter base address and offset size for "+regbank_name;
        regbank_dialog = Ui_Dialog();
        regbank_dialog.setupUi(dialog);
        regbank_dialog.accept_button.clicked.connect(dialog.accept);
        regbank_dialog.main_label.setText(label_text);
        base_addr = offset_size = 2;
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
        self.signal_connect_target.emit(self.targets_list[self.target_selection.currentIndex()]);

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
