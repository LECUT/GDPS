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
import copy
import warnings
warnings.filterwarnings(action='ignore')
import resources_rc

# global variable
sol_data = np.nan
font_size = 16

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

class plot_sat(QMainWindow):
    def __init__(self, ratio, curdir_ini):
        super(plot_sat, self).__init__()
        self.ratio = ratio
        self.curdir_ini = curdir_ini
        self.setWindowTitle("Plot_satellite")
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
        zlable_w   = 35*self.ratio
        zlable_h   = 25*self.ratio
        button_w   = 80*self.ratio
        button_h   = 25*self.ratio
        checkbox_w = 45*self.ratio
        checkbox_h = 25*self.ratio
        bobox_w    = 70*self.ratio
        bobox_h    = 25*self.ratio
        LineEdit_w = 300*self.ratio
        LineEdit_h = 25*self.ratio
        Pagemargin = 5*self.ratio
        canvas_h   = 240*self.ratio
        #-------------------------------------------------------
        self.bar = self.menuBar()
        self.File = self.bar.addMenu("File")
        self.save = self.File.addAction("Save Figure")
        self.save.triggered.connect(self.save_figure)
        self.Map = self.bar.addMenu("Mapview")
        self.point_map = self.Map.addAction("Pos2map")
        self.point_kml = self.Map.addAction("Pos2kml")

        #-----------------------menu------------------------
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
        self.sol_files_edit.setPlaceholderText("eg.: C:/Users/Admin/Desktop/aber0010.list")

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
        self.figtype_gnss = ['Ele', 'Azi', 'Ele-Azi', 'C/N0', 'C/N0-Ele', 'Code MP', 'Code MP-Ele', 'Phase MP', 'Phase MP-Ele', 'IOD', 'IOD-Ele', 'Code Noise', 'Phase Noise', 'DIR', 'DSR', 'Cycle Slips']
        self.figtype_combobox.addItems(self.figtype_gnss)
        self.figtype_combobox.setMinimumSize(QSize(bobox_w, bobox_h))

        self.sys_label = QLabel('Sys', self)
        self.sys_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sys_label.setAlignment(Qt.AlignCenter)
        self.sys_label.setMinimumSize(QSize(zlable_w, zlable_h))
        self.sys_label.setMaximumSize(QSize(zlable_w, zlable_h))

        self.sys_combobox = QComboBox(self)
        self.sys_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sys_ty = ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS']
        # sys_combobox.setStyleSheet("#typeCmb{border:1px solid rgb(204,204,204);border-radius:3px;height:28px;}QAbstractItemView::item {height: 28px;}")
        self.sys_combobox.addItems(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'NavIC', 'SBS'])
        self.sys_combobox.setMinimumSize(QSize(bobox_w, bobox_h))
        self.sys_combobox.currentIndexChanged.connect(self.select_sys)

        self.band_label = QLabel('Band', self)
        self.band_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.band_label.setAlignment(Qt.AlignCenter)
        self.band_label.setMinimumSize(QSize(zlable_w, zlable_h))
        self.band_label.setMaximumSize(QSize(zlable_w, zlable_h))

        self.band_combobox = QComboBox(self)
        self.band_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # band_combobox.setStyleSheet("QComboBox{background:white}")
        self.band_combobox.addItems(['All', 'L1', 'L2', 'L5'])
        self.band_gps = ['L1', 'L2', 'L5']
        self.band_glo = ['G1', 'G2']
        self.band_gal = ['E1', 'E5a', 'E5b', 'E6', 'E5']
        self.band_bds = ['B1I', 'B2I', 'B3I', 'B1c', 'B2a', 'B2b', 'B2ab']
        self.band_qzs = ['L1', 'L2', 'L5', 'L6']
        self.band_irn = ['L5', 'S', 'L1']
        self.band_sbs = ['L1', 'L5']
        self.band_all = ['G_L1', 'G_L2', 'G_L5', 'R_G1', 'R_G2', 'E_E1', 'E_E5a', 'E_E5b', 'E_E6', 'E_E5', 'C_B1I', 'C_B2I', 'C_B2a', 'C_B3I', 'C_B2a+b', 'C_B2c', 'J_L1', 'J_L2', 'J_L5', 'I_L5', 'I_S', 'S_L1', 'S_L5']
        self.band_combobox.setMinimumSize(QSize(bobox_w, bobox_h))
        # self.band_combobox.activated.connect(self.select_band)


        self.sate_label = QLabel('Sat', self)
        self.sate_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.sate_label.setAlignment(Qt.AlignCenter)
        self.sate_label.setMinimumSize(QSize(zlable_w, zlable_h))
        self.sate_label.setMaximumSize(QSize(zlable_w, zlable_h))

        self.sate_combobox = QComboBox(self)
        self.sate_combobox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        # sate_combobox.setStyleSheet("QComboBox{background:white}")
        self.sate_combobox.setMinimumSize(QSize(bobox_w, bobox_h))

        self.draw_btn = QPushButton('Execute', self)
        self.draw_btn.setMinimumSize(QSize(button_w, button_h))
        self.draw_btn.clicked.connect(self.plot_fig)

        self.grid_checkbox = QCheckBox('Grid', self)
        self.grid_checkbox.setMinimumSize(QSize(checkbox_w, checkbox_h))
        self.grid_checkbox.setChecked(True)
        self.grid_checkbox.stateChanged.connect(self.choose_grid)

        sol_box.setSpacing(Pagemargin)
        sol_box.addWidget(self.sol_files_lable, 0, 0, 1, 1)
        sol_box.addWidget(self.sol_files_edit, 0, 1, 1, 7)
        sol_box.addWidget(self.sol_files_btn, 0, 8, 1, 2)
        sol_box.addWidget(self.figtype_label, 1, 0, 1, 1)
        sol_box.addWidget(self.figtype_combobox, 1, 1, 1, 1)
        sol_box.addWidget(self.sys_label, 1, 2, 1, 1)
        sol_box.addWidget(self.sys_combobox, 1, 3, 1, 1)
        sol_box.addWidget(self.band_label, 1, 4, 1, 1)
        sol_box.addWidget(self.band_combobox, 1, 5, 1, 1)
        sol_box.addWidget(self.sate_label, 1, 6, 1, 1)
        sol_box.addWidget(self.sate_combobox, 1, 7, 1, 1)
        sol_box.addWidget(self.draw_btn, 1, 8, 1, 1)
        sol_box.addWidget(self.grid_checkbox, 1, 9, 1, 1)
        sol_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        # spacerItem4 = QSpacerItem(1, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # fig_box.addItem(spacerItem4)

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

        layout = QHBoxLayout(self)
        layout.addWidget(splitterRight)
        layout.setContentsMargins(0, 0, 0, 0)
        #
        mainFrame = QWidget()
        mainFrame.setLayout(layout)
        self.setCentralWidget(mainFrame)
        self.show()

    def canvas_(self):
        figure_ntb_h = 25*self.ratio
        Pagemargin   = 5*self.ratio
        self.figure_layout = QVBoxLayout(self)
        self.figure = Canvas()
        self.figure_ntb = NavigationToolbar(self.figure, self)
        self.figure_ntb.setStyleSheet("{background:white}")
        self.figure_ntb.setMaximumHeight(figure_ntb_h)
        self.figure.setStyleSheet("{background:white}")
        self.figure_ntb.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.figure_layout.addWidget(self.figure_ntb)
        self.figure_layout.addWidget(self.figure)
        self.figure_layout.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        return self.figure_layout

    def status_bar_show_msg(self):
        self.status.showMessage("East China University of Technology", 0)


    def save_figure(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Figure", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;SVG Files (*.svg *.svgz)")
        if filename:
            resolution, ok = QInputDialog.getDouble(self, "Select Dpi", "Please Input Dpi:", 300, 1, 10000, 2)
            if ok:
                size, ok1 = QInputDialog.getText(self, "Select Size", "Please Input Size（Width*Height）:", QLineEdit.Normal, '12.9*7')
                if ok1:
                    if '*' in size and len(size.split('*'))==2:
                        font_size_, ok2 = QInputDialog.getInt(self, "Font Size", "Please Input Font Size:", QLineEdit.Normal, 16)

                        if ok2:
                            file_ext = filename.split('.')[-1]
                            # set figure size
                            width, height = size.split('*')
                            self.figure.fig.set_size_inches(float(width), float(height))
                            # set fugure ax font size
                            font = {'family': 'Times New Roman', 'size': font_size_}
                            ax = self.figure.fig.axes[0]
                            ax.xaxis.label.set_fontproperties(font)
                            ax.yaxis.label.set_fontproperties(font)
                            ax.xaxis.set_tick_params(labelsize=font['size'])
                            ax.yaxis.set_tick_params(labelsize=font['size'])
                            try:
                                for text in ax.get_legend().texts:
                                    text.set_fontsize(font['size'])
                            except AttributeError:
                                pass
                            # save figure
                            self.figure.fig.savefig(filename, dpi=resolution, format=file_ext, bbox_inches='tight')
                            QMessageBox.information(self, 'Tips', 'Success Save Figure')
                    else:
                        QMessageBox.information(self, 'Tips', 'Input Size Mode Error')

    # --------------Grid select---------------------------------------------------------------------------------------------
    def choose_grid(self):
        """根据复选框的状态切换格网显示与否"""
        if self.grid_checkbox.isChecked():
            if hasattr(self, 'ax'):
                self.ax.grid(True,linestyle='--')
        else:
            if hasattr(self, 'ax'):
                self.ax.grid(False)
        self.figure.draw()


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
        from quality_check import rtkcmn as com
        prn_id = []
        sol_sys = np.array(self.sol_data['sat'])
        self.prn_sys = dict(zip(['GPS', 'GLO', 'GAL', 'BDS', 'QZS', 'NavIC', 'SBS', 'All'], [[], [], [], [], [], [], [], []]))
        for i in range(len(sol_sys)):
            prn_ = com.sat2id(sol_sys[i])
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
        self.prn_id_ = self.prn_sys['GPS'].copy()
        self.sate_combobox.addItems(['All'] + self.prn_sys['GPS'])
        self.band_id = self.band_gps
        self.point_map.triggered.connect(lambda checked: self.map_gui(self.sol_data, self.curdir_ini))
        self.point_kml.triggered.connect(lambda checked: self.kml_gui(self.sol_data, self.sol_filename))
        print('[{}] success load satellite info of observation file'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        QMessageBox.information(self, 'Tips', 'Load success')

###########################################function##########################################################
    def select_sys(self):
        from quality_check import rtkcmn as com
        if self.sol_data != None:
            sol_sys = np.array(self.sol_data['sat'])
            stat =1
        else:
            stat = 0
        if 'All' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_all)
            self.band_id = self.band_all
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['All']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'GPS' in self.sys_combobox.currentText() :
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_gps)
            self.band_id = self.band_gps
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['GPS']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'GLO' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_glo)
            self.band_id = self.band_glo
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['GLO']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'GAL' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_gal)
            self.band_id = self.band_gal
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['GAL']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'BDS' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_bds)
            self.band_id = self.band_bds
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['BDS']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'QZS' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_qzs)
            self.band_id = self.band_qzs
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['QZS']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'NavIC' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_irn)
            self.band_id = self.band_irn
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['NavIC']
                self.sate_combobox.addItems(['All'] + self.prn_id_)

        elif 'SBS' in self.sys_combobox.currentText():
            self.band_combobox.clear()
            self.band_combobox.addItems(['All'] + self.band_sbs)
            self.band_id = self.band_sbs
            self.sate_combobox.clear()
            if stat > 0:
                self.prn_id_ = self.prn_sys['SBS']
                self.sate_combobox.addItems(['All'] + self.prn_id_)
        else:
            if stat > 0:
                self.prn_id_ = self.prn_id.copy()
                self.sate_combobox.addItems(self.prn_id_)


    def plot_fig(self):
        if self.sol_data != None:
            stat =1
        else:
            stat = 0

        if stat > 0:
            # select data type
            fig_type = self.figtype_combobox.currentText()
            sys_type = self.sys_combobox.currentText()
            sat_type = self.sate_combobox.currentText()
            band_type = self.band_combobox.currentText()

            if  fig_type != '' and sys_type != '' and sat_type != '' and band_type != '':
                # draw data quality result
                # elevation
                if fig_type == 'Ele':
                    from plot import plot_elevation as mplot
                    import pandas as pd
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        ele_data = self.sol_data['ele']
                        prn_ = [sat_type]
                        data = ele_data[prn_]
                        time = ele_data['Epoch'].to_frame()
                        # mplot.elev_time(time, data, prn_)

                        sat_num = data.shape[1]
                        for i in range(sat_num):
                            self.ax.scatter(time, data.iloc[:, i], s=25, marker='o', label=prn_[i])
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)
                        self.ax.set_ylim(0, 90)
                        self.ax.set_xlim(time.head(1), time.tail(1))
                        self.ax.set_xlabel(u"GPST (HH:MM)", font)
                        self.ax.set_ylabel(u"Elevation (°)", font)
                        import matplotlib.dates as mdate
                        xfmt = mdate.DateFormatter('%H:%M')
                        self.ax.xaxis.set_major_formatter(xfmt)
                        plt.tight_layout()
                        self.figure.draw()
                    else:
                        ele_data = self.sol_data['ele']
                        prn_ = self.prn_id_
                        data = ele_data[prn_]
                        # time = pd.concat([ele_data['Epoch']]*data.shape[1], axis=1).to_frame() # repmat n*2
                        time = ele_data['Epoch'].to_frame()
                        # mplot.elev_time(time, data, prn_)

                        sat_num = data.shape[1]
                        for i in range(sat_num):
                            self.ax.scatter(time, data.iloc[:, i], s=25, marker='o', label=prn_[i])
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)
                        self.ax.set_ylim(0, 90)
                        self.ax.set_xlim(time.head(1), time.tail(1))
                        self.ax.set_xlabel(u"GPST (HH:MM)", font)
                        self.ax.set_ylabel(u"Elevation (°)", font)
                        import matplotlib.dates as mdate
                        xfmt = mdate.DateFormatter('%H:%M')
                        self.ax.xaxis.set_major_formatter(xfmt)
                        self.figure.draw()

                # azimuth
                elif fig_type == 'Azi':
                    from plot import plot_azimuth as mplot
                    import pandas as pd
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        t_data = self.sol_data['azi']
                        prn_ = [sat_type]
                        data = t_data[prn_]
                        time = t_data['Epoch'].to_frame()
                        # mplot.azim(time, data, prn_)

                        sat_num = data.shape[1]
                        # colors = distinctipy.get_colors(sat_num)
                        for i in range(sat_num):
                            df = data.iloc[:, i].apply(lambda x: x - 180 if x > 180 else x + 180)
                            self.ax.scatter(time, df, s=25, marker='o', label=prn_[i])
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        legend_ax = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)
                        self.ax.set_ylim([0, 360])
                        self.ax.set_xlabel(u"GPST (HH:MM)", font)
                        self.ax.set_ylabel(u"Azimuth (°)", font)
                        import matplotlib.dates as mdate
                        xfmt = mdate.DateFormatter('%H:%M')
                        self.ax.xaxis.set_major_formatter(xfmt)
                        self.figure.draw()
                    else:
                        t_data = self.sol_data['azi']
                        prn_ = self.prn_id_
                        data = t_data[prn_]
                        # time = pd.concat([ele_data['Epoch']]*data.shape[1], axis=1).to_frame() # repmat n*2
                        time = t_data['Epoch'].to_frame()
                        # mplot.azim(time, data, prn_)

                        sat_num = data.shape[1]
                        # colors = distinctipy.get_colors(sat_num)
                        for i in range(sat_num):
                            df = data.iloc[:, i].apply(lambda x: x - 180 if x > 180 else x + 180)
                            self.ax.scatter(time, df, s=25, marker='o', label=prn_[i])
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        legend_ax = self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)
                        self.ax.set_ylim([0, 360])
                        self.ax.set_xlabel(u"GPST (HH:MM)", font)
                        self.ax.set_ylabel(u"Azimuth (°)", font)
                        import matplotlib.dates as mdate
                        xfmt = mdate.DateFormatter('%H:%M')
                        self.ax.xaxis.set_major_formatter(xfmt)
                        self.figure.draw()

                elif fig_type == 'Ele-Azi':
                    from plot import plot_elevation_azimuth as mplot
                    import pandas as pd
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        a_data = self.sol_data['azi']
                        e_data = self.sol_data['ele']
                        prn_ = [sat_type]
                        data_a = a_data[prn_]
                        data_e = e_data[prn_]
                        # mplot.azi_ele(data_a, data_e, prn_)

                        sat_num = data_e.shape[1]
                        # colors = distinctipy.get_colors(sat_num)
                        for i in range(sat_num):
                            df = data_a.iloc[:, i].apply(lambda x: x - 180 if x > 180 else x + 180)
                            self.ax.scatter(df, data_e.iloc[:, i], s=20, marker='.', label=prn_[i])
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        self.ax.set_xlim([0, 360])
                        self.ax.set_ylim([0, 90])
                        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        self.ax.set_xlabel(u"Azimuth (°)", font)
                        self.ax.set_ylabel(u"Elevation (°)", font)
                        self.figure.draw()
                    else:
                        a_data = self.sol_data['azi']
                        e_data = self.sol_data['ele']
                        prn_ = self.prn_id_
                        data_a = a_data[prn_]
                        data_e = e_data[prn_]
                        # mplot.azi_ele(data_a, data_e, prn_)
                        sat_num = data_e.shape[1]
                        # colors = distinctipy.get_colors(sat_num)
                        for i in range(sat_num):
                            df = data_a.iloc[:, i].apply(lambda x: x - 180 if x > 180 else x + 180)
                            self.ax.scatter(df, data_e.iloc[:, i], s=20, marker='.', label=prn_[i])
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        self.ax.set_xlim([0, 360])
                        self.ax.set_ylim([0, 90])
                        self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        self.ax.set_xlabel(u"Azimuth (°)", font)
                        self.ax.set_ylabel(u"Elevation (°)", font)
                        self.figure.draw()

                # CN0
                elif fig_type == 'C/N0':
                    import pandas as pd
                    import matplotlib.dates as mdate

                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'],[['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'],['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'],  ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            CN0_data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]
                            for i, band_pos_ in enumerate(band_pos):
                                time = CN0_data[band_pos_]['Epoch']
                                mean_ = CN0_data[band_pos_][[sat_type]].mean(axis=0)
                                data_ = CN0_data[band_pos_][[sat_type]]
                                if ~data_.isna().all().all():
                                    self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]]+' Mean:'+str(np.round(mean_.values, 2)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Carrier to Noise Ratio (dB-Hz)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.8)
                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            CN0_data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]
                            prn_ = self.prn_id_
                            ncol = 1

                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    time = pd.concat([CN0_data[band_pos_]['Epoch']]*len(prn_), axis=1)
                                    mean_ = CN0_data[band_pos_][prn_].mean(axis=0).to_frame().mean(axis=0)
                                    data_ = CN0_data[band_pos_][prn_]
                                    if ~data_.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(time, data_, s=30, marker='o', label=sys_band_[band_pos[i]]+' Mean:'+str(np.round(mean_.values, 2)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Carrier to Noise Ratio (dB-Hz)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.8)

                            self.figure.draw()

                # CN0-ele
                elif fig_type == 'C/N0-Ele':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            ele_data = self.sol_data['ele']
                            CN0_data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]
                            for i, band_pos_ in enumerate(band_pos):
                                data_e = ele_data[[sat_type]]
                                mean_ = CN0_data[band_pos_][[sat_type]].mean(axis=0)
                                data_c = CN0_data[band_pos_][[sat_type]]
                                if ~data_c.isna().all().all():
                                    self.ax.scatter(data_e, data_c, s=25, marker='o', label=sys_band_[band_pos[i]]+' Mean:'+str(np.round(mean_.values, 2)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"Elevation (°)", font)
                            self.ax.set_ylabel(u"Carrier to Noise Ratio (dB-Hz)", font)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            ele_data = self.sol_data['ele']
                            CN0_data = [self.sol_data['CN0']['CNRS1':'CNRS1'], self.sol_data['CN0']['CNRS2':'CNRS2'], self.sol_data['CN0']['CNRS3':'CNRS3'], self.sol_data['CN0']['CNRS4':'CNRS4'], self.sol_data['CN0']['CNRS5':'CNRS5'], self.sol_data['CN0']['CNRS6':'CNRS6'], self.sol_data['CN0']['CNRS7':'CNRS7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    data_e = ele_data[prn_]
                                    mean_  = CN0_data[band_pos_][prn_].mean(axis=0).to_frame().mean(axis=0)
                                    data_c = CN0_data[band_pos_][prn_]
                                    if ~data_c.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(data_e, data_c, s=30, marker='o', label=sys_band_[band_pos[i]]+ ' Mean:' + str(np.round(mean_.values, 2)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"Elevation (°)", font)
                            self.ax.set_ylabel(u"Carrier to Noise Ratio (dB-Hz)", font)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                # mp
                elif fig_type == 'Code MP':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            MP_data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                            for i, band_pos_ in enumerate(band_pos):
                                time  = MP_data[band_pos_]['Epoch']
                                rms_ = (MP_data[band_pos_][[sat_type]]**2).mean(axis=0)**(1/2)
                                data_ = MP_data[band_pos_][[sat_type]]
                                if ~data_.isna().all().all():
                                    self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]] + ' RMS:' + str(np.round(rms_.values, 2)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Code Multipath (m)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            MP_data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    time  = pd.concat([MP_data[band_pos_]['Epoch']]*len(prn_), axis=1)
                                    rms_ = ((MP_data[band_pos_][prn_]**2).mean(axis=0)**(1/2)).to_frame().mean(axis=0)
                                    data_ = MP_data[band_pos_][prn_]
                                    if ~data_.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]] + ' RMS:' + str(np.round(rms_.values, 2)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Code Multipath (m)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                # mp-ele
                elif fig_type == 'Code MP-Ele':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            ele_data = self.sol_data['ele']
                            MP_data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                            for i, band_pos_ in enumerate(band_pos):
                                data_e = ele_data[[sat_type]]
                                rms_ = (MP_data[band_pos_][[sat_type]]**2).mean(axis=0)**(1/2)
                                data_c = MP_data[band_pos_][[sat_type]]
                                if ~data_c.isna().all().all():
                                    self.ax.scatter(data_e, data_c, s=25, marker='o', label=sys_band_[band_pos[i]] + ' RMS:' + str(np.round(rms_.values, 2)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"Elevation (°)", font)
                            self.ax.set_ylabel(u"Code Multipath (m)", font)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)
                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            ele_data = self.sol_data['ele']
                            MP_data = [self.sol_data['MP']['MPM1':'MPM1'], self.sol_data['MP']['MPM2':'MPM2'], self.sol_data['MP']['MPM3':'MPM3'], self.sol_data['MP']['MPM4':'MPM4'], self.sol_data['MP']['MPM5':'MPM5'], self.sol_data['MP']['MPM6':'MPM6'], self.sol_data['MP']['MPM7':'MPM7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    data_e = ele_data[prn_]
                                    rms_ = ((MP_data[band_pos_][prn_]**2).mean(axis=0)**(1/2)).to_frame().mean(axis=0)
                                    data_c = MP_data[band_pos_][prn_]
                                    if ~data_c.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(data_e, data_c, s=25, marker='o', label=sys_band_[band_pos[i]]+ ' RMS:' + str(np.round(rms_.values, 2)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"Elevation (°)", font)
                            self.ax.set_ylabel(u"Code Multipath (m)", font)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                # gfif
                elif fig_type == 'Phase MP':
                    import pandas as pd
                    import matplotlib.dates as mdate

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        GFIF_data = self.sol_data['GFIF']
                        time = GFIF_data['Epoch']
                        data_ = GFIF_data[[sat_type]]
                        if ~data_.isna().all().all():
                            self.ax.scatter(time, data_*100, s=25, marker='o', label=sat_type)
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                 }
                        self.ax.set_xlabel(u"GPST (HH:MM)", font)
                        self.ax.set_ylabel(u"Phase Multipath (cm)", font)
                        xfmt = mdate.DateFormatter('%H:%M')
                        self.ax.xaxis.set_major_formatter(xfmt)
                        legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)

                        self.figure.draw()
                    else:
                        GFIF_data = self.sol_data['GFIF']
                        prn_ = self.prn_id_
                        time = GFIF_data['Epoch']
                        if len(prn_)>0:
                            for prn in prn_:
                                self.ax.scatter(time,  GFIF_data[prn]*100, s=25, marker='o', label=prn)
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                 }
                        self.ax.set_xlabel(u"GPST (HH:MM)", font)
                        self.ax.set_ylabel(u"Phase Multipath (cm)", font)
                        xfmt = mdate.DateFormatter('%H:%M')
                        self.ax.xaxis.set_major_formatter(xfmt)
                        legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)

                        self.figure.draw()


                # GFIF-ele
                elif fig_type == 'Phase MP-Ele':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        ele_data = self.sol_data['ele']
                        GFIF_data = self.sol_data['GFIF']
                        self.ax.scatter(ele_data[[sat_type]], GFIF_data[[sat_type]]*100, s=25, marker='o', label=sat_type)
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        self.ax.set_xlabel(u"Elevation (°)", font)
                        self.ax.set_ylabel(u"Phase Multipath (cm)", font)
                        legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)

                        self.figure.draw()
                    else:
                        ele_data = self.sol_data['ele']
                        GFIF_data = self.sol_data['GFIF']
                        prn_ = self.prn_id_
                        if len(prn_) > 0:
                            for sat_ in prn_:
                                self.ax.scatter(ele_data[[sat_]], GFIF_data[[sat_]]*100, s=25, marker='o', label=sat_)
                        self.ax.grid(linestyle='--')
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        self.ax.set_xlabel(u"Elevation (°)", font)
                        self.ax.set_ylabel(u"Phase Multipath (cm)", font)
                        legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_sizes([10])
                            handle.set_alpha(0.4)

                        self.figure.draw()

                # iod
                elif fig_type == 'IOD':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            iod_data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]
                            for i, band_pos_ in enumerate(band_pos):
                                time = iod_data[band_pos_]['Epoch']
                                rms_ = (iod_data[band_pos_][[sat_type]]**2).mean(axis=0)**(1/2)
                                data_ = iod_data[band_pos_][[sat_type]]
                                if ~data_.isna().all().all():
                                    self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]] + ' Mean:' + str(np.round(rms_.values, 4)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"ionospheric delay rate (m/s)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            iod_data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    time = pd.concat([iod_data[band_pos_]['Epoch']]*len(prn_), axis=1)
                                    rms_ = ((iod_data[band_pos_][prn_]**2).mean(axis=0)**(1/2)).to_frame().mean(axis=0)
                                    data_ = iod_data[band_pos_][prn_]
                                    if ~data_.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]]+ ' RMS:' + str(np.round(rms_.values, 4)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Ionospheric Delay Rate (m/s)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                # iod-ele
                elif fig_type == 'IOD-Ele':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            ele_data = self.sol_data['ele']
                            iod_data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]
                            for i, band_pos_ in enumerate(band_pos):
                                data_e = ele_data[[sat_type]]
                                rms_ = (iod_data[band_pos_][[sat_type]]**2).mean(axis=0)**(1/2)
                                data_i = iod_data[band_pos_][[sat_type]]
                                if ~data_i.isna().all().all():
                                    self.ax.scatter(data_e, data_i, s=25, marker='o', label=sys_band_[band_pos[i]]+' RMS:'+str(np.round(rms_.values, 4)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"Elevation (°)", font)
                            self.ax.set_ylabel(u"Ionospheric Delay Rate (m/s)", font)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            ele_data = self.sol_data['ele']
                            iod_data = [self.sol_data['iod']['IODI1':'IODI1'], self.sol_data['iod']['IODI2':'IODI2'], self.sol_data['iod']['IODI3':'IODI3'], self.sol_data['iod']['IODI4':'IODI4'], self.sol_data['iod']['IODI5':'IODI5'], self.sol_data['iod']['IODI6':'IODI6'], self.sol_data['iod']['IODI7':'IODI7']]
                            prn_ = self.prn_id_

                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    data_e = ele_data[prn_]
                                    rms_ = ((iod_data[band_pos_][prn_]**2).mean(axis=0)**(1/2)).to_frame().mean(axis=0)
                                    data_i = iod_data [band_pos_][prn_]
                                    if ~data_i.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(data_e, data_i, s=30, marker='o', label=sys_band_[band_pos[i]] + ' RMS:' + str(np.round(rms_.values, 4)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_xlabel(u"Elevation (°)", font)
                            self.ax.set_ylabel(u"Ionospheric Delay Rate (m/s)", font)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                # intebarplot
                elif fig_type == 'DIR':
                    from quality_check import rtkcmn as com
                    import pandas as pd
                    band_sys = {'GPS': ['L1', 'L2', 'L5'], 'GLO': ['G1', 'G2', 'G3'], 'BDS': ['B1I', 'B2I', 'B3I', 'B1c', 'B2a', 'B2b', 'B2ab'],
                                'GAL': ['E1', 'E5a', 'E5b', 'E6', 'E5'], 'QZS': ['L1', 'L2', 'L5', 'L6'], 'NavIC': ['L5', 'S', 'L1'],
                                'SBS': ['L1', 'L5']}
                    # colors = plt.get_cmap('hsv', 6)
                    colors = ['m', 'b', 'deeppink', 'turquoise', 'orange', 'r', 'green', 'c']
                    color_sys = {'GPS': [colors[0], colors[1], colors[2]], 'GLO': [colors[0], colors[1], colors[2]], 'BDS': [colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6]],
                                 'GAL': [colors[0], colors[1], colors[2], colors[3], colors[4]], 'QZS': [colors[0], colors[1], colors[2], colors[3]], 'NavIC': [colors[0], colors[1], colors[2]],
                                 'SBS': [colors[0], colors[1]]}

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    prn_ = self.prn_sys[sys_type]
                    inte_data = self.sol_data['inte']

                    if len(prn_)>0:
                        x0 = np.arange(len(prn_))*8
                        total_width, n = 6, len(band_sys[sys_type])
                        width = total_width/n
                        x = x0 - (total_width - width)/2
                        if sys_type != 'BDS':
                            for i in range(n):
                                self.ax.bar(x + width*i, np.array(inte_data[prn_].iloc[i, :]).T.astype(np.float64), width=width, color=color_sys[sys_type][i], label=band_sys[sys_type][i])
                        else:
                            bdsband_pos = [0, 1, 3, 5, 2, 6, 4]
                            for i in range(n):
                                self.ax.bar(x + width*i, np.array(inte_data[prn_].iloc[bdsband_pos[i], :]).T.astype(np.float64), width=width, color=color_sys[sys_type][i], label=band_sys[sys_type][i])
                        self.ax.set_xticks(x0)
                        self.ax.set_xticklabels(prn_)
                        plt.xticks(rotation=90)
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                 }
                        self.ax.set_ylabel(r"Data Integrity Rate (%)", font)
                        self.ax.grid(linestyle='--')
                        legend_ax = self.ax.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=n, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_alpha(0.8)

                    self.figure.draw()

                # fullbarplot
                elif fig_type == 'DSR':
                    from quality_check import rtkcmn as com
                    import pandas as pd
                    band_sys = {'GPS': ['L1', 'L2', 'L5'], 'GLO': ['G1', 'G2', 'G3'], 'BDS': ['B1I', 'B2I', 'B3I', 'B1c', 'B2a', 'B2b', 'B2ab'],
                                'GAL': ['E1', 'E5a', 'E5b', 'E6', 'E5'], 'QZS': ['L1', 'L2', 'L5', 'L6'], 'NavIC': ['L5', 'S', 'L1'],
                                'SBS': ['L1', 'L5']}
                    # colors = plt.get_cmap('hsv', 6)
                    colors = ['m', 'b', 'deeppink', 'turquoise', 'orange', 'r', 'green', 'c']
                    color_sys = {'GPS': [colors[0], colors[1], colors[2]], 'GLO': [colors[0], colors[1], colors[2]], 'BDS': [colors[0], colors[1], colors[2], colors[3], colors[4], colors[5], colors[6]],
                                 'GAL': [colors[0], colors[1], colors[2], colors[3], colors[4]], 'QZS': [colors[0], colors[1], colors[2], colors[3]], 'NavIC': [colors[0], colors[1], colors[2]],
                                 'SBS': [colors[0], colors[1]]}

                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    prn_ = self.prn_sys[sys_type]
                    full_data = self.sol_data['satu']

                    if len(prn_)>0:
                        x0 = np.arange(len(prn_))*8
                        total_width, n = 6, len(band_sys[sys_type])
                        width = total_width/n
                        x = x0 - (total_width - width)/2
                        if sys_type != 'BDS':
                            for i in range(n):

                                aa = np.array(full_data[prn_].iloc[i, :]).T.astype(np.float64)
                                self.ax.bar(x + width*i, np.array(full_data[prn_].iloc[i, :]).T.astype(np.float64), width=width, color=color_sys[sys_type][i], label=band_sys[sys_type][i])
                        else:
                            bdsband_pos = [0, 1, 3, 5, 2, 6, 4]
                            for i in range(n):
                                self.ax.bar(x + width*i, np.array(full_data[prn_].iloc[bdsband_pos[i], :]).T.astype(np.float64), width=width, color=color_sys[sys_type][i], label=band_sys[sys_type][i])
                        self.ax.set_xticks(x0)
                        self.ax.set_xticklabels(prn_)
                        plt.xticks(rotation=90)
                        font = {'family': 'Times New Roman',
                                'size': font_size,
                                'weight': 'bold',
                                }
                        self.ax.set_ylabel(r"Data Saturation Rate (%)", font)
                        self.ax.grid(linestyle='--')
                        legend_ax = self.ax.legend(loc='upper right', bbox_to_anchor=(1, 1.1), ncol=n, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                        for handle in legend_ax.legendHandles:
                            handle.set_alpha(0.8)

                    self.figure.draw()

                # Pnoisebarplot
                elif fig_type == 'Code Noise':
                    from quality_check import rtkcmn as com
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            pnoise_data = [self.sol_data['Pnoise']['PNSN1':'PNSN1'], self.sol_data['Pnoise']['PNSN2':'PNSN2'], self.sol_data['Pnoise']['PNSN3':'PNSN3'], self.sol_data['Pnoise']['PNSN4':'PNSN4'], self.sol_data['Pnoise']['PNSN5':'PNSN5'], self.sol_data['Pnoise']['PNSN6':'PNSN6'], self.sol_data['Pnoise']['PNSN7':'PNSN7']]
                            for i, band_pos_ in enumerate(band_pos):
                                time = pnoise_data[band_pos_]['Epoch']
                                rms_ = (pnoise_data[band_pos_][[sat_type]]**2).mean(axis=0)**(1/2)
                                data_ = pnoise_data[band_pos_][[sat_type]]
                                if ~data_.isna().all().all():
                                    self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]]+ ' RMS:' + str(np.round(rms_.values, 4)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Code Noise (m)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            pnoise_data = [self.sol_data['Pnoise']['PNSN1':'PNSN1'], self.sol_data['Pnoise']['PNSN2':'PNSN2'], self.sol_data['Pnoise']['PNSN3':'PNSN3'], self.sol_data['Pnoise']['PNSN4':'PNSN4'], self.sol_data['Pnoise']['PNSN5':'PNSN5'], self.sol_data['Pnoise']['PNSN6':'PNSN6'], self.sol_data['Pnoise']['PNSN7':'PNSN7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    time = pd.concat([pnoise_data[band_pos_]['Epoch']]*len(prn_), axis=1)
                                    rms_ = ((pnoise_data[band_pos_][prn_]**2).mean(axis=0)**(1/2)).to_frame().mean(axis=0)
                                    data_ = pnoise_data[band_pos_][prn_]
                                    if ~data_.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]]+ ' RMS:' + str(np.round(rms_.values, 4)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Code Noise (m)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                # Cnoisebarplot
                elif fig_type == 'Phase Noise':
                    import pandas as pd
                    import matplotlib.dates as mdate
                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'], [['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'], ['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'], ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            cnoise_data = [self.sol_data['Cnoise']['CNSN1':'CNSN1'], self.sol_data['Cnoise']['CNSN2':'CNSN2'], self.sol_data['Cnoise']['CNSN3':'CNSN3'], self.sol_data['Cnoise']['CNSN4':'CNSN4'], self.sol_data['Cnoise']['CNSN5':'CNSN5'], self.sol_data['Cnoise']['CNSN6':'CNSN6'], self.sol_data['Cnoise']['CNSN7':'CNSN7']]
                            for i, band_pos_ in enumerate(band_pos):
                                time = cnoise_data[band_pos_]['Epoch']
                                rms_ = (cnoise_data[band_pos_][[sat_type]]**2).mean(axis=0)**(1/2)
                                data_ = cnoise_data[band_pos_][[sat_type]]
                                if ~data_.isna().all().all():
                                    self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]]+ ' RMS:' + str(np.round(rms_.values, 4)[0]))
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Phase Noise (Cycle)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            cnoise_data = [self.sol_data['Cnoise']['CNSN1':'CNSN1'], self.sol_data['Cnoise']['CNSN2':'CNSN2'], self.sol_data['Cnoise']['CNSN3':'CNSN3'], self.sol_data['Cnoise']['CNSN4':'CNSN4'], self.sol_data['Cnoise']['CNSN5':'CNSN5'], self.sol_data['Cnoise']['CNSN6':'CNSN6'], self.sol_data['Cnoise']['CNSN7':'CNSN7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    time = pd.concat([cnoise_data[band_pos_]['Epoch']]*len(prn_), axis=1)
                                    rms_ = ((cnoise_data[band_pos_][prn_]**2).mean(axis=0)**(1/2)).to_frame().mean(axis=0)
                                    data_ = cnoise_data[band_pos_][prn_]
                                    if ~data_.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]] + ' RMS:' + str(np.round(rms_.values, 4)[0]))
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Phase Noise (Cycle)", font)
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.4)

                            self.figure.draw()

                elif fig_type == 'Cycle Slips':
                    import pandas as pd
                    import matplotlib.dates as mdate

                    sys_band = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC'],[['L1', 'L2', 'L5'], ['G1', 'G2', 'G3'],['B1I', 'B2I', 'B2a', 'B3I', 'B2ab', 'B1c', 'B2b'],  ['E1', 'E5a', 'E5b', 'E6', 'E5'], ['L1', 'L2', 'L5', 'L6'], ['L1', 'L5'], ['L5', 'S', 'L1']]))
                    sys_band_ = sys_band[sys_type]
                    self.figure.fig.clear()
                    fig = self.figure.fig
                    self.ax = fig.add_subplot(111)
                    if sat_type != 'All':
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            cycle_data = [self.sol_data['cycle']['CYCLE1':'CYCLE1'], self.sol_data['cycle']['CYCLE2':'CYCLE2'], self.sol_data['cycle']['CYCLE3':'CYCLE3'], self.sol_data['cycle']['CYCLE4':'CYCLE4'], self.sol_data['cycle']['CYCLE5':'CYCLE5'], self.sol_data['cycle']['CYCLE6':'CYCLE6'], self.sol_data['cycle']['CYCLE7':'CYCLE7']]
                            for i, band_pos_ in enumerate(band_pos):
                                time = cycle_data[band_pos_]['Epoch']
                                mean_ = cycle_data[band_pos_][[sat_type]].mean(axis=0)
                                data_ = cycle_data[band_pos_][[sat_type]]
                                if ~data_.isna().all().all():
                                    self.ax.scatter(time, data_, s=25, marker='o', label=sys_band_[band_pos[i]])
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                     }
                            self.ax.set_title(u"(0:Normal 1:Slip)", font)
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Cycle Slip Indicator", font)
                            self.ax.set_ylim([-0.5, 1.5])
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=3, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.8)
                            self.figure.draw()
                    else:
                        band_pos = self.search_band(sys_type, band_type)
                        band_flag = self.band_id
                        if band_pos != None:
                            cycle_data = [self.sol_data['cycle']['CYCLE1':'CYCLE1'], self.sol_data['cycle']['CYCLE2':'CYCLE2'], self.sol_data['cycle']['CYCLE3':'CYCLE3'], self.sol_data['cycle']['CYCLE4':'CYCLE4'], self.sol_data['cycle']['CYCLE5':'CYCLE5'], self.sol_data['cycle']['CYCLE6':'CYCLE6'], self.sol_data['cycle']['CYCLE7':'CYCLE7']]
                            prn_ = self.prn_id_
                            ncol = 1
                            for i, band_pos_ in enumerate(band_pos):
                                if len(prn_)>0:
                                    time = pd.concat([cycle_data[band_pos_]['Epoch']]*len(prn_), axis=1)
                                    data_ = cycle_data[band_pos_][prn_]
                                    if ~data_.isna().all().all():
                                        if sys_type != 'All':
                                            self.ax.scatter(time, data_, s=30, marker='o', label=sys_band_[band_pos[i]])
                                            ncol = 3
                            self.ax.grid(linestyle='--')
                            font = {'family': 'Times New Roman',
                                    'size': font_size,
                                    'weight': 'bold',
                                    }
                            self.ax.set_title(u"(0:Normal 1:Slip)", font)
                            self.ax.set_xlabel(u"GPST (HH:MM)", font)
                            self.ax.set_ylabel(u"Cycle Slip Indicator", font)
                            self.ax.set_ylim([-0.5,1.5])
                            xfmt = mdate.DateFormatter('%H:%M')
                            self.ax.xaxis.set_major_formatter(xfmt)
                            legend_ax = self.ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=ncol, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
                            for handle in legend_ax.legendHandles:
                                handle.set_sizes([10])
                                handle.set_alpha(0.8)

                            self.figure.draw()



    def search_band(self, sys_type, band_type):
        band_pos = None
        if 'GPS' in sys_type:
            if band_type != 'All':
                band_pos = [self.band_gps.index(band_type)]
            else:
                band_pos = list(np.arange(len(self.band_gps)))
        elif 'GLO' in sys_type:
            if band_type != 'All':
                band_pos = [self.band_glo.index(band_type)]
            else:
                band_pos = list(np.arange(len(self.band_glo)))
        elif 'GAL' in sys_type:
            if band_type != 'All':
                band_pos = [self.band_gal.index(band_type)]
            else:
                band_pos = list(np.arange(len(self.band_gal)))
        elif 'BDS' in sys_type:
            band_pos_ = [0, 1, 3, 5, 2, 6, 4]
            if band_type != 'All':
                band_pos = [band_pos_[self.band_bds.index(band_type)]]
            else:
                band_pos = band_pos_
        elif 'QZS' in sys_type:
            if band_type != 'All':
                band_pos = [self.band_qzs.index(band_type)]
            else:
                band_pos = list(np.arange(len(self.band_qzs)))
        elif 'NavIC' in sys_type:
            if band_type != 'All':
                band_pos = [self.band_irn.index(band_type)]
            else:
                band_pos = list(np.arange(len(self.band_irn)))
        elif 'SBS' in sys_type:
            if band_type != 'All':
                band_pos = [self.band_sbs.index(band_type)]
            else:
                band_pos = list(np.arange(len(self.band_sbs)))
        elif 'All' in sys_type:
            band_pos = list(np.arange(len(self.band_bds)))
        return band_pos


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


#######################################matplotlib######################################################

class Canvas(FigureCanvas):

    def __init__(self, parent=None):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'

        params = {
            'font.family': 'Times new roman',
            'font.size': font_size,
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

class Canvas_save(FigureCanvas):

    def __init__(self, parent=None):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'

        params = {
            'font.family': 'Times new roman',
            'font.size': font_size,
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
    # import qdarkstyle


    app = QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet())
    # app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5', palette=LightPalette()))
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    print(dpi)
    ratio = dpi/96
    # framelessWnd = FramelessWindow()
    form = plot_sat(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    # font.setPointSize(9)
    font.setPixelSize(14*ratio)
    # font.setStyleSheet("color:blue")
    # font.setPointSize(11)
    app.setFont(font)
    # framelessWnd.setContent(form)
    # framelessWnd.show()
    form.show()
    sys.exit(app.exec_())