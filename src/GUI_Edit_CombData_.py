from PyQt5.QtGui import QIcon, QFont, QGuiApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidget, QGridLayout, QHBoxLayout, QLabel, QHeaderView, QPushButton, QLineEdit,QMessageBox,\
                            QWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import QSize, Qt
from ast import literal_eval
import sys
import re
import time
import os
from data_edit import file_combination
import configparser
import resources_rc

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

curdir = os.getcwd()
class Data_Combine(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Data Combine")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.resize(550*self.ratio, 450*self.ratio)
        # self.setFixedSize(550*self.ratio, 450*self.ratio)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.setup_ui()

    def setup_ui(self):
        label_w            = 60*self.ratio
        label_h            = 25*self.ratio
        blabel_w           = 60*self.ratio
        blabel_h           = 10*self.ratio
        QTableWidget_w     = 400*self.ratio
        QTableWidget_h     = 178*self.ratio
        QTableWidget_colw1 = 250*self.ratio
        QTableWidget_colw2 = 250*self.ratio
        QTableWidget_colw3 = 100*self.ratio
        QTableWidget_rowh1 = 37*self.ratio
        PushButton_w       = 100*self.ratio
        PushButton_h       = 25*self.ratio
        LineEdit_w         = 300*self.ratio
        LineEdit_h         = 25*self.ratio
        zPushButton_w      = 25*self.ratio
        zPushButton_h      = 25*self.ratio
        rPushButton_w      = 100*self.ratio
        rPushButton_h      = 25*self.ratio
        Pagemargin         = 10*self.ratio
        #****************************************************************************
        com_box = QGridLayout()
        self.choose_input_path_wuyong_label = QLabel('List Files:', self)
        self.choose_input_path_wuyong_label.setMinimumSize(QSize(label_w, label_h))
        self.choose_input_path_wuyong_label.setMaximumSize(QSize(label_w, label_h))

        # layout = QHBoxLayout()
        self.main_table = QTableWidget(self)
        self.main_table.setColumnCount(3)
        self.main_table.setRowCount(100)
        self.main_table.setMinimumSize(QSize(QTableWidget_w, QTableWidget_h))
        self.main_table.setHorizontalHeaderLabels(['Filepath', 'Filename', ''])
        # self.main_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.main_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.main_table.horizontalHeader().setStyleSheet("QHeaderView::section { border: 0.5px solid rgb(210, 210, 210);background-color: rgb(255, 255, 255); color: black;}")
        self.main_table.verticalHeader().setStyleSheet("border: 0.5px solid rgb(210, 210, 210)")
        self.main_table.resizeRowsToContents()
        self.main_table.verticalHeader().setDefaultSectionSize(QTableWidget_rowh1)
        self.main_table.setColumnWidth(0, QTableWidget_colw1)
        self.main_table.setColumnWidth(1, QTableWidget_colw2)
        self.main_table.setColumnWidth(2, QTableWidget_colw3)
        self.main_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.main_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.main_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Fixed)
        self.main_table.horizontalHeader().setDisabled(True) # set no edit header
        self.hlayout = QHBoxLayout()
        for i in range(self.main_table.rowCount()):
            self.main_table.setCellWidget(i, 2, self.buttonForRow())  # add operate button

        self.one_key_clean = QPushButton('Clean', self)
        self.one_key_clean.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.one_key_clean.clicked.connect(self.one_key_clean_function)

        self.choose_output_path_wuyong_label = QLabel('Output:', self)
        self.choose_output_path_wuyong_label.setMinimumSize(QSize(label_w, label_h))
        self.choose_output_path_wuyong_label.setMaximumSize(QSize(label_w, label_h))

        self.show_outputsave_files_path_button = QLineEdit(self)
        self.show_outputsave_files_path_button.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_outputsave_files_path_button = QPushButton(self)
        self.choose_outputsave_files_path_button.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.choose_outputsave_files_path_button.setMaximumSize(QSize(zPushButton_w, zPushButton_h))
        self.choose_outputsave_files_path_button.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_outputsave_files_path_button.clicked.connect(self.choose_output_files_path_function)

        self.data_combine_but = QPushButton('Execute', self)
        self.data_combine_but.setMinimumSize(QSize(rPushButton_w, rPushButton_h))
        self.data_combine_but.clicked.connect(self.sure_btn_link)

        blank_label = QLabel('')
        blank_label.setMinimumSize(QSize(blabel_w, blabel_h))
        com_box.setSpacing(1)
        com_box.addWidget(self.choose_input_path_wuyong_label, 0, 0, 1, 1)
        com_box.addWidget(self.main_table, 0, 1, 1, 3)
        com_box.addWidget(self.one_key_clean, 1, 1, 1, 3)
        com_box.addWidget(blank_label, 2, 0)
        com_box.addWidget(self.choose_output_path_wuyong_label, 3, 0, 1, 1)
        com_box.addWidget(self.show_outputsave_files_path_button, 3, 1, 1, 2)
        com_box.addWidget(self.choose_outputsave_files_path_button, 3, 3, 1, 1)
        com_box.addWidget(blank_label, 4, 0)
        com_box.addWidget(self.data_combine_but, 5, 0, 1, 4)
        com_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        mainFrame = QWidget()
        mainFrame.setLayout(com_box)
        self.setCentralWidget(mainFrame)

        self.conf = configparser.ConfigParser()
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.read(conf_path, encoding='utf-8-sig')

    # data merge
    def sure_btn_link(self):
        t1 = time.time()
        print('Start execute')
        output_path = self.show_outputsave_files_path_button.text()
        raw_table_list = []
        for i in range(self.main_table.rowCount()):
            if self.main_table.item(i, 0) and self.main_table.item(i, 1):
                file_all_path = str(self.main_table.item(i, 0).text()) + '/' + str(self.main_table.item(i, 1).text())
                raw_table_list.append(file_all_path)
        raw_table_list = list(set(raw_table_list)) # only data
        self.conf.set('Parameter', 'combine_file', str(raw_table_list))
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.write(open(conf_path, 'w', encoding='utf-8'))

        raw_table_str = self.conf.get('Parameter', 'combine_file')
        raw_table_list = literal_eval(raw_table_str)
        if len(raw_table_list) == 0:
            QMessageBox.information(self, 'Prompt', 'not added data')
            return
        if self.show_outputsave_files_path_button.text() == '':
            QMessageBox.information(self, 'Prompt', 'not added data path')
            return
        converd_text = file_combination.File_Combination_Function(raw_table_list)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for i in converd_text:
                    f.write(str(i))
        except:
            os.remove(output_path)
            return
        t2 = time.time()
        print('Completed, total time: %s seconds' % ((t2 - t1)))
        QMessageBox.information(self, 'Prompt', 'Execution complete')

    # table operate
    def buttonForRow(self):
        QPushButton_w = 25*self.ratio
        QPushButton_h =25*self.ratio
        Pagemargin_row = 5*self.ratio
        Pagemargin_col = 10*self.ratio
        widget = QWidget()
        # add
        self.addBtn = QPushButton(self)
        self.addBtn.setMinimumSize(QSize(QPushButton_w, QPushButton_h))
        self.addBtn.setMaximumSize(QSize(QPushButton_w, QPushButton_h))
        self.addBtn.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.addBtn.clicked.connect(self.AddButton)
        # delete
        self.deleteBtn = QPushButton(self)
        self.deleteBtn.setMinimumSize(QSize(QPushButton_w, QPushButton_h))
        self.deleteBtn.setMaximumSize(QSize(QPushButton_w, QPushButton_h))
        self.deleteBtn.setStyleSheet("QPushButton{border-image: url(':/icon/delete_file.ico')}")
        self.deleteBtn.clicked.connect(self.DeleteButton)
        hLayout = QHBoxLayout()
        hLayout.addWidget(self.addBtn)
        hLayout.addWidget(self.deleteBtn)
        hLayout.setContentsMargins(Pagemargin_row, Pagemargin_col, Pagemargin_row, Pagemargin_col)
        widget.setLayout(hLayout)
        return widget


    #  add one file
    def AddButton(self):
        button = self.sender()
        if button:
            # default path
            desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
            desktop_path = desktop_path.replace("\\", "/")
            unzip_default_download_path = desktop_path
            if os.path.exists(unzip_default_download_path):
                zip_complute_route, unused_suffix = QFileDialog.getOpenFileNames(self, 'Select the file to be merged', './', 'o_file(*MO.rnx *.*o *.*O);;All_File(*)')
            else:
                zip_complute_route, unused_suffix = QFileDialog.getOpenFileNames(self, 'Select the file to be merged', './', 'o_file(*MO.rnx *.*o *.*O);;All_File(*))')

            if unused_suffix != '':
                os.chdir(os.path.dirname(zip_complute_route[0]))

            dealed_add_file_rote_list = []
            for one_rote in zip_complute_route:
                one_rote_list = ['/'.join(one_rote.split('/')[:-1]), one_rote.split('/')[-1]]
                dealed_add_file_rote_list.append(one_rote_list)


            for one_list in dealed_add_file_rote_list:
                row = self.main_table.indexAt(button.parent().pos()).row()# row
                self.main_table.insertRow(row)
                for i, j in zip(one_list, range(len(one_list))):
                    newItem = QTableWidgetItem(i)
                    newItem.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                    self.main_table.setItem(row, j, newItem)
                self.main_table.setCellWidget(row, 2, self.buttonForRow())
        # output path
        raw_table_list = []
        for i in range(self.main_table.rowCount()):
            if self.main_table.item(i, 0) and self.main_table.item(i, 1):
                file_all_path = str(self.main_table.item(i, 0).text()) + '/' + str(self.main_table.item(i, 1).text())
                raw_table_list.append(file_all_path)
        if len(raw_table_list) != 0:
            input_file_name = raw_table_list[0].split('/')[-1]
            input_path = raw_table_list[0].replace(input_file_name, '')
            if input_file_name[0].islower():
                output_file_name = 'comb' + input_file_name[4:]
            else:
                output_file_name = 'COMB' + input_file_name[4:]
            output_file_path = input_path + output_file_name
            self.show_outputsave_files_path_button.setText(output_file_path)


    # detele file
    def DeleteButton(self):
        button = self.sender()
        if button:
            row = self.main_table.indexAt(button.parent().pos()).row()
            for delete_num in range(2):
                self.main_table.setItem(row, delete_num, QTableWidgetItem(''))


    # clean
    def one_key_clean_function(self):
        now_table_all_row_num = self.main_table.rowCount()
        for i in range(now_table_all_row_num):
            self.main_table.setItem(i, 0, QTableWidgetItem(''))
            self.main_table.setItem(i, 1, QTableWidgetItem(''))


    # select output oath
    def choose_output_files_path_function(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', './')
        if save_path == '':
            pass
        else:
            # add file
            raw_table_list = []
            for i in range(self.main_table.rowCount()):
                if self.main_table.item(i, 0) and self.main_table.item(i, 1):
                    file_all_path = str(self.main_table.item(i, 0).text()) + '/' + str(
                        self.main_table.item(i, 1).text())
                    raw_table_list.append(file_all_path)
            if len(raw_table_list) != 0:
                input_file_name = raw_table_list[0].split('/')[-1]
                if input_file_name[0].islower():
                    output_file_name = 'comb' + input_file_name[4:]
                else:
                    output_file_name = 'COMB' + input_file_name[4:]
                output_file_path = save_path + '/' + output_file_name

            self.show_outputsave_files_path_button.setText(output_file_path)

def on_exit():
    logger.info('Program ended.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting the program.")
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    print(dpi)
    ratio = dpi/96
    win = Data_Combine(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(14*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())