from PyQt5 import QtCore, QtGui
from PyQt5.Qt import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sys
import os
from time import strftime, localtime
import numpy as np
import datetime

#---------------------------------PYQT5  matplotlib-------------------------------
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QSizePolicy, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
#----------------------------------------------------------------------------------

#---------------------------PYQT5 html---------------------------------------------
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
#----------------------------------------------------------------------------------
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QPushButton
# import qdarkstyle
#----------------------------read function-----------------------------------------
from read_sol import read_list, read_data
#----------------------------------------------------------------------------------
import resources_rc
import warnings
warnings.filterwarnings(action='ignore', message='Passing the fontdict parameter of _set_ticklabels() positionally is deprecated since Matplotlib 3.3')
warnings.filterwarnings(action='ignore', message='Attempting to set identical bottom == top == 0.5 results in singular transformations; automatically expanding')
warnings.filterwarnings(action='ignore', message='Passing the fontdict parameter of _set_ticklabels() positionally is deprecated since Matplotlib 3.3; the parameter will become keyword-only two minor releases later')
warnings.filterwarnings(action='ignore')


# global variable
sol_data = np.nan

class Worker_plot(QThread):
    sig = pyqtSignal(str)
    sig1 = pyqtSignal(dict)

    def __init__(self, sol_path):
        super(Worker_plot, self).__init__()
        self.sol_path = sol_path

    def run(self):
        self.sig1.emit()


class Worker(QThread):
    sig = pyqtSignal(str)
    sig1 = pyqtSignal(dict)

    def __init__(self, sol_path):
        super(Worker, self).__init__()
        self.sol_path = sol_path

    def run(self):
        sol_file_dict, path_ = read_list(self.sol_path)
        sol_data = read_data(sol_file_dict, path_)
        self.sig1.emit(sol_data)


curdir = os.getcwd() # work path

class plot_sys(QMainWindow):
    def __init__(self, ratio, curdir_ini):
        super(plot_sys, self).__init__()
        self.ratio = ratio
        self.curdir_ini = curdir_ini
        self.setWindowTitle("Plot_system")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.resize(1000, 800)
        self.resize(600*self.ratio, 500*self.ratio)
        # self.setFixedSize(600*self.ratio, 500*self.ratio)
        # self.setMinimumSize(QSize(950, 700))
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        # self.setFixedSize(1000, 870)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        # self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.setup_ui()
        # data
        self.sol_data = None

    def setup_ui(self):
        #-------------------------------------------------------
        lable_w    = 60*self.ratio
        lable_h    = 25*self.ratio
        zlable_w   = 50*self.ratio
        zlable_h   = 25*self.ratio
        button_w   = 80*self.ratio
        button_h   = 25*self.ratio
        bobox_w    = 150*self.ratio
        bobox_h    = 25*self.ratio
        LineEdit_w = 350*self.ratio
        LineEdit_h = 25*self.ratio
        Pagemargin = 5*self.ratio
        canvas_h   = 240*self.ratio
        #-------------------------------------------------------
        self.bar = self.menuBar()
        self.File = self.bar.addMenu("File")
        # self.true_point = self.File.addAction("Set")
        # self.true_point.triggered.connect(self.true_gui)
        self.save = self.File.addAction("Save")
        self.save.triggered.connect(self.save_figure)
        self.Map = self.bar.addMenu("Mapview")
        self.point_map = self.Map.addAction("Pos2map")
        self.point_kml = self.Map.addAction("Pos2kml")

        #-----------------------status bar------------------------
        # self.status = self.statusBar()
        # self.showWechat = QLabel("E-mail:L_team@163.com")
        #
        # self.status.addPermanentWidget(self.showWechat, stretch=0)
        #
        # timer = QtCore.QTimer(self)
        # timer.timeout.connect(self.status_bar_show_msg)
        # timer.start()

        #----------------------------------------------------

        sol_box = QGridLayout()
        self.sol_files_lable = QLabel('File Path', self)
        self.sol_files_lable.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.sol_files_lable.setAlignment(Qt.AlignCenter)
        self.sol_files_lable.setMinimumSize(QSize(lable_w, lable_h))
        self.sol_files_lable.setMaximumSize(QSize(lable_w, lable_h))

        self.sol_files_edit = QLineEdit(self)
        self.sol_files_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sol_files_edit.setStyleSheet("QLineEdit"
                                "{"
                                # "border : 5px solid;"
                                "border-color : black"
                                "}")

        self.sol_files_edit.setAttribute(QtCore.Qt.WA_MacShowFocusRect, 0)
        # sol_files_edit.setAlignment(Qt.AlignCenter)
        self.sol_files_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.sol_files_edit.setPlaceholderText("C:/Users/Admin/Desktop/aber0010.list")

        self.sol_files_btn = QPushButton('Select', self)
        self.sol_files_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.sol_files_btn.setMinimumSize(QSize(button_w, button_h))
        self.sol_files_btn.clicked.connect(self.choose_file)

        #------------------------------------------------------

        # fig_box = QHBoxLayout()
        self.figtype_label = QLabel('Fig Type', self)
        self.figtype_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.figtype_label.setAlignment(Qt.AlignCenter)
        self.figtype_label.setMinimumSize(QSize(lable_w, lable_h))
        self.figtype_label.setMaximumSize(QSize(lable_w, lable_h))

        self.figtype_combobox = QComboBox(self)
        self.figtype_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.figtype_gnss = ['Ele', 'Azi', 'C/N0', 'Code MP', 'Phase MP', 'IOD', 'DIR', 'DSR', 'Code Noise', 'Phase Noise', 'Skyplot', 'Sat Vis', 'DOP', 'XYZ', 'NEU', 'CDF', 'Boxplot',
                             'Sat Vis MP', 'Sat Vis C/N0', 'Sat Vis IOD', 'Sat Vis Code Noise', 'Sat Vis Phase Noise', 'Skyplot MP', 'Skyplot C/N0', 'Skyplot IOD', 'Skyplot Code Noise', 'Skyplot Phase Noise']
        self.figtype_combobox.addItems(self.figtype_gnss)
        self.figtype_combobox.setMinimumSize(QSize(bobox_w, bobox_h))
        self.figtype_combobox.setMaximumHeight(bobox_h)
        self.figtype_combobox.currentIndexChanged.connect(self.select_fig)

        self.sys_label = QLabel('Sys', self)
        self.sys_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sys_label.setAlignment(Qt.AlignCenter)
        self.sys_label.setMinimumSize(QSize(zlable_w, zlable_h))
        self.sys_label.setMaximumSize(QSize(zlable_w, zlable_h))

        self.sys_combobox = QComboBox(self)
        self.sys_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sys_ty = ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']
        # sys_combobox.setStyleSheet("#typeCmb{border:1px solid rgb(204,204,204);border-radius:3px;height:28px;}QAbstractItemView::item {height: 28px;}")
        self.sys_combobox.addItems(['All'])
        self.sys_combobox.setMinimumSize(QSize(bobox_w, bobox_h))
        self.sys_combobox.setMaximumHeight(bobox_h)
        self.sys_combobox.currentIndexChanged.connect(self.select_sys)

        self.band_combobox = QComboBox()
        self.band_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.band_combobox.addItems(['L1', 'L2', 'L5'])
        self.band_gps = ['L1', 'L2', 'L5']
        self.band_glo = ['G1', 'G2', 'G3']
        self.band_gal = ['E1', 'E5a', 'E5b', 'E6', 'E5']
        self.band_bds = ['B1I', 'B2I', 'B3I', 'B1c', 'B2a', 'B2b', 'B2ab']
        self.band_qzs = ['L1', 'L2', 'L5', 'L6']
        self.band_irn = ['L5', 'S', 'L1']
        self.band_sbs = ['L1', 'L5']
        self.band_all = ['L1', 'L2', 'L5', 'G1', 'G2', 'E1', 'E5a', 'E5b', 'E6', 'E5', 'B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B2c', 'L1', 'L2', 'L5', 'L5', 'S', 'L1', 'L5']
        self.band_combobox.setMinimumSize(QSize(bobox_w, bobox_h))

        #--------------------------------------------------------------------
        self.dop_ty = ['All', 'NS', 'GDOP', 'PDOP', 'HDOP', 'VDOP']
        self.disable_first_checkbox = False
        dop_box = QHBoxLayout()
        self.dop_check = {}
        for i, ty_ in enumerate(self.dop_ty):
            self.dop_check[ty_]  = QCheckBox(ty_)

            dop_box.addWidget(self.dop_check[ty_])
            self.dop_check[ty_].stateChanged.connect(self.check_state_changed)
        self.dop_check[self.dop_ty[0]].setChecked(True)

        self.dop_wg = QWidget()
        self.dop_wg.setLayout(dop_box)
        self.dop_wg.setContentsMargins(0, 0, 0, 0)
        #---------------------------------------------------------------------

        self.draw_btn = QPushButton('Execute', self)
        self.draw_btn.setMinimumSize(QSize(button_w, button_h))
        self.draw_btn.clicked.connect(self.plot_fig)

        sol_box.setSpacing(Pagemargin)
        sol_box.addWidget(self.sol_files_lable, 0, 0, 1, 1)
        sol_box.addWidget(self.sol_files_edit, 0, 1, 1, 5)
        sol_box.addWidget(self.sol_files_btn, 0, 6, 1, 1)
        sol_box.addWidget(self.figtype_label, 1, 0, 1, 1)
        sol_box.addWidget(self.figtype_combobox, 1, 1, 1, 2)
        sol_box.addWidget(self.sys_label, 1, 3, 1, 1)
        sol_box.addWidget(self.sys_combobox, 1, 4, 1, 1)
        sol_box.addWidget(self.band_combobox, 1, 5, 1, 1)
        sol_box.addWidget(self.dop_wg, 1, 5, 1, 1)

        sol_box.addWidget(self.draw_btn, 1, 6, 1, 1)
        sol_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        # spacerItem4 = QSpacerItem(1, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # fig_box.addItem(spacerItem4)

        self.band_combobox.setVisible(False)
        self.dop_wg.setVisible(False)

        sol_wg = QFrame()
        sol_wg.setFrameShape(QFrame.StyledPanel)
        sol_wg.setLayout(sol_box)
        sol_wg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        #--------------------------------------------------------------------------------------------
        canvas_wg = QFrame()
        canvas_wg.setFrameShape(QFrame.StyledPanel)
        canvas_wg.setLayout(self.canvas_())
        canvas_wg.setMinimumHeight(canvas_h)
        canvas_wg.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        #---------------------------------------------------------------------------------------------
        self.work_path = os.getcwd()
        # ---------------------------------------------------------------------------------------------

        splitterRight = QSplitter(Qt.Vertical)
        splitterRight.addWidget(sol_wg)
        splitterRight.addWidget(canvas_wg)
        # splitterRight.addWidget(self.tab)

        layout = QHBoxLayout()
        layout.addWidget(splitterRight)
        layout.setContentsMargins(0, 0, 0, 0)
        #
        mainFrame = QWidget()
        mainFrame.setLayout(layout)
        self.setCentralWidget(mainFrame)
        self.show()

        # define true coordinate
        self.true_pos = []

    def canvas_(self):
        figure_ntb_h = 25*self.ratio
        Pagemargin   = 5*self.ratio
        self.figure_layout = QVBoxLayout(self)
        self.figure = Canvas()
        self.figure_ntb = NavigationToolbar(self.figure, self)
        # self.figure_ntb.setStyleSheet("{background:white}")
        self.figure_ntb.setMaximumHeight(figure_ntb_h)
        self.figure.setStyleSheet("{background:white}")
        self.figure_ntb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.figure_layout.addWidget(self.figure_ntb)
        self.figure_layout.addWidget(self.figure)
        self.figure_layout.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        return self.figure_layout

    def status_bar_show_msg(self):
        self.status.showMessage("East China University of Technology", 0)

    def check_state_changed(self):
        sender = self.sender()
        if sender == self.dop_check[self.dop_ty[0]]:
            if sender.isChecked():
                self.disable_first_checkbox = True
                for option in self.dop_ty[1:]:
                    self.dop_check[option].setChecked(False)
                self.disable_first_checkbox = False
        elif not self.disable_first_checkbox:
            self.dop_check[self.dop_ty[0]].setChecked(False)

    def save_figure(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Figure", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;SVG Files (*.svg *.svgz)")
        if filename:
            resolution, ok = QInputDialog.getDouble(self, "Select Dpi", "Please Input Dpi:", 300, 1, 10000, 2)
            if ok:
                size, ok1 = QInputDialog.getText(self, "Select Size", "Please Input Size（Width*Height）:", QLineEdit.Normal, '12.9*7')
                if ok1:
                    if '*' in size and len(size.split('*'))==2:
                        font_size_, ok2 = QInputDialog.getInt(self, "Font Size", "Please Input Font Size:", QLineEdit.Normal, 24)

                        if ok2:
                            file_ext = filename.split('.')[-1]
                            # set figure size
                            width, height = size.split('*')
                            self.figure.fig.set_size_inches(float(width), float(height))
                            # set fugure ax font size
                            font = {'family': 'Times New Roman', 'size': font_size_}
                            ax = self.figure.fig.axes[0]
                            if len(self.figure.fig.axes) > 1:
                                ax_r = self.figure.fig.axes[1]
                                ax_r_bool = True
                            else:
                                ax_r_bool = False
                            ax.xaxis.label.set_fontproperties(font)
                            ax.yaxis.label.set_fontproperties(font)
                            ax.xaxis.set_tick_params(labelsize=font['size'])
                            ax.yaxis.set_tick_params(labelsize=font['size'])
                            if ax_r_bool:
                                ax_r.xaxis.label.set_fontproperties(font)
                                ax_r.yaxis.label.set_fontproperties(font)
                                ax_r.xaxis.set_tick_params(labelsize=font['size'])
                                ax_r.yaxis.set_tick_params(labelsize=font['size'])
                            try:
                                for text in ax.get_legend().texts:
                                    text.set_fontsize(font['size'])
                            except AttributeError:
                                pass

                            # # set marksize
                            # new_markersize = 8
                            # for line in ax.get_lines():
                            #     line.set_markersize(new_markersize)

                            # save figure
                            self.figure.fig.savefig(filename, dpi=resolution, format=file_ext, bbox_inches='tight')
                            QMessageBox.information(self, 'Tips', 'Success Save Figure')
                    else:
                        QMessageBox.information(self, 'Tips', 'Input Size Mode Error')


    # --------------File select---------------------------------------------------------------------------------------------

    def choose_file(self):
        self.sol_filename = ''
        self.sol_filename, self.filetype = QFileDialog.getOpenFileName(self, 'select file', './', 'solution file (*.list)')
        if len(self.sol_filename) != 0:
            os.chdir(os.path.dirname(self.sol_filename))
            try:
                self.sol_files_edit.setText(self.sol_filename)
                # Independent Threads
                self.thread = Worker(self.sol_filename)
                self.thread.sig1.connect(self.read_sol)
                self.thread.start()
                print('[{}] success load solution file: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.sol_filename))
            except Exception as e:
                print('[{}] erross: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))
        else:
            try:
                self.sol_files_edit.setText('')
                QMessageBox.information(self, 'Tips', 'no select data')
                print('[{}] no load solution file'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
            except Exception as e:
                print('[{}] erross: {}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), e))

    def read_sol(self, sol_data_):
        global sol_data
        sol_data = sol_data_
        self.sol_data = sol_data
        from quality_check import rtkcmn as common
        prn_id = []
        sol_sys = np.array(self.sol_data['sat'])
        self.prn_sys = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS', 'All'], [[], [], [], [], [], [], [], []]))
        for i in range(len(sol_sys)):
            prn_ = common.sat2id(sol_sys[i])
            prn_id.append(prn_)
            self.prn_sys['All'].append(prn_)
            if prn_[0] == 'G':
                self.prn_sys['GPS'].append(prn_)
            elif prn_[0] == 'R':
                self.prn_sys['GLO'].append(prn_)
            elif prn_[0] == 'E':
                self.prn_sys['GAL'].append(prn_)
            elif prn_[0] == 'C':
                self.prn_sys['BDS'].append(prn_)
            elif prn_[0] == 'J':
                self.prn_sys['QZS'].append(prn_)
            elif prn_[0] == 'I':
                self.prn_sys['NavIC'].append(prn_)
            elif prn_[0] == 'S':
                self.prn_sys['SBS'].append(prn_)
        self.prn_id = prn_id.copy()
        self.prn_id_ = self.prn_sys['GPS']
        self.point_map.triggered.connect(lambda checked: self.map_gui(self.sol_data, self.curdir_ini))
        self.point_kml.triggered.connect(lambda checked: self.kml_gui(self.sol_data, self.sol_filename))
        print('[{}] success load satellite info of observation file'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        QMessageBox.information(self, 'Tips', 'Load success')

# --------------logical function---------------------------------------------------------------------------------------------
    def select_fig(self):
        self.sys_combobox.clear()
        if 'Ele' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Azi' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'C/N0' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Code MP' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Phase MP' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'IOD' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'DIR' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'DSR' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Code Noise' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Phase Noise' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Skyplot' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All', 'GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Sat Vis' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All', 'GPS', 'BDS', 'GLO', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'DOP' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS', 'MIX'])
            self.dop_wg.setVisible(True)
            self.band_combobox.setVisible(False)

        elif 'XYZ' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All', 'GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS', 'MIX'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'NEU' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['All', 'GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS', 'MIX'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'CDF' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS', 'MIX'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Boxplot' in self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS', 'MIX'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(False)

        elif 'Sat Vis MP' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Sat Vis C/N0' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Sat Vis IOD' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'GAL', 'BDS', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Sat Vis Code Noise' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Sat Vis Phase Noise' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Skyplot MP' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Skyplot C/N0' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Skyplot IOD' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'GAL', 'BDS', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Skyplot Code Noise' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)

        elif 'Skyplot Phase Noise' == self.figtype_combobox.currentText():
            self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
            self.dop_wg.setVisible(False)
            self.band_combobox.setVisible(True)


    def select_sys(self):
        if self.sol_data != None:
            stat =1
        else:
            stat = 0
        self.band_combobox.clear()
        if 'All' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['All']
                self.band_combobox.addItems(self.band_all)
                self.band_id = self.band_all

        elif 'GPS' in self.sys_combobox.currentText() :
            if stat > 0:
                self.prn_id_ = self.prn_sys['GPS']
                self.band_combobox.addItems(self.band_gps)
                self.band_id = self.band_gps

        elif 'GLO' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['GLO']
                self.band_combobox.addItems(self.band_glo)
                self.band_id = self.band_glo

        elif 'GAL' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['GAL']
                self.band_combobox.addItems(self.band_gal)
                self.band_id = self.band_gal

        elif 'BDS' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['BDS']
                self.band_combobox.addItems(self.band_bds)
                self.band_id = self.band_bds

        elif 'QZS' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['QZS']
                self.band_combobox.addItems(self.band_qzs)
                self.band_id = self.band_qzs

        elif 'NavIC' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['NavIC']
                self.band_combobox.addItems(self.band_irn)
                self.band_id = self.band_irn

        elif 'SBS' in self.sys_combobox.currentText():
            if stat > 0:
                self.prn_id_ = self.prn_sys['SBS']
                self.band_combobox.addItems(self.band_sbs)
                self.band_id = self.band_sbs

    def plot_fig(self):
        if self.sol_data != None:
            stat =1
        else:
            stat = 0

        if stat > 0:
            # select data type
            fig_type = self.figtype_combobox.currentText()
            sys_type = self.sys_combobox.currentText()
            band_type= self.band_combobox.currentText()

            if  fig_type != '' and sys_type != '':
                # draw data quality result
                # elevation
                if fig_type == 'Ele':
                    sys_name = ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']
                    data = self.sol_data['ele']
                    data_sys = {}
                    for i, sys in enumerate(sys_name):
                        data_sys_ = data[self.prn_sys[sys]].mean(axis=0).to_frame().mean(axis=0).values
                        if ~np.isnan(data_sys_):
                             data_sys[sys] = float(data_sys_)
                    sys_name = list(data_sys.keys())
                    data_sys = list(data_sys.values())
                    data_sys = [np.nan if x == 0 else x for x in data_sys]

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']
                    bars = ax.bar(sys_name, data_sys, color=colors, width=0.3)

                    plt.xticks(rotation=0)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(r"Mean Elevation (°)", font)
                    ax.grid(linestyle='--')

                    self.figure.draw()


                # azimuth
                elif fig_type == 'Azi':

                    sys_name = ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']
                    data = self.sol_data['azi']
                    data_sys = {}
                    for i, sys in enumerate(sys_name):
                        data_sys_ = data[self.prn_sys[sys]].mean(axis=0).to_frame().mean(axis=0).values
                        if ~np.isnan(data_sys_):
                            data_sys[sys] = float(data_sys_)

                    sys_name = list(data_sys.keys())
                    data_sys = list(data_sys.values())
                    data_sys = [np.nan if x == 0 else x for x in data_sys]

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']
                    bars = ax.bar(sys_name, data_sys, color=colors, width=0.3)

                    plt.xticks(rotation=0)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(r"Mean Azimuth (°)", font)
                    ax.grid(linestyle='--')

                    self.figure.draw()


                # CN0
                elif fig_type == 'C/N0':

                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]
                    data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]

                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = data[sys_band_pos[i]][self.prn_sys[sys.split('-')[0]]].mean(axis=0).to_frame().mean(axis=0).values
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green','green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(r"Mean Carrier to Noise Ratio (dB-Hz)", font)
                    ax.grid(linestyle='--')
                    self.figure.draw()

                # mp
                elif fig_type == 'Code MP':

                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]
                    data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                    # data = self.sol_data['CN0']
                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = ((data[sys_band_pos[i]][self.prn_sys[sys.split('-')[0]]]**2).mean(axis=0).to_frame()**(1/2)).mean(axis=0).values
                    # data_sys[np.isnan(data_sys)] = 0
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green', 'green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(r"Code Multipath RMS (m)", font)
                    ax.grid(linestyle='--')
                    self.figure.draw()



                # Phase MP
                elif fig_type == 'Phase MP':
                    sys_name = ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']
                    data = self.sol_data['GFIF']
                    data_sys = np.zeros(len(sys_name))
                    for i, sys in enumerate(sys_name):
                        data_sys[i] = ((data[self.prn_sys[sys.split('-')[0]]]**2).mean(axis=0).to_frame()**(1/2)).mean(axis=0).values*100
                    # data_sys[np.isnan(data_sys)] = 0
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.3)

                    plt.xticks(rotation=0)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(u"Phase Multipath RMS (cm)", font)
                    ax.grid(linestyle='--')

                    self.figure.draw()


                # iod
                elif fig_type == 'IOD':

                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]

                    data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]

                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = ((data[sys_band_pos[i]][self.prn_sys[sys.split('-')[0]]]**2).mean(axis=0).to_frame()**(1/2)).mean(axis=0).values

                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green', 'green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(u"Ionospheric Delay Rate RMS (m/s)", font)
                    ax.grid(linestyle='--')
                    self.figure.draw()



                # intebarplot
                elif fig_type == 'DIR':

                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]

                    data = self.sol_data['inte']
                    # data = self.sol_data['CN0']
                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = (data.iloc[sys_band_pos[i], :].to_frame().T)[self.prn_sys[sys.split('-')[0]]].mean(axis=0).to_frame().mean(axis=0).values
                    # data_sys[np.isnan(data_sys)] = 0
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green', 'green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(u"Data Integrity Rate (%)", font)
                    ax.grid(linestyle='--')
                    self.figure.draw()



                # fullbarplot
                elif fig_type == 'DSR':
                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]

                    data = self.sol_data['satu']
                    # data = self.sol_data['CN0']
                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = (data.iloc[sys_band_pos[i], :].to_frame().T)[self.prn_sys[sys.split('-')[0]]].mean(axis=0).to_frame().mean(axis=0).values
                    # data_sys[np.isnan(data_sys)] = 0
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green', 'green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(u"Data Saturation Rate (%)", font)
                    ax.grid(linestyle='--')
                    self.figure.draw()


                # Pnoisebarplot
                elif fig_type == 'Code Noise':
                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]

                    data = [self.sol_data['Pnoise']['PNSN1':'PNSN1'], self.sol_data['Pnoise']['PNSN2':'PNSN2'], self.sol_data['Pnoise']['PNSN3':'PNSN3'], self.sol_data['Pnoise']['PNSN4':'PNSN4'], self.sol_data['Pnoise']['PNSN5':'PNSN5'], self.sol_data['Pnoise']['PNSN6':'PNSN6'], self.sol_data['Pnoise']['PNSN7':'PNSN7']]
                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = ((data[sys_band_pos[i]][self.prn_sys[sys.split('-')[0]]]**2).mean(axis=0).to_frame()**(1/2)).mean(axis=0).values
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green', 'green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(u"Code Noise RMS (m)", font)
                    ax.grid(linestyle='--')

                    self.figure.draw()


                # Cnoisebarplot
                elif fig_type == 'Phase Noise':

                    sys_band_name = ['GPS-L1', 'GPS-L2', 'GPS-L5', 'GLO-G1', 'GLO-G2', 'GLO-G3', 'BDS-B1I', 'BDS-B2I', 'BDS-B2a', 'BDS-B3I', 'BDS-B2ab', 'BDS-B1C', 'BDS-B2b',
                                     'GAL-E1', 'GAL-E5a', 'GAL-E5b', 'GAL-E6', 'GAL-E5', 'QZS-L1', 'QZS-L2', 'QZS-L5', 'QZS-L6', 'NavIC-L5',
                                     'NavIC-S', 'NavIC-L1', 'SBS-L1', 'SBS-L2']
                    sys_band_pos = [0, 1, 2, 0, 1, 2, 0, 1, 2, 3, 4, 5, 6, 0, 1, 2, 3, 4, 0, 1, 2, 3, 0, 1, 2, 0, 1]

                    data = [self.sol_data['Cnoise']['CNSN1':'CNSN1'], self.sol_data['Cnoise']['CNSN2':'CNSN2'], self.sol_data['Cnoise']['CNSN3':'CNSN3'], self.sol_data['Cnoise']['CNSN4':'CNSN4'], self.sol_data['Cnoise']['CNSN5':'CNSN5'], self.sol_data['Cnoise']['CNSN6':'CNSN6'], self.sol_data['Cnoise']['CNSN7':'CNSN7']]

                    data_sys = np.zeros(len(sys_band_name))
                    for i, sys in enumerate(sys_band_name):
                        data_sys[i] = ((data[sys_band_pos[i]][self.prn_sys[sys.split('-')[0]]]**2).mean(axis=0).to_frame()**(1/2)).mean(axis=0).values
                    non_nan_pos = np.where(~np.isnan(data_sys))[0]
                    data_sys = data_sys.tolist()

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    colors = ['r', 'r', 'r', 'b', 'b', 'b', 'green', 'green', 'green', 'green', 'green', 'green', 'green',
                              'm', 'm', 'm', 'm', 'm', 'orange', 'orange', 'orange', 'orange', 'c',
                              'c', 'c', 'deeppink', 'deeppink']

                    x = []
                    y = []
                    c = []
                    for i in non_nan_pos:
                        x.append(sys_band_name[i])
                        y.append(data_sys[i])
                        c.append(colors[i])

                    bars = ax.bar(x, y, color=c, width=0.5)
                    # for i, bar in enumerate(bars):
                    #     bar.set_label(labels[i])

                    plt.xticks(rotation=30)
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    ax.set_ylabel(u"Phase Noise RMS (Cycle)", font)
                    ax.grid(linestyle='--')
                    self.figure.draw()



                # skyview
                elif fig_type == 'Skyplot':
                    import matplotlib.patches as mpatches
                    azi_data = self.sol_data['azi']
                    ele_data = self.sol_data['ele']
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    sky_ = fig.add_subplot(111, polar=True)
                    sky_.set_theta_direction(-1)
                    sky_.set_theta_zero_location('N')
                    sky_.set_rticks([0, 15, 30, 45, 60, 75, 90])
                    sky_.yaxis.set_label_position('right')
                    sky_.grid(True)
                    prn_ = self.prn_sys[sys_type]
                    if len(prn_)>0:
                        for sat_ in self.prn_id_:
                            sky_.scatter(azi_data[sat_]*np.pi/180, ele_data[sat_], s=14, marker='o', color=sys_colors[sat_[0]])

                    GPS_patch = mpatches.Patch(color='r', label='GPS')
                    GLO_patch = mpatches.Patch(color='b', label='GLO')
                    GAL_patch = mpatches.Patch(color='green', label='BDS')
                    BDS_patch = mpatches.Patch(color='m', label='GAL')
                    QZS_patch = mpatches.Patch(color='orange', label='QZS')
                    IRN_patch = mpatches.Patch(color='c', label='NavIC')
                    SBS_patch = mpatches.Patch(color='deeppink', label='SBS')

                    plt.legend(handles=[GPS_patch, GLO_patch, GAL_patch, BDS_patch, QZS_patch, IRN_patch, SBS_patch],
                               bbox_to_anchor=(1.1, 0.5), loc='center left', ncol=1, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)

                    plt.gca().invert_yaxis()
                    sky_.set_ylim([90, 0])
                    self.figure.draw()


                # Sat Vis
                elif fig_type == 'Sat Vis':
                    import matplotlib.dates as mdate
                    from matplotlib.pyplot import MultipleLocator
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)
                    time = self.sol_data['ele']['Epoch']
                    prn_ = self.prn_sys[sys_type]
                    track_data = np.array(self.sol_data['ele'][prn_].astype(np.float64))
                    track_data[~np.isnan(track_data)] = 1
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    for i, sat_ in enumerate(prn_):
                        ax.scatter(time, track_data[:, i]+i, s=20, marker='s', color=sys_colors[sat_[0]])
                    ax.grid(linestyle='--')
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                             }
                    font1 = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                             }
                    ax.set_ylim(0.5, len(prn_)+0.5)
                    # self.figure13.ax13.set_yticks(self.prn_id, minor=True)

                    ax.yaxis.set_minor_locator(MultipleLocator(1))
                    ax.set_yticks(np.arange(len(prn_))+1)
                    ax.set_yticklabels(prn_, fontdict=font1)

                    ax.set_xlabel(u"GPST (HH:MM)", font)
                    ax.set_ylabel(u"Satellite Visibility", font)

                    ax.set_xlim(time.iloc[0], time.iloc[-1])
                    xfmt = mdate.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)

                    self.figure.draw()

                # DOP
                elif fig_type == 'DOP':
                    import matplotlib.dates as mdate
                    self.figure.fig.clear()
                    # fig = self.figure.fig

                    pos_data = self.sol_data['sol']
                    row_name = sorted(list(set(pos_data.index.tolist())))
                    # colors = plt.get_cmap('rainbow', 5)
                    colors = ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']
                    colors_dop = dict(zip(['NS', 'GDOP', 'PDOP', 'HDOP', 'VDOP'], [colors[0], colors[1], colors[2], colors[3], colors[4]]))
                    data_ = {}

                    if self.dop_check['All'].isChecked():
                        ax_l = plt.subplot(111)
                        ax_r = ax_l.twinx()
                        if sys_type in row_name:
                            sys_ = sys_type
                            data_[sys_] = pos_data[sys_:sys_]
                            ax_r.scatter(data_[sys_]['Epoch'], data_[sys_]['NS'], s=25, marker='o', color=colors_dop['NS'], label='NS')
                            ax_l.plot(data_[sys_]['Epoch'], data_[sys_]['GDOP'], '-o', markersize=5, color=colors_dop['GDOP'], label='GDOP')
                            ax_l.plot(data_[sys_]['Epoch'], data_[sys_]['PDOP'], '-o', markersize=5, color=colors_dop['PDOP'], label='PDOP')
                            ax_l.plot(data_[sys_]['Epoch'], data_[sys_]['HDOP'], '-o', markersize=5,  color=colors_dop['HDOP'], label='HDOP')
                            ax_l.plot(data_[sys_]['Epoch'], data_[sys_]['VDOP'], '-o', markersize=5,  color=colors_dop['VDOP'], label='VDOP')

                        lines_l, labels_l = ax_l.get_legend_handles_labels()
                        lines_r, labels_r = ax_r.get_legend_handles_labels()
                        lines = lines_l + lines_r
                        labels = labels_l + labels_r
                        ax_l.legend(lines, labels, bbox_to_anchor=(1, 1.1), loc='upper right',
                                    ncol=5, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01, markerscale=2, frameon=True)

                        ax_l.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': 16,
                                'weight': 'bold',
                                 }
                        ax_r.set_ylabel(u"Number of Satellites", font)
                        ax_l.set_ylabel(u"Dilution of Precision", font)
                        ax_l.set_ylim([0, 5])
                        # plt.axis('auto')
                        xfmt = mdate.DateFormatter('%H:%M')
                        ax_l.xaxis.set_major_formatter(xfmt)
                        ax_l.set_xlabel(u"GPST (HH:MM)", font)

                    else:
                        # get plot type
                        dop_type = []
                        for option, checkbox in self.dop_check.items():
                            if option != 'All':
                                if checkbox.isChecked():
                                    dop_type.append(option)

                        # define font size
                        font = {'family': 'Times New Roman',
                                'size': 16,
                                'weight': 'bold',}

                        ax_l = plt.subplot(111)
                        # if ax_r burn on
                        if len(dop_type) > 1 and 'NS' in dop_type:
                            ax_r = ax_l.twinx()
                            ax_r_bool = True
                        else:
                            ax_r_bool = False

                        if sys_type in row_name:
                            sys_ = sys_type
                            data_[sys_] = pos_data[sys_:sys_]

                            for i, dop_ in enumerate(dop_type):
                                if len(dop_type)>1:
                                    if dop_ != 'NS':
                                        ax_l.plot(data_[sys_]['Epoch'], data_[sys_][dop_], '-o', markersize=5, color=colors_dop[dop_], label=dop_)
                                else:
                                    ax_l.plot(data_[sys_]['Epoch'], data_[sys_][dop_], '-o', markersize=5, color=colors_dop[dop_], label=dop_)

                                if ax_r_bool and dop_ == 'NS':
                                    ax_r.plot(data_[sys_]['Epoch'], data_[sys_][dop_], '-o', markersize=5, color=colors_dop[dop_], label=dop_)

                                lines_l, labels_l = ax_l.get_legend_handles_labels()
                                if ax_r_bool:
                                    lines_r, labels_r = ax_r.get_legend_handles_labels()
                                else:
                                    lines_r, labels_r = [], []
                                lines = lines_l + lines_r
                                labels = labels_l + labels_r
                                ax_l.legend(lines, labels, bbox_to_anchor=(1, 1.1), loc='upper right',
                                            ncol=5, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01, markerscale=2, frameon=True)

                                if dop_ == 'NS':
                                    ax_l.set_ylabel(u"Number of Satellites", font)
                                else:
                                    ax_l.set_ylabel(u"Dilution of Precision", font)
                                    ax_l.set_ylim([0, 5])

                                xfmt = mdate.DateFormatter('%H:%M')
                                ax_l.xaxis.set_major_formatter(xfmt)
                                ax_l.set_xlabel(u"GPST (HH:MM)", font)

                                if ax_r_bool:
                                    ax_r.set_ylabel(u"Number of Satellites", font)

                            ax_l.grid(linestyle='--')

                    self.figure.draw()

                # SPP
                elif fig_type == 'XYZ':

                    data = self.sol_data['sol']
                    colors = ['r', 'b', 'green', 'cyan', 'm', 'orange', 'c', 'deeppink']
                    row_name = sorted(list(set(data.index.tolist())))
                    # colors = plt.get_cmap('rainbow', len(row_name))
                    data_ = {}

                    import matplotlib.dates as mdate
                    import matplotlib.patches as mpatches

                    self.figure.fig.clear()
                    fig = self.figure.fig

                    if sys_type != 'All':
                        x_ = fig.add_subplot(311)
                        y_ = fig.add_subplot(312)
                        z_ = fig.add_subplot(313)

                        if sys_type in row_name:
                            sys_ = sys_type
                            data_[sys_] = data[sys_:sys_]
                            XYZ = np.array(data_[sys_][['X(m)', 'Y(m)', 'Z(m)']])
                            used_flag = np.array(data_[sys_]['Q'])
                            XYZ_mean = np.mean(XYZ[used_flag > 0], axis=0)
                            from map import kml_gen as kml
                            dXYZ = np.full([XYZ.shape[0], XYZ.shape[1]], np.nan)
                            for i in range(XYZ.shape[0]):
                                if used_flag[i] > 0:
                                    dXYZ[i, :] = XYZ[i] - XYZ_mean

                            x_.scatter(data_[sys_]['Epoch'], dXYZ[:, 0], s=25, marker='o', color=colors[0])
                            y_.scatter(data_[sys_]['Epoch'], dXYZ[:, 1], s=25, marker='o', color=colors[1])
                            z_.scatter(data_[sys_]['Epoch'], dXYZ[:, 2], s=25, marker='o', color=colors[2])

                            from quality_check import rtkcmn as com
                            dx_patch = mpatches.Patch(color='r', label='X,RMS=' + str(np.round(com.rms(dXYZ[:, 0]), 3)))
                            dy_patch = mpatches.Patch(color='b', label='Y,RMS=' + str(np.round(com.rms(dXYZ[:, 1]), 3)))
                            dz_patch = mpatches.Patch(color='green', label='Z,RMS=' + str(np.round(com.rms(dXYZ[:, 2]), 3)))

                            x_.legend(handles=[dx_patch, dy_patch, dz_patch],
                                      bbox_to_anchor=(1, 1.2), loc='upper right', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)

                        x_.grid(linestyle='--')
                        y_.grid(linestyle='--')
                        z_.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': 16,
                                'weight': 'bold',
                                }
                        xfmt = mdate.DateFormatter('%H:%M')
                        z_.xaxis.set_major_formatter(xfmt)
                        y_.xaxis.set_major_formatter(xfmt)
                        x_.xaxis.set_major_formatter(xfmt)

                        z_.set_xlabel(u"GPST (HH:MM)", font)
                        x_.set_ylabel(u"X (m)", font)
                        y_.set_ylabel(u"Y (m)", font)
                        z_.set_ylabel(u"Z (m)", font)
                        x_.set_xticklabels([])
                        y_.set_xticklabels([])
                        self.figure.draw()

                    else:
                        data_rms = {}
                        for sys_ in row_name:
                            data_[sys_] = data[sys_:sys_]
                            XYZ = np.array(data_[sys_][['X(m)', 'Y(m)', 'Z(m)']])
                            used_flag = np.array(data_[sys_]['Q'])
                            XYZ_mean = np.mean(XYZ[used_flag > 0], axis=0)
                            from map import kml_gen as kml
                            dXYZ = np.full([XYZ.shape[0], XYZ.shape[1]], np.nan)
                            for i in range(XYZ.shape[0]):
                                if used_flag[i] > 0:
                                    dXYZ[i, :] = XYZ[i] - XYZ_mean
                            from quality_check import rtkcmn as com
                            data_rms[sys_] = list(com.rms(dXYZ))

                        ax = fig.add_subplot(111)
                        colors = ['r', 'b', 'green', 'm', 'orange', 'k', 'deeppink']

                        categories = list(data_rms.keys())
                        values = np.array(list(data_rms.values()))

                        num_bars = len(categories)
                        bar_width = 0.2

                        index = np.arange(num_bars)

                        # barplot
                        for i in range(values.shape[1]):
                            ax.bar(index + (i*bar_width), values[:, i], bar_width, color=colors[i])

                        ax.set_xticks(index + ((values.shape[1] - 1)*0.5*bar_width))
                        ax.set_xticklabels(categories)

                        plt.xticks(rotation=0)
                        font = {'family': 'Times New Roman',
                                'size': 16,
                                'weight': 'bold',
                                }
                        ax.set_ylabel(r"Position Error (m)", font)
                        ax.grid(linestyle='--')
                        N_patch = mpatches.Patch(color='r', label='X')
                        E_patch = mpatches.Patch(color='b', label='Y')
                        U_patch = mpatches.Patch(color='green', label='Z')

                        plt.legend(handles=[N_patch, E_patch, U_patch],
                                   bbox_to_anchor=(1, 1.05), loc='upper right', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        self.figure.draw()


                # SPP
                elif fig_type == 'NEU':

                    data = self.sol_data['sol']
                    colors = ['r', 'b', 'green', 'cyan', 'm', 'orange', 'c', 'deeppink']
                    row_name = sorted(list(set(data.index.tolist())))
                    # colors = plt.get_cmap('rainbow', len(row_name))
                    data_ = {}

                    import matplotlib.dates as mdate
                    import matplotlib.patches as mpatches

                    self.figure.fig.clear()
                    fig = self.figure.fig

                    if sys_type != 'All':
                        x_ = fig.add_subplot(311)
                        y_ = fig.add_subplot(312)
                        z_ = fig.add_subplot(313)

                        if sys_type in row_name:
                            sys_ = sys_type
                            data_[sys_] = data[sys_:sys_]
                            XYZ = np.array(data_[sys_][['X(m)', 'Y(m)', 'Z(m)']])
                            used_flag = np.array(data_[sys_]['Q'])
                            XYZ_mean = np.mean(XYZ[used_flag>0], axis=0)
                            from map import kml_gen as kml
                            NEU = np.full([XYZ.shape[0], XYZ.shape[1]], np.nan)
                            for i in range(XYZ.shape[0]):
                                if used_flag[i] > 0:
                                    NEU[i, :] = kml.XYZ_NEH(XYZ[i], XYZ_mean)

                            x_.scatter(data_[sys_]['Epoch'], NEU[:, 0], s=25,  marker='o', color=colors[0])
                            y_.scatter(data_[sys_]['Epoch'], NEU[:, 1], s=25, marker='o', color=colors[1])
                            z_.scatter(data_[sys_]['Epoch'], NEU[:, 2], s=25, marker='o', color=colors[2])

                            from quality_check import rtkcmn as com
                            N_patch = mpatches.Patch(color='r', label='N,RMS=' + str(np.round(com.rms(NEU[:, 0]), 3)))
                            E_patch = mpatches.Patch(color='b', label='E,RMS=' + str(np.round(com.rms(NEU[:, 1]), 3)))
                            U_patch = mpatches.Patch(color='green', label='U,RMS=' + str(np.round(com.rms(NEU[:, 2]), 3)))

                            x_.legend(handles=[N_patch, E_patch, U_patch],
                                      bbox_to_anchor=(1, 1.2), loc='upper right', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)

                        x_.grid(linestyle='--')
                        y_.grid(linestyle='--')
                        z_.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': 16,
                                'weight': 'bold',
                                }
                        xfmt = mdate.DateFormatter('%H:%M')
                        z_.xaxis.set_major_formatter(xfmt)
                        y_.xaxis.set_major_formatter(xfmt)
                        x_.xaxis.set_major_formatter(xfmt)

                        z_.set_xlabel(u"GPST (HH:MM)", font)
                        x_.set_ylabel(u"N (m)", font)
                        y_.set_ylabel(u"E (m)", font)
                        z_.set_ylabel(u"U (m)", font)
                        x_.set_xticklabels([])
                        y_.set_xticklabels([])
                        self.figure.draw()

                    else:
                        data_rms = {}
                        for sys_ in row_name:
                            data_[sys_] = data[sys_:sys_]
                            XYZ = np.array(data_[sys_][['X(m)', 'Y(m)', 'Z(m)']])
                            used_flag = np.array(data_[sys_]['Q'])
                            XYZ_mean = np.mean(XYZ[used_flag>0], axis=0)
                            from map import kml_gen as kml
                            NEU = np.full([XYZ.shape[0], XYZ.shape[1]], np.nan)
                            for i in range(XYZ.shape[0]):
                                if used_flag[i] > 0:
                                    NEU[i, :] = kml.XYZ_NEH(XYZ[i], XYZ_mean)
                            from quality_check import rtkcmn as com
                            data_rms[sys_] = list(com.rms(NEU))

                        ax = fig.add_subplot(111)
                        colors = ['r', 'b', 'green', 'm', 'orange', 'k', 'deeppink']

                        categories = list(data_rms.keys())
                        values = np.array(list(data_rms.values()))

                        num_bars = len(categories)
                        bar_width = 0.2

                        index = np.arange(num_bars)

                        # barplot
                        for i in range(values.shape[1]):
                            ax.bar(index + (i*bar_width), values[:, i], bar_width, color=colors[i])

                        ax.set_xticks(index + ((values.shape[1] - 1)*0.5*bar_width))
                        ax.set_xticklabels(categories)

                        plt.xticks(rotation=0)
                        font = {'family': 'Times New Roman',
                                'size': 16,
                                'weight': 'bold',
                                }
                        ax.set_ylabel(r"Position Error (m)", font)
                        ax.grid(linestyle='--')
                        N_patch = mpatches.Patch(color='r', label='N')
                        E_patch = mpatches.Patch(color='b', label='E')
                        U_patch = mpatches.Patch(color='green', label='U')

                        plt.legend(handles=[N_patch, E_patch, U_patch],
                                  bbox_to_anchor=(1, 1.05), loc='upper right', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        self.figure.draw()

                elif fig_type == 'CDF':
                    import statsmodels.api as sm
                    import matplotlib.patches as mpatches
                    from scipy import stats

                    data = self.sol_data['sol']
                    row_name = sorted(list(set(data.index.tolist())))
                    colors = plt.get_cmap('rainbow', 5)
                    data_ = {}
                    data_neu = {}

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    sys_ = sys_type
                    if sys_ in row_name:
                        data_[sys_] = data[sys_:sys_]
                        XYZ = np.array(data_[sys_][['X(m)', 'Y(m)', 'Z(m)']])
                        used_flag = np.array(data_[sys_]['Q'])
                        XYZ_mean = np.mean(data_[sys_][used_flag>0], axis=0)
                        from map import kml_gen as kml
                        NEU = np.full([XYZ.shape[0], XYZ.shape[1]], np.nan)
                        for i in range(XYZ.shape[0]):
                            if used_flag[i] > 0:
                                NEU[i, :] = kml.XYZ_NEH(XYZ[i], XYZ_mean)
                        from quality_check import rtkcmn as com
                        data_neu[sys_] = NEU


                        ecdf_N = sm.distributions.ECDF(np.abs(NEU[:, 0]))
                        ecdf_E = sm.distributions.ECDF(np.abs(NEU[:, 1]))
                        ecdf_U = sm.distributions.ECDF(np.abs(NEU[:, 2]))

                        ax.plot(ecdf_N.x, ecdf_N.y, '-', linewidth=4, color=colors(0))
                        N_percentile_95 = stats.scoreatpercentile(np.abs(NEU[:, 0]), 95)
                        ax.axvline(x=N_percentile_95, color=colors(0), linestyle='--')
                        ax.text(N_percentile_95, 1.01, f'95%={N_percentile_95:.2f}', color=colors(0), verticalalignment='bottom')

                        ax.plot(ecdf_E.x, ecdf_E.y, '-', linewidth=4, color=colors(1))
                        E_percentile_95 = stats.scoreatpercentile(np.abs(NEU[:, 1]), 95)
                        ax.axvline(x=E_percentile_95, color=colors(1), linestyle='--')
                        ax.text(E_percentile_95, 1.01,f'95%={E_percentile_95:.2f}', color=colors(1), verticalalignment='bottom')

                        ax.plot(ecdf_U.x, ecdf_U.y, '-', linewidth=4, color=colors(2))
                        U_percentile_95 = stats.scoreatpercentile(np.abs(NEU[:, 2]), 95)
                        ax.axvline(x=U_percentile_95, color=colors(2), linestyle='--')
                        ax.text(U_percentile_95, 1.01, f'95%={U_percentile_95:.2f}', color=colors(2), verticalalignment='bottom')

                    ax.grid(linestyle='--')
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    ax.set_xlabel(u"Position Error (m)", font)
                    ax.set_ylabel(u"Cumulative Distribution Function", font)

                    N_patch = mpatches.Patch(color=colors(0), label='N')
                    E_patch = mpatches.Patch(color=colors(1), label='E')
                    U_patch = mpatches.Patch(color=colors(2), label='U')

                    plt.legend(handles=[N_patch, E_patch, U_patch],
                               bbox_to_anchor=(1, 1.1), loc='upper right', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)

                    self.figure.draw()

                elif fig_type == 'Boxplot':
                    import statsmodels.api as sm
                    import matplotlib.patches as mpatches
                    from scipy import stats

                    data = self.sol_data['sol']
                    row_name = sorted(list(set(data.index.tolist())))
                    data_ = {}
                    data_neu = {}

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)

                    sys_ = sys_type
                    if sys_ in row_name:
                        data_[sys_] = data[sys_:sys_]
                        XYZ = np.array(data_[sys_][['X(m)', 'Y(m)', 'Z(m)']])
                        XYZ_mean = np.mean(data_[sys_], axis=0)
                        from map import kml_gen as kml
                        NEU = np.full([XYZ.shape[0], XYZ.shape[1]], np.nan)
                        for i in range(XYZ.shape[0]):
                            NEU[i, :] = kml.XYZ_NEH(XYZ[i], XYZ_mean)
                        from quality_check import rtkcmn as com
                        data_neu[sys_] = NEU

                        ax.boxplot(np.abs(NEU[:, 0]), positions=[0], labels='N', sym="r+", showmeans=True, patch_artist=True, boxprops={'color': 'red', 'facecolor': 'orangered'}, whiskerprops={'color': 'red'}, capprops={'color': 'red'}, autorange='True', showfliers=False, whis=(5, 95))
                        ax.boxplot(np.abs(NEU[:, 1]), positions=[1], labels='E', sym="g+", showmeans=True, patch_artist=True, boxprops={'color': 'green', 'facecolor': 'lime'}, whiskerprops={'color': 'green'}, capprops={'color': 'green'}, autorange='True', showfliers=False, whis=(5, 95))
                        ax.boxplot(np.abs(NEU[:, 2]), positions=[2], labels='U', sym="b+", showmeans=True, patch_artist=True, boxprops={'color': 'blue', 'facecolor': 'aqua'}, whiskerprops={'color': 'blue'}, capprops={'color': 'blue'}, autorange='True', showfliers=False, whis=(5, 95))


                    ax.grid(linestyle='--')
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    ax.set_ylabel(u"Position Error (m)", font)

                    self.figure.draw()

                elif fig_type == 'Sat Vis MP':
                    from quality_check import rtkcmn as com
                    import matplotlib.patches as mpatches
                    import matplotlib.dates as mdate
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)
                    data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                    time = self.sol_data['ele']['Epoch']
                    prn_ = self.prn_id_
                    track_data = np.array(self.sol_data['ele'][prn_].astype(np.float64))
                    track_data[~np.isnan(track_data)] = 1
                    sys_colors = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    sys_id = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']))
                    band_pos = self.search_band(sys_type, band_type)
                    sys_ = {}

                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    if len(prn_) > 0:
                        color_data = data[band_pos[0]][prn_]
                        for i, sat_ in enumerate(prn_):
                            sys_[sat_[0]] = sys_id[sat_[0]]
                            x = time
                            y = track_data[:, i] + i
                            z = data[band_pos[0]][sat_]

                            # h = ax.scatter(x, y, c=sys_colors[sys_[sat_[0]]], s=z.abs()*1000+100, alpha=0.9, vmin=-1, vmax=1, marker='.',  edgecolors='black', linewidths=0.1)
                            h = ax.scatter(x, y, c=z, cmap='gist_rainbow', s=50, alpha=0.9, vmin=-1, vmax=1, marker='s', edgecolors='black', linewidths=0.1)

                        sm = plt.cm.ScalarMappable(cmap='gist_rainbow', norm=plt.Normalize(vmin=-1, vmax=1))
                        sm.set_array([])
                        cbar = plt.colorbar(sm, format='%.2f', shrink=0.92, label='Code Multipath')
                        cbar.set_label('Code Multipath', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('m', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    ax.grid(linestyle='--')
                    ax.set_xlim(x.head(1), x.tail(1))
                    ax.set_ylim(0.5, len(prn_) + 0.5)
                    from matplotlib.pyplot import MultipleLocator
                    ax.yaxis.set_minor_locator(MultipleLocator(1))
                    ax.set_yticks(np.arange(len(prn_)) + 1)
                    ax.set_yticklabels(prn_, fontdict=font)

                    ax.set_xlabel(u"GPST (HH:MM)", font)
                    ax.set_ylabel(u"Satellite Visibility", font)

                    ax.set_xlim(time.iloc[0], time.iloc[-1])
                    xfmt = mdate.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.subplots_adjust(right=0.9)

                    self.figure.draw()

                elif fig_type == 'Sat Vis C/N0':
                    from quality_check import rtkcmn as com
                    import matplotlib.patches as mpatches
                    import matplotlib.dates as mdate
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)
                    data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]
                    time = self.sol_data['ele']['Epoch']
                    prn_ = self.prn_sys[sys_type]
                    track_data = np.array(self.sol_data['ele'][prn_].astype(np.float64))
                    track_data[~np.isnan(track_data)] = 1
                    sys_colors = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    sys_id = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']))
                    band_pos = self.search_band(sys_type, band_type)
                    sys_ = {}

                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    if len(prn_) > 0:
                        color_data = data[band_pos[0]][prn_]
                        min_value = np.nanmin(color_data)
                        max_value = np.nanmax(color_data)

                        for i, sat_ in enumerate(prn_):
                            sys_[sat_[0]] = sys_id[sat_[0]]
                            x = time
                            y = track_data[:, i] + i
                            z = data[band_pos[0]][sat_]

                            # h = ax.scatter(x, y, c=z, s=z.abs()*200, cmap='jet', alpha=0.75, vmin=-1, vmax=1, marker='o')
                            h = ax.scatter(x, y, c=z, cmap='gist_rainbow', s=50, alpha=0.75, marker='s', edgecolors='black', linewidths=0.1, vmin=min_value, vmax=max_value)


                        sm = plt.cm.ScalarMappable(cmap='gist_rainbow', norm=plt.Normalize(vmin=min_value, vmax=max_value))
                        sm.set_array([])
                        cbar = plt.colorbar(sm, format='%.2f', shrink=0.92, label='Carrier to Noise Ratio')
                        cbar.set_label('Carrier to Noise Ratio', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('dB-Hz', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    ax.grid(linestyle='--')
                    ax.set_ylim(0.5, len(prn_) + 0.5)
                    from matplotlib.pyplot import MultipleLocator
                    ax.yaxis.set_minor_locator(MultipleLocator(1))
                    ax.set_yticks(np.arange(len(prn_)) + 1)
                    ax.set_yticklabels(prn_, fontdict=font)

                    ax.set_xlabel(u"GPST (HH:MM)", font)
                    ax.set_ylabel(u"Satellite Visibility", font)

                    ax.set_xlim(time.iloc[0], time.iloc[-1])
                    xfmt = mdate.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.subplots_adjust(right=0.9)

                    self.figure.draw()

                elif fig_type == 'Sat Vis IOD':
                    from quality_check import rtkcmn as com
                    import matplotlib.patches as mpatches
                    import matplotlib.dates as mdate
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)
                    data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]
                    time = self.sol_data['ele']['Epoch']
                    prn_ = self.prn_sys[sys_type]
                    track_data = np.array(self.sol_data['ele'][prn_].astype(np.float64))
                    track_data[~np.isnan(track_data)] = 1
                    sys_colors = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    sys_id = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']))
                    band_pos = self.search_band(sys_type, band_type)
                    sys_ = {}

                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    if len(prn_) > 0:
                        color_data = data[band_pos[0]][prn_]
                        min_value = np.nanmin(color_data)
                        max_value = np.nanmax(color_data)
                        for i, sat_ in enumerate(prn_):
                            sys_[sat_[0]] = sys_id[sat_[0]]
                            x = time
                            y = track_data[:, i] + i
                            z = data[band_pos[0]][sat_]

                            # h = ax.scatter(x, y, c=z, s=z.abs()*200, cmap='jet', alpha=0.75, vmin=-1, vmax=1, marker='o')
                            h = ax.scatter(x, y, c=z, s=50, alpha=0.75, marker='s', cmap='gist_rainbow', edgecolors='black', linewidths=0.1, vmin=min_value, vmax=max_value)

                        sm = plt.cm.ScalarMappable(cmap='gist_rainbow', norm=plt.Normalize(vmin=min_value, vmax=max_value))
                        sm.set_array([])
                        cbar = plt.colorbar(sm, format='%.2f', shrink=0.92, label='Ionospheric Delay Rate')
                        cbar.set_label('Ionospheric Delay Rate', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('m/s', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    ax.grid(linestyle='--')
                    ax.set_ylim(0.5, len(prn_) + 0.5)
                    from matplotlib.pyplot import MultipleLocator
                    ax.yaxis.set_minor_locator(MultipleLocator(1))
                    ax.set_yticks(np.arange(len(prn_)) + 1)
                    ax.set_yticklabels(prn_, fontdict=font)

                    ax.set_xlabel(u"GPST (HH:MM)", font)
                    ax.set_ylabel(u"Satellite Visibility", font)

                    ax.set_xlim(time.iloc[0], time.iloc[-1])
                    xfmt = mdate.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.subplots_adjust(right=0.9)
                    self.figure.draw()


                elif fig_type == 'Sat Vis Code Noise':
                    from quality_check import rtkcmn as com
                    import matplotlib.patches as mpatches
                    import matplotlib.dates as mdate
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)
                    data = [self.sol_data['Pnoise']['PNSN1':'PNSN1'], self.sol_data['Pnoise']['PNSN2':'PNSN2'], self.sol_data['Pnoise']['PNSN3':'PNSN3'], self.sol_data['Pnoise']['PNSN4':'PNSN4'], self.sol_data['Pnoise']['PNSN5':'PNSN5'], self.sol_data['Pnoise']['PNSN6':'PNSN6'], self.sol_data['Pnoise']['PNSN7':'PNSN7']]
                    time = self.sol_data['ele']['Epoch']
                    prn_ = self.prn_sys[sys_type]
                    track_data = np.array(self.sol_data['ele'][prn_].astype(np.float64))
                    track_data[~np.isnan(track_data)] = 1
                    sys_colors = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    sys_id = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']))
                    band_pos = self.search_band(sys_type, band_type)
                    sys_ = {}

                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }
                    if len(prn_) > 0:
                        color_data = data[band_pos[0]][prn_]
                        min_value = np.nanmin(color_data)
                        max_value = np.nanmax(color_data)
                        for i, sat_ in enumerate(prn_):
                            sys_[sat_[0]] = sys_id[sat_[0]]
                            x = time
                            y = track_data[:, i] + i
                            z = data[band_pos[0]][sat_]

                            # h = ax.scatter(x, y, c=z, s=z.abs()*200, cmap='jet', alpha=0.75, vmin=-1, vmax=1, marker='o')
                            ax.scatter(x, y, c=z, s=50, alpha=0.75, marker='s', cmap='gist_rainbow', edgecolors='black', linewidths=0.1, vmin=min_value, vmax=max_value)

                        sm = plt.cm.ScalarMappable(cmap='gist_rainbow', norm=plt.Normalize(vmin=min_value, vmax=max_value))
                        sm.set_array([])
                        cbar = plt.colorbar(sm, format='%.2f', shrink=0.92, label='Code Noise')
                        cbar.set_label('Code Noise', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('m', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    ax.grid(linestyle='--')
                    ax.set_ylim(0.5, len(prn_) + 0.5)
                    from matplotlib.pyplot import MultipleLocator
                    ax.yaxis.set_minor_locator(MultipleLocator(1))
                    ax.set_yticks(np.arange(len(prn_)) + 1)
                    ax.set_yticklabels(prn_, fontdict=font)

                    ax.set_xlabel(u"GPST (HH:MM)", font)
                    ax.set_ylabel(u"Satellite Visibility", font)

                    ax.set_xlim(time.iloc[0], time.iloc[-1])
                    xfmt = mdate.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.subplots_adjust(right=0.9)

                    self.figure.draw()

                elif fig_type == 'Sat Vis Phase Noise':
                    from quality_check import rtkcmn as com
                    import matplotlib.patches as mpatches
                    import matplotlib.dates as mdate

                    data = [self.sol_data['Cnoise']['CNSN1':'CNSN1'], self.sol_data['Cnoise']['CNSN2':'CNSN2'], self.sol_data['Cnoise']['CNSN3':'CNSN3'], self.sol_data['Cnoise']['CNSN4':'CNSN4'], self.sol_data['Cnoise']['CNSN5':'CNSN5'], self.sol_data['Cnoise']['CNSN6':'CNSN6'], self.sol_data['Cnoise']['CNSN7':'CNSN7']]
                    time = self.sol_data['ele']['Epoch']
                    prn_ = self.prn_sys[sys_type]
                    track_data = np.array(self.sol_data['ele'][prn_].astype(np.float64))
                    track_data[~np.isnan(track_data)] = 1
                    sys_colors = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    sys_id = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']))
                    band_pos = self.search_band(sys_type, band_type)
                    sys_ = {}

                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    ax = fig.add_subplot(111)
                    if len(prn_) > 0:
                        color_data = data[band_pos[0]][prn_]
                        min_value = np.nanmin(color_data)
                        max_value = np.nanmax(color_data)
                        for i, sat_ in enumerate(prn_):
                            sys_[sat_[0]] = sys_id[sat_[0]]
                            x = time
                            y = track_data[:, i] + i
                            z = data[band_pos[0]][sat_]

                            # h = ax.scatter(x, y, c=z, s=z.abs()*200, cmap='jet', alpha=0.75, vmin=-1, vmax=1, marker='o')
                            ax.scatter(x, y, c=z, s=50, alpha=0.75, marker='s', cmap='gist_rainbow', edgecolors='black', linewidths=0.1, vmin=min_value, vmax=max_value)

                        sm = plt.cm.ScalarMappable(cmap='gist_rainbow', norm=plt.Normalize(vmin=min_value, vmax=max_value))
                        sm.set_array([])
                        cbar = plt.colorbar(sm, format='%.2f', shrink=0.92, label='Phase Noise')
                        cbar.set_label('Phase Noise', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('Cycle', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    ax.grid(linestyle='--')
                    ax.set_ylim(0.5, len(prn_) + 0.5)
                    from matplotlib.pyplot import MultipleLocator
                    ax.yaxis.set_minor_locator(MultipleLocator(1))
                    ax.set_yticks(np.arange(len(prn_)) + 1)
                    ax.set_yticklabels(prn_, fontdict=font)

                    ax.set_xlabel(u"GPST (HH:MM)", font)
                    ax.set_ylabel(u"Satellite Visibility", font)

                    ax.set_xlim(time.iloc[0], time.iloc[-1])
                    xfmt = mdate.DateFormatter('%H:%M')
                    ax.xaxis.set_major_formatter(xfmt)
                    plt.subplots_adjust(right=0.9)

                    self.figure.draw()


                elif fig_type == 'Skyplot MP':
                    import matplotlib.patches as mpatches
                    azi_data = self.sol_data['azi']
                    ele_data = self.sol_data['ele']
                    data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    sky_ = fig.add_subplot(111, polar=True)
                    sky_.set_theta_direction(-1)
                    sky_.set_theta_zero_location('N')
                    sky_.set_rticks([0, 15, 30, 45, 60, 75, 90])
                    sky_.yaxis.set_label_position('right')
                    sky_.grid(True)
                    prn_ = self.prn_sys[sys_type]
                    band_pos = self.search_band(sys_type, band_type)
                    if len(prn_) > 0:
                        x = np.array(azi_data[prn_]*np.pi/180)
                        y = np.array(ele_data[prn_])
                        z = np.array(data[band_pos[0]][prn_])
                        h = sky_.scatter(x, y, s=25, marker='o', c=z, cmap='gist_rainbow')

                        cbar = plt.colorbar(h, format='%.2f', shrink=0.92, label='Multipath')
                        cbar.set_label('Code Multipath', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('m', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    plt.gca().invert_yaxis()
                    sky_.set_ylim([90, 0])
                    self.figure.draw()

                elif fig_type == 'Skyplot C/N0':
                    import matplotlib.patches as mpatches
                    azi_data = self.sol_data['azi']
                    ele_data = self.sol_data['ele']
                    data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'k', 'deeppink']))
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    sky_ = fig.add_subplot(111, polar=True)
                    sky_.set_theta_direction(-1)
                    sky_.set_theta_zero_location('N')
                    sky_.set_rticks([0, 15, 30, 45, 60, 75, 90])
                    sky_.yaxis.set_label_position('right')
                    sky_.grid(True)
                    prn_ = self.prn_sys[sys_type]
                    band_pos = self.search_band(sys_type, band_type)
                    if len(prn_) > 0:
                        x = np.array(azi_data[prn_]*np.pi/180)
                        y = np.array(ele_data[prn_])
                        z = np.array(data[band_pos[0]][prn_])
                        h = sky_.scatter(x, y, s=25, marker='o', c=z, cmap='gist_rainbow')

                        cbar = plt.colorbar(h, format='%.2f', shrink=0.92, label='Carrier to Noise Ratio')
                        cbar.set_label('Carrier to Noise Ratio', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('dB-Hz', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        # cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    plt.gca().invert_yaxis()
                    sky_.set_ylim([90, 0])
                    self.figure.draw()

                elif fig_type == 'Skyplot IOD':
                    import matplotlib.patches as mpatches
                    azi_data = self.sol_data['azi']
                    ele_data = self.sol_data['ele']
                    data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'k', 'deeppink']))
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    sky_ = fig.add_subplot(111, polar=True)
                    sky_.set_theta_direction(-1)
                    sky_.set_theta_zero_location('N')
                    sky_.set_rticks([0, 15, 30, 45, 60, 75, 90])
                    sky_.yaxis.set_label_position('right')
                    sky_.grid(True)
                    prn_ = self.prn_sys[sys_type]
                    band_pos = self.search_band(sys_type, band_type)
                    if len(prn_) > 0:
                        x = np.array(azi_data[prn_]*np.pi/180)
                        y = np.array(ele_data[prn_])
                        z = np.array(data[band_pos[0]][prn_])
                        h = sky_.scatter(x, y, s=25, marker='o', c=z, cmap='gist_rainbow')

                        cbar = plt.colorbar(h, format='%.2f', shrink=0.92, label='Ionospheric Delay Rate')
                        cbar.set_label('Ionospheric Delay Rate', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('m/s', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    plt.gca().invert_yaxis()
                    sky_.set_ylim([90, 0])
                    self.figure.draw()

                elif fig_type == 'Skyplot Code Noise':
                    import matplotlib.patches as mpatches
                    azi_data = self.sol_data['azi']
                    ele_data = self.sol_data['ele']
                    data = [self.sol_data['Pnoise']['PNSN1':'PNSN1'], self.sol_data['Pnoise']['PNSN2':'PNSN2'], self.sol_data['Pnoise']['PNSN3':'PNSN3'], self.sol_data['Pnoise']['PNSN4':'PNSN4'], self.sol_data['Pnoise']['PNSN5':'PNSN5'], self.sol_data['Pnoise']['PNSN6':'PNSN6'], self.sol_data['Pnoise']['PNSN7':'PNSN7']]
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'k', 'deeppink']))
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    sky_ = fig.add_subplot(111, polar=True)
                    sky_.set_theta_direction(-1)
                    sky_.set_theta_zero_location('N')
                    sky_.set_rticks([0, 15, 30, 45, 60, 75, 90])
                    sky_.yaxis.set_label_position('right')
                    sky_.grid(True)
                    prn_ = self.prn_sys[sys_type]
                    band_pos = self.search_band(sys_type, band_type)
                    if len(prn_) > 0:
                        x = np.array(azi_data[prn_]*np.pi/180)
                        y = np.array(ele_data[prn_])
                        z = np.array(data[band_pos[0]][prn_])
                        h = sky_.scatter(x, y, s=25, marker='o', c=z, cmap='gist_rainbow')

                        cbar = plt.colorbar(h, format='%.2f', shrink=0.92, label='Code Noise')
                        cbar.set_label('Code Noise', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('m', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    plt.gca().invert_yaxis()
                    sky_.set_ylim([90, 0])
                    self.figure.draw()

                elif fig_type == 'Skyplot Phase Noise':
                    import matplotlib.patches as mpatches
                    azi_data = self.sol_data['azi']
                    ele_data = self.sol_data['ele']
                    data = [self.sol_data['Cnoise']['CNSN1':'CNSN1'], self.sol_data['Cnoise']['CNSN2':'CNSN2'], self.sol_data['Cnoise']['CNSN3':'CNSN3'], self.sol_data['Cnoise']['CNSN4':'CNSN4'], self.sol_data['Cnoise']['CNSN5':'CNSN5'], self.sol_data['Cnoise']['CNSN6':'CNSN6'], self.sol_data['Cnoise']['CNSN7':'CNSN7']]
                    sys_colors = dict(zip(['G', 'R', 'C', 'E', 'J', 'I', 'S'], ['r', 'b', 'green', 'm', 'orange', 'c', 'deeppink']))
                    font = {'family': 'Times New Roman',
                            'size': 16,
                            'weight': 'bold',
                            }

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    sky_ = fig.add_subplot(111, polar=True)
                    sky_.set_theta_direction(-1)
                    sky_.set_theta_zero_location('N')
                    sky_.set_rticks([0, 15, 30, 45, 60, 75, 90])
                    sky_.yaxis.set_label_position('right')
                    sky_.grid(True)
                    prn_ = self.prn_sys[sys_type]
                    band_pos = self.search_band(sys_type, band_type)
                    if len(prn_) > 0:
                        x = np.array(azi_data[prn_]*np.pi/180)
                        y = np.array(ele_data[prn_])
                        z = np.array(data[band_pos[0]][prn_])

                        h = sky_.scatter(x, y, s=25, marker='o', c=z, cmap='gist_rainbow')

                        cbar = plt.colorbar(h, format='%.2f', shrink=0.92, label='Phase Noise')
                        cbar.set_label('Phase Noise', fontproperties=font, weight='bold')
                        cbar.ax.tick_params(labelsize=13)
                        cbar.ax.set_title('Cycle', fontsize=13, fontproperties=font)
                        cbar.ax.tick_params(which='major', direction='in', labelsize=13, length=7.5)
                        cbar.ax.tick_params(which='minor', direction='in')
                        cbar.locator = plt.MaxNLocator(5)
                        cbar.update_ticks()

                    plt.gca().invert_yaxis()
                    sky_.set_ylim([90, 0])
                    self.figure.draw()


    def map_gui(self, sol_data=None, work_path=None):
        if sol_data != None and work_path != None:
            from map import point_map
            pos_data = sol_data['sol']['MIX':'MIX']
            point_map.point_map(pos_data, work_path)
            self.windows = Map()
            self.windows.show()

    def kml_gui(self, sol_data=None, sol_filename=None):
        if sol_data != None and sol_filename != None:
            kml_dir = os.path.splitext(sol_filename)[0]
            pos_data = sol_data['sol']['MIX':'MIX']
            from map import kml_gen
            kml_file = kml_gen.kml_expos(pos_data, kml_dir)
            QMessageBox.information(self, 'Tips', 'success generated kml')

    def search_band(self, sys_type, band_type):
        band_pos = None
        if 'GPS' in sys_type:
            band_pos = [self.band_gps.index(band_type)]
        elif 'GLO' in sys_type:
            band_pos = [self.band_glo.index(band_type)]
        elif 'BDS' in sys_type:
            band_pos_ = [0, 1, 3, 5, 2, 6, 4]
            band_pos = [band_pos_[self.band_bds.index(band_type)]]
        elif 'GAL' in sys_type:
            band_pos = [self.band_gal.index(band_type)]
        elif 'QZS' in sys_type:
            band_pos = [self.band_qzs.index(band_type)]
        elif 'NavIC' in sys_type:
            band_pos = [self.band_irn.index(band_type)]
        elif 'SBS' in sys_type:
            band_pos = [self.band_sbs.index(band_type)]
        return band_pos

#######################################matplotlib######################################################

class Canvas(FigureCanvas):

    def __init__(self, parent=None):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'

        params = {
            'font.family': 'Times new roman',
            'font.size': 16,
            'font.weight': 'bold',
            # 'mathtext.fontset': 'Times new roman',
            'font.serif': ['Times new roman'],
        }
        plt.rcParams.update(params)

        self.fig = plt.figure(linewidth=1)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(linestyle='--')
        self.axel = plt.gca()
        self.axel.spines['bottom'].set_linewidth(1)
        self.axel.spines['left'].set_linewidth(1)
        self.axel.spines['right'].set_linewidth(1)
        self.axel.spines['top'].set_linewidth(1)
        xfmt = mdate.DateFormatter('%H:%M')
        self.ax.xaxis.set_major_formatter(xfmt)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

#------------------------------------------------------------------------------------------------------
# point map

class Map(QMainWindow):
    def __init__(self):
        super(Map, self).__init__()
        self.setWindowTitle('SPP-Map')
        self.resize(1355, 730)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        url = os.path.abspath(os.path.join(os.path.dirname(__file__), "./lib/map/spp_map.html"))
        local_url = QUrl.fromLocalFile(url)
        # load url
        self.browser.load(local_url)
        self.setCentralWidget(self.browser)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)

#------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    import qdarkstyle
    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    ratio = dpi/96
    form = plot_sys(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    # font.setPointSize(9)
    font.setPixelSize(14*ratio)
    app.setFont(font)
    form.show()
    sys.exit(app.exec_())