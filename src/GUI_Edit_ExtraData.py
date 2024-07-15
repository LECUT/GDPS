from datetime import *
from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
from ast import literal_eval
import sys
import re
import time
import os
from data_edit import code_extraction
from data_edit import prn_extraction
from data_edit import system_extraction
from data_edit import interval_extraction
from data_edit import time_extraction
import configparser
import resources_rc

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

curdir = os.getcwd()
class Data_Extract(QWidget):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Extract")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.resize(900, 490)
        self.resize(550*self.ratio, 450*self.ratio)
        # self.setFixedSize(550*self.ratio, 450*self.ratio)
        self.setup_ui()

    def setup_ui(self):
        label_w         = 75*self.ratio
        label_h         = 25*self.ratio
        ulabel_w        = 75*self.ratio
        ulabel_h        = 25*self.ratio
        LineEdit_w      = 340*self.ratio
        LineEdit_h      = 25*self.ratio
        PushButton_w    = 25*self.ratio
        PushButton_h    = 25*self.ratio
        sPushButton_w   = 200*self.ratio
        sPushButton_h   = 25*self.ratio
        fPushButton_w   = 200*self.ratio
        fPushButton_h   = 25*self.ratio
        rPushButton_w   = 200*self.ratio
        rPushButton_h   = 25*self.ratio
        QDateTimeEdit_w = 140*self.ratio
        QDateTimeEdit_h = 25*self.ratio
        QComboBox_w     = 140*self.ratio
        QComboBox_h     = 25*self.ratio
        QCheckBox_w     = 75*self.ratio
        QCheckBox_h     = 25*self.ratio
        Pagemargin      = 10*self.ratio

        #************************************************************************************
        edit_box = QGridLayout()
        self.choose_input_path_wuyong_label = QLabel('Input:', self)
        self.choose_input_path_wuyong_label.setMinimumSize(QSize(label_w, label_h))
        self.choose_input_path_wuyong_label.setMaximumSize(QSize(label_w, label_h))

        self.show_inputsave_files_path_button = QLineEdit(self)
        self.show_inputsave_files_path_button.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_inputsave_files_path_button = QPushButton(self)
        self.choose_inputsave_files_path_button.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_inputsave_files_path_button.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_inputsave_files_path_button.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_inputsave_files_path_button.clicked.connect(self.import_obs_file)

        self.start_time_label = QLabel('Time Start:', self)
        self.start_time_label.setMinimumSize(QSize(label_w, label_h))
        self.start_time_label.setMaximumSize(QSize(label_w, label_h))

        self.startTime_dateEdit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.startTime_dateEdit.setMinimumSize(QSize(QDateTimeEdit_w, QDateTimeEdit_h))
        self.startTime_dateEdit.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.startTime_dateEdit.setCalendarPopup(True)

        self.end_time_label = QLabel('Time End:', self)
        self.end_time_label.setMinimumSize(QSize(label_w, label_h))
        self.end_time_label.setMaximumSize(QSize(label_w, label_h))

        self.endTime_dateEdit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.endTime_dateEdit.setMinimumSize(QSize(QDateTimeEdit_w, QDateTimeEdit_h))
        self.endTime_dateEdit.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.endTime_dateEdit.setCalendarPopup(True)


        self.interval_label = QLabel('Interval:', self)
        self.interval_label.setMinimumSize(QSize(label_w, label_h))
        self.interval_label.setMaximumSize(QSize(label_w, label_h))

        self.interval_combox = QComboBox(self)
        self.interval_combox.setMinimumSize(QSize(QComboBox_w, QComboBox_h))
        self.interval_combox.addItems(['1', '5', '10', '15', '20', '30', 'custom'])
        self.interval_combox.setCurrentText('30')
        self.interval_combox.currentIndexChanged.connect(self.selectionchange)

        self.interval_label_unit = QLabel('  （unit:s）', self)
        self.interval_label_unit.setMinimumSize(QSize(ulabel_w, ulabel_h))
        # self.interval_label_unit.setMaximumSize(QSize(ulabel_w, ulabel_h))

        self.satellite_system_label = QLabel('System:', self)
        self.satellite_system_label.setMinimumSize(QSize(label_w, label_h))
        self.satellite_system_label.setMaximumSize(QSize(label_w, label_h))

        self.G_checkbox = QCheckBox('GPS', self)
        self.G_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.G_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px; height: 15px;}")
        self.R_checkbox = QCheckBox('GLO', self)
        self.R_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.R_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px;height: 15px;}")
        self.C_checkbox = QCheckBox('BDS', self)
        self.C_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.C_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px;height: 15px;}")
        self.E_checkbox = QCheckBox('GAL', self)
        self.E_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.E_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px;height: 15px;}")
        self.J_checkbox = QCheckBox('QZS', self)
        self.J_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.J_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px;height: 15px;}")
        self.I_checkbox = QCheckBox('NavIC', self)
        self.I_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.I_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px;height: 15px;}")
        self.S_checkbox = QCheckBox('SBS', self)
        self.S_checkbox.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.S_checkbox.setStyleSheet("QCheckBox::indicator{width: 30px;height: 15px;}")

        self.PRN_button = QPushButton('Select PRN', self)
        self.PRN_button.setMinimumSize(QSize(sPushButton_w, sPushButton_h))
        self.PRN_button.clicked.connect(self.select_PRN_link)

        self.ObsType_button = QPushButton('Select Band', self)
        self.ObsType_button.setMinimumSize(QSize(fPushButton_w, fPushButton_h))
        self.ObsType_button.clicked.connect(self.select_obs_type_link)

        self.choose_output_path_wuyong_label = QLabel('Output:', self)
        self.choose_output_path_wuyong_label.setMinimumSize(QSize(label_w, label_h))
        self.choose_output_path_wuyong_label.setMaximumSize(QSize(label_w, label_h))

        self.show_outputsave_files_path_button = QLineEdit(self)
        self.show_outputsave_files_path_button.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_outputsave_files_path_button = QPushButton(self)
        self.choose_outputsave_files_path_button.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_outputsave_files_path_button.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_outputsave_files_path_button.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_outputsave_files_path_button.clicked.connect(self.choose_output_files_path_function)


        self.data_extra_but = QPushButton('Execute', self)
        self.data_extra_but.setMinimumSize(QSize(rPushButton_w, rPushButton_h))
        self.data_extra_but.clicked.connect(self.data_extraction_function)


        blank_label = QLabel('')
        edit_box.setSpacing(1)
        edit_box.addWidget(self.choose_input_path_wuyong_label, 0, 0, 1, 1)
        edit_box.addWidget(self.show_inputsave_files_path_button, 0, 1, 1, 7)
        edit_box.addWidget(self.choose_inputsave_files_path_button, 0, 8, 1, 1)

        edit_box.addWidget(blank_label, 1, 0)
        edit_box.addWidget(self.start_time_label, 2, 0, 1, 1)
        edit_box.addWidget(self.startTime_dateEdit, 2, 1, 1, 2)
        edit_box.addWidget(blank_label, 2, 3, 1, 2)
        edit_box.addWidget(self.end_time_label, 2, 5, 1, 1)
        edit_box.addWidget(self.endTime_dateEdit, 2, 6, 1, 2)
        edit_box.addWidget(blank_label, 3, 0)

        edit_box.addWidget(self.interval_label, 4, 0, 1, 1)
        edit_box.addWidget(self.interval_combox, 4, 1, 1, 2)
        edit_box.addWidget(self.interval_label_unit, 4, 3, 1, 1)

        edit_box.addWidget(blank_label, 5, 0)
        edit_box.addWidget(self.satellite_system_label, 6, 0, 1, 1)
        edit_box.addWidget(self.G_checkbox, 6, 1, 1, 1)
        edit_box.addWidget(self.R_checkbox, 6, 2, 1, 1)
        edit_box.addWidget(self.C_checkbox, 6, 3, 1, 1)
        edit_box.addWidget(self.E_checkbox, 6, 4, 1, 1)

        edit_box.addWidget(self.J_checkbox, 6, 5, 1, 1)
        edit_box.addWidget(self.I_checkbox, 6, 6, 1, 1)
        edit_box.addWidget(self.S_checkbox, 6, 7, 1, 1)

        edit_box.addWidget(blank_label, 7, 0)
        edit_box.addWidget(self.PRN_button, 8, 0, 1, 4)
        edit_box.addWidget(self.ObsType_button, 8, 4, 1, 4)

        edit_box.addWidget(blank_label, 9, 0)
        edit_box.addWidget(self.choose_output_path_wuyong_label, 10, 0, 1, 1)
        edit_box.addWidget(self.show_outputsave_files_path_button, 10, 1, 1, 7)
        edit_box.addWidget(self.choose_outputsave_files_path_button, 10, 8, 1, 1)

        edit_box.addWidget(blank_label, 11, 0)
        edit_box.addWidget(self.data_extra_but, 12, 0, 1, 8)

        edit_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        self.setLayout(edit_box)

        self.allowed_select_prn_list = ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10", "G11",
                                        "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G19", "G20", "G21", "G22",
                                        "G33", "G24", "G25", "G26", "G27", "G28", "G29", "G30", "G31", "G32", "R01",
                                        "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10", "R11", "R12",
                                        "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20", "R21", "R22", "R23",
                                        "R24", "R25", "R26", "E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08",
                                        "E09", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19",
                                        "E20", "E21", "E22", "E33", "E24", "E25", "E26", "E27", "E28", "E29", "E30",
                                        "E31", "E32", "E33", "E34", "E35", "E36", "C01", "C02", "C03", "C04", "C05",
                                        "C06", "C07", "C08", "C09", "C10", "C11", "C12", "C13", "C14", "C16",
                                        "C19", "C20", "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29",
                                        "C30", "C32", "C33", "C34", "C35", "C36", "C37", "C38",
                                        "C39", "C40", "C41", "C42", "C43", "C44", "C45", "C46",
                                        "C56", "C57", "C58", "C59", "C60", "C61", "C62",
                                        "J01", "J02", "J03", "J04", "J05", "J06", "J07", "I01", "I02", "I03",
                                        "I04", "I05", "I06", "I07", "I08", "I09", "I10", "S01", "S02", "S03", "S04",
                                        "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12", "S13", "S14", "S15",
                                        "S16", "S17", "S18", "S19", "S20", "S21", "S22", "S33", "S24", "S25", "S26",
                                        "S27", "S28", "S29", "S30", "S31", "S32", "S33", "S34", "S35", "S36", "S37",
                                        "S38", "S39", "S40"]
        self.selected_prn_list = []
        # self.file_interval = '1'
        self.interval = 1
        self.RINEX_version = ''
        self.allowed_select_obscode_list = [['G', 'C1C', 'L1C', 'D1C', 'S1C', 'C2C', 'L2C', 'D2C', 'S2C', 'C5I', 'L5I', 'D5I', 'S5I'],
                                            ['R', 'C1C', 'L1C', 'D1C', 'S1C', 'C4A', 'L4A', 'D4A', 'S4A', 'C2C', 'L2C', 'D2C', 'S2C',
                                             'C6A', 'L6A', 'D6A', 'S6A', 'C3I', 'L3I', 'D3I', 'S3I'],
                                            ['E', 'C1A', 'L1A', 'D1A', 'S1A', 'C5I', 'L5I', 'D5I', 'S5I', 'C7I', 'L7I', 'D7I', 'S7I',
                                             'C8I', 'L8I', 'D8I', 'S8I', 'C6A', 'L6A', 'D6A', 'S6A'],
                                            ['C', 'C2I', 'L2I', 'D2I', 'S2I', 'C1D', 'L1D', 'D1D', 'S1D', 'C1S', 'L1S', 'D1S', 'S1S',
                                             'C5D', 'L5D', 'D5D', 'S5D', 'C7I', 'L7I', 'D7I', 'S7I', 'C8D', 'L8D', 'D8D', 'S8D',
                                             'C6I', 'L6I', 'D6I', 'S6I'],
                                            ['J', 'C1C', 'L1C', 'D1C', 'S1C', 'C2S', 'L2S', 'D2S', 'S2S', 'C5I', 'L5I', 'D5I', 'S5I',
                                             'C6S', 'L6S', 'D6S', 'S6S'],
                                            ['I', 'C5A', 'L5A', 'D5A', 'S5A', 'C9A', 'L9A', 'D9A', 'S9A', 'C1D', 'L1D', 'D1D', 'S1D'],
                                            ['S', 'C1C', 'L1C', 'D1C', 'S1C', 'C5I', 'L5I', 'D5I', 'S5I']]
        self.selected_obscode_list = []
        self.conf = configparser.ConfigParser()
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.read(conf_path, encoding='utf-8-sig')


    def selectionchange(self):
        if self.interval_combox.currentText() == 'custom':
            self.s = selfdiy_intv(self.interval, self.ratio)
            self.s.mySignal.connect(self.getDialogSignal)
            self.s.exec_()
        else:
            pass
    def getDialogSignal(self, connect):
        diy_intvi = str(connect)
        self.interval_combox.addItem(diy_intvi)
        self.interval_combox.setCurrentText(diy_intvi)
        self.conf.set('Parameter', 'interval', diy_intvi)
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.write(open(conf_path, 'w', encoding='utf-8'))


    def select_PRN_link(self):
        self.s = select_PRN(self.allowed_select_prn_list, self.selected_prn_list)
        self.s.mySignal.connect(self.getSelectedPRN)
        self.s.exec_()
    def getSelectedPRN(self, connect):
        self.selected_prn_list = connect
        print('selected_prn_list', self.selected_prn_list)


    def select_obs_type_link(self):
        self.s = select_obs_type(self.RINEX_version, self.allowed_select_obscode_list, self.selected_obscode_list)
        self.s.mySignal.connect(self.getSelectedObsCode)
        self.s.exec_()
    def getSelectedObsCode(self, connect):
        self.selected_obscode_list = connect
        print('22222  selected_obscode_list', self.selected_obscode_list)


    def import_obs_file(self):
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        unzip_default_download_path = desktop_path
        if os.path.exists(unzip_default_download_path):
            path1, parh2 = QFileDialog.getOpenFileName(self, 'Select the file', './', 'o_file(*MO.rnx *.*o *.*O);;All_File(*)')
        else:
            path1, parh2 = QFileDialog.getOpenFileName(self, 'Select the file', './', 'o_file(*MO.rnx *.*o *.*O);;All_File(*)')

        if parh2 != '':
            os.chdir(os.path.dirname(path1))

        if parh2 != '':
            # try:
            input_file_name = path1.split('/')[-1]
            input_path = path1.replace(input_file_name, '')
            if input_file_name[0].islower():
                self.output_file_name = 'ext_' + input_file_name
            else:
                self.output_file_name = 'EXT_' + input_file_name
            output_file_path = input_path + self.output_file_name
            self.show_outputsave_files_path_button.setText(output_file_path)

            with open(path1, 'r') as f:
                first_line = f.readline()
                self.RINEX_version = first_line[:10].strip()
                if first_line[20:36].upper() != 'OBSERVATION DATA':
                    QMessageBox.information(self, 'Error', 'The file is non-observation！')
                    return
            self.show_inputsave_files_path_button.setText(path1)
            self.input_file_extract_time(path1)
            self.input_file_extract_interv(path1)
            self.input_file_extract_prn_sys(path1)
            self.input_file_extract_obscode(path1)
            # except Exception as e:
            #     print(e)
                # QMessageBox.information(self, 'Error', "Invalid file, please re-import!")
                # return


    def input_file_extract_time(self, input_file_path):
        with open(input_file_path, 'r') as f:
            raw_rinex_text_list = f.readlines()
        f.close()
        #  Head info
        raw_header_info = []
        for i in range(len(raw_rinex_text_list)):
            line_text = raw_rinex_text_list[i].strip('\n')
            temp_info_list = [line_text[0:60], line_text[60:80]]
            raw_header_info = raw_header_info + [temp_info_list]
            if 'END OF HEADER' in line_text:
                end_header_rows = i
                break
        raw_data_record = raw_rinex_text_list[end_header_rows + 1:]

        for i in raw_data_record:
            if len(i[:27].split()) > 5:
                first_time_list = i[:27].split()
                break
        for j in reversed(raw_data_record):
            if len(j[:27].split()) > 5:
                last_time_list = j[:27].split()
                break
        #  Time start
        if len(first_time_list[0]) == 2:
            start_year = 2000 + int(first_time_list[0])
            start_month = int(first_time_list[1])
            start_day = int(first_time_list[2])
            start_hour = int(first_time_list[3])
            start_monter = int(first_time_list[4])
            start_second = int(float(first_time_list[5]))
        else:
            start_year = int(first_time_list[1])
            start_month = int(first_time_list[2])
            start_day = int(first_time_list[3])
            start_hour = int(first_time_list[4])
            start_monter = int(first_time_list[5])
            start_second = int(float(first_time_list[6]))
        #  Time end
        if len(last_time_list[0]) == 2:
            last_year = 2000 + int(last_time_list[0])
            last_month = int(last_time_list[1])
            last_day = int(last_time_list[2])
            last_hour = int(last_time_list[3])
            last_monter = int(last_time_list[4])
            last_second = int(float(last_time_list[5]))
        else:
            last_year = int(last_time_list[1])
            last_month = int(last_time_list[2])
            last_day = int(last_time_list[3])
            last_hour = int(last_time_list[4])
            last_monter = int(last_time_list[5])
            last_second = int(float(last_time_list[6]))
        self.first_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
        self.last_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
        # print('Time Start', self.first_time) # 2021-01-01 00:00:00
        # print('Time End', self.last_time) # 2021-01-01 23:59:30
        self.startTime_dateEdit.setMinimumDateTime(self.first_time)
        self.startTime_dateEdit.setMaximumDateTime(self.last_time)
        self.endTime_dateEdit.setMinimumDateTime(self.first_time)
        self.endTime_dateEdit.setMaximumDateTime(self.last_time)
        self.startTime_dateEdit.setDateTime(self.first_time)
        self.endTime_dateEdit.setDateTime(self.last_time)

    def input_file_extract_interv(self, input_file_path):
        with open(input_file_path, 'r') as f:
            raw_rinex_text_list = f.readlines()

        raw_header_info = []
        for i in range(len(raw_rinex_text_list)):
            line_text = raw_rinex_text_list[i].strip('\n')
            temp_info_list = [line_text[0:60], line_text[60:80]]
            raw_header_info = raw_header_info + [temp_info_list]
            if 'END OF HEADER' in line_text:
                end_header_rows = i
                break
        raw_data_record = raw_rinex_text_list[end_header_rows + 1:]

        ture_judge = True
        for i in raw_data_record:
            if len(i[:27].split()) > 5:
                if ture_judge:
                    first_time_list = i[:27].split()
                    ture_judge = False
                else:
                    second_time_list = i[:27].split()
                    break

        if len(first_time_list[0]) == 2:
            start_year = 2000 + int(first_time_list[0])
            start_month = int(first_time_list[1])
            start_day = int(first_time_list[2])
            start_hour = int(first_time_list[3])
            start_monter = int(first_time_list[4])
            start_second = int(float(first_time_list[5]))
        else:
            start_year = int(first_time_list[1])
            start_month = int(first_time_list[2])
            start_day = int(first_time_list[3])
            start_hour = int(first_time_list[4])
            start_monter = int(first_time_list[5])
            start_second = int(float(first_time_list[6]))

        if len(second_time_list[0]) == 2:
            last_year = 2000 + int(second_time_list[0])
            last_month = int(second_time_list[1])
            last_day = int(second_time_list[2])
            last_hour = int(second_time_list[3])
            last_monter = int(second_time_list[4])
            last_second = int(float(second_time_list[5]))
        else:
            last_year = int(second_time_list[1])
            last_month = int(second_time_list[2])
            last_day = int(second_time_list[3])
            last_hour = int(second_time_list[4])
            last_monter = int(second_time_list[5])
            last_second = int(float(second_time_list[6]))
        first_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
        second_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
        self.interval = (second_time - first_time).total_seconds()

        self.interval_combox.clear()
        new_items = []
        for num in range(1, 6):
            add_value = str(int(self.interval) * num)
            new_items.append(add_value)
        new_items.append('custom')
        self.interval_combox.addItems(new_items)
        self.interval_combox.setCurrentText(new_items[0])
        pass


    def input_file_extract_prn_sys(self, input_file_path):
        with open(input_file_path, 'r') as f:
            raw_rinex_text_list = f.readlines()

        type_of_observ_judge = True
        for i in range(len(raw_rinex_text_list)):
            line_text = raw_rinex_text_list[i].strip('\n')
            if line_text[60:80].strip() == '# / TYPES OF OBSERV':
                if type_of_observ_judge:
                    input_file_code_num = int(line_text[:10].strip())
                    type_of_observ_judge = False
            if 'END OF HEADER' in line_text:
                end_header_rows = i
                break
        raw_data_record = raw_rinex_text_list[end_header_rows + 1:]

        #  PRN
        copy_raw_data_record = raw_data_record[:]
        list_copy_raw_data_record = iter(copy_raw_data_record)
        all_record_prn_list = []
        if re.search(r'>\s\d{4}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}.\d{7}', raw_data_record[0]):  #
            for line in list_copy_raw_data_record:
                if line[0] != '>':
                    if re.search(r'[A-Z]..', line[0:3]):
                        all_record_prn_list.append(line[:3])
        else:
            for line in list_copy_raw_data_record:
                if re.search(r'\s\d{2}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', line):
                    the_moment_site_satellite_num = int(line[30:32])
                    all_monment_prn_list = line[32:].split('\n')[0]
                    all_monment_prn_list = "".join(re.findall('[A-Z]..', all_monment_prn_list)).replace(' ', '0')
                    divisible_moment_satellite = the_moment_site_satellite_num % 12
                    if divisible_moment_satellite == 0:
                        record_satellite_row = the_moment_site_satellite_num // 12 - 1
                    else:
                        record_satellite_row = the_moment_site_satellite_num // 12
                    skip_record_num_1 = record_satellite_row
                    while skip_record_num_1 > 0:
                        all_monment_prn_list += str(next(list_copy_raw_data_record).split('\n')[0].strip()).replace(' ', '0')
                        skip_record_num_1 -= 1
                    all_monment_prn_list = re.findall(r'[A-Z]..', all_monment_prn_list)
                    all_record_prn_list.extend(all_monment_prn_list)

        self.all_record_prn_list = list(set(all_record_prn_list))
        self.all_record_prn_list.sort()

        self.all_record_sys_list = []
        for prn in self.all_record_prn_list:
            if prn[0] not in self.all_record_sys_list:
                self.all_record_sys_list.append(prn[0])

        self.allowed_select_prn_list = self.all_record_prn_list[:]
        self.selected_prn_list = self.all_record_prn_list[:]
        unallowed_sys_list = ['G', 'R', 'E', 'C', 'J', 'I', 'S']
        for sys in self.all_record_sys_list:
            exec("self.{}_checkbox.setChecked(True)".format(sys))
            unallowed_sys_list.remove(sys)
        for sys in unallowed_sys_list:
            exec("self.{}_checkbox.setCheckable(False)".format(sys))
            exec("self.{}_checkbox.setEnabled(False)".format(sys))
        pass

    def input_file_extract_obscode(self, input_file_path):
        with open(input_file_path, 'r') as f:
            raw_rinex_text_list = f.readlines()
        for i in range(len(raw_rinex_text_list)):
            line_text = raw_rinex_text_list[i].strip('\n')
            if 'END OF HEADER' in line_text:
                end_header_rows = i
                break
        raw_data_record = raw_rinex_text_list[end_header_rows + 1:]

        #
        type_of_observe_num = True
        raw_type_of_observe = []
        num = 0
        for deal_row in range(end_header_rows):
            add_dealed_list = []
            current_row_list = raw_rinex_text_list[deal_row].strip('\n')
            header_label = current_row_list[60:80].strip()
            if header_label == 'RINEX VERSION / TYPE':
                rinex_version = current_row_list[:10].strip()
            elif header_label == '# / TYPES OF OBSERV':  # RINEX 2
                if type_of_observe_num:
                    sys_obs_type_insert_num = num
                    type_of_observe_num = False
                raw_type_of_observe.append(current_row_list)
            elif header_label == 'SYS / # / OBS TYPES':  # RINEX 4
                if type_of_observe_num:
                    sys_obs_type_insert_num = num
                    type_of_observe_num = False
                raw_type_of_observe.append(current_row_list[:60])
            num += 1
        # print(raw_type_of_observe)

        #   default code transform [['G', 'L1', 'L2', 'C1'], ['R', 'L1', 'L2', 'C1'], ['C', 'L1', 'L2', 'C1']]
        sys_obscode_list = []
        if raw_data_record[0][0] == '>':  #
            raw_one_sys_obs_list = []  # [['G   18 C1C L1C D1C S1C C1W S1W    S2L C5Q L5Q D5Q S5Q          '], ...]
            for i in raw_type_of_observe:
                if i[0] != ' ':
                    raw_one_sys_obs_list += [i]
                else:
                    raw_one_sys_obs_list[-1] = raw_one_sys_obs_list[-1] + [i]
                if len(raw_one_sys_obs_list[-1]) != 1:
                    temp_list = ''
                    for j in raw_one_sys_obs_list[-1]:
                        temp_list += j
                    raw_one_sys_obs_list[-1] = [temp_list]
            sys_obscode_list = []  # [['G', ['C1C', 'L1C']], ['R', ['C1C']]]
            for i in raw_one_sys_obs_list:
                temp_list = i[0].split()
                temp_list01 = temp_list[2:len(temp_list)]
                temp_list01.insert(0, temp_list[0])
                sys_obscode_list.append(temp_list01)
                pass
        else:
            #
            copy_raw_data_record = raw_data_record[:]
            list_copy_raw_data_record = iter(copy_raw_data_record)
            all_record_prn_list = []
            for line in list_copy_raw_data_record:
                if len(line[:27].split()) > 5:
                    the_moment_site_satellite_num = int(line[30:32])
                    all_monment_prn_list = line[32:].split('\n')[0]
                    all_monment_prn_list = "".join(re.findall('[A-Z]..', all_monment_prn_list)).replace(' ', '0')
                    divisible_moment_satellite = the_moment_site_satellite_num % 12
                    if divisible_moment_satellite == 0:
                        record_satellite_row = the_moment_site_satellite_num // 12 - 1
                    else:
                        record_satellite_row = the_moment_site_satellite_num // 12
                    skip_record_num_1 = record_satellite_row
                    while skip_record_num_1 > 0:
                        all_monment_prn_list += str(next(list_copy_raw_data_record).split('\n')[0].strip()).replace(' ',
                                                                                                                    '0')
                        skip_record_num_1 -= 1
                    all_monment_prn_list = re.findall(r'.{3}', all_monment_prn_list)
                    all_record_prn_list.extend(all_monment_prn_list)
            all_record_sys_list = [i[0] for i in all_record_prn_list]
            all_record_sys_list = list(set(all_record_sys_list))
            all_record_sys_list.sort()

            all_type_of_observe_code = []
            for one_row_of_type_observe in raw_type_of_observe:
                temp_type_of_observe_list = (one_row_of_type_observe.split('#')[0]).split()
                for one_observe_code in temp_type_of_observe_list:
                    if len(one_observe_code) == 2:
                        if one_observe_code.isdigit():
                            pass
                        else:
                            all_type_of_observe_code.append(one_observe_code)
            for sys in all_record_sys_list:
                temp_list = all_type_of_observe_code[:]
                temp_list.insert(0, sys)
                sys_obscode_list.append(temp_list)
        # print('code', sys_obscode_list) #  [['G', 'L1', 'L2', 'C1'], ['R', 'L1', 'L2', 'C1'], ['C', 'L1', 'L2']]
        self.allowed_select_obscode_list = sys_obscode_list[:]
        self.selected_obscode_list = sys_obscode_list[:]



    #
    def choose_output_files_path_function(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', 'C:/')
        if save_path == '':
            pass
        else:
            output_file_path = save_path + '/' + self.output_file_name
            self.show_outputsave_files_path_button.setText(output_file_path)


    #
    def data_extraction_function(self):
        if self.show_inputsave_files_path_button.text() == '':
            QMessageBox.information(self, 'Error', "Please import the file!")
            return
        #
        input_file_path = self.show_inputsave_files_path_button.text()
        output_file_path = self.show_outputsave_files_path_button.text()
        seted_start_time = self.startTime_dateEdit.dateTime()
        seted_end_time = self.endTime_dateEdit.dateTime()
        seted_interval = self.interval_combox.currentText()
        seted_sys = []
        for sys in ['G', 'R', 'C', 'E', 'J', 'I', 'S']:
            exec("if self.{}_checkbox.isChecked() == True: seted_sys.append(sys)".format(sys))
            # exec("if self.{}_checkbox.isChecked() == True: seted_sys.append(self.{}_checkbox.text())".format(sys, sys)
        self.conf.set('Parameter', 'input_file_path', input_file_path)
        self.conf.set('Parameter', 'output_file_path', output_file_path)
        self.conf.set('Parameter', 'interval', seted_interval)
        self.conf.set('Parameter', 'sys_list', str(seted_sys))
        self.conf.set('Parameter', 'prn_list', str(self.selected_prn_list))
        self.conf.set('Parameter', 'code_list', str(self.selected_obscode_list))


        #
        time_extract_judge = False
        start_time_T = str(self.startTime_dateEdit.dateTime().toString(Qt.ISODate))
        start_time_T = start_time_T[0:10] + ' ' + start_time_T[11:19]
        end_time_T = str(self.endTime_dateEdit.dateTime().toString(Qt.ISODate))
        end_time_T = end_time_T[0:10] + ' ' + end_time_T[11:19]
        self.conf.set('Parameter', 'start_time', start_time_T)
        self.conf.set('Parameter', 'end_time', end_time_T)
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.write(open(conf_path, 'w', encoding='utf-8'))

        start_time_T = self.conf.get('Parameter', 'start_time')
        end_time_T = self.conf.get('Parameter', 'end_time')
        dt1 = datetime.strptime(start_time_T, '%Y-%m-%d %H:%M:%S')
        dt2 = datetime.strptime(end_time_T, '%Y-%m-%d %H:%M:%S')
        difference_time = dt2 - dt1
        if difference_time.days >= 0:
            if self.first_time == seted_start_time and self.last_time == seted_end_time:
                pass
            else:
                time_extract_judge = True
        else:
            QMessageBox.information(self, 'prompt', 'Error Time Order！')
            return
        pass

        #
        interval_extract_judge = False
        seted_interval = self.conf.get('Parameter', 'interval')
        if seted_interval != str(int(self.interval)):

            interval_extract_judge = True
        else:
            pass

        sys_extract_judge = False
        temp_list = self.all_record_sys_list[:]
        temp_list.sort()
        if len(seted_sys) != 0:
            seted_sys_str = self.conf.get('Parameter', 'sys_list')
            seted_sys = literal_eval(seted_sys_str)
            seted_sys.sort()
            if seted_sys != temp_list:

                sys_extract_judge = True
            else:
                pass
        else:
            QMessageBox.information(self, 'Prompt', 'At least Select one satellite system！')
            return

        # PRN
        prn_extract_judge = False
        self.selected_prn_str = self.conf.get('Parameter', 'prn_list')
        self.selected_prn_list = literal_eval(self.selected_prn_str)
        self.all_record_prn_list.sort()
        self.selected_prn_list.sort()
        if len(self.selected_prn_list) != 0:
            if self.all_record_prn_list != self.selected_prn_list:
                prn_extract_judge = True
            else:
                pass
        else:
            QMessageBox.information(self, 'Prompt', 'At least Select one satellite PRN！')
            return
        input_file_path = self.conf.get('Parameter', 'input_file_path')
        with open(input_file_path, 'r') as f:
            raw_rinex_text_list = f.readlines()
        if time_extract_judge:
            raw_rinex_text_list = time_extraction.Time_Extraction_Function(raw_rinex_text_list, dt1, dt2)
            pass
        if interval_extract_judge:
            raw_rinex_text_list = interval_extraction.Interval_Extraction_Function(raw_rinex_text_list, float(seted_interval))
            pass
        if sys_extract_judge:
            raw_rinex_text_list = system_extraction.System_Extraction_Function(raw_rinex_text_list, seted_sys)
            pass
        if prn_extract_judge:
            raw_rinex_text_list = prn_extraction.PRN_Extraction_Function(raw_rinex_text_list, self.selected_prn_list)
            pass
        #
        self.selected_obscode_str = self.conf.get('Parameter', 'code_list')
        self.selected_obscode_list = literal_eval(self.selected_obscode_str)
        raw_rinex_text_list = code_extraction.Code_Extraction_Function(raw_rinex_text_list, self.selected_obscode_list)

        #
        output_file_path = self.conf.get('Parameter', 'output_file_path')
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for i in raw_rinex_text_list:
                f.write(str(i))
        QMessageBox.information(self, 'Prompt', 'Extraction completed！')


class select_PRN(QDialog):
    mySignal = pyqtSignal(list)
    def __init__(self, allowed_select_prn_list, selected_prn_list):
        super().__init__()
        self.allowed_select_prn_list = allowed_select_prn_list
        self.selected_prn_list = selected_prn_list
        self.setWindowTitle("PRN")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.move(365, 90)
        self.GPS_listCheckBox = ["G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10",
                                 "G11", "G12", "G13", "G14", "G15", "G16", "G17", "G18", "G19", "G20",
                                 "G21", "G22", "G24", "G25", "G26", "G27", "G28", "G29", "G30",
                                 "G31", "G32"]
        self.GLONASS_listCheckBox = ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10",
                                     "R11", "R12", "R13", "R14", "R15", "R16", "R17", "R18", "R19", "R20",
                                     "R21", "R22", "R23", "R24", "R25", "R26"]
        self.GALILEO_listCheckBox = ["E01", "E02", "E03", "E04", "E05", "E06", "E07", "E08", "E09", "E10",
                                     "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20",
                                     "E21", "E22", "E33", "E24", "E25", "E26", "E27", "E28", "E29", "E30",
                                     "E31", "E32", "E33", "E34", "E35", "E36"]
        self.BDS_listCheckBox = ["C01", "C02", "C03", "C04", "C05", "C06", "C07", "C08", "C09", "C10",
                                 "C11", "C12", "C13", "C14", "C16",  "C19", "C20",
                                 "C21", "C22", "C23", "C24", "C25", "C26", "C27", "C28", "C29", "C30",
                                 "C32", "C33", "C34", "C35", "C36", "C37", "C38", "C39", "C40",
                                 "C41", "C42", "C43", "C44", "C45", "C46",
                                 "C56", "C57", "C58", "C59", "C60", "C61", "C62"]
        self.QZSS_listCheckBox = ["J01", "J02", "J03", "J04", "J05", "J06", "J07"]
        self.IRNSS_listCheckBox = ["I01", "I02", "I03", "I04", "I05", "I06", "I07", "I08", "I09", "I10"]
        self.SBAS_listCheckBox = ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10",
                                  "S11", "S12", "S13", "S14", "S15", "S16", "S17", "S18", "S19", "S20",
                                  "S21", "S22", "S33", "S24", "S25", "S26", "S27", "S28", "S29", "S30",
                                  "S31", "S32", "S33", "S34", "S35", "S36", "S37", "S38", "S39", "S40"]

        grid = QGridLayout()
        self.GPS_label = QLabel("GPS")
        grid.addWidget(self.GPS_label, 0, 0)
        self.GPS_all = QCheckBox("All")
        self.GPS_all.stateChanged.connect(self.GPS_global)
        self.GPS_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        grid.addWidget(self.GPS_all, 0, 1)
        for i1, v1 in enumerate(self.GPS_listCheckBox):
            self.GPS_listCheckBox[i1] = QCheckBox(v1)
            self.GPS_listCheckBox[i1].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v1 not in self.allowed_select_prn_list:
                self.GPS_listCheckBox[i1].setCheckable(False)
                self.GPS_listCheckBox[i1].setEnabled(False)
            if v1 in self.selected_prn_list:
                self.GPS_listCheckBox[i1].setChecked(True)
            grid.addWidget(self.GPS_listCheckBox[i1], int(i1/20 + 1), int(i1%20))


        self.blank_space_label = QLabel("")
        grid.addWidget(self.blank_space_label, 4, 0)
        self.GLONASS_label = QLabel("GLO")
        grid.addWidget(self.GLONASS_label, 5, 0)
        self.GLONASS_all = QCheckBox("All")
        self.GLONASS_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.GLONASS_all.stateChanged.connect(self.GLONASS_global)
        grid.addWidget(self.GLONASS_all, 5, 1)
        for i2, v2 in enumerate(self.GLONASS_listCheckBox):
            self.GLONASS_listCheckBox[i2] = QCheckBox(v2)
            self.GLONASS_listCheckBox[i2].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v2 not in self.allowed_select_prn_list:
                self.GLONASS_listCheckBox[i2].setCheckable(False)
                self.GLONASS_listCheckBox[i2].setEnabled(False)
            if v2 in self.selected_prn_list:
                self.GLONASS_listCheckBox[i2].setChecked(True)
            grid.addWidget(self.GLONASS_listCheckBox[i2], int(i2/20 + 6), int(i2%20))

        self.blank_space_label = QLabel("")
        grid.addWidget(self.blank_space_label, 9, 0)
        self.BDS_label = QLabel("BDS")
        grid.addWidget(self.BDS_label, 10, 0)
        self.BDS_all = QCheckBox("All")
        self.BDS_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.BDS_all.stateChanged.connect(self.BDS_global)
        grid.addWidget(self.BDS_all, 10, 1)
        for i3, v3 in enumerate(self.BDS_listCheckBox):
            self.BDS_listCheckBox[i3] = QCheckBox(v3)
            self.BDS_listCheckBox[i3].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v3 not in self.allowed_select_prn_list:
                self.BDS_listCheckBox[i3].setCheckable(False)
                self.BDS_listCheckBox[i3].setEnabled(False)
            if v3 in self.selected_prn_list:
                self.BDS_listCheckBox[i3].setChecked(True)
            grid.addWidget(self.BDS_listCheckBox[i3], int(i3/20 + 11), int(i3%20))

        self.blank_space_label = QLabel("")
        grid.addWidget(self.blank_space_label, 16, 0)
        self.GALILEO_label = QLabel("GAL")
        grid.addWidget(self.GALILEO_label, 17, 0)
        self.GALILEO_all = QCheckBox("All")
        self.GALILEO_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.GALILEO_all.stateChanged.connect(self.GALILEO_global)
        grid.addWidget(self.GALILEO_all, 17, 1)
        for i4, v4 in enumerate(self.GALILEO_listCheckBox):
            self.GALILEO_listCheckBox[i4] = QCheckBox(v4)
            self.GALILEO_listCheckBox[i4].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v4 not in self.allowed_select_prn_list:
                self.GALILEO_listCheckBox[i4].setCheckable(False)
                self.GALILEO_listCheckBox[i4].setEnabled(False)
            if v4 in self.selected_prn_list:
                self.GALILEO_listCheckBox[i4].setChecked(True)
            grid.addWidget(self.GALILEO_listCheckBox[i4], int(i4/20+18), int(i4%20))

        self.blank_space_label = QLabel("")
        grid.addWidget(self.blank_space_label, 20, 0)
        self.QZSS_label = QLabel("QZS")
        grid.addWidget(self.QZSS_label, 21, 0)
        self.QZSS_all = QCheckBox("All")
        self.QZSS_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.QZSS_all.stateChanged.connect(self.QZSS_global)
        grid.addWidget(self.QZSS_all, 21, 1)
        for i5, v5 in enumerate(self.QZSS_listCheckBox):
            self.QZSS_listCheckBox[i5] = QCheckBox(v5)
            self.QZSS_listCheckBox[i5].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v5 not in self.allowed_select_prn_list:
                self.QZSS_listCheckBox[i5].setCheckable(False)
                self.QZSS_listCheckBox[i5].setEnabled(False)
            if v5 in self.selected_prn_list:
                self.QZSS_listCheckBox[i5].setChecked(True)
            grid.addWidget(self.QZSS_listCheckBox[i5], int(i5/20+22), int(i5%20))

        self.blank_space_label = QLabel("")
        grid.addWidget(self.blank_space_label, 23, 0)
        self.IRNSS_label = QLabel('NavIC')
        grid.addWidget(self.IRNSS_label, 24, 0)
        self.IRNSS_all = QCheckBox("All")
        self.IRNSS_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.IRNSS_all.stateChanged.connect(self.IRNSS_global)
        grid.addWidget(self.IRNSS_all, 24, 1)
        for i6, v6 in enumerate(self.IRNSS_listCheckBox):
            self.IRNSS_listCheckBox[i6] = QCheckBox(v6)
            self.IRNSS_listCheckBox[i6].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v6 not in self.allowed_select_prn_list:
                self.IRNSS_listCheckBox[i6].setCheckable(False)
                self.IRNSS_listCheckBox[i6].setEnabled(False)
            if v6 in self.selected_prn_list:
                self.IRNSS_listCheckBox[i6].setChecked(True)
            grid.addWidget(self.IRNSS_listCheckBox[i6], int(i6/20+25), int(i6%20))

        self.blank_space_label = QLabel("")
        grid.addWidget(self.blank_space_label, 27, 0)
        self.SBAS_label = QLabel("SBS")
        grid.addWidget(self.SBAS_label, 28, 0)
        self.SBAS_all = QCheckBox("All")
        self.SBAS_all.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.SBAS_all.stateChanged.connect(self.SBAS_global)
        grid.addWidget(self.SBAS_all, 28, 1)
        for i7, v7 in enumerate(self.SBAS_listCheckBox):
            self.SBAS_listCheckBox[i7] = QCheckBox(v7)
            self.SBAS_listCheckBox[i7].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            if v7 not in self.allowed_select_prn_list:
                self.SBAS_listCheckBox[i7].setCheckable(False)
                self.SBAS_listCheckBox[i7].setEnabled(False)
            if v7 in self.selected_prn_list:
                self.SBAS_listCheckBox[i7].setChecked(True)
            grid.addWidget(self.SBAS_listCheckBox[i7], int(i7/20+29), int(i7%20))

        gnss_wg = QFrame()
        gnss_wg.setFrameShape(QFrame.Box)
        # frame_wg.setStyleSheet('border:1px solid #5F92B2;border-radius:5px;')
        gnss_wg.setLayout(grid)

        gnss_wg.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)


        bnt_box = QHBoxLayout()
        self.global_button = QPushButton("Set All")
        self.global_button.clicked.connect(self.total_global)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_global)
        self.sure_button = QPushButton("OK")
        self.sure_button.clicked.connect(self.sure_function)
        blank_space_label = QLabel("")

        spacerItem_V = QSpacerItem(1, 2, QSizePolicy.Minimum, QSizePolicy.Expanding)
        bnt_box.addItem(spacerItem_V)
        bnt_box.addWidget(blank_space_label)
        bnt_box.addWidget(blank_space_label)
        bnt_box.addWidget(blank_space_label)
        bnt_box.addWidget(self.global_button)
        bnt_box.addWidget(self.cancel_button)
        bnt_box.addWidget(self.sure_button)

        bnt_wg = QFrame()
        bnt_wg.setLayout(bnt_box)

        main_box = QVBoxLayout()
        main_box.addWidget(gnss_wg)
        main_box.addWidget(bnt_wg)

        self.setLayout(main_box)

    def sure_function(self):
        choice_1 = []
        for i1, v1 in enumerate(self.GPS_listCheckBox):
            if self.GPS_listCheckBox[i1].isChecked() == True:
                choice_1.append(self.GPS_listCheckBox[i1].text())
        for i2, v2 in enumerate(self.GLONASS_listCheckBox):
            if self.GLONASS_listCheckBox[i2].isChecked() == True:
                choice_1.append(self.GLONASS_listCheckBox[i2].text())
        for i3, v3 in enumerate(self.BDS_listCheckBox):
            if self.BDS_listCheckBox[i3].isChecked() == True:
                choice_1.append(self.BDS_listCheckBox[i3].text())
        for i4, v4 in enumerate(self.GALILEO_listCheckBox):
            if self.GALILEO_listCheckBox[i4].isChecked() == True:
                choice_1.append(self.GALILEO_listCheckBox[i4].text())
        for i5, v5 in enumerate(self.QZSS_listCheckBox):
            if self.QZSS_listCheckBox[i5].isChecked() == True:
                choice_1.append(self.QZSS_listCheckBox[i5].text())
        for i6, v6 in enumerate(self.IRNSS_listCheckBox):
            if self.IRNSS_listCheckBox[i6].isChecked() == True:
                choice_1.append(self.IRNSS_listCheckBox[i6].text())
        for i7, v7 in enumerate(self.SBAS_listCheckBox):
            if self.SBAS_listCheckBox[i7].isChecked() == True:
                choice_1.append(self.SBAS_listCheckBox[i7].text())
        self.mySignal.emit(choice_1)
        self.hide()
        return choice_1

    # GPS
    def GPS_global(self):
        for i1, v1 in enumerate(self.GPS_listCheckBox):
            if self.GPS_all.isChecked() == True:
                self.GPS_listCheckBox[i1].setChecked(True)
            elif self.GPS_all.isChecked() == False:
                self.GPS_listCheckBox[i1].setChecked(False)

    # GLONASS
    def GLONASS_global(self):
        for i2, v2 in enumerate(self.GLONASS_listCheckBox):
            if self.GLONASS_all.isChecked() == True:
                self.GLONASS_listCheckBox[i2].setChecked(True)
            elif self.GLONASS_all.isChecked() == False:
                self.GLONASS_listCheckBox[i2].setChecked(False)

    # BDS
    def BDS_global(self):
        for i3, v3 in enumerate(self.BDS_listCheckBox):
            if self.BDS_all.isChecked() == True:
                self.BDS_listCheckBox[i3].setChecked(True)
            elif self.BDS_all.isChecked() == False:
                self.BDS_listCheckBox[i3].setChecked(False)

    # GALILEO
    def GALILEO_global(self):
        for i4, v4 in enumerate(self.GALILEO_listCheckBox):
            if self.GALILEO_all.isChecked() == True:
                self.GALILEO_listCheckBox[i4].setChecked(True)
            elif self.GALILEO_all.isChecked() == False:
                self.GALILEO_listCheckBox[i4].setChecked(False)

    # QZSS
    def QZSS_global(self):
        for i5, v5 in enumerate(self.QZSS_listCheckBox):
            if self.QZSS_all.isChecked() == True:
                self.QZSS_listCheckBox[i5].setChecked(True)
            elif self.QZSS_all.isChecked() == False:
                self.QZSS_listCheckBox[i5].setChecked(False)

    # IRNSS
    def IRNSS_global(self):
        for i6, v6 in enumerate(self.IRNSS_listCheckBox):
            if self.IRNSS_all.isChecked() == True:
                self.IRNSS_listCheckBox[i6].setChecked(True)
            elif self.IRNSS_all.isChecked() == False:
                self.IRNSS_listCheckBox[i6].setChecked(False)

    # SBAS
    def SBAS_global(self):
        for i7, v7 in enumerate(self.SBAS_listCheckBox):
            if self.SBAS_all.isChecked() == True:
                self.SBAS_listCheckBox[i7].setChecked(True)
            elif self.SBAS_all.isChecked() == False:
                self.SBAS_listCheckBox[i7].setChecked(False)

    # All
    def total_global(self):
        for i1, v1 in enumerate(self.GPS_listCheckBox):
            self.GPS_listCheckBox[i1].setChecked(True)
        for i2, v2 in enumerate(self.GLONASS_listCheckBox):
            self.GLONASS_listCheckBox[i2].setChecked(True)
        for i3, v3 in enumerate(self.BDS_listCheckBox):
            self.BDS_listCheckBox[i3].setChecked(True)
        for i4, v4 in enumerate(self.GALILEO_listCheckBox):
            self.GALILEO_listCheckBox[i4].setChecked(True)
        for i5, v5 in enumerate(self.QZSS_listCheckBox):
            self.QZSS_listCheckBox[i5].setChecked(True)
        for i6, v6 in enumerate(self.IRNSS_listCheckBox):
            self.IRNSS_listCheckBox[i6].setChecked(True)
        for i7, v7 in enumerate(self.SBAS_listCheckBox):
            self.SBAS_listCheckBox[i7].setChecked(True)

    # Concel
    def cancel_global(self):
        self.GPS_all.setChecked(False)
        for i1, v1 in enumerate(self.GPS_listCheckBox):
            self.GPS_listCheckBox[i1].setChecked(False)

        self.GLONASS_all.setChecked(False)
        for i2, v2 in enumerate(self.GLONASS_listCheckBox):
            self.GLONASS_listCheckBox[i2].setChecked(False)

        self.BDS_all.setChecked(False)
        for i3, v3 in enumerate(self.BDS_listCheckBox):
            self.BDS_listCheckBox[i3].setChecked(False)

        self.GALILEO_all.setChecked(False)
        for i4, v4 in enumerate(self.GALILEO_listCheckBox):
            self.GALILEO_listCheckBox[i4].setChecked(False)

        self.QZSS_all.setChecked(False)
        for i5, v5 in enumerate(self.QZSS_listCheckBox):
            self.QZSS_listCheckBox[i5].setChecked(False)

        self.IRNSS_all.setChecked(False)
        for i6, v6 in enumerate(self.IRNSS_listCheckBox):
            self.IRNSS_listCheckBox[i6].setChecked(False)

        self.SBAS_all.setChecked(False)
        for i7, v7 in enumerate(self.SBAS_listCheckBox):
            self.SBAS_listCheckBox[i7].setChecked(False)

class select_obs_type(QDialog):
    mySignal = pyqtSignal(list)
    def __init__(self, RINEX_version, allowed_select_obscode_list, selected_obscode_list):
        super().__init__()
        self.setWindowTitle("Band")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.RINEX_version = RINEX_version
        self.selected_obscode_list = selected_obscode_list
        self.allowed_select_obscode_list = allowed_select_obscode_list
        self.setup_ui()

    def setup_ui(self):
        self.Channel_Code_list = [['G', 'L1', {'C1': ['C1', 'P1', 'CA', 'CB', 'C1C', 'C1S', 'C1L', 'C1X', 'C1P', 'C1W', 'C1Y', 'C1M', 'C1R']},
                                  {'L1': ['L1', 'LA', 'LB', 'L1C', 'L1S', 'L1L', 'L1X', 'L1P', 'L1W', 'L1Y', 'L1M', 'L1N', 'L1R']},
                              {'D1': ['D1', 'DA', 'DB', 'D1C', 'D1S', 'D1L', 'D1X', 'D1P', 'D1W', 'D1Y', 'D1M', 'D1N', 'D1R']},
                              {'S1': ['S1', 'SA', 'SB', 'S1C', 'S1S', 'S1L', 'S1X', 'S1P', 'S1W', 'S1Y', 'S1M', 'S1N', 'S1R']}],
                             ['G', 'L2', {'C2': ['C2', 'CC', 'P2', 'C2C', 'C2D', 'C2S', 'C2L', 'C2X', 'C2P', 'C2W', 'C2Y', 'C2M', 'C2R']},
                              {'L2': ['L2', 'LC', 'L2C', 'L2D', 'L2S', 'L2L', 'L2X', 'L2P', 'L2W', 'L2Y', 'L2M', 'L2N', 'L2R']},
                              {'D2': ['D2', 'DC', 'D2C', 'D2S', 'D2S', 'D2L', 'D2X', 'D2P', 'D2W', 'D2Y', 'D2M', 'D2N', 'D2R']},
                              {'S2': ['S2', 'SC', 'S2C', 'S2D', 'S2S', 'S2L', 'S2X', 'S2P', 'S2W', 'S2Y', 'S2M', 'S2N', 'S2R']}],
                             ['G', 'L5', {'C5': ['C5', 'C5I', 'C5Q', 'C5X']},
                              {'L5': ['L5', 'L5I', 'L5Q', 'L5X']},
                              {'D5': ['D5', 'D5I', 'D5Q', 'D5X']},
                              {'S5': ['S5', 'S5I', 'S5Q', 'S5X']}],
                             ['R', 'G1', {'C1': ['C1', 'CA', 'P1', 'C1C', 'C1P']},
                              {'L1': ['L1', 'LA', 'L1C', 'L1P']},
                              {'D1': ['D1', 'DA', 'D1C', 'D1P']},
                              {'S1': ['S1', 'SA', 'S1C', 'S1P']}],
                             ['R', 'G1a', {'C4': ['C4A', 'C4B', 'C4X']},
                              {'L4': ['L4A', 'L4B', 'L4X']},
                              {'D4': ['D4A', 'D4B', 'D4X']},
                              {'S4': ['S4A', 'S4B', 'S4X']}],
                             ['R', 'G2', {'C2': ['C2', 'CD', 'P2', 'C2C', 'C2P']},
                              {'L2': ['L2', 'LD', 'L2C', 'L2P']},
                              {'D2': ['D2', 'DD', 'D2C', 'D2P']},
                              {'S2': ['S2', 'SD', 'S2C', 'S2P']}],
                             ['R', 'G2a', {'C6': ['C6A', 'C6B', 'C6X']},
                              {'L6': ['L6A', 'L6B', 'L6X']},
                              {'D6': ['D6A', 'D6B', 'D6X']},
                              {'S6': ['S6A', 'S6B', 'S6X']}],
                             ['R', 'G3', {'C3': ['C3I', 'C3Q', 'C3X']},
                              {'L3': ['L3I', 'L3Q', 'L3X']},
                              {'D3': ['D3I', 'D3Q', 'D3X']},
                              {'S3': ['S3I', 'S3Q', 'S3X']}],
                             ['E', 'E1', {'C1': ['C1', 'C1A', 'C1B', 'C1C', 'C1X', 'C1Z']},
                              {'L1': ['L1', 'L1A', 'L1B', 'L1C', 'L1X', 'L1Z']},
                              {'D1': ['D1', 'D1A', 'D1B', 'D1C', 'D1X', 'D1Z']},
                              {'S1': ['S1', 'S1A', 'S1B', 'S1C', 'S1X', 'S1Z']}],
                             ['E', 'E5a', {'C5': ['C5', 'C5I', 'C5Q', 'C5X']},
                              {'L5': ['L5', 'L5I', 'L5Q', 'L5X']},
                              {'D5': ['D5', 'D5I', 'D5Q', 'D5X']},
                              {'S5': ['S5', 'S5I', 'S5Q', 'S5X']}],
                             ['E', 'E5b', {'C7': ['C7', 'C7I', 'C7Q', 'C7X']},
                              {'L7': ['L7', 'L7I', 'L7Q', 'L7X']},
                              {'D7': ['D7', 'D7I', 'D7Q', 'D7X']},
                              {'S7': ['S7', 'S7I', 'S7Q', 'S7X']}],
                             ['E', 'E5ab', {'C8': ['C8', 'C8I', 'C8Q', 'C8X']},
                              {'L8': ['L8', 'L8I', 'L8Q', 'L8X']},
                              {'D8': ['D8', 'D8I', 'D8Q', 'D8X']},
                              {'S8': ['S8', 'S8I', 'S8Q', 'S8X']}],
                             ['E', 'E6', {'C6': ['C6', 'C6A', 'C6B', 'C6C', 'C6X', 'C6Z']},
                              {'L6': ['L6', 'L6A', 'L6B', 'L6C', 'L6X', 'L6Z']},
                              {'D6': ['D6', 'D6A', 'D6B', 'D6C', 'D6X', 'D6Z']},
                              {'S6': ['S6', 'S6A', 'S6B', 'S6C', 'S6X', 'S6Z']}],
                             ['C', 'B1', {'C2': ['C2', 'C2I', 'C2Q', 'C2X']},
                              {'L2': ['L2', 'L2I', 'L2Q', 'L2X']},
                              {'D2': ['D2', 'D2I', 'D2Q', 'D2X']},
                              {'S2': ['S2', 'S2I', 'S2Q', 'S2X']}],
                             ['C', 'B1C', {'C1': ['C1D', 'C1P', 'C1X']},
                              {'L1': ['L1D', 'L1P', 'L1X']},
                              {'D1': ['D1D', 'D1P', 'D1X']},
                              {'S1': ['S1D', 'S1P', 'S1X']}],
                             ['C', 'B1A', {'C1': ['C1S', 'C1L', 'C1Z']},
                              {'L1': ['L1S', 'L1L', 'L1Z']},
                              {'D1': ['D1S', 'D1L', 'D1Z']},
                              {'S1': ['S1S', 'S1L', 'S1Z']}],
                             ['C', 'B2a', {'C5': ['C5D', 'C5P', 'C5X']},
                              {'L5': ['L5D', 'L5P', 'L5X']},
                              {'D5': ['D5D', 'D5P', 'D5X']},
                              {'S5': ['S5D', 'S5P', 'S5X']}],
                             ['C', 'B2', {'C7': ['C7', 'C7I', 'C7Q', 'C7X']},
                              {'L7': ['L7', 'L7I', 'L7Q', 'L7X']},
                              {'D7': ['D7', 'D7I', 'D7Q', 'D7X']},
                              {'S7': ['S7', 'S7I', 'S7Q', 'S7X']}],
                             ['C', 'B2b', {'C7': ['C7D', 'C7P', 'C7Z']},
                              {'L7': ['L7D', 'L7P', 'L7Z']},
                              {'D7': ['D7D', 'D7P', 'D7Z']},
                              {'S7': ['S7D', 'S7P', 'S7Z']}],
                             ['C', 'B2ab', {'C8': ['C8D', 'C8P', 'C8X']},
                              {'L8': ['L8D', 'L8P', 'L8X']},
                              {'D8': ['D8D', 'D8P', 'D8X']},
                              {'S8': ['S8D', 'S8P', 'S8X']}],
                             ['C', 'B3', {'C6': ['C6', 'C6I', 'C6Q', 'C6X']},
                              {'L6': ['L6', 'L6I', 'L6Q', 'L6X']},
                              {'D6': ['D6', 'D6I', 'D6Q', 'D6X']},
                              {'S6': ['S6', 'S6I', 'S6Q', 'S6X']}],
                             ['C', 'B3A', {'C6': ['C6D', 'C6P', 'C6Z']},
                              {'L6': ['L6D', 'L6P', 'L6Z']},
                              {'D6': ['D6D', 'D6P', 'D6Z']},
                              {'S6': ['S6D', 'S6P', 'S6Z']}],
                             ['J', 'L1', {'C1': ['C1C', 'C1E', 'C1S', 'C1L', 'C1X', 'C1Z', 'C1B']},
                              {'L1': ['L1C', 'L1E', 'L1S', 'L1L', 'L1X', 'L1Z', 'L1B']},
                              {'D1': ['D1C', 'D1E', 'D1S', 'D1L', 'D1X', 'D1Z', 'D1B']},
                              {'S1': ['S1C', 'S1E', 'S1S', 'S1L', 'S1X', 'S1Z', 'S1B']}],
                             ['J', 'L2', {'C2': ['C2S', 'C2L', 'C2X']},
                              {'L2': ['L2S', 'L2L', 'L2X']},
                              {'D2': ['D2S', 'D2L', 'D2X']},
                              {'S2': ['S2S', 'S2L', 'S2X']}],
                             ['J', 'L5', {'C5': ['C5I', 'C5Q', 'C5X', 'C5D', 'C5P', 'C5Z']},
                              {'L5': ['L5I', 'L5Q', 'L5X', 'C5D', 'C5P', 'C5Z']},
                              {'D5': ['D5I', 'D5Q', 'D5X', 'C5D', 'C5P', 'C5Z']},
                              {'S5': ['S5I', 'S5Q', 'S5X', 'C5D', 'C5P', 'C5Z']}],
                             ['J', 'L6', {'C6': ['C6S', 'C6L', 'C6X', 'C6E', 'C6Z']},
                              {'L6': ['L6S', 'L6L', 'L6X', 'L6E', 'L6Z']},
                              {'D6': ['D6S', 'D6L', 'D6X', 'D6E', 'D6Z']},
                              {'S6': ['S6S', 'S6L', 'S6X', 'S6E', 'S6Z']}],
                             ['I', 'L5', {'C5': ['C5A', 'C5B', 'C5C', 'C5X']},
                                         {'L5': ['L5A', 'L5B', 'L5C', 'C5X']},
                                         {'D5': ['D5A', 'D5B', 'D5C', 'C5X']},
                                         {'S5': ['S5A', 'S5B', 'S5C', 'C5X']}],
                             ['I', 'S', {'C9': ['C9A', 'C9B', 'C9C', 'C9X']},
                                        {'L9': ['L9A', 'L9B', 'L9C', 'C9X']},
                                        {'D9': ['D9A', 'D9B', 'D9C', 'C9X']},
                                        {'S9': ['S9A', 'S9B', 'S9C', 'C9X']}],
                             ['I', 'L1', {'C1': ['C1D', 'C1P', 'C1X']},
                                        {'L1': ['L1D', 'L1P', 'L1X']},
                                        {'D1': ['D1D', 'D1P', 'D1X']},
                                        {'S1': ['S1D', 'S1P', 'S1X']}],
                             ['S', 'L1', {'C1': ['C1', 'C1C']},
                              {'L1': ['L1', 'L1C']},
                              {'D1': ['D1', 'D1C']},
                              {'S1': ['S1', 'S1C']}],
                             ['S', 'L5', {'C5': ['C5', 'C5I', 'C5Q', 'C5X']},
                              {'L5': ['L5', 'L5I', 'L5Q', 'L5X']},
                              {'D5': ['D5', 'D5I', 'D5Q', 'D5X']},
                              {'S5': ['S5', 'S5I', 'S5Q', 'S5X']}]
                             ]
        if self.RINEX_version == '3.02':
            self.Channel_Code_list[13] = ['C', 'B1', {'C1': ['C1I', 'C1Q', 'C1X']},
                                                     {'L1': ['L1I', 'L1Q', 'L1X']},
                                                     {'D1': ['D1I', 'D1Q', 'D1X']},
                                                     {'S1': ['S1I', 'S1Q', 'S1X']}]

        # GPS
        self.G_listCheckBox = ["C1", "L1", "D1", "S1",
                               "C2", "L2", "D2", "S2",
                               "C5", "L5", "D5", "S5"]
        # GLONASS
        self.R_listCheckBox = ["C1", "L1", "D1", "S1",
                               "C4", "L4", "D4", "S4",
                               "C2", "L2", "D2", "S2",
                               "C6", "L6", "D6", "S6",
                               "C3", "L3", "D3", "S3"]
        # BDS
        if self.RINEX_version != '3.02':
            self.C_listCheckBox = ["C2", "L2", "D2", "S2",
                                   "C1", "L1", "D1", "S1",
                                   "C1", "L1", "D1", "S1",
                                   "C5", "L5", "D5", "S5",
                                   "C7", "L7", "D7", "S7",
                                   "C7", "L7", "D7", "S7",
                                   "C8", "L8", "D8", "S8",
                                   "C6", "L6", "D6", "S6",
                                   "C6", "L6", "D6", "S6"]
        else:
            self.C_listCheckBox = ["C1", "L1", "D1", "S1",
                                   "C1 ", "L1 ", "D1 ", "S1 ",
                                   "C1 ", "L1 ", "D1 ", "S1 ",
                                   "C5", "L5", "D5", "S5",
                                   "C7", "L7", "D7", "S7",
                                   "C7 ", "L7 ", "D7 ", "S7 ",
                                   "C8", "L8", "D8", "S8",
                                   "C6", "L6", "D6", "S6",
                                   "C6 ", "L6 ", "D6 ", "S6 "]
        # Galileo
        self.E_listCheckBox = ["C1", "L1", "D1", "S1",
                               "C5", "L5", "D5", "S5",
                               "C7", "L7", "D7", "S7",
                               "C8", "L8", "D8", "S8",
                               "C6", "L6", "D6", "S6"]
        # QZSS
        self.J_listCheckBox = ["C1", "L1", "D1", "S1",
                               "C2", "L2", "D2", "S2",
                               "C5", "L5", "D5", "S5",
                               "C6", "L6", "D6", "S6"]
        # IRNSS
        self.I_listCheckBox = ["C5", "L5", "D5", "S5",
                               "C9", "L9", "D9", "S9",
                               "C1", "L1", "D1", "S1"]
        # SBAS
        self.S_listCheckBox = ["C1", "L1", "D1", "S1",
                               "C5", "L5", "D5", "S5"]

        grid = QGridLayout()
        self.G_label = QLabel("GPS")
        grid.addWidget(self.G_label, 0, 0)
        self.G_Pseudorange = QCheckBox("Code")
        self.G_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_Pseudorange.stateChanged.connect(self.G_Pseudorange_function)
        grid.addWidget(self.G_Pseudorange, 0, 1)
        self.G_phase = QCheckBox("Phase")
        self.G_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_phase.stateChanged.connect(self.G_phase_function)
        grid.addWidget(self.G_phase, 0, 2)
        self.G_MP = QCheckBox("Doppler")
        self.G_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_MP.stateChanged.connect(self.G_MP_function)
        grid.addWidget(self.G_MP, 0, 3)
        self.G_SN = QCheckBox("Signal")
        self.G_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_SN.stateChanged.connect(self.G_SN_function)
        grid.addWidget(self.G_SN, 0, 4)

        self.G_L1 = QCheckBox("L1")
        self.G_L1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_L1.stateChanged.connect(self.G_L1_function)
        grid.addWidget(self.G_L1, 1, 0)
        self.G_L2 = QCheckBox("L2")
        self.G_L2.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_L2.stateChanged.connect(self.G_L2_function)
        grid.addWidget(self.G_L2, 2, 0)
        self.G_L5 = QCheckBox("L5")
        self.G_L5.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.G_L5.stateChanged.connect(self.G_L5_function)
        grid.addWidget(self.G_L5, 3, 0)

        # self.allowed_select_obscode_list = [['G', 'C1C', 'L1C', 'D1C', 'S1C', 'L1S', 'S1M', 'L2D', 'C5I'],
        #                                     ['R', 'C2P', 'L2P', 'D2P', 'S2P', 'C2C', 'D1P'],
        #                                     ['C', 'C1D', 'L1D', 'D1D', 'C7I', 'L7I', 'L7D']]
        # self.selected_obscode_list = [['G', 'C1C', 'L1C', 'L1S', 'S1M', 'L2D', 'C5I'],
        #                               ['R', 'C2P', 'S2P', 'C2C', 'D1P'],
        #                               ['C', 'C1D', 'L1D', 'D1D', 'C7I', 'L7I', 'L7D']]

        converd_allowed_select_obscode_list = []
        for sys_code in self.allowed_select_obscode_list:
            temp_list = [sys_code[0]]
            for code in sys_code[1:]:
                for search_Channel_Code_list in self.Channel_Code_list:
                    if sys_code[0] == search_Channel_Code_list[0]:
                        for freq_code_library in search_Channel_Code_list[2:]:
                            if code in list(freq_code_library.values())[0]:
                                add_freq_band = list(freq_code_library.keys())[0]
                                temp_list.append(add_freq_band)
                                break
            converd_allowed_select_obscode_list.append(temp_list)

        converd_selected_obscode_list = []
        for sys_code in self.selected_obscode_list:
            temp_list = [sys_code[0]]
            for code in sys_code[1:]:
                for search_Channel_Code_list in self.Channel_Code_list:
                    if sys_code[0] == search_Channel_Code_list[0]:
                        for freq_code_library in search_Channel_Code_list[2:]:
                            if code in list(freq_code_library.values())[0]:
                                add_freq_band = list(freq_code_library.keys())[0]
                                temp_list.append(add_freq_band)
                                break
            converd_selected_obscode_list.append(temp_list)

        for i1, v1 in enumerate(self.G_listCheckBox):
            self.G_listCheckBox[i1] = QCheckBox(v1)
            self.G_listCheckBox[i1].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.G_listCheckBox[i1], int(i1 / 4 + 1), int(i1 % 4 + 1))
            self.G_listCheckBox[i1].setCheckable(False)
            self.G_listCheckBox[i1].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'G':
                    if v1 in sys_code:
                        self.G_listCheckBox[i1].setCheckable(True)
                        self.G_listCheckBox[i1].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'G':
                    if v1 in sys_code:
                        self.G_listCheckBox[i1].setChecked(True)

        self.R_label = QLabel("GLO")
        grid.addWidget(self.R_label, 0, 5)
        self.R_Pseudorange = QCheckBox("Code")
        self.R_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_Pseudorange.stateChanged.connect(self.R_Pseudorange_function)
        grid.addWidget(self.R_Pseudorange, 0, 6)
        self.R_phase = QCheckBox("Phase")
        self.R_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_phase.stateChanged.connect(self.R_phase_function)
        grid.addWidget(self.R_phase, 0, 7)
        self.R_MP = QCheckBox("Doppler")
        self.R_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_MP.stateChanged.connect(self.R_MP_function)
        grid.addWidget(self.R_MP, 0, 8)
        self.R_SN = QCheckBox("Signal")
        self.R_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_SN.stateChanged.connect(self.R_SN_function)
        grid.addWidget(self.R_SN, 0, 9)

        self.R_G1 = QCheckBox("G1")
        self.R_G1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_G1.stateChanged.connect(self.R_G1_function)
        grid.addWidget(self.R_G1, 1, 5)
        self.R_G1a = QCheckBox("G1a")
        self.R_G1a.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_G1a.stateChanged.connect(self.R_G1a_function)
        grid.addWidget(self.R_G1a, 2, 5)
        self.R_G2 = QCheckBox("G2")
        self.R_G2.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_G2.stateChanged.connect(self.R_G2_function)
        grid.addWidget(self.R_G2, 3, 5)
        self.R_G2a = QCheckBox("G2a")
        self.R_G2a.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_G2a.stateChanged.connect(self.R_G2a_function)
        grid.addWidget(self.R_G2a, 4, 5)
        self.R_G3 = QCheckBox("G3")
        self.R_G3.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.R_G3.stateChanged.connect(self.R_G3_function)
        grid.addWidget(self.R_G3, 5, 5)

        for i2, v2 in enumerate(self.R_listCheckBox):
            self.R_listCheckBox[i2] = QCheckBox(v2)
            self.R_listCheckBox[i2].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.R_listCheckBox[i2], int(i2 / 4 + 1), int(i2 % 4 + 6))
            self.R_listCheckBox[i2].setCheckable(False)
            self.R_listCheckBox[i2].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'R':
                    if v2 in sys_code:
                        self.R_listCheckBox[i2].setCheckable(True)
                        self.R_listCheckBox[i2].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'R':
                    if v2 in sys_code:
                        self.R_listCheckBox[i2].setChecked(True)

        self.C_label = QLabel("BDS")
        grid.addWidget(self.C_label, 6, 0)
        self.C_Pseudorange = QCheckBox("Code")
        self.C_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_Pseudorange.stateChanged.connect(self.C_Pseudorange_function)
        grid.addWidget(self.C_Pseudorange, 6, 1)
        self.C_phase = QCheckBox("Phase")
        self.C_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_phase.stateChanged.connect(self.C_phase_function)
        grid.addWidget(self.C_phase, 6, 2)
        self.C_MP = QCheckBox("Doppler")
        self.C_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_MP.stateChanged.connect(self.C_MP_function)
        grid.addWidget(self.C_MP, 6, 3)
        self.C_SN = QCheckBox("Signal")
        self.C_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_SN.stateChanged.connect(self.C_SN_function)
        grid.addWidget(self.C_SN, 6, 4)

        self.C_B1 = QCheckBox("B1I")
        self.C_B1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B1.stateChanged.connect(self.C_B1_function)
        grid.addWidget(self.C_B1, 7, 0)
        self.C_B1C = QCheckBox("B1C")
        self.C_B1C.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B1C.stateChanged.connect(self.C_B1C_function)
        grid.addWidget(self.C_B1C, 8, 0)
        self.C_B1A = QCheckBox("B1A")
        self.C_B1A.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B1A.stateChanged.connect(self.C_B1A_function)
        grid.addWidget(self.C_B1A, 9, 0)
        self.C_B2a = QCheckBox("B2a")
        self.C_B2a.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B2a.stateChanged.connect(self.C_B2a_function)
        grid.addWidget(self.C_B2a, 10, 0)
        self.C_B2 = QCheckBox("B2I")
        self.C_B2.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B2.stateChanged.connect(self.C_B2_function)
        grid.addWidget(self.C_B2, 11, 0)
        self.C_B2b = QCheckBox("B2b")
        self.C_B2b.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B2b.stateChanged.connect(self.C_B2b_function)
        grid.addWidget(self.C_B2b, 12, 0)
        self.C_B2ab = QCheckBox("B2ab")
        self.C_B2ab.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B2ab.stateChanged.connect(self.C_B2ab_function)
        grid.addWidget(self.C_B2ab, 13, 0)
        self.C_B3 = QCheckBox("B3I")
        self.C_B3.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B3.stateChanged.connect(self.C_B3_function)
        grid.addWidget(self.C_B3, 14, 0)
        self.C_B3A = QCheckBox("B3A")
        self.C_B3A.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.C_B3A.stateChanged.connect(self.C_B3A_function)
        grid.addWidget(self.C_B3A, 15, 0)

        for i3, v3 in enumerate(self.C_listCheckBox):
            self.C_listCheckBox[i3] = QCheckBox(v3)
            self.C_listCheckBox[i3].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.C_listCheckBox[i3], int(i3 / 4 + 7), int(i3 % 4 + 1))
            self.C_listCheckBox[i3].setCheckable(False)
            self.C_listCheckBox[i3].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'C':
                    if v3 in sys_code:
                        self.C_listCheckBox[i3].setCheckable(True)
                        self.C_listCheckBox[i3].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'C':
                    if v3 in sys_code:
                        self.C_listCheckBox[i3].setChecked(True)

        self.E_label = QLabel("GAL")
        grid.addWidget(self.E_label, 6, 5)
        self.E_Pseudorange = QCheckBox("Code")
        self.E_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_Pseudorange.stateChanged.connect(self.E_Pseudorange_function)
        grid.addWidget(self.E_Pseudorange, 6, 6)
        self.E_phase = QCheckBox("Phase")
        self.E_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_phase.stateChanged.connect(self.E_phase_function)
        grid.addWidget(self.E_phase, 6, 7)
        self.E_MP = QCheckBox("Doppler")
        self.E_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_MP.stateChanged.connect(self.E_MP_function)
        grid.addWidget(self.E_MP, 6, 8)
        self.E_SN = QCheckBox("Signal")
        self.E_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_SN.stateChanged.connect(self.E_SN_function)
        grid.addWidget(self.E_SN, 6, 9)

        self.E_E1 = QCheckBox("E1")
        self.E_E1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_E1.stateChanged.connect(self.E_E1_function)
        grid.addWidget(self.E_E1, 7, 5)
        self.E_E5a = QCheckBox("E5a")
        self.E_E5a.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_E5a.stateChanged.connect(self.E_E5a_function)
        grid.addWidget(self.E_E5a, 8, 5)
        self.E_E5b = QCheckBox("E5b")
        self.E_E5b.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_E5b.stateChanged.connect(self.E_E5b_function)
        grid.addWidget(self.E_E5b, 9, 5)
        self.E_E5ab = QCheckBox("E5ab")
        self.E_E5ab.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_E5ab.stateChanged.connect(self.E_E5ab_function)
        grid.addWidget(self.E_E5ab, 10, 5)
        self.E_E6 = QCheckBox("E6")
        self.E_E6.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.E_E6.stateChanged.connect(self.E_E6_function)
        grid.addWidget(self.E_E6, 11, 5)

        for i4, v4 in enumerate(self.E_listCheckBox):
            self.E_listCheckBox[i4] = QCheckBox(v4)
            self.E_listCheckBox[i4].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.E_listCheckBox[i4], int(i4 / 4 + 7), (i4 % 4 + 6))
            self.E_listCheckBox[i4].setCheckable(False)
            self.E_listCheckBox[i4].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'E':
                    if v4 in sys_code:
                        self.E_listCheckBox[i4].setCheckable(True)
                        self.E_listCheckBox[i4].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'E':
                    if v4 in sys_code:
                        self.E_listCheckBox[i4].setChecked(True)

        self.J_label = QLabel("QZS")
        grid.addWidget(self.J_label, 16, 0)
        self.J_Pseudorange = QCheckBox("Code")
        self.J_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_Pseudorange.stateChanged.connect(self.J_Pseudorange_function)
        grid.addWidget(self.J_Pseudorange, 16, 1)
        self.J_phase = QCheckBox("Phase")
        self.J_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_phase.stateChanged.connect(self.J_phase_function)
        grid.addWidget(self.J_phase, 16, 2)
        self.J_MP = QCheckBox("Doppler")
        self.J_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_MP.stateChanged.connect(self.J_MP_function)
        grid.addWidget(self.J_MP, 16, 3)
        self.J_SN = QCheckBox("Signal")
        self.J_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_SN.stateChanged.connect(self.J_SN_function)
        grid.addWidget(self.J_SN, 16, 4)

        self.J_L1 = QCheckBox("L1")
        self.J_L1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_L1.stateChanged.connect(self.J_L1_function)
        grid.addWidget(self.J_L1, 17, 0)
        self.J_L2 = QCheckBox("L2")
        self.J_L2.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_L2.stateChanged.connect(self.J_L2_function)
        grid.addWidget(self.J_L2, 18, 0)
        self.J_L5 = QCheckBox("L5")
        self.J_L5.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_L5.stateChanged.connect(self.J_L5_function)
        grid.addWidget(self.J_L5, 19, 0)
        self.J_L6 = QCheckBox("L6")
        self.J_L6.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.J_L6.stateChanged.connect(self.J_L6_function)
        grid.addWidget(self.J_L6, 20, 0)

        for i5, v5 in enumerate(self.J_listCheckBox):
            self.J_listCheckBox[i5] = QCheckBox(v5)
            self.J_listCheckBox[i5].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.J_listCheckBox[i5], int(i5 / 4 + 17), (i5 % 4 + 1))
            self.J_listCheckBox[i5].setCheckable(False)
            self.J_listCheckBox[i5].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'J':
                    if v5 in sys_code:
                        self.J_listCheckBox[i5].setCheckable(True)
                        self.J_listCheckBox[i5].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'J':
                    if v5 in sys_code:
                        self.J_listCheckBox[i5].setChecked(True)

        self.I_label = QLabel('NavIC')
        grid.addWidget(self.I_label, 16, 5)
        self.I_Pseudorange = QCheckBox("Code")
        self.I_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_Pseudorange.stateChanged.connect(self.I_Pseudorange_function)
        grid.addWidget(self.I_Pseudorange, 16, 6)
        self.I_phase = QCheckBox("Phase")
        self.I_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_phase.stateChanged.connect(self.I_phase_function)
        grid.addWidget(self.I_phase, 16, 7)
        self.I_MP = QCheckBox("Doppler")
        self.I_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_MP.stateChanged.connect(self.I_MP_function)
        grid.addWidget(self.I_MP, 16, 8)
        self.I_SN = QCheckBox("Signal")
        self.I_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_SN.stateChanged.connect(self.I_SN_function)
        grid.addWidget(self.I_SN, 16, 9)

        self.I_L5 = QCheckBox("L5")
        self.I_L5.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_L5.stateChanged.connect(self.I_L5_function)
        grid.addWidget(self.I_L5, 17, 5)
        self.I_S = QCheckBox("S")
        self.I_S.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_S.stateChanged.connect(self.I_S_function)
        grid.addWidget(self.I_S, 18, 5)

        self.I_L1 = QCheckBox("L1")
        self.I_L1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.I_L1.stateChanged.connect(self.I_L1_function)
        grid.addWidget(self.I_L1, 19, 5)

        for i6, v6 in enumerate(self.I_listCheckBox):
            self.I_listCheckBox[i6] = QCheckBox(v6)
            self.I_listCheckBox[i6].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.I_listCheckBox[i6], int(i6 / 4 + 17), (i6 % 4 + 6))
            self.I_listCheckBox[i6].setCheckable(False)
            self.I_listCheckBox[i6].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'I':
                    if v6 in sys_code:
                        self.I_listCheckBox[i6].setCheckable(True)
                        self.I_listCheckBox[i6].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'I':
                    if v6 in sys_code:
                        self.I_listCheckBox[i6].setChecked(True)

        self.S_label = QLabel("SBS")
        grid.addWidget(self.S_label, 21, 0)
        self.S_Pseudorange = QCheckBox("Code")
        self.S_Pseudorange.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.S_Pseudorange.stateChanged.connect(self.S_Pseudorange_function)
        grid.addWidget(self.S_Pseudorange, 21, 1)
        self.S_phase = QCheckBox("Phase")
        self.S_phase.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.S_phase.stateChanged.connect(self.S_phase_function)
        grid.addWidget(self.S_phase, 21, 2)
        self.S_MP = QCheckBox("Doppler")
        self.S_MP.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.S_MP.stateChanged.connect(self.S_MP_function)
        grid.addWidget(self.S_MP, 21, 3)
        self.S_SN = QCheckBox("Signal")
        self.S_SN.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.S_SN.stateChanged.connect(self.S_SN_function)
        grid.addWidget(self.S_SN, 21, 4)

        self.S_L1 = QCheckBox("L1")
        self.S_L1.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.S_L1.stateChanged.connect(self.S_L1_function)
        grid.addWidget(self.S_L1, 22, 0)
        self.S_L5 = QCheckBox("L5")
        self.S_L5.setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
        self.S_L5.stateChanged.connect(self.S_L5_function)
        grid.addWidget(self.S_L5, 23, 0)

        for i7, v7 in enumerate(self.S_listCheckBox):
            self.S_listCheckBox[i7] = QCheckBox(v7)
            self.S_listCheckBox[i7].setStyleSheet("QCheckBox::indicator { width: 30px;height: 15px; }")
            grid.addWidget(self.S_listCheckBox[i7], int(i7 / 4 + 22), (i7 % 4 + 1))
            self.S_listCheckBox[i7].setCheckable(False)
            self.S_listCheckBox[i7].setEnabled(False)
            for sys_code in converd_allowed_select_obscode_list:
                if sys_code[0] == 'S':
                    if v7 in sys_code:
                        self.S_listCheckBox[i7].setCheckable(True)
                        self.S_listCheckBox[i7].setEnabled(True)
            for sys_code in converd_selected_obscode_list:
                if sys_code[0] == 'S':
                    if v7 in sys_code:
                        self.S_listCheckBox[i7].setChecked(True)

        band_wg = QFrame()
        band_wg.setFrameShape(QFrame.Box)
        # frame_wg.setStyleSheet('border:1px solid #5F92B2;border-radius:5px;')
        band_wg.setLayout(grid)


        bnt_box = QHBoxLayout()
        self.global_button = QPushButton("Set All", self)
        self.global_button.clicked.connect(self.total_global)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_global)
        self.sure_button = QPushButton("OK", self)
        self.sure_button.clicked.connect(self.sure_function)
        blank_space_label = QLabel("")

        spacerItem_V = QSpacerItem(1, 2, QSizePolicy.Minimum, QSizePolicy.Expanding)
        bnt_box.addItem(spacerItem_V)
        bnt_box.addWidget(blank_space_label)
        bnt_box.addWidget(blank_space_label)
        bnt_box.addWidget(blank_space_label)
        bnt_box.addWidget(self.global_button)
        bnt_box.addWidget(self.cancel_button)
        bnt_box.addWidget(self.sure_button)

        bnt_wg = QFrame()
        bnt_wg.setLayout(bnt_box)

        main_box = QVBoxLayout()
        main_box.addWidget(band_wg)
        main_box.addWidget(bnt_wg)

        self.setLayout(main_box)


    # ok
    def sure_function(self):
        choice_G = []
        for i1, v1 in enumerate(self.G_listCheckBox):
            if self.G_listCheckBox[i1].isChecked() == True:
                choice_G.append(self.G_listCheckBox[i1].text())
        if len(choice_G) == 0:
            z_choice_G_str = ''
        else:
            choice_G_str = ','.join(choice_G)
            z_choice_G_str = 'G:' + choice_G_str + '+'
        # print(z_choice_G_str)

        choice_R = []
        for i2, v2 in enumerate(self.R_listCheckBox):
            if self.R_listCheckBox[i2].isChecked() == True:
                choice_R.append(self.R_listCheckBox[i2].text())
        if len(choice_R) == 0:
            z_choice_R_str = ''
        else:
            choice_R_str = ','.join(choice_R)
            z_choice_R_str = 'R:' + choice_R_str + '+'
        # print(z_choice_R_str)

        choice_C = []
        for i3, v3 in enumerate(self.C_listCheckBox):
            if self.C_listCheckBox[i3].isChecked() == True:
                choice_C.append(self.C_listCheckBox[i3].text())
        if len(choice_C) == 0:
            z_choice_C_str = ''
        else:
            choice_C_str = ','.join(choice_C)
            z_choice_C_str = 'C:' + choice_C_str + '+'
        # print(z_choice_C_str)

        choice_E = []
        for i4, v4 in enumerate(self.E_listCheckBox):
            if self.E_listCheckBox[i4].isChecked() == True:
                choice_E.append(self.E_listCheckBox[i4].text())
        if len(choice_E) == 0:
            z_choice_E_str = ''
        else:
            choice_E_str = ','.join(choice_E)
            z_choice_E_str = 'E:' + choice_E_str + '+'
        # print(z_choice_E_str)

        choice_J = []
        for i5, v5 in enumerate(self.J_listCheckBox):
            if self.J_listCheckBox[i5].isChecked() == True:
                choice_J.append(self.J_listCheckBox[i5].text())
        if len(choice_J) == 0:
            z_choice_J_str = ''
        else:
            choice_J_str = ','.join(choice_J)
            z_choice_J_str = 'J:' + choice_J_str + '+'
        # print(z_choice_J_str)

        choice_I = []
        for i6, v6 in enumerate(self.I_listCheckBox):
            if self.I_listCheckBox[i6].isChecked() == True:
                choice_I.append(self.I_listCheckBox[i6].text())
        if len(choice_I) == 0:
            z_choice_I_str = ''
        else:
            choice_I_str = ','.join(choice_I)
            z_choice_I_str = 'I:' + choice_I_str + '+'
        # print(z_choice_I_str)

        choice_S = []
        for i7, v7 in enumerate(self.S_listCheckBox):
            if self.S_listCheckBox[i7].isChecked() == True:
                choice_I.append(self.S_listCheckBox[i7].text())
        if len(choice_S) == 0:
            z_choice_S_str = ''
        else:
            choice_S_str = ','.join(choice_S)
            z_choice_S_str = 'S:' + choice_S_str + '+'
        # print(z_choice_S_str)

        choice_all_str = z_choice_G_str + z_choice_R_str + z_choice_C_str + z_choice_E_str + z_choice_J_str + z_choice_I_str + z_choice_S_str
        z_choice_all_str = choice_all_str.strip('+')
        z_choice_all_list = []
        if z_choice_all_str != '':
            for sys_code_text in z_choice_all_str.split('+'):
                code_list = sys_code_text[2:].split(',')
                code_list.insert(0, sys_code_text[0])
                z_choice_all_list.append(code_list)
        print(z_choice_all_list) # [['R', 'S2'], ['C', 'D1', 'C1']]

        # self.selected_obscode_list = [['G', 'C1C', 'L1C', 'L1S', 'S1M', 'L2D', 'C5I'],
        #                               ['R', 'C2P', 'S2P', 'C2C', 'D1P'],
        #                               ['C', 'C1D', 'L1D', 'D1D', 'C7I', 'L7I', 'L7D']]
        output_sys_code_list = []
        for sys_code_list in z_choice_all_list:
            temp_list = []
            temp_list.append(sys_code_list[0])
            for search_sys_code_list in self.Channel_Code_list:
                if sys_code_list[0] == search_sys_code_list[0]:
                    for search_dic in search_sys_code_list[2:]:
                        for ferq_band in sys_code_list[1:]:
                            if ferq_band == list(search_dic.keys())[0]:
                                for initial_sys_code_list in self.allowed_select_obscode_list:
                                    if initial_sys_code_list[0] == sys_code_list[0]:
                                        for initial_code in initial_sys_code_list[1:]:
                                            if initial_code in list(search_dic.values())[0]:
                                                if initial_code not in temp_list:
                                                    temp_list.append(initial_code)
            output_sys_code_list.append(temp_list)
        # print(output_sys_code_list)
        self.mySignal.emit(output_sys_code_list)
        self.hide()
        return output_sys_code_list


    # G
    def G_global(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if self.G_all.isChecked() == True:
                self.G_listCheckBox[i1].setChecked(True)
            elif self.G_all.isChecked() == False:
                self.G_listCheckBox[i1].setChecked(False)

    def G_Pseudorange_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_Pseudorange.isChecked() == True) & (int(i1 % 4 + 1) == 1):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_Pseudorange.isChecked() == False) & (int(i1 % 4 + 1) == 1):
                self.G_listCheckBox[i1].setChecked(False)

    def G_phase_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_phase.isChecked() == True) & (int(i1 % 4 + 1) == 2):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_phase.isChecked() == False) & (int(i1 % 4 + 1) == 2):
                self.G_listCheckBox[i1].setChecked(False)

    def G_MP_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_MP.isChecked() == True) & (int(i1 % 4 + 1) == 3):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_MP.isChecked() == False) & (int(i1 % 4 + 1) == 3):
                self.G_listCheckBox[i1].setChecked(False)

    def G_SN_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_SN.isChecked() == True) & (int(i1 % 4 + 1) == 4):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_SN.isChecked() == False) & (int(i1 % 4 + 1) == 4):
                self.G_listCheckBox[i1].setChecked(False)

    def G_L1_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_L1.isChecked() == True) & (int(i1 / 4 + 1) == 1):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_L1.isChecked() == False) & (int(i1 / 4 + 1) == 1):
                self.G_listCheckBox[i1].setChecked(False)

    def G_L2_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_L2.isChecked() == True) & (int(i1 / 4 + 1) == 2):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_L2.isChecked() == False) & (int(i1 / 4 + 1) == 2):
                self.G_listCheckBox[i1].setChecked(False)

    def G_L5_function(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            if (self.G_L5.isChecked() == True) & (int(i1 / 4 + 1) == 3):
                self.G_listCheckBox[i1].setChecked(True)
            elif (self.G_L5.isChecked() == False) & (int(i1 / 4 + 1) == 3):
                self.G_listCheckBox[i1].setChecked(False)

    # R
    def R_global(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if self.R_all.isChecked() == True:
                self.R_listCheckBox[i2].setChecked(True)
            elif self.R_all.isChecked() == False:
                self.R_listCheckBox[i2].setChecked(False)

    def R_Pseudorange_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_Pseudorange.isChecked() == True) & (int(i2 % 4 + 1) == 1):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_Pseudorange.isChecked() == False) & (int(i2 % 4 + 1) == 1):
                self.R_listCheckBox[i2].setChecked(False)

    def R_phase_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_phase.isChecked() == True) & (int(i2 % 4 + 1) == 2):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_phase.isChecked() == False) & (int(i2 % 4 + 1) == 2):
                self.R_listCheckBox[i2].setChecked(False)

    def R_MP_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_MP.isChecked() == True) & (int(i2 % 4 + 1) == 3):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_MP.isChecked() == False) & (int(i2 % 4 + 1) == 3):
                self.R_listCheckBox[i2].setChecked(False)

    def R_SN_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_SN.isChecked() == True) & (int(i2 % 4 + 1) == 4):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_SN.isChecked() == False) & (int(i2 % 4 + 1) == 4):
                self.R_listCheckBox[i2].setChecked(False)

    def R_G1_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_G1.isChecked() == True) & (int(i2 / 4 + 6) == 6):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_G1.isChecked() == False) & (int(i2 / 4 + 6) == 6):
                self.R_listCheckBox[i2].setChecked(False)

    def R_G1a_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_G1a.isChecked() == True) & (int(i2 / 4 + 6) == 7):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_G1a.isChecked() == False) & (int(i2 / 4 + 6) == 7):
                self.R_listCheckBox[i2].setChecked(False)

    def R_G2_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_G2.isChecked() == True) & (int(i2 / 4 + 6) == 8):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_G2.isChecked() == False) & (int(i2 / 4 + 6) == 8):
                self.R_listCheckBox[i2].setChecked(False)

    def R_G2a_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_G2a.isChecked() == True) & (int(i2 / 4 + 6) == 9):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_G2a.isChecked() == False) & (int(i2 / 4 + 6) == 9):
                self.R_listCheckBox[i2].setChecked(False)

    def R_G3_function(self):
        for i2, v2 in enumerate(self.R_listCheckBox):
            if (self.R_G3.isChecked() == True) & (int(i2 / 4 + 6) == 10):
                self.R_listCheckBox[i2].setChecked(True)
            elif (self.R_G3.isChecked() == False) & (int(i2 / 4 + 6) == 10):
                self.R_listCheckBox[i2].setChecked(False)

    # C
    def C_global(self):
        for i3, v3 in enumerate(self.C_listCheckBox):
            if self.C_all.isChecked() == True:
                self.C_listCheckBox[i3].setChecked(True)
            elif self.C_all.isChecked() == False:
                self.C_listCheckBox[i3].setChecked(False)

    def C_Pseudorange_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_Pseudorange.isChecked() == True) & (int(i2 % 4 + 1) == 1):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_Pseudorange.isChecked() == False) & (int(i2 % 4 + 1) == 1):
                self.C_listCheckBox[i2].setChecked(False)

    def C_phase_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_phase.isChecked() == True) & (int(i2 % 4 + 1) == 2):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_phase.isChecked() == False) & (int(i2 % 4 + 1) == 2):
                self.C_listCheckBox[i2].setChecked(False)

    def C_MP_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_MP.isChecked() == True) & (int(i2 % 4 + 1) == 3):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_MP.isChecked() == False) & (int(i2 % 4 + 1) == 3):
                self.C_listCheckBox[i2].setChecked(False)

    def C_SN_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_SN.isChecked() == True) & (int(i2 % 4 + 1) == 4):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_SN.isChecked() == False) & (int(i2 % 4 + 1) == 4):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B1_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B1.isChecked() == True) & (int(i2 / 4 + 13) == 13):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B1.isChecked() == False) & (int(i2 / 4 + 13) == 13):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B1C_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B1C.isChecked() == True) & (int(i2 / 4 + 13) == 14):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B1C.isChecked() == False) & (int(i2 / 4 + 13) == 14):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B1A_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B1A.isChecked() == True) & (int(i2 / 4 + 13) == 15):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B1A.isChecked() == False) & (int(i2 / 4 + 13) == 15):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B2a_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B2a.isChecked() == True) & (int(i2 / 4 + 13) == 16):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B2a.isChecked() == False) & (int(i2 / 4 + 13) == 16):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B2_function(self):
        for i3, v3 in enumerate(self.C_listCheckBox):
            if (self.C_B2.isChecked() == True) & (int(i3 / 4 + 13) == 17):
                self.C_listCheckBox[i3].setChecked(True)
            elif (self.C_B2.isChecked() == False) & (int(i3 / 4 + 13) == 17):
                self.C_listCheckBox[i3].setChecked(False)

    def C_B2b_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B2b.isChecked() == True) & (int(i2 / 4 + 13) == 18):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B2b.isChecked() == False) & (int(i2 / 4 + 13) == 18):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B2ab_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B2ab.isChecked() == True) & (int(i2 / 4 + 13) == 19):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B2ab.isChecked() == False) & (int(i2 / 4 + 13) == 19):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B3_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B3.isChecked() == True) & (int(i2 / 4 + 13) == 20):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B3.isChecked() == False) & (int(i2 / 4 + 13) == 20):
                self.C_listCheckBox[i2].setChecked(False)

    def C_B3A_function(self):
        for i2, v2 in enumerate(self.C_listCheckBox):
            if (self.C_B3A.isChecked() == True) & (int(i2 / 4 + 13) == 21):
                self.C_listCheckBox[i2].setChecked(True)
            elif (self.C_B3A.isChecked() == False) & (int(i2 / 4 + 13) == 21):
                self.C_listCheckBox[i2].setChecked(False)

    # E
    def E_global(self):
        for i4, v4 in enumerate(self.E_listCheckBox):
            if self.E_all.isChecked() == True:
                self.E_listCheckBox[i4].setChecked(True)
            elif self.E_all.isChecked() == False:
                self.E_listCheckBox[i4].setChecked(False)

    def E_Pseudorange_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_Pseudorange.isChecked() == True) & (int(i2 % 4 + 1) == 1):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_Pseudorange.isChecked() == False) & (int(i2 % 4 + 1) == 1):
                self.E_listCheckBox[i2].setChecked(False)

    def E_phase_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_phase.isChecked() == True) & (int(i2 % 4 + 1) == 2):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_phase.isChecked() == False) & (int(i2 % 4 + 1) == 2):
                self.E_listCheckBox[i2].setChecked(False)

    def E_MP_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_MP.isChecked() == True) & (int(i2 % 4 + 1) == 3):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_MP.isChecked() == False) & (int(i2 % 4 + 1) == 3):
                self.E_listCheckBox[i2].setChecked(False)

    def E_SN_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_SN.isChecked() == True) & (int(i2 % 4 + 1) == 4):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_SN.isChecked() == False) & (int(i2 % 4 + 1) == 4):
                self.E_listCheckBox[i2].setChecked(False)

    def E_E1_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_E1.isChecked() == True) & (int(i2 / 4 + 24) == 24):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_E1.isChecked() == False) & (int(i2 / 4 + 24) == 24):
                self.E_listCheckBox[i2].setChecked(False)

    def E_E5a_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_E5a.isChecked() == True) & (int(i2 / 4 + 24) == 25):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_E5a.isChecked() == False) & (int(i2 / 4 + 24) == 25):
                self.E_listCheckBox[i2].setChecked(False)

    def E_E5b_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_E5b.isChecked() == True) & (int(i2 / 4 + 24) == 26):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_E5b.isChecked() == False) & (int(i2 / 4 + 24) == 26):
                self.E_listCheckBox[i2].setChecked(False)

    def E_E5ab_function(self):
        for i3, v3 in enumerate(self.E_listCheckBox):
            if (self.E_E5ab.isChecked() == True) & (int(i3 / 4 + 24) == 27):
                self.E_listCheckBox[i3].setChecked(True)
            elif (self.E_E5ab.isChecked() == False) & (int(i3 / 4 + 24) == 27):
                self.E_listCheckBox[i3].setChecked(False)

    def E_E6_function(self):
        for i2, v2 in enumerate(self.E_listCheckBox):
            if (self.E_E6.isChecked() == True) & (int(i2 / 4 + 24) == 28):
                self.E_listCheckBox[i2].setChecked(True)
            elif (self.E_E6.isChecked() == False) & (int(i2 / 4 + 24) == 28):
                self.E_listCheckBox[i2].setChecked(False)

    # J
    def J_global(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if self.J_all.isChecked() == True:
                self.J_listCheckBox[i1].setChecked(True)
            elif self.J_all.isChecked() == False:
                self.J_listCheckBox[i1].setChecked(False)

    def J_Pseudorange_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_Pseudorange.isChecked() == True) & (int(i1 % 4 + 1) == 1):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_Pseudorange.isChecked() == False) & (int(i1 % 4 + 1) == 1):
                self.J_listCheckBox[i1].setChecked(False)

    def J_phase_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_phase.isChecked() == True) & (int(i1 % 4 + 1) == 2):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_phase.isChecked() == False) & (int(i1 % 4 + 1) == 2):
                self.J_listCheckBox[i1].setChecked(False)

    def J_MP_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_MP.isChecked() == True) & (int(i1 % 4 + 1) == 3):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_MP.isChecked() == False) & (int(i1 % 4 + 1) == 3):
                self.J_listCheckBox[i1].setChecked(False)

    def J_SN_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_SN.isChecked() == True) & (int(i1 % 4 + 1) == 4):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_SN.isChecked() == False) & (int(i1 % 4 + 1) == 4):
                self.J_listCheckBox[i1].setChecked(False)

    def J_L1_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_L1.isChecked() == True) & (int(i1 / 4 + 31) == 31):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_L1.isChecked() == False) & (int(i1 / 4 + 31) == 31):
                self.J_listCheckBox[i1].setChecked(False)

    def J_L2_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_L2.isChecked() == True) & (int(i1 / 4 + 31) == 32):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_L2.isChecked() == False) & (int(i1 / 4 + 31) == 32):
                self.J_listCheckBox[i1].setChecked(False)

    def J_L5_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_L5.isChecked() == True) & (int(i1 / 4 + 31) == 33):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_L5.isChecked() == False) & (int(i1 / 4 + 31) == 33):
                self.J_listCheckBox[i1].setChecked(False)

    def J_L6_function(self):
        for i1, v1 in enumerate(self.J_listCheckBox):
            if (self.J_L6.isChecked() == True) & (int(i1 / 4 + 31) == 34):
                self.J_listCheckBox[i1].setChecked(True)
            elif (self.J_L6.isChecked() == False) & (int(i1 / 4 + 31) == 34):
                self.J_listCheckBox[i1].setChecked(False)

    # I
    def I_global(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            if self.I_all.isChecked() == True:
                self.I_listCheckBox[i1].setChecked(True)
            elif self.I_all.isChecked() == False:
                self.I_listCheckBox[i1].setChecked(False)

    def I_Pseudorange_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            if (self.I_Pseudorange.isChecked() == True) & (int(i1 % 4 + 1) == 1):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_Pseudorange.isChecked() == False) & (int(i1 % 4 + 1) == 1):
                self.I_listCheckBox[i1].setChecked(False)

    def I_phase_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            if (self.I_phase.isChecked() == True) & (int(i1 % 4 + 1) == 2):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_phase.isChecked() == False) & (int(i1 % 4 + 1) == 2):
                self.I_listCheckBox[i1].setChecked(False)

    def I_MP_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            if (self.I_MP.isChecked() == True) & (int(i1 % 4 + 1) == 3):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_MP.isChecked() == False) & (int(i1 % 4 + 1) == 3):
                self.I_listCheckBox[i1].setChecked(False)

    def I_SN_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            if (self.I_SN.isChecked() == True) & (int(i1 % 4 + 1) == 4):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_SN.isChecked() == False) & (int(i1 % 4 + 1) == 4):
                self.I_listCheckBox[i1].setChecked(False)

    def I_L5_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            if (self.I_L5.isChecked() == True) & (int(i1 / 4 + 37) == 37):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_L5.isChecked() == False) & (int(i1 / 4 + 37) == 37):
                self.I_listCheckBox[i1].setChecked(False)

    def I_S_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            aa = int(i1 / 4 + 37)
            if (self.I_S.isChecked() == True) & (int(i1 / 4 + 37) == 38):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_S.isChecked() == False) & (int(i1 / 4 + 37) == 38):
                self.I_listCheckBox[i1].setChecked(False)


    def I_L1_function(self):
        for i1, v1 in enumerate(self.I_listCheckBox):
            aa = int(i1/4 + 37)
            aaa = self.I_L1.isChecked()
            if (self.I_L1.isChecked() == True) & (int(i1/4 + 37) == 39):
                self.I_listCheckBox[i1].setChecked(True)
            elif (self.I_L1.isChecked() == False) & (int(i1/4 + 37) == 39):
                self.I_listCheckBox[i1].setChecked(False)

    # S
    def S_global(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if self.S_all.isChecked() == True:
                self.S_listCheckBox[i1].setChecked(True)
            elif self.S_all.isChecked() == False:
                self.S_listCheckBox[i1].setChecked(False)

    def S_Pseudorange_function(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if (self.S_Pseudorange.isChecked() == True) & (int(i1 % 4 + 1) == 1):
                self.S_listCheckBox[i1].setChecked(True)
            elif (self.S_Pseudorange.isChecked() == False) & (int(i1 % 4 + 1) == 1):
                self.S_listCheckBox[i1].setChecked(False)

    def S_phase_function(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if (self.S_phase.isChecked() == True) & (int(i1 % 4 + 1) == 2):
                self.S_listCheckBox[i1].setChecked(True)
            elif (self.S_phase.isChecked() == False) & (int(i1 % 4 + 1) == 2):
                self.S_listCheckBox[i1].setChecked(False)

    def S_MP_function(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if (self.S_MP.isChecked() == True) & (int(i1 % 4 + 1) == 3):
                self.S_listCheckBox[i1].setChecked(True)
            elif (self.S_MP.isChecked() == False) & (int(i1 % 4 + 1) == 3):
                self.S_listCheckBox[i1].setChecked(False)

    def S_SN_function(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if (self.S_SN.isChecked() == True) & (int(i1 % 4 + 1) == 4):
                self.S_listCheckBox[i1].setChecked(True)
            elif (self.S_SN.isChecked() == False) & (int(i1 % 4 + 1) == 4):
                self.S_listCheckBox[i1].setChecked(False)

    def S_L1_function(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if (self.S_L1.isChecked() == True) & (int(i1 / 4 + 41) == 41):
                self.S_listCheckBox[i1].setChecked(True)
            elif (self.S_L1.isChecked() == False) & (int(i1 / 4 + 41) == 41):
                self.S_listCheckBox[i1].setChecked(False)

    def S_L5_function(self):
        for i1, v1 in enumerate(self.S_listCheckBox):
            if (self.S_L5.isChecked() == True) & (int(i1 / 4 + 41) == 42):
                self.S_listCheckBox[i1].setChecked(True)
            elif (self.S_L5.isChecked() == False) & (int(i1 / 4 + 41) == 42):
                self.S_listCheckBox[i1].setChecked(False)

    # all
    def total_global(self):
        for i1, v1 in enumerate(self.G_listCheckBox):
            self.G_listCheckBox[i1].setChecked(True)
        for i2, v2 in enumerate(self.R_listCheckBox):
            self.R_listCheckBox[i2].setChecked(True)
        for i3, v3 in enumerate(self.C_listCheckBox):
            self.C_listCheckBox[i3].setChecked(True)
        for i4, v4 in enumerate(self.E_listCheckBox):
            self.E_listCheckBox[i4].setChecked(True)
        for i5, v5 in enumerate(self.J_listCheckBox):
            self.J_listCheckBox[i5].setChecked(True)
        for i6, v6 in enumerate(self.I_listCheckBox):
            self.I_listCheckBox[i6].setChecked(True)
        for i7, v7 in enumerate(self.S_listCheckBox):
            self.S_listCheckBox[i7].setChecked(True)

    # Cancel
    def cancel_global(self):
        # self.G_all.setChecked(False)
        self.G_Pseudorange.setChecked(False)
        self.G_phase.setChecked(False)
        self.G_MP.setChecked(False)
        self.G_SN.setChecked(False)
        self.G_L1.setChecked(False)
        self.G_L2.setChecked(False)
        self.G_L5.setChecked(False)
        for i1, v1 in enumerate(self.G_listCheckBox):
            self.G_listCheckBox[i1].setChecked(False)

        # self.R_all.setChecked(False)
        self.E_Pseudorange.setChecked(False)
        self.E_phase.setChecked(False)
        self.E_MP.setChecked(False)
        self.E_SN.setChecked(False)
        self.E_E1.setChecked(False)
        self.E_E5a.setChecked(False)
        self.E_E5b.setChecked(False)
        self.E_E5ab.setChecked(False)
        self.E_E6.setChecked(False)
        for i2, v2 in enumerate(self.R_listCheckBox):
            self.R_listCheckBox[i2].setChecked(False)

        # self.C_all.setChecked(False)
        self.C_Pseudorange.setChecked(False)
        self.C_phase.setChecked(False)
        self.C_MP.setChecked(False)
        self.C_SN.setChecked(False)
        self.C_B1.setChecked(False)
        self.C_B1C.setChecked(False)
        self.C_B1A.setChecked(False)
        self.C_B2a.setChecked(False)
        self.C_B2.setChecked(False)
        self.C_B2b.setChecked(False)
        self.C_B2ab.setChecked(False)
        self.C_B3.setChecked(False)
        self.C_B3A.setChecked(False)
        for i3, v3 in enumerate(self.C_listCheckBox):
            self.C_listCheckBox[i3].setChecked(False)

        # self.E_all.setChecked(False)
        self.E_Pseudorange.setChecked(False)
        self.E_phase.setChecked(False)
        self.E_MP.setChecked(False)
        self.E_SN.setChecked(False)
        self.E_E1.setChecked(False)
        self.E_E5a.setChecked(False)
        self.E_E5b.setChecked(False)
        self.E_E5ab.setChecked(False)
        self.E_E6.setChecked(False)
        for i4, v4 in enumerate(self.E_listCheckBox):
            self.E_listCheckBox[i4].setChecked(False)

        # self.J_all.setChecked(False)
        self.J_Pseudorange.setChecked(False)
        self.J_phase.setChecked(False)
        self.J_MP.setChecked(False)
        self.J_SN.setChecked(False)
        self.J_L1.setChecked(False)
        self.J_L2.setChecked(False)
        self.J_L5.setChecked(False)
        self.J_L6.setChecked(False)
        for i5, v5 in enumerate(self.J_listCheckBox):
            self.J_listCheckBox[i5].setChecked(False)

        # self.I_all.setChecked(False)
        self.I_Pseudorange.setChecked(False)
        self.I_phase.setChecked(False)
        self.I_MP.setChecked(False)
        self.I_SN.setChecked(False)
        self.I_L5.setChecked(False)
        self.I_S.setChecked(False)
        for i4, v4 in enumerate(self.I_listCheckBox):
            self.I_listCheckBox[i4].setChecked(False)

        # self.S_all.setChecked(False)
        self.S_Pseudorange.setChecked(False)
        self.S_phase.setChecked(False)
        self.S_MP.setChecked(False)
        self.S_SN.setChecked(False)
        self.S_L1.setChecked(False)
        self.S_L5.setChecked(False)
        for i4, v4 in enumerate(self.S_listCheckBox):
            self.S_listCheckBox[i4].setChecked(False)


class selfdiy_intv(QDialog):
    mySignal = pyqtSignal(str)
    def __init__(self, file_interval, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Custom")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        # self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.resize(330*self.ratio, 80*self.ratio)
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        self.file_interval = file_interval
        self.setup_ui()

    def setup_ui(self):
        interval_box = QHBoxLayout()
        self.input = QLineEdit(self)
        self.input.setMinimumSize(QSize(60*self.ratio, 25*self.ratio))
        self.input.setPlaceholderText("eg.：120s")

        self.sure = QPushButton("OK", self)
        self.sure.setMinimumSize(QSize(40*self.ratio, 25*self.ratio))
        self.sure.clicked.connect(self.one)

        interval_box.setSpacing(10)
        interval_box.addWidget(self.input)
        interval_box.addWidget(self.sure)
        self.setLayout(interval_box)

    def one(self):
        if float(self.input.text()) % self.file_interval != 0:
            QMessageBox.information(self, 'Error', 'The sampling interval should be an integer multiple of the original data (%s second)！'% self.file_interval)
            return
        diy_intvi = self.input.text()
        self.mySignal.emit(diy_intvi)
        self.hide()
        return diy_intvi

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
    win = Data_Extract(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(13*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())