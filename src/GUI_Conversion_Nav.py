from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys
import re
import time
import os
from format_convert import *
import configparser
import resources_rc

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

curdir = os.getcwd()

class Nav_RINEX_Conversion(QMainWindow):
    global input_file_version
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('Broadcast Ephemeris')
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        win_width = screen.width()
        win_height = screen.height()
        self.resize(550*self.ratio, 450*self.ratio)
        # self.setFixedSize(550*self.ratio, 450*self.ratio)
        # self.setGeometry((screen.width() - 880 / 1920 * win_width) / 2, (screen.height() - 500 / 1080 * win_height) / 2, 900 / 1920 * win_width, 385 / 1080 * win_height)
        self.setup_ui()

    def setup_ui(self):

        label_h       = 25*self.ratio
        label_w       = 52*self.ratio
        blabel_h      = 5*self.ratio
        blabel_w      = 30*self.ratio
        lineEdit_h    = 25*self.ratio
        lineEdit_w    = 400*self.ratio
        pushbutton_h  = 25*self.ratio
        pushbutton_w  = 100*self.ratio
        fpushbutton_h = 25*self.ratio
        fpushbutton_w = 25*self.ratio
        Pagemargin    = 10*self.ratio
        Pagemargin_row = 10*self.ratio
        Pagemargin_col = 30*self.ratio

        #----------------------------------------------------------------
        conb_box = QGridLayout()
        self.choose_input_path_wuyong_label = QLabel('Input:', self)
        self.choose_input_path_wuyong_label.setMinimumSize(QSize(label_w, label_h))
        self.choose_input_path_wuyong_label.setMaximumSize(QSize(label_w, label_h))

        self.show_inputsave_files_path_button = QLineEdit(self)
        self.show_inputsave_files_path_button.setMinimumSize(QSize(lineEdit_w, lineEdit_h))

        self.choose_inputsave_files_path_button = QPushButton(self)
        self.choose_inputsave_files_path_button.setMinimumSize(QSize(fpushbutton_w, fpushbutton_h))
        self.choose_inputsave_files_path_button.setMaximumSize(QSize(fpushbutton_w, fpushbutton_h))

        self.choose_inputsave_files_path_button.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_inputsave_files_path_button.clicked.connect(self.save_input_files_path_function)

        self.choose_gloal_rinex_version = QLabel('Version:', self)
        self.choose_gloal_rinex_version.setMinimumSize(QSize(label_w, label_h))
        self.choose_gloal_rinex_version.setMaximumSize(QSize(label_w, label_h))

        self.cheack211 = QRadioButton("RINEX 2.11", self)
        # self.cheack212 = QRadioButton("RINEX 2.12", self)
        self.cheack300 = QRadioButton("RINEX 3.00", self)
        self.cheack301 = QRadioButton("RINEX 3.01", self)
        self.cheack302 = QRadioButton("RINEX 3.02", self)
        self.cheack303 = QRadioButton("RINEX 3.03", self)
        self.cheack304 = QRadioButton("RINEX 3.04", self)
        self.cheack305 = QRadioButton("RINEX 3.05", self)
        self.cheack400 = QRadioButton("RINEX 4.00", self)
        self.cheack401 = QRadioButton("RINEX 4.01", self)
        self.choose_rinex_version_cheack_group = QButtonGroup(self)
        self.choose_rinex_version_cheack_group.addButton(self.cheack211, 211)
        # self.choose_rinex_version_cheack_group.addButton(self.cheack212, 212)
        self.choose_rinex_version_cheack_group.addButton(self.cheack300, 300)
        self.choose_rinex_version_cheack_group.addButton(self.cheack301, 301)
        self.choose_rinex_version_cheack_group.addButton(self.cheack302, 302)
        self.choose_rinex_version_cheack_group.addButton(self.cheack303, 303)
        self.choose_rinex_version_cheack_group.addButton(self.cheack304, 304)
        self.choose_rinex_version_cheack_group.addButton(self.cheack305, 305)
        self.choose_rinex_version_cheack_group.addButton(self.cheack400, 400)
        self.choose_rinex_version_cheack_group.addButton(self.cheack401, 401)
        self.choose_rinex_version_cheack_group.buttonClicked[int].connect(self.check_version_button_group_change)

        self.choose_output_path_wuyong_label = QLabel('Output:', self)
        self.choose_output_path_wuyong_label.setMinimumSize(QSize(label_w, label_h))
        self.choose_output_path_wuyong_label.setMaximumSize(QSize(label_w, label_h))

        self.show_outputsave_files_path_button = QLineEdit(self)
        self.show_outputsave_files_path_button.setMinimumSize(QSize(lineEdit_w, lineEdit_h))

        self.choose_outputsave_files_path_button = QPushButton(self)
        self.choose_outputsave_files_path_button.setMinimumSize(QSize(fpushbutton_w, fpushbutton_h))
        self.choose_outputsave_files_path_button.setMaximumSize(QSize(fpushbutton_w, fpushbutton_h))
        self.choose_outputsave_files_path_button.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_outputsave_files_path_button.clicked.connect(self.choose_output_files_path_function)

        self.igs_name_sure_but = QPushButton('Execute', self)
        self.igs_name_sure_but.setMinimumSize(QSize(pushbutton_w, pushbutton_h))
        self.igs_name_sure_but.clicked.connect(self.convert_function)

        # self.all_about_btn = QLabel("<A href='www.baidu.com'>About</a>")
        # self.all_about_btn.setAlignment(Qt.AlignRight)

        blank_label = QLabel('')
        blank_label.setMinimumSize(QSize(blabel_w, blabel_h))
        blank_label.setMaximumSize(QSize(blabel_w, blabel_h))
        conb_box.setSpacing(Pagemargin)
        conb_box.addWidget(self.choose_input_path_wuyong_label, 0, 0, 1, 1)
        conb_box.addWidget(self.show_inputsave_files_path_button, 0, 1, 1, 3)
        conb_box.addWidget(self.choose_inputsave_files_path_button, 0, 4, 1, 1)
        conb_box.addWidget(blank_label, 1, 0)
        conb_box.addWidget(self.choose_gloal_rinex_version, 2, 0, 3, 1)
        conb_box.addWidget(self.cheack211, 2, 1, 1, 1)
        # conb_box.addWidget(self.cheack212, 2, 2, 1, 1)
        conb_box.addWidget(self.cheack300, 2, 2, 1, 1)
        conb_box.addWidget(self.cheack301, 2, 3, 1, 1)
        conb_box.addWidget(self.cheack302, 3, 1, 1, 1)
        conb_box.addWidget(self.cheack303, 3, 2, 1, 1)
        conb_box.addWidget(self.cheack304, 3, 3, 1, 1)
        conb_box.addWidget(self.cheack305, 4, 1, 1, 1)
        conb_box.addWidget(self.cheack400, 4, 2, 1, 1)
        conb_box.addWidget(self.cheack401, 4, 3, 1, 1)
        conb_box.addWidget(blank_label, 6, 0)
        conb_box.addWidget(self.choose_output_path_wuyong_label, 7, 0, 1, 1)
        conb_box.addWidget(self.show_outputsave_files_path_button, 7, 1, 1, 3)
        conb_box.addWidget(self.choose_outputsave_files_path_button, 7, 4, 1, 1)
        conb_box.addWidget(blank_label, 8, 0)
        conb_box.addWidget(self.igs_name_sure_but, 9, 2, 1, 1)
        conb_box.setContentsMargins(Pagemargin_row, Pagemargin_col, Pagemargin_row, Pagemargin_col)

        # spacerItem_V = QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        # conb_box.addItem(spacerItem_V, 8, 0)
        # conb_box.addItem(spacerItem_V, 8, 4)
        # conb_box.addWidget(self.all_about_btn, 0, 0, 1, 1)

        mainFrame = QWidget()
        mainFrame.setLayout(conb_box)
        self.setCentralWidget(mainFrame)

        self.conf = configparser.ConfigParser()
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.read(conf_path, encoding='utf-8-sig')


    #
    def check_version_button_group_change(self, id):
        try:
            #
            filename_input_rinexo = fileinfo01.fileName()
            input_folder = path1.strip(filename_input_rinexo)
            #
            head1, sep1, tail1 = filename_input_rinexo.rpartition('.')
            # print(head1, sep1, tail1)
            if input_file_version == '2' or input_file_version == '2.11':
                if id == 200 or id == 211:
                    output_file_name = 'vc_' + head1 + '.' + tail1
                else:
                    output_file_name = head1[0:4].upper() + '00XXX_R_20' + tail1[0:2] + head1[4:7] + '0000_01D_MN.rnx'
            else:
                if id == 200 or id == 211:
                    output_file_name = ''
                else:
                    output_file_name = 'VC_' + head1[0:4].upper() + '00XXX_R_20' + tail1[0:2] + head1[4:7] + '0000_01D_MN.rnx'
            self.show_outputsave_files_path_button.setText('/'.join(self.show_inputsave_files_path_button.text().split('/')[:-1]) + '/' + output_file_name)
        except:
            pass

    #
    def save_input_files_path_function(self):
        self.show_outputsave_files_path_button.setText('')
        #
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        unzip_default_download_path = desktop_path
        global path1
        if os.path.exists(unzip_default_download_path):
            path1, parh2 = QFileDialog.getOpenFileName(self, 'Select the file', './', 'n_file(*MN.rnx *.*n *.*N *.*p *.*P *.nav);;All_File(*)')
        else:
            path1, parh2 = QFileDialog.getOpenFileName(self, 'Select the file', './', 'n_file(*MN.rnx *.*n *.*N *.*p *.*P *.nav);;All_File(*)')

        if parh2 != '':
            os.chdir(os.path.dirname(path1))

        # self.cheack200.setCheckable(True)
        self.cheack211.setCheckable(True)
        self.cheack300.setCheckable(True)
        self.cheack301.setCheckable(True)
        self.cheack302.setCheckable(True)
        self.cheack303.setCheckable(True)
        self.cheack304.setCheckable(True)
        self.cheack305.setCheckable(True)
        self.cheack400.setCheckable(True)
        self.cheack401.setCheckable(True)
        # self.cheack200.setEnabled(True)
        self.cheack211.setEnabled(True)
        self.cheack300.setEnabled(True)
        self.cheack301.setEnabled(True)
        self.cheack302.setEnabled(True)
        self.cheack303.setEnabled(True)
        self.cheack304.setEnabled(True)
        self.cheack305.setEnabled(True)
        self.cheack400.setEnabled(True)
        self.cheack401.setEnabled(True)
        # self.cheack200.setChecked(False)
        self.cheack211.setChecked(False)
        self.cheack300.setChecked(False)
        self.cheack301.setChecked(False)
        self.cheack302.setChecked(False)
        self.cheack303.setChecked(False)
        self.cheack304.setChecked(False)
        self.cheack305.setChecked(False)
        self.cheack400.setChecked(False)
        self.cheack401.setChecked(False)
        # self.cheack200.setCheckable(True)
        self.cheack211.setCheckable(True)
        self.cheack300.setCheckable(True)
        self.cheack301.setCheckable(True)
        self.cheack302.setCheckable(True)
        self.cheack303.setCheckable(True)
        self.cheack304.setCheckable(True)
        self.cheack305.setCheckable(True)
        self.cheack400.setCheckable(True)
        self.cheack401.setCheckable(True)
        if parh2 == '':
            pass
        else:
            try:
                with open(path1, 'r') as f00:
                    first_line = f00.readline()
                    if 'NAV' not in first_line[20:35]:
                        QMessageBox.information(self, 'Error', 'The file is broadcast ephemeris！')
                        return
                    global input_file_version
                    input_file_version = first_line[5:9].strip()
                    self.conf.set('Parameter', 'input_rinex_version', input_file_version)
                if input_file_version == '2':
                    # self.cheack200.setEnabled(False)
                    self.cheack211.setEnabled(False)
                elif input_file_version == '2.11':
                    self.cheack211.setEnabled(False)
                elif input_file_version == '4.00':
                    self.cheack400.setEnabled(False)
                elif input_file_version == '4.01':
                    self.cheack401.setEnabled(False)
                elif input_file_version == '3.00' or input_file_version == '3.01' or input_file_version == '3.02' or input_file_version == '3.03' or input_file_version == '3.04' or input_file_version == '3.05':
                    self.cheack300.setEnabled(False)
                    self.cheack301.setEnabled(False)
                    self.cheack302.setEnabled(False)
                    self.cheack303.setEnabled(False)
                    self.cheack304.setEnabled(False)
                    self.cheack305.setEnabled(False)
                else:
                    QMessageBox.information(self, 'Error', "Invalid file, please re-import!")
                    return
                self.show_inputsave_files_path_button.setText(path1)
            except:
                QMessageBox.information(self, 'Error', "Invalid file, please re-import!")
                return
            global fileinfo01
            fileinfo01 = QFileInfo(path1)


    #
    def choose_output_files_path_function(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', 'C:/')
        if save_path == '':
            pass
        else:
            self.show_outputsave_files_path_button.setText(save_path)


    def convert_function(self):
        input_path = self.show_inputsave_files_path_button.text()
        output_path = self.show_outputsave_files_path_button.text()
        if input_path == '':
            QMessageBox.information(self, 'Error', "Please import the file!")
            return
        if output_path == '':
            QMessageBox.information(self, 'Error', "Please select the output path!")
            return
        self.conf.set('Parameter', 'input_file_path', input_path)
        self.conf.set('Parameter', 'output_file_path', output_path)
        #
        target_version = None
        # if self.cheack200.isChecked():
        #     target_version = '2'
        if self.cheack211.isChecked():
            target_version = '2.11'
        elif self.cheack300.isChecked():
            target_version = '3.00'
        elif self.cheack301.isChecked():
            target_version = '3.01'
        elif self.cheack302.isChecked():
            target_version = '3.02'
        elif self.cheack303.isChecked():
            target_version = '3.03'
        elif self.cheack304.isChecked():
            target_version = '3.04'
        elif self.cheack305.isChecked():
            target_version = '3.05'
        elif self.cheack400.isChecked():
            target_version = '4.00'
        elif self.cheack401.isChecked():
            target_version = '4.01'
        self.conf.set('Parameter', 'output_rinex_version', target_version)
        global curdir
        conf_path = os.path.join(curdir, 'lib/conf/parameter.ini')
        self.conf.write(open(conf_path, 'w', encoding='utf-8'))

        input_path = self.conf.get('Parameter', 'input_file_path')
        input_file_version = self.conf.get('Parameter', 'input_rinex_version')
        target_version = self.conf.get('Parameter', 'output_rinex_version')
        output_path = self.conf.get('Parameter', 'output_file_path')
        if target_version:
            try:
                T1 = time.time()
                write_judge = True
                #
                if target_version == '2' or target_version == '2.11':
                    if input_file_version == '4.00' or input_file_version == '4.01':
                        nav_4to2.NAV_rinex4_to_rinex2(input_path, target_version, output_path)
                        write_judge = False
                    else:
                        nav_3to2.NAV_rinex3_to_rinex2(input_path, target_version, output_path)
                        write_judge = False
                        pass
                elif target_version == '3.00' or target_version == '3.01' or target_version == '3.02' or target_version == '3.03' or target_version == '3.04' or target_version == '3.05':
                    if input_file_version == '2' or input_file_version == '2.11':
                        convert_list = nav_2to3.NAV_rinex2_to_rinex3(input_path, target_version)
                    else:
                        convert_list = nav_4to3.NAV_rinex4_to_rinex3(input_path, target_version)
                        pass
                elif target_version == '4.00' or target_version == '4.01':
                    if input_file_version == '2' or input_file_version == '2.11':
                        convert_list = nav_2to4.Nav_rinex2_to_rinex4(input_path, target_version)
                    elif input_file_version in ['3.00', '3.02', '3.03', '3.04', '3.05', '4.00', '4.01']:
                        convert_list = nav_3to4.NAV_rinex3_to_rinex4(input_path, target_version)
            except Exception as e:
                print(e)
                QMessageBox.information(self, 'prompt', "Failure: The import file format needs to be corrected！")
                return

            #
            # print(convert_list)
            if write_judge:
                with open(output_path, 'w', encoding='utf-8') as f:
                    for i in convert_list:
                        for j in i:
                            f.write(str(j))
                            f.write('\n')
            T2 = time.time()

            self.box = QMessageBox(self)
            self.box.setWindowIcon(QIcon(":/icon/logo.ico"))
            self.box.setWindowTitle('prompt')
            self.box.setText('Complete，Total Time:%ss！' % (int(T2 - T1)))
            self.box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            button_Look = self.box.button(QMessageBox.Yes)
            button_Look.setText('View')
            button_Sure = self.box.button(QMessageBox.No)
            button_Sure.setText('OK')
            self.box.exec_()
            if float(target_version) > 2.99:
                if self.box.clickedButton() == button_Look:
                    self.s = Look_Over_File_details(output_path, self.ratio)
                    self.s.show()
                else:
                    pass
        else:
            QMessageBox.warning(self, 'prompt', "Please set the target version!")


class Look_Over_File_details(QWidget):
    def __init__(self, converted_file, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("View")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.resize(400*self.ratio, 500*self.ratio)
        # self.setGeometry(490, 150, 1000, 800)
        self.setup_ui(converted_file)

    def setup_ui(self, converted_file):
        layout = QHBoxLayout()
        self.textEdit = QTextEdit()
        self.textEdit = QPlainTextEdit(self)
        self.textEdit.setUndoRedoEnabled(False)
        # self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        # self.textEdit.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.textEdit)
        layout.setContentsMargins(0, 0, 0, 0)

        with open(converted_file, 'r') as f:
            msg = f.read()
        self.textEdit.setPlainText(msg)
        self.textEdit.setFont(QFont("Source Code Pro", 9))
        self.setLayout(layout)

def on_exit():
    logger.info('Program ended.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting the program.")
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    print(dpi)
    ratio = dpi/96
    win = Nav_RINEX_Conversion(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(14*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())