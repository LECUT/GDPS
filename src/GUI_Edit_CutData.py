from datetime import *
from PyQt5.QtGui import QIcon, QFont, QGuiApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QDesktopWidget, QTableWidget, QGridLayout, QHBoxLayout, QLabel, QHeaderView, QPushButton, QLineEdit,QMessageBox,\
                            QWidget, QFileDialog, QTableWidgetItem, QComboBox, QDialog
from PyQt5.QtCore import QSize, Qt, QFileInfo, pyqtSignal
import sys
import time
import os
from data_edit import file_segmentation
import configparser
import resources_rc

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

# program path
curdir = os.getcwd()
class Data_Cut(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Data segmentation")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.resize(500, 300)
        self.resize(500*self.ratio, 300*self.ratio)
        # self.setFixedSize(500*self.ratio, 300*self.ratio)
        # self.setGeometry((screen.width() - 900 / 1920 * win_width) / 2, (screen.height() - 400 / 1080 * win_height) / 2, 900 / 1920 * win_width, 245 / 1080 * win_height)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.setup_ui()

    def setup_ui(self):

        label_w        = 80*self.ratio
        label_h        = 25*self.ratio
        blabel_w       = 40*self.ratio
        blabel_h       = 10*self.ratio
        clabel_w       = 250*self.ratio
        clabel_h       = 25*self.ratio
        dlabel_w       = 40*self.ratio
        dlabel_h       = 25*self.ratio
        lineEdit_w     = 300*self.ratio
        lineEdit_h     = 25*self.ratio
        PushButton_w   = 50*self.ratio
        PushButton_h   = 25*self.ratio
        zPushButton_w  = 25*self.ratio
        zPushButton_h  = 25*self.ratio
        QComboBox_w    = 80*self.ratio
        QComboBox_h    = 25*self.ratio
        Pagemargin     = 10*self.ratio
        Pagemargin_row = 10*self.ratio
        Pagemargin_col = 10*self.ratio
        #**************************************************************
        cut_box = QGridLayout()
        self.choose_input_path_wuyong_label = QLabel('Input', self)
        self.choose_input_path_wuyong_label.setMinimumSize(QSize(dlabel_w, dlabel_h))
        self.choose_input_path_wuyong_label.setMaximumSize(QSize(dlabel_w, dlabel_h))
        # self.choose_input_path_wuyong_label.setGeometry(35, 30, 360, 30)

        self.show_inputsave_files_path_button = QLineEdit(self)
        self.show_inputsave_files_path_button.setMinimumSize(QSize(lineEdit_w, lineEdit_h))
        # self.show_inputsave_files_path_button.setGeometry(150, 30, 690, 35)

        self.choose_inputsave_files_path_button = QPushButton(self)
        self.choose_inputsave_files_path_button.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.choose_inputsave_files_path_button.setMaximumSize(QSize(zPushButton_w, zPushButton_h))
        # self.choose_inputsave_files_path_button.setGeometry(850, 34, 27, 27)
        self.choose_inputsave_files_path_button.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_inputsave_files_path_button.clicked.connect(self.save_input_files_path_function)


        self.show_file_long_label01 = QLabel('Total Time', self)
        self.show_file_long_label01.setMinimumSize(QSize(label_w, label_h))
        # self.show_file_long_label01.setGeometry(35, 100, 360, 30)

        self.show_file_long_label02 = QLabel('', self)
        self.show_file_long_label02.setMinimumSize(QSize(clabel_w, clabel_h))
        # self.show_file_long_label02.setGeometry(220, 100, 360, 30)


        self.show_file_cut_label01 = QLabel('File Divide',self)
        self.show_file_cut_label01.setMinimumSize(QSize(label_w, label_h))
        self.show_file_cut_label01.setMaximumSize(QSize(label_w, label_h))
        # self.show_file_cut_label01.setGeometry(450, 100, 160, 30)

        self.time_combox = QComboBox(self)
        self.time_combox.addItems(['1', '2', '3', '4', '6', 'custom'])
        self.time_combox.setCurrentText('1')
        self.time_combox.setMinimumSize(QSize(QComboBox_w, QComboBox_h))
        # self.time_combox.setGeometry(590, 100, 60, 30)
        self.time_combox.currentIndexChanged.connect(self.selectionchange)

        self.show_file_cut_label02 = QLabel('h/file',self)
        self.show_file_cut_label02.setMinimumSize(QSize(dlabel_w, dlabel_h))
        # self.show_file_cut_label02.setGeometry(660, 100, 260, 30)


        self.data_cut_but = QPushButton('Execute', self)
        self.data_cut_but.setMinimumSize(QSize(PushButton_w, PushButton_h))
        # self.data_cut_but.setGeometry(35, 160, 830, 40)
        self.data_cut_but.clicked.connect(self.sure_function)

        # self.all_about_btn = QLabel("<A href='www.baidu.com'>about</a>")
        # # self.all_about_btn.setFont(QFont("Times New Roman", 10))
        # self.all_about_btn.setAlignment(Qt.AlignRight)
        # # self.all_about_btn.move(840, 220)

        blank_label = QLabel('')
        blank_label.setMinimumSize(QSize(blabel_w, blabel_h))
        cut_box.setSpacing(Pagemargin)
        # cut_box.addWidget(blank_label, 0, 0)
        cut_box.addWidget(self.choose_input_path_wuyong_label, 0, 0, 1, 1)
        cut_box.addWidget(self.show_inputsave_files_path_button, 0, 1, 1, 5)
        cut_box.addWidget(self.choose_inputsave_files_path_button, 0, 6, 1, 1)
        # cut_box.addWidget(blank_label, 1, 0)
        cut_box.addWidget(self.show_file_long_label01, 1, 0, 1, 2)
        cut_box.addWidget(self.show_file_long_label02, 1, 2, 1, 2)
        cut_box.addWidget(self.show_file_cut_label01, 1, 4, 1, 1)
        cut_box.addWidget(self.time_combox, 1, 5, 1, 1)
        cut_box.addWidget(self.show_file_cut_label02, 1, 6, 1, 1)
        # cut_box.addWidget(blank_label, 3, 0)
        cut_box.addWidget(self.data_cut_but, 2, 0, 1, 7)
        cut_box.setContentsMargins(Pagemargin_row, Pagemargin_col, Pagemargin_row, Pagemargin_col)
        # cut_box.addWidget(self.all_about_btn, 6, 5, 1, 1)

        mainFrame = QWidget()
        mainFrame.setLayout(cut_box)
        self.setCentralWidget(mainFrame)


        self.conf = configparser.ConfigParser()
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.read(conf_path, encoding='utf-8-sig')

    #  ok
    def sure_function(self):
        if self.show_inputsave_files_path_button.text() == '':
            QMessageBox.information(self, 'Prompt', "Please enter data!")
            return

        T1 = time.time()
        input_path = self.show_inputsave_files_path_button.text()
        cut_long = self.time_combox.currentText()

        if float(cut_long)<(60/3600):
            QMessageBox.information(self, 'Prompt', "The time for segmentation needs to exceed 60 seconds!")
            return

        self.conf.set('Parameter', 'input_file_path', input_path)
        self.conf.set('Parameter', 'cut_time_long', cut_long)
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.write(open(conf_path, 'w', encoding='utf-8'))

        # try:
        input_path = self.conf.get('Parameter', 'input_file_path')
        cut_long = self.conf.get('Parameter', 'cut_time_long')
        file_segmentation.File_Segmentation_Function(input_path, cut_long)
        # except Exception as e:
        #     print(e)
        #     QMessageBox.warning(self, 'Prompt', "Error convert!")
        #     return
        T2 = time.time()
        print('completed, the total time: %s seconds' % ((T2 - T1)))
        QMessageBox.information(self, 'Prompt', "completion!")


    #  combox data
    def selectionchange(self):
        if self.time_combox.currentText() == 'custom':
            self.s = selfdiy_intv(self.ratio)
            self.s.mySignal.connect(self.getDialogSignal)
            self.s.exec_()
        else:
            global aa223
            aa223 = self.time_combox.currentText()
    def getDialogSignal(self, connect):
        global time_combox
        diy_intvi = str(connect)
        self.time_combox.addItem(diy_intvi)
        self.time_combox.setCurrentText(diy_intvi)
        global aa223
        aa223 = diy_intvi


    #  select input
    def save_input_files_path_function(self):
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        unzip_default_download_path = desktop_path + '/download'
        if os.path.exists(unzip_default_download_path):
            path1, parh2 = QFileDialog.getOpenFileName(self, 'Select the object file', './', 'o_file(*MO.rnx *.*o *.*O);;All_File(*)')
        else:
            path1, parh2 = QFileDialog.getOpenFileName(self, 'Select the object file', './', 'o_file(*MO.rnx *.*o *.*O);;All_File(*)')

        if parh2 != '':
            os.chdir(os.path.dirname(path1))

        if parh2 != '':
            try:
                with open(path1, 'r') as f00:
                    first_line = f00.readline()
                    raw_rinex_text_list = f00.readlines()
                    print(first_line[20:36].upper())
                    if first_line[20:36].upper() != 'OBSERVATION DATA':
                        QMessageBox.information(self, 'error', 'Data type is no observation!')
                        return
                    global input_file_version
                    input_file_version = first_line[5:9].strip()
                    lines_o = f00.readlines()
                print('observed data version', input_file_version)
                self.show_inputsave_files_path_button.setText(path1)

                #  header row
                raw_header_info = []
                for i in range(len(raw_rinex_text_list)):
                    line_text = raw_rinex_text_list[i].strip('\n')
                    temp_info_list = [line_text[0:60], line_text[60:80]]
                    raw_header_info = raw_header_info + [temp_info_list]
                    if 'END OF HEADER' in line_text:
                        end_header_rows = i
                        break
                raw_data_record = raw_rinex_text_list[end_header_rows + 1:]

                #  get time
                for i in raw_data_record:
                    if len(i[:27].split()) > 5:
                        first_time_list = i[:27].split()
                        break
                for j in reversed(raw_data_record):
                    if len(j[:27].split()) > 5:
                        last_time_list = j[:27].split()
                        break
                #  tiem start
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

                #  time end
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

                start_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
                end_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)

                timelonglong = (end_time - start_time).seconds
                timelonglong = round(timelonglong / 3600, 2)
                timelonglong = str(timelonglong) + 'h'
                print(timelonglong)
                self.show_file_long_label02.setText(timelonglong)
                # self.abstract_time_long.setText(timelonglong)
                # self.dateEditstart.setDateTime(start_time)
                # self.dateEditend.setDateTime(end_time)
            except:
                QMessageBox.warning(self, 'error', "Error file, please re-import!")
                return
            global fileinfo01
            fileinfo01 = QFileInfo(path1)
            print(fileinfo01)



class selfdiy_intv(QDialog):
    mySignal = pyqtSignal(str)
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Custom")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        # self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.resize(330*self.ratio, 80*self.ratio)
        self.setup_ui()

    def setup_ui(self):
        interval_box = QHBoxLayout()
        self.input = QLineEdit(self)
        # self.lab002.move(30, 30)
        self.input.setMinimumSize(QSize(60*self.ratio, 25*self.ratio))
        self.input.setPlaceholderText("eg.：1h")

        self.sure = QPushButton("OK", self)
        self.sure.setMinimumSize(QSize(40*self.ratio, 25*self.ratio))
        self.sure.clicked.connect(self.one)

        interval_box.setSpacing(10*self.ratio)
        interval_box.addWidget(self.input)
        interval_box.addWidget(self.sure)
        self.setLayout(interval_box)

    def one(self):
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
    win = Data_Cut(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(14*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())