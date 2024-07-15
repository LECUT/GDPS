from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui
import sys
import os
import copy
import configparser
from config_format import conf_estimate
from GUI_Quality_Check_setup import Data_Preprocessing_Setup
from GUI_Quality_Check_plotsys import plot_sys
from GUI_Quality_Check_plotsat import plot_sat
import resources_rc


# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)


class Worker(QThread):
    sig = pyqtSignal(str)
    sig1 = pyqtSignal(str)

    def __init__(self, sol_path):
        super(Worker, self).__init__()
        self.sol_path = sol_path
        self.is_running = True
        self.process_pool = None
        import concurrent.futures
        import multiprocessing
        # self.executor = concurrent.futures.ProcessPoolExecutor(max_workers=4)
        self.executor = multiprocessing.Pool(processes=4)

    def run(self):
        import quality_check as ep
        self.process_pool = ep.expos(self.sol_path, self.executor)
        import datetime
        self.sig1.emit('[{}] Solution completed'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    # def stop(self):
    #     self.is_running = False
    #     print('stopping thread...')
    #     self.terminate()
    #     self.finished.emit()

    def stop_expos(self):
        self.executor.terminate()
        print('stopping process...')

        self.finished.emit()
        self.terminate()
        print('stopping thread...')


curdir = os.getcwd() # work path

class Data_Preprocessing(QMainWindow):
    Signal_OneParameter = pyqtSignal(str)
    def __init__(self, ratio, curdir_ini):
        super().__init__()
        self.ratio = ratio
        self.curdir_ini = curdir_ini
        self.setWindowTitle("Data estimate")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.resize(800, 600)
        # self.resize(800, 600)
        self.resize(550*self.ratio, 400*self.ratio)
        # self.setMinimumSize(QSize(550*self.ratio, 400*self.ratio))
        # self.setFixedSize(550*self.ratio, 450*self.ratio)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.setup_ui()

    def setup_ui(self):
        Label_w       = 100*self.ratio
        Label_h       = 25*self.ratio
        LineEdit_w    = 400*self.ratio
        LineEdit_h    = 25*self.ratio
        PushButton_w  = 25*self.ratio
        PushButton_h  = 25*self.ratio
        QCheckBox_w   = 100*self.ratio
        QCheckBox_h   = 25*self.ratio
        QComboBox_w   = 100*self.ratio
        QComboBox_h   = 25*self.ratio
        zPushButton_w = 80*self.ratio
        zPushButton_h = 25*self.ratio
        blabel_w      = 10*self.ratio
        blabel_h      = 5*self.ratio
        Pagemargin    = 5*self.ratio

        self.setStyleSheet("QMainWindow::title {font-size: 20px;}")

        import_box = QGridLayout()
        self.input_title = QLabel('Input:', self)
        self.input_title.setStyleSheet("border: none;")
        self.input_title.setMinimumSize(QSize(Label_w, Label_h))
        self.input_title.setMaximumHeight(Label_h)

        self.show_obs_files_path = QLineEdit(self)
        self.show_obs_files_path.setPlaceholderText('observation data')
        self.show_obs_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_obs_files_path = QPushButton(self)
        self.choose_obs_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_obs_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.choose_obs_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_obs_files_path.clicked.connect(self.import_obs_file)
        self.view_obs_files_path = QPushButton(self)
        self.view_obs_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_obs_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.view_obs_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_obs_files_path.clicked.connect(self.view_obs_file)

        self.show_nav_files_path = QLineEdit(self)
        self.show_nav_files_path.setPlaceholderText('broadcast ephemeris')
        self.show_nav_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_nav_files_path = QPushButton(self)
        self.choose_nav_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_nav_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.choose_nav_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_nav_files_path.clicked.connect(self.import_nav_file)
        self.view_nav_files_path = QPushButton(self)
        self.view_nav_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_nav_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.view_nav_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_nav_files_path.clicked.connect(self.view_nav_file)


        import_box.setSpacing(Pagemargin)
        import_box.addWidget(self.input_title, 0, 0, 1, 4)
        import_box.addWidget(self.show_obs_files_path, 1, 0, 1, 2)
        import_box.addWidget(self.choose_obs_files_path, 1, 2, 1, 1)
        import_box.addWidget(self.view_obs_files_path, 1, 3, 1, 1)
        import_box.addWidget(self.show_nav_files_path, 2, 0, 1, 2)
        import_box.addWidget(self.choose_nav_files_path, 2, 2, 1, 1)
        import_box.addWidget(self.view_nav_files_path, 2, 3, 1, 1)
        import_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        import_wg = QFrame()
        import_wg.setStyleSheet("QFrame {border-radius: 3px; border: 0.5px solid gray;}")
        import_wg.setFrameShape(QFrame.Box)
        # import_wg.setStyleSheet('''QFrame{border:1px solid #5F92B2;border-radius:5px;}''')
        import_wg.setLayout(import_box)


        time_box = QGridLayout()
        self.start_time_check = QCheckBox('Time Start', self)

        self.start_time_check.setStyleSheet("QCheckBox::indicator { width: 30px; height: 20px; }")
        self.start_time_check.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.start_time_check.setChecked(True)
        self.start_time_check.stateChanged.connect(self.open_startTime_dateEdit)
        self.startTime_dateEdit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.startTime_dateEdit.setMinimumSize(QSize(QComboBox_w, QComboBox_h))

        self.startTime_dateEdit.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.startTime_dateEdit.setMinimumDate(QDate.currentDate().addDays(-365*12))
        self.startTime_dateEdit.setMaximumDate(QDate.currentDate().addDays(365*12))
        self.startTime_dateEdit.setCalendarPopup(True)

        self.end_time_check = QCheckBox('Time End', self)
        self.end_time_check.setStyleSheet("QCheckBox::indicator { width: 30px; height: 20px; }")
        self.end_time_check.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))

        self.end_time_check.setChecked(True)
        self.end_time_check.stateChanged.connect(self.open_endTime_dateEdit)
        self.endTime_dateEdit = QDateTimeEdit(QDateTime.currentDateTime(), self)
        self.endTime_dateEdit.setMinimumSize(QSize(QComboBox_w, QComboBox_h))

        self.endTime_dateEdit.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.endTime_dateEdit.setMinimumDate(QDate.currentDate().addDays(-365*12))
        self.endTime_dateEdit.setMaximumDate(QDate.currentDate().addDays(365*12))
        self.endTime_dateEdit.setCalendarPopup(True)

        self.interval_check = QCheckBox('Interval', self)
        self.interval_check.setStyleSheet("QCheckBox::indicator {width: 30px; height: 20px;}")
        self.interval_check.setMinimumSize(QSize(QCheckBox_w, QCheckBox_h))
        self.interval_check.setChecked(True)
        self.interval_check.stateChanged.connect(self.open_interval)
        self.interval_combox = QComboBox(self)
        self.interval_combox.setEditable(True)
        self.interval_combox.setMinimumSize(QSize(QComboBox_w, QComboBox_h))

        self.interval_combox.addItems(['1', '5', '10', '15', '25', '30', 'custom'])
        self.interval_combox.setCurrentText('30')
        self.interval = 1
        self.interval_combox.currentIndexChanged.connect(self.selectionchange)

        time_box.setSpacing(5)
        time_box.addWidget(self.start_time_check, 0, 0, 1, 2)
        time_box.addWidget(self.startTime_dateEdit, 1, 0, 1, 2)
        time_box.addWidget(self.end_time_check, 0, 4, 1, 2)
        time_box.addWidget(self.endTime_dateEdit, 1, 4, 1, 2)
        time_box.addWidget(self.interval_check, 0, 6, 1, 2)
        time_box.addWidget(self.interval_combox, 1, 6, 1, 2)
        time_box.setContentsMargins(5, 5, 5, 5)
        time_wg = QFrame()
        time_wg.setFrameShape(QFrame.Box)
        # frame_wg.setStyleSheet('border-radius: 10px; border: 1px solid rgb(100, 100, 189)')
        time_wg.setLayout(time_box)


        sol_box = QGridLayout()
        self.output_title = QLabel('Solution:', self)
        self.output_title.setMinimumSize(QSize(Label_w, Label_h))
        self.output_title.setMaximumHeight(Label_h)

        self.show_ele_files_path = QLineEdit(self)
        self.show_ele_files_path.setPlaceholderText('elevation data')
        self.show_ele_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_ele_files_path = QPushButton(self)
        self.choose_ele_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_ele_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.choose_ele_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_ele_files_path.clicked.connect(self.output_ele_file)
        self.view_ele_files_path = QPushButton(self)
        self.view_ele_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_ele_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.view_ele_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_ele_files_path.clicked.connect(self.view_ele_file)

        self.show_azi_files_path = QLineEdit(self)
        self.show_azi_files_path.setPlaceholderText('azimuth data')
        self.show_azi_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.choose_azi_files_path = QPushButton(self)
        self.choose_azi_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_azi_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.choose_azi_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_azi_files_path.clicked.connect(self.output_azi_file)
        self.view_azi_files_path = QPushButton(self)
        self.view_azi_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_azi_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))

        self.view_azi_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_azi_files_path.clicked.connect(self.view_azi_file)

        self.show_ite_files_path = QLineEdit(self)
        self.show_ite_files_path.setPlaceholderText('data integrity rate')
        self.show_ite_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_ite_files_path = QPushButton(self)
        self.choose_ite_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_ite_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_ite_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_ite_files_path.clicked.connect(self.output_ite_file)
        self.view_ite_files_path = QPushButton(self)
        self.view_ite_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_ite_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_ite_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_ite_files_path.clicked.connect(self.view_ite_file)

        self.show_stu_files_path = QLineEdit(self)
        self.show_stu_files_path.setPlaceholderText('data fullness rate')
        self.show_stu_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_stu_files_path = QPushButton(self)
        self.choose_stu_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_stu_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_stu_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_stu_files_path.clicked.connect(self.output_stu_file)
        self.view_stu_files_path = QPushButton(self)
        self.view_stu_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_stu_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_stu_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_stu_files_path.clicked.connect(self.view_stu_file)

        self.show_mp_files_path = QLineEdit(self)
        self.show_mp_files_path.setPlaceholderText('code multipath data')
        self.show_mp_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_mp_files_path = QPushButton(self)
        self.choose_mp_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_mp_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_mp_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_mp_files_path.clicked.connect(self.output_mp_file)
        self.view_mp_files_path = QPushButton(self)
        self.view_mp_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_mp_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_mp_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_mp_files_path.clicked.connect(self.view_mp_file)

        self.show_gfif_files_path = QLineEdit(self)
        self.show_gfif_files_path.setPlaceholderText('phase multipath data')
        self.show_gfif_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_gfif_files_path = QPushButton(self)
        self.choose_gfif_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_gfif_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_gfif_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_gfif_files_path.clicked.connect(self.output_gfif_file)
        self.view_gfif_files_path = QPushButton(self)
        self.view_gfif_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_gfif_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_gfif_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_gfif_files_path.clicked.connect(self.view_gfif_file)

        self.show_iod_files_path = QLineEdit(self)
        self.show_iod_files_path.setPlaceholderText('ionospheric delay rate data')
        self.show_iod_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_iod_files_path = QPushButton(self)
        self.choose_iod_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_iod_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_iod_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_iod_files_path.clicked.connect(self.output_iod_file)
        self.view_iod_files_path = QPushButton(self)
        self.view_iod_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_iod_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_iod_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_iod_files_path.clicked.connect(self.view_iod_file)

        self.show_nosp_files_path = QLineEdit(self)
        self.show_nosp_files_path.setPlaceholderText('code noise data')
        self.show_nosp_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_nosp_files_path = QPushButton(self)
        self.choose_nosp_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_nosp_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_nosp_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_nosp_files_path.clicked.connect(self.output_nosp_file)
        self.view_nosp_files_path = QPushButton(self)
        self.view_nosp_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_nosp_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_nosp_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_nosp_files_path.clicked.connect(self.view_nosp_file)

        self.show_nosc_files_path = QLineEdit(self)
        self.show_nosc_files_path.setPlaceholderText('phase noise data')
        self.show_nosc_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_nosc_files_path = QPushButton(self)
        self.choose_nosc_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_nosc_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_nosc_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_nosc_files_path.clicked.connect(self.output_nosc_file)
        self.view_nosc_files_path = QPushButton(self)
        self.view_nosc_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_nosc_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_nosc_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_nosc_files_path.clicked.connect(self.view_nosc_file)

        self.show_pos_files_path = QLineEdit(self)
        self.show_pos_files_path.setPlaceholderText('standard single point positioning data')
        self.show_pos_files_path.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.choose_pos_files_path = QPushButton(self)
        self.choose_pos_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.choose_pos_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.choose_pos_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/choose_file.ico')}")
        self.choose_pos_files_path.clicked.connect(self.output_pos_file)
        self.view_pos_files_path = QPushButton(self)
        self.view_pos_files_path.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.view_pos_files_path.setMaximumSize(QSize(PushButton_w, PushButton_h))
        self.view_pos_files_path.setStyleSheet("QPushButton{border-image: url(':/icon/view_file.ico')}")
        self.view_pos_files_path.clicked.connect(self.view_pos_file)

        sol_box.setSpacing(Pagemargin)
        sol_box.addWidget(self.output_title, 0, 0, 1, 4)

        sol_box.addWidget(self.show_ele_files_path, 1, 0, 1, 2)
        sol_box.addWidget(self.choose_ele_files_path, 1, 2, 1, 1)
        sol_box.addWidget(self.view_ele_files_path, 1, 3, 1, 1)

        sol_box.addWidget(self.show_azi_files_path, 2, 0, 1, 2)
        sol_box.addWidget(self.choose_azi_files_path, 2, 2, 1, 1)
        sol_box.addWidget(self.view_azi_files_path, 2, 3, 1, 1)

        sol_box.addWidget(self.show_ite_files_path, 3, 0, 1, 2)
        sol_box.addWidget(self.choose_ite_files_path, 3, 2, 1, 1)
        sol_box.addWidget(self.view_ite_files_path, 3, 3, 1, 1)

        sol_box.addWidget(self.show_stu_files_path, 4, 0, 1, 2)
        sol_box.addWidget(self.choose_stu_files_path, 4, 2, 1, 1)
        sol_box.addWidget(self.view_stu_files_path, 4, 3, 1, 1)

        sol_box.addWidget(self.show_mp_files_path, 5, 0, 1, 2)
        sol_box.addWidget(self.choose_mp_files_path, 5, 2, 1, 1)
        sol_box.addWidget(self.view_mp_files_path, 5, 3, 1, 1)

        sol_box.addWidget(self.show_gfif_files_path, 6, 0, 1, 2)
        sol_box.addWidget(self.choose_gfif_files_path, 6, 2, 1, 1)
        sol_box.addWidget(self.view_gfif_files_path, 6, 3, 1, 1)

        sol_box.addWidget(self.show_iod_files_path, 7, 0, 1, 2)
        sol_box.addWidget(self.choose_iod_files_path, 7, 2, 1, 1)
        sol_box.addWidget(self.view_iod_files_path, 7, 3, 1, 1)

        sol_box.addWidget(self.show_nosp_files_path, 8, 0, 1, 2)
        sol_box.addWidget(self.choose_nosp_files_path, 8, 2, 1, 1)
        sol_box.addWidget(self.view_nosc_files_path, 8, 3, 1, 1)

        sol_box.addWidget(self.show_nosc_files_path, 9, 0, 1, 2)
        sol_box.addWidget(self.choose_nosc_files_path, 9, 2, 1, 1)
        sol_box.addWidget(self.view_nosp_files_path, 9, 3, 1, 1)

        sol_box.addWidget(self.show_pos_files_path, 10, 0, 1, 2)
        sol_box.addWidget(self.choose_pos_files_path, 10, 2, 1, 1)
        sol_box.addWidget(self.view_pos_files_path, 10, 3, 1, 1)

        sol_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        sol_wg = QFrame()
        sol_wg.setFrameShape(QFrame.Box)
        # frame_wg.setStyleSheet('border:1px solid #5F92B2;border-radius:5px;')
        sol_wg.setLayout(sol_box)
        scroll_wg = QScrollArea()
        scroll_wg.setWidgetResizable(True)
        scroll_wg.setWidget(sol_wg)

        # self.Progress_bar = QProgressBar(self)
        # self.Progress_bar.setGeometry(20, 680, 780, 35)
        # self_step = 0
        # self.Progress_bar.setValue(self_step)

        bnt_box = QHBoxLayout()
        self.setup_but = QPushButton('Options')
        self.setup_but.setIcon(QtGui.QIcon(':/icon/set.ico'))

        self.setup_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.setup_but.clicked.connect(self.setup_function)

        self.running_but = QPushButton('Execute')
        self.running_but.setIcon(QtGui.QIcon(':/icon/start.ico'))
        self.running_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.running_but.clicked.connect(self.running_function)

        self.running_but.setCheckable(True)
        self.running_but.toggled.connect(self.toggle_thread)
        self.running_but_ostyle = self.running_but.styleSheet()
        self.running_but_isblink = False
        self.running_but.clicked.connect(self.toggle_blink)

        self.running_but_timer = QTimer()
        self.running_but_timer.timeout.connect(self.blink)

        self.stop_but = QPushButton('Stop')
        self.stop_but.setIcon(QtGui.QIcon(':/icon/stop.ico'))
        self.stop_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.stop_but.clicked.connect(self.stop_thread)


        self.draw_sys_but = QPushButton('Plot_sys')
        self.draw_sys_but.setIcon(QtGui.QIcon(':/icon/chart.ico'))
        self.draw_sys_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.draw_sys_but.clicked.connect(self.draw_sys_function)

        self.draw_sat_but = QPushButton('Plot_sat')
        self.draw_sat_but.setIcon(QtGui.QIcon(':/icon/scatter.ico'))
        self.draw_sat_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.draw_sat_but.clicked.connect(self.draw_sat_function)

        self.log_but = QPushButton('Log')
        self.log_but.setIcon(QtGui.QIcon(':/icon/stat_file.ico'))
        self.log_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.log_but.clicked.connect(self.log_function)

        blank_label = QLabel('', self)
        blank_label.setMinimumSize(QSize(blabel_w, blabel_h))
        bnt_box.setSpacing(1)
        bnt_box.addWidget(self.setup_but)
        bnt_box.addWidget(blank_label)
        bnt_box.addWidget(self.running_but)
        bnt_box.addWidget(blank_label)
        bnt_box.addWidget(self.stop_but)
        bnt_box.addWidget(blank_label)
        bnt_box.addWidget(self.draw_sys_but)
        bnt_box.addWidget(blank_label)
        bnt_box.addWidget(self.draw_sat_but)
        bnt_box.addWidget(blank_label)
        bnt_box.addWidget(self.log_but)
        bnt_wg = QWidget()
        bnt_wg.setLayout(bnt_box)

        estimate_box = QVBoxLayout(self)
        estimate_box.addWidget(import_wg)
        estimate_box.addWidget(time_wg)
        estimate_box.addWidget(scroll_wg)
        estimate_box.addWidget(bnt_wg)
        estimate_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        mainFrame = QWidget()
        mainFrame.setLayout(estimate_box)
        self.setCentralWidget(mainFrame)

        self.log_v = QTextEdit()

        #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # default conf parameter
        self.conf_inp = copy.copy(conf_estimate().conf_inp)
        self.conf_gen = copy.copy(conf_estimate().conf_gen)
        self.conf_qc  = copy.copy(conf_estimate().conf_qc)
        # create conf class
        self.config = copy.copy(conf_estimate().conf)
        #---------------------------------------------------------------------------------------------
        global curdir
        self.file_folder   = curdir
        self.ele_filename  = 'result' + '.ele'
        self.azi_filename  = 'result' + '.azi'
        self.ite_filename  = 'result' + '.inte'
        self.stu_filename  = 'result' + '.satu'
        self.mp_filename   = 'result' + '.pmp'
        self.gfif_filename = 'result' + '.lmp'
        self.iod_filename  = 'result' + '.iod'
        self.nosp_filename = 'result' + '.pnoise'
        self.nosc_filename = 'result' + '.lnoise'
        self.pos_filename  = 'result' + '.pos'


    def toggle_thread(self, checked):
        if checked:
            self.running_but.setEnabled(False)
            self.running_but.setText("Running")
            self.running_but.setIcon(QtGui.QIcon(':/icon/run.ico'))
            self.running_but.setProperty("Running", True)
        else:
            self.running_but.setEnabled(False)

    def toggle_blink(self):
        if not self.running_but_timer.isActive():
            self.running_but.setStyleSheet("""
            QPushButton:disabled {
                background-color: lightblue;
                color: green;
                font-weight: bold;
            }
        """)
            self.running_but_timer.start(500)
        else:
            self.running_but.setStyleSheet("""
            QPushButton:disabled {
                background-color: lightblue;
                color: k;
                font-weight: bold;
            }
        """)
            self.running_but_timer.stop()

    def blink(self):
        if self.running_but_isblink:
            self.running_but.setStyleSheet("""
            QPushButton:disabled {
                background-color: lightblue;
                color: green;
                font-weight: bold;
            }
        """)
            self.running_but_isblink = False
        else:
            self.running_but.setStyleSheet("""
            QPushButton:disabled {
                background-color: lightblue;
                color: k;
                font-weight: bold;
            }
        """)
            self.running_but_isblink = True

    def stop_thread(self):
        if hasattr(self, 'thread_sol'):
            self.thread_sol.stop_expos()
            # self.thread_sol.stop()
            self.running_but.setChecked(False)
            self.running_but.setText("Execute")
            self.running_but.setIcon(QtGui.QIcon(':/icon/start.ico'))
            self.running_but.setEnabled(True)
            self.running_but.setProperty("running", False)

            self.running_but.setStyleSheet(self.running_but_ostyle)
            self.running_but_timer.stop()


    def printLog(self, logStr):
        import time
        import datetime
        time.sleep(0.001)
        nowtimeStrft = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        logStr = '[' + nowtimeStrft + ']: ' + logStr
        self.log_v.setFontWeight(QFont.Normal)
        self.log_v.append(logStr)

    def import_obs_file(self):
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        unzip_default_download_path = desktop_path
        if os.path.exists(unzip_default_download_path):
            filepath, filetype = QFileDialog.getOpenFileName(self, 'RINEX OBS File', './', 'RINEX OBS(*O.rnx *.*o *.*O *.obs *rnx);;All_File(*)')
        else:
            filepath, filetype = QFileDialog.getOpenFileName(self, 'RINEX OBS File', './', 'RINEX OBS(*O.rnx *.*o *.*O *.obs *rnx);;All_File(*)')

        if filetype != '':
            # program path to file path
            os.chdir(os.path.dirname(filepath))
            # first_time, last_time, interval for observation data
            from map import time_info
            first_time, last_time, interval = time_info.obs_time(filepath)

            self.endTime_dateEdit.setMinimumDateTime(first_time)
            self.endTime_dateEdit.setMaximumDateTime(last_time)
            self.startTime_dateEdit.setDateTime(first_time)
            self.endTime_dateEdit.setDateTime(last_time)

            self.startTime_dateEdit.setDateTime(first_time)
            self.endTime_dateEdit.setDateTime(last_time)
            if interval != None:
                self.interval_combox.setCurrentText(str(interval))
            else:
                self.interval_combox.setCurrentIndex(-1)
                QMessageBox.information(self, 'Prompt', 'No sampling interval info. Please resume entering')
                logger.error('No sampling interval info. Please resume entering')


            # set output
            self.file_folder = os.path.dirname(filepath)
            obsfile_name = os.path.basename(filepath)
            self.file_header, file_basename = os.path.splitext(obsfile_name)
            output_folder      = self.file_folder + '/result/'
            self.ele_filename  = self.file_header + '.ele'
            self.azi_filename  = self.file_header + '.azi'
            self.ite_filename  = self.file_header + '.inte'
            self.stu_filename  = self.file_header + '.satu'
            self.mp_filename   = self.file_header + '.pmp'
            self.gfif_filename = self.file_header + '.lmp'
            self.iod_filename  = self.file_header + '.iod'
            self.nosp_filename = self.file_header + '.pnoise'
            self.nosc_filename = self.file_header + '.lnoise'
            self.pos_filename  = self.file_header + '.pos'
            self.show_obs_files_path.setText(filepath)
            self.show_ele_files_path.setText(output_folder + self.ele_filename)
            self.show_azi_files_path.setText(output_folder + self.azi_filename)
            self.show_ite_files_path.setText(output_folder + self.ite_filename)
            self.show_stu_files_path.setText(output_folder + self.stu_filename)
            self.show_mp_files_path.setText(output_folder + self.mp_filename)
            self.show_gfif_files_path.setText(output_folder + self.gfif_filename)
            self.show_iod_files_path.setText(output_folder + self.iod_filename)
            self.show_nosp_files_path.setText(output_folder + self.nosp_filename)
            self.show_nosc_files_path.setText(output_folder + self.nosc_filename)
            self.show_pos_files_path.setText(output_folder + self.pos_filename)

            self.printLog('Load RINEX OBS File:' + obsfile_name)
            logger.info('Load RINEX OBS File:' + obsfile_name)


    def view_obs_file(self):
        if os.path.exists(self.show_obs_files_path.text()):
            # self.s = Look_Over_File_details(self.show_obs_files_path.text())
            self.s = Look_Over_File_details(self.show_obs_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'No load data!')
            logger.error('No load data!')


    def import_nav_file(self):
        desktop_path = os.path.join(os.path.expanduser('~'), "Desktop")
        desktop_path = desktop_path.replace("\\", "/")
        unzip_default_download_path = desktop_path
        if os.path.exists(unzip_default_download_path):
            filepath, filetype = QFileDialog.getOpenFileName(self, 'RINEX NAV File', './', 'RINEX NAV(*N.rnx *.nav *.gnav *.hnav *.qnav *.*n *.*g *.*h *.*l *.*j *.*q *.*p);;All_File(*)')
        else:
            filepath, filetype = QFileDialog.getOpenFileName(self, 'RINEX NAV File', './', 'RINEX NAV(*N.rnx *.nav *.gnav *.hnav *.qnav *.*n *.*g *.*h *.*l *.*j *.*q *.*p);;All_File(*)')
        if filetype != '':
            self.show_nav_files_path.setText(filepath)
        navfile_name = os.path.basename(filepath)
        self.printLog('Load RINEX NAV File:' + navfile_name)
        logger.info('Load RINEX NAV File:' + navfile_name)


    def view_nav_file(self):
        if os.path.exists(self.show_nav_files_path.text()):
            self.s = Look_Over_File_details(self.show_nav_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'No load data!')
            logger.error('No load data!')

    def open_startTime_dateEdit(self):
        if self.start_time_check.isChecked() == True:
            self.startTime_dateEdit.setEnabled(True)
        else:
            self.startTime_dateEdit.setEnabled(False)

    def open_endTime_dateEdit(self):
        if self.end_time_check.isChecked() == True:
            self.endTime_dateEdit.setEnabled(True)
        else:
            self.endTime_dateEdit.setEnabled(False)

    def open_interval(self):
        if self.interval_check.isChecked() == True:
            self.interval_combox.setEnabled(True)
        else:
            self.interval_combox.setEnabled(False)

    #  custom
    def selectionchange(self):
        if self.interval_combox.currentText() == 'custom':
            self.s = selfdiy_intv(self.interval, self.ratio)
            self.s.mySignal.connect(self.getDialogSignal)
            self.s.exec_()

    def getDialogSignal(self, connect):
        diy_intvi = str(connect)
        self.interval_combox.addItem(diy_intvi)
        self.interval_combox.setCurrentText(diy_intvi)

    def output_ele_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_ele_files_path.setText(save_path + '/' + self.ele_filename)

    def output_azi_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_azi_files_path.setText(save_path + '/' + self.azi_filename)

    def output_ite_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_ite_files_path.setText(save_path + '/' + self.ite_filename)

    def output_stu_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_stu_files_path.setText(save_path + '/' + self.stu_filename)

    def output_mp_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_mp_files_path.setText(save_path + '/' + self.mp_filename)

    def output_gfif_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_gfif_files_path.setText(save_path + '/' + self.gfif_filename)

    def output_iod_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_iod_files_path.setText(save_path + '/' + self.iod_filename)

    def output_nosp_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_nosp_files_path.setText(save_path + '/' + self.nosp_filename)

    def output_nosc_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_nosc_files_path.setText(save_path + '/' + self.nosc_filename)

    def output_pos_file(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Output Path', self.file_folder)
        if save_path == '':
            pass
        else:
            self.show_pos_files_path.setText(save_path + '/' + self.pos_filename)


    def view_ele_file(self):
        if os.path.exists(self.show_ele_files_path.text()):
            self.s = solfile_view(self.show_ele_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_azi_file(self):
        if os.path.exists(self.show_azi_files_path.text()):
            self.s = solfile_view(self.show_azi_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_ite_file(self):
        if os.path.exists(self.show_ite_files_path.text()):
            self.s = solfile_view(self.show_ite_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_stu_file(self):
        if os.path.exists(self.show_stu_files_path.text()):
            self.s = solfile_view(self.show_stu_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_mp_file(self):
        if os.path.exists(self.show_mp_files_path.text()):
            self.s = solfile_view(self.show_mp_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_gfif_file(self):
        if os.path.exists(self.show_gfif_files_path.text()):
            self.s = solfile_view(self.show_gfif_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_iod_file(self):
        if os.path.exists(self.show_iod_files_path.text()):
            self.s = solfile_view(self.show_iod_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_nosp_file(self):
        if os.path.exists(self.show_nosp_files_path.text()):
            self.s = solfile_view(self.show_nosp_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_nosc_file(self):
        if os.path.exists(self.show_nosc_files_path.text()):
            self.s = solfile_view(self.show_nosc_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def view_pos_file(self):
        if os.path.exists(self.show_pos_files_path.text()):
            self.s = solfile_view(self.show_pos_files_path.text(), self.ratio)
            self.s.show()
        else:
            QMessageBox.information(self, 'Prompt', 'Data does not exist')

    def setup_function(self):
        self.option = Data_Preprocessing_Setup(self.conf_gen, self.conf_qc, self.ratio)
        self.option.show()
        self.option._signal.connect(self.get_option)

    def get_option(self, conf_gen, conf_qc):
        self.conf_gen = conf_gen
        self.conf_qc  = conf_qc

    def running_function(self):
        if self.show_obs_files_path.text() != '' and self.show_nav_files_path.text() != '' and self.interval_combox.currentText() != '':
            self.conf_inp['rinexo']     = self.show_obs_files_path.text()
            self.conf_inp['rinexn']     = self.show_nav_files_path.text()

            self.conf_gen['start_time'] = str(self.startTime_dateEdit.dateTime().toString('yyyy MM dd HH mm ss'))
            self.conf_gen['end_time']   = str(self.endTime_dateEdit.dateTime().toString('yyyy MM dd HH mm ss'))
            self.conf_gen['interval']   = self.interval_combox.currentText()

            self.config.set('inp', 'rinexo', self.conf_inp['rinexo'])
            self.config.set('inp', 'rinexn', self.conf_inp['rinexn'])

            self.config.set('gen', 'start_time', self.conf_gen['start_time'])
            self.config.set('gen', 'end_time',   self.conf_gen['end_time'])
            self.config.set('gen', 'interval',   self.conf_gen['interval'])
            self.config.set('gen', 'satsys',     self.conf_gen['satsys'])
            self.config.set('gen', 'gps_band',   self.conf_gen['gps_band'])
            self.config.set('gen', 'glo_band',   self.conf_gen['glo_band'])
            self.config.set('gen', 'gal_band',   self.conf_gen['gal_band'])
            self.config.set('gen', 'qzs_band',   self.conf_gen['qzs_band'])
            self.config.set('gen', 'bds_band',   self.conf_gen['bds_band'])
            self.config.set('gen', 'irn_band',   self.conf_gen['irn_band'])
            self.config.set('gen', 'sbs_band',   self.conf_gen['sbs_band'])

            self.config.set('qc', 'elmin',      self.conf_qc['elmin'])
            self.config.set('qc', 'cnrmin',     self.conf_qc['cnrmin'])
            self.config.set('qc', 'sateph',     self.conf_qc['sateph'])
            self.config.set('qc', 'ionoopt',    self.conf_qc['ionoopt'])
            self.config.set('qc', 'tropopt',    self.conf_qc['tropopt'])
            self.config.set('qc', 'pos_banpos', self.conf_qc['pos_banpos'])
            self.config.set('qc', 'pos_option', self.conf_qc['pos_option'])
            self.config.set('qc', 'pos_elcut',  self.conf_qc['pos_elcut'])
            self.config.set('qc', 'pos_cnrcut', self.conf_qc['pos_cnrcut'])
            # self.config.set('qc', 'mw_limit',   self.conf_qc['mw_limit'])
            # self.config.set('qc', 'gf_limit',   self.conf_qc['gf_limit'])
            self.config.set('qc', 'pos_kin',    self.conf_qc['pos_kin'])
            self.config.set('qc', 'int_pcs',    self.conf_qc['int_pcs'])

            confname = self.file_header + '.ini'
            confpath = os.path.join(self.file_folder, confname)
            self.config.write(open(confpath, 'w', encoding='utf-8'))

            # independent thread run
            self.thread_sol = Worker(confpath)
            self.thread_sol.sig1.connect(self.comput_tips)
            self.thread_sol.start()
        else:
            QMessageBox.information(self, 'Prompt', 'Please Load data')
            logger.error('No load data!')

            self.running_but.setChecked(False)
            self.running_but.setText("Execute")
            self.running_but.setIcon(QtGui.QIcon(':/icon/start.ico'))
            self.running_but.setEnabled(True)
            self.running_but.setProperty("running", False)

            self.running_but.setStyleSheet(self.running_but_ostyle)
            self.running_but_timer.stop()

    def comput_tips(self, tips):
        self.running_but.setChecked(False)
        self.running_but.setText("Execute")
        self.running_but.setIcon(QtGui.QIcon(':/icon/start.ico'))
        self.running_but.setEnabled(True)
        self.running_but.setProperty("running", False)

        self.running_but.setStyleSheet(self.running_but_ostyle)
        self.running_but_timer.stop()

        QMessageBox.information(self, 'Prompt', tips)
        self.printLog('Solution completed')
        logger.error(tips)

    def draw_sys_function(self):
        self.s = plot_sys(self.ratio, self.curdir_ini)
        self.s.show()

    def draw_sat_function(self):
        self.s = plot_sat(self.ratio, self.curdir_ini)
        self.s.show()

    def log_function(self):
        # self.printLog('End of The Program Running')
        self.s = log_view(self.log_v, self.ratio)
        # self.Signal_OneParameter.emit('End of The Program Running')
        self.s.show()


class Look_Over_File_details(QMainWindow):
    def __init__(self, converted_file, ratio):
        super().__init__()
        self.ratio = ratio
        file_name = QFileInfo(converted_file).fileName()
        self.setWindowTitle(file_name)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.resize(500*self.ratio, 400*self.ratio)
        # self.setGeometry(490, 150, 1000, 800)
        self.setup_ui(converted_file)

    def setup_ui(self, converted_file):
        widget = QWidget()
        gride = QHBoxLayout()
        textEdit = QTextEdit()
        textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)

        with open(converted_file, 'r') as f:
            msg = f.read()
        f.close()
        textEdit.setPlainText(msg)
        gride.addWidget(textEdit)
        gride.setContentsMargins(0 ,0, 0, 0)
        widget.setLayout(gride)
        self.setCentralWidget(widget)
        textEdit.setFont(QFont("Source Code Pro", 9))


class solfile_view(QMainWindow):
    def __init__(self, solfile_path, ratio):
        super().__init__()
        self.ratio = ratio
        file_name = QFileInfo(solfile_path).fileName()
        self.setWindowTitle(file_name)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.setGeometry(490, 150, 1000, 800)
        self.resize(500*self.ratio, 400*self.ratio)
        self.setup_ui(solfile_path)

    def setup_ui(self, solfile_path):
        from GUI_tableview import PandasModel, Table
        # load data
        import pandas as pd
        if os.path.splitext(solfile_path)[-1] == '.pos':
            data = pd.read_csv(solfile_path, '\s+', header=0)
        else:
            data = pd.read_csv(solfile_path, '\s+', header=0)

        status = self.statusBar()
        status.showMessage('Row:{} Column:{}'.format(data.shape[0], data.shape[1]))
        # tableview
        model = PandasModel(data)
        table = Table(model)

        widget = QWidget()
        layout_h = QHBoxLayout()
        layout_h.setContentsMargins(0, 1, 1, 0)

        layout_h.addWidget(table)
        widget.setLayout(layout_h)
        self.setCentralWidget(widget)


class selfdiy_intv(QDialog):
    mySignal = pyqtSignal(str)
    def __init__(self, file_interval, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Custom Interval")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.resize(330*self.ratio, 80*self.ratio)
        self.file_interval = file_interval
        self.setup_ui()

    def setup_ui(self):
        interval_box = QHBoxLayout()
        self.edit = QLineEdit(self)
        self.edit.setMinimumSize(QSize(60*self.ratio, 25*self.ratio))
        self.edit.setPlaceholderText("eg.：20s")

        self.edit_button = QPushButton("OK", self)
        self.edit_button.setMinimumSize(QSize(40*self.ratio, 25*self.ratio))
        self.edit_button.clicked.connect(self.one)

        interval_box.setSpacing(10*self.ratio)
        interval_box.addWidget(self.edit)
        interval_box.addWidget(self.edit_button)
        self.setLayout(interval_box)

    def one(self):
        if float(self.edit.text()) % self.file_interval != 0:
            QMessageBox.information(self, 'Error', 'defined interval should be an integer multiple of the origin interval (%s second)'% self.file_interval)
            return
        diy_intvi = self.edit.text()
        self.mySignal.emit(diy_intvi)
        self.hide()
        return diy_intvi


class log_view(QMainWindow):
    def __init__(self, qTextEdit, ratio):
        super().__init__()
        self.setWindowTitle('Log')
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.setGeometry(490, 150, 1000, 800)
        self.resize(500*ratio, 400*ratio)
        self.setup_ui(qTextEdit)

    def setup_ui(self, qTextEdit):
        self.logPrint = qTextEdit
        self.logPrint.setLineWrapMode(QTextEdit.NoWrap)
        self.logPrint.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.logPrint.setReadOnly(True)

        layout_h = QHBoxLayout()
        layout_h.addWidget(self.logPrint)
        layout_h.setContentsMargins(0, 0, 0, 0)

        widget = QFrame()
        # widget.setFrameShape(QFrame.StyledPanel)
        widget.setLayout(layout_h)
        self.setCentralWidget(widget)


def on_exit():
    logger.info('Program ended.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting the program.")
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    ratio = dpi/96
    win = Data_Preprocessing(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(12*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())