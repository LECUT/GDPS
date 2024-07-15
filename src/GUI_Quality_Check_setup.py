from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
import sys
import os
import configparser
import resources_rc

curdir = os.getcwd()

class Data_Preprocessing_Setup(QMainWindow):
    _signal = pyqtSignal(dict, dict)
    def __init__(self, conf_gen, conf_qc, ratio):
        super().__init__()
        self.conf_gen = conf_gen
        self.conf_qc  = conf_qc
        self.ratio = ratio
        self.setWindowTitle("Option")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.setGeometry(720, 287, 470, 380)
        self.resize(350, 150)
        self.setFixedSize(450*self.ratio, 390*self.ratio)
        # self.setMinimumSize(QSize(570, 560))
        # self.setFixedHeight(560)
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        self.setup_ui()

    def setup_ui(self):
        Label_w       = 60*self.ratio
        Label_h       = 25*self.ratio
        bLabel_w      = 50*self.ratio
        bLabel_h      = 25*self.ratio
        LineEdit_w    = 80*self.ratio
        LineEdit_h    = 25*self.ratio
        zPushButton_w = 80*self.ratio
        zPushButton_h = 25*self.ratio
        Pagemargin    = 5*self.ratio
        QSpacerItem_w = 10*self.ratio
        QSpacerItem_h = 1*self.ratio

        set_box = QGridLayout()
        self.height_angle_label = QLabel('Elevation Mask')
        self.height_angle_label.setMinimumSize(QSize(Label_w, Label_h))
        self.height_angle_lineedit = QLineEdit()
        self.height_angle_lineedit.setText('0')
        self.height_angle_lineedit.setPlaceholderText(' 0~90')
        self.height_angle_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.carrier_noise_label = QLabel('Carrier to Noise Ratio Mask')
        self.carrier_noise_label.setMinimumSize(QSize(Label_w, Label_h))
        self.carrier_noise_lineedit = QLineEdit()
        self.carrier_noise_lineedit.setText('0')
        self.carrier_noise_lineedit.setPlaceholderText(' 0')
        self.carrier_noise_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))


        self.pos_height_angle_label = QLabel('SPP Elevation Mask')
        self.pos_height_angle_label.setMinimumSize(QSize(Label_w, Label_h))
        self.pos_height_angle_lineedit = QLineEdit()
        self.pos_height_angle_lineedit.setText('5')
        self.pos_height_angle_lineedit.setPlaceholderText(' 5~90')
        self.pos_height_angle_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.pos_carrier_noise_label = QLabel('SPP Carrier to Noise Ratio Mask')
        self.pos_carrier_noise_label.setMinimumSize(QSize(Label_w, Label_h))
        self.pos_carrier_noise_lineedit = QLineEdit()
        self.pos_carrier_noise_lineedit.setText('0')
        self.pos_carrier_noise_lineedit.setPlaceholderText(' 0')
        self.pos_carrier_noise_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))


        self.iono_correction_label = QLabel('SPP Ion Correction')
        self.iono_correction_label.setMinimumSize(QSize(Label_w, Label_h))
        self.iono_correction_combox = QComboBox()
        self.iono_correction_combox.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.iono_correction_combox.addItems(['ON (klobuchar model)', 'OFF (no correct)'])

        self.trop_correction_label = QLabel('SPP Trop Correction')
        self.trop_correction_label.setMinimumSize(QSize(Label_w, Label_h))
        self.trop_correction_combox = QComboBox()
        self.trop_correction_combox.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.trop_correction_combox.addItems(['ON (saastamoinen model)', 'OFF (no correct)ON'])

        self.motion_mode_label = QLabel('Motion Mode')
        self.motion_mode_label.setMinimumSize(QSize(Label_w, Label_h))
        self.motion_mode_combox = QComboBox()
        self.motion_mode_combox.setMinimumSize(QSize(LineEdit_w, LineEdit_h))
        self.motion_mode_combox.addItems(['0 (static)', '1 (dynamic)'])

        self.continuous_epoch_label = QLabel('Min Number of Continuous Epoch')
        self.continuous_epoch_label.setMinimumSize(QSize(Label_w, Label_h))
        self.continuous_epoch_lineedit = QLineEdit()
        self.continuous_epoch_lineedit.setText('1')
        self.continuous_epoch_lineedit.setPlaceholderText('1')
        self.continuous_epoch_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        set_box.setSpacing(1)
        set_box.addWidget(self.height_angle_label, 0, 0)
        set_box.addWidget(self.height_angle_lineedit, 0, 1)
        set_box.addWidget(self.carrier_noise_label, 1, 0)
        set_box.addWidget(self.carrier_noise_lineedit, 1, 1)
        set_box.addWidget(self.pos_height_angle_label, 2, 0)
        set_box.addWidget(self.pos_height_angle_lineedit, 2, 1)
        set_box.addWidget(self.pos_carrier_noise_label, 3, 0)
        set_box.addWidget(self.pos_carrier_noise_lineedit, 3, 1)
        set_box.addWidget(self.iono_correction_label, 4, 0)
        set_box.addWidget(self.iono_correction_combox, 4, 1)
        set_box.addWidget(self.trop_correction_label, 5, 0)
        set_box.addWidget(self.trop_correction_combox, 5, 1)
        set_box.addWidget(self.motion_mode_label, 6, 0)
        set_box.addWidget(self.motion_mode_combox, 6, 1)
        set_box.addWidget(self.continuous_epoch_label, 7, 0)
        set_box.addWidget(self.continuous_epoch_lineedit, 7, 1)
        set_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        set_wg = QFrame()
        set_wg.setFrameShape(QFrame.Box)
        set_wg.setLayout(set_box)

        sys_box = QGridLayout()
        self.choose_system_label = QLabel('System：')
        self.choose_system_label.setMaximumSize(QSize(Label_w, Label_h))
        self.G_checkbox = QCheckBox('GPS')
        self.G_checkbox.setChecked(True)
        self.G_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")
        self.C_checkbox = QCheckBox('BDS')
        self.C_checkbox.setChecked(True)
        self.C_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")
        self.R_checkbox = QCheckBox('GLO')
        self.R_checkbox.setChecked(True)
        self.R_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")
        self.E_checkbox = QCheckBox('GAL')
        self.E_checkbox.setChecked(True)
        self.E_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")
        self.J_checkbox = QCheckBox('QZS')
        self.J_checkbox.setChecked(True)
        self.J_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")
        self.I_checkbox = QCheckBox('NavIC')
        self.I_checkbox.setChecked(True)
        self.I_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")
        self.S_checkbox = QCheckBox('SBS')
        self.S_checkbox.setChecked(True)
        self.S_checkbox.setStyleSheet("QCheckBox::indicator { width: 30px; height: 15px; }")

        sys_box.setSpacing(1)
        sys_box.addWidget(self.choose_system_label, 0, 0)
        sys_box.addWidget(self.G_checkbox, 0, 1)
        sys_box.addWidget(self.C_checkbox, 0, 3)
        sys_box.addWidget(self.R_checkbox, 0, 2)
        sys_box.addWidget(self.E_checkbox, 1, 0)
        sys_box.addWidget(self.J_checkbox, 1, 1)
        sys_box.addWidget(self.I_checkbox, 1, 2)
        sys_box.addWidget(self.S_checkbox, 1, 3)
        sys_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        sys_wg = QFrame()
        sys_wg.setFrameShape(QFrame.Box)
        sys_wg.setLayout(sys_box)


        band_box = QGridLayout()
        self.choose_sys_freq_label = QLabel('Band：', self)
        self.choose_sys_freq_label.setAlignment(Qt.AlignCenter)
        self.choose_sys_freq_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.choose_sys_freq_label.setMaximumSize(QSize(bLabel_w, bLabel_h))

        self.G_label = QLabel('GPS', self)
        self.G_label.setAlignment(Qt.AlignCenter)
        self.G_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.G_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        self.G_lineedit = QLineEdit(self)
        self.G_lineedit.setText('1/2/5')
        self.G_lineedit.setPlaceholderText('1/2/5')
        self.G_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.C_label = QLabel('BDS', self)
        self.C_label.setAlignment(Qt.AlignCenter)
        self.C_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.C_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        self.C_lineedit = QLineEdit(self)
        self.C_lineedit.setText('2/7/6/1/5/8')
        self.C_lineedit.setPlaceholderText('2/7/6/1/5/8')
        self.C_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.R_label = QLabel('GLO', self)
        self.R_label.setAlignment(Qt.AlignCenter)
        self.R_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.R_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        self.R_lineedit = QLineEdit(self)
        self.R_lineedit.setText('1/2/3')
        self.R_lineedit.setPlaceholderText('1/2/3')
        self.R_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.E_label = QLabel('GAL', self)
        self.E_label.setAlignment(Qt.AlignCenter)
        self.E_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.E_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        self.E_lineedit = QLineEdit(self)
        self.E_lineedit.setText('1/5/7/8/6')
        self.E_lineedit.setPlaceholderText('1/5/7/8/6')
        self.E_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.J_label = QLabel('QZS', self)
        self.J_label.setAlignment(Qt.AlignCenter)
        self.J_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.J_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        # self.J_label.move(320, 270)
        self.J_lineedit = QLineEdit(self)
        self.J_lineedit.setText('1/2/5/6')
        self.J_lineedit.setPlaceholderText('1/2/5/6')
        self.J_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.I_label = QLabel('NavIC', self)
        self.I_label.setAlignment(Qt.AlignCenter)
        self.I_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.I_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        self.I_lineedit = QLineEdit(self)
        self.I_lineedit.setText('5/9')
        self.I_lineedit.setPlaceholderText('5/9')
        self.I_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.S_label = QLabel('SBS', self)
        self.S_label.setAlignment(Qt.AlignCenter)
        self.S_label.setMinimumSize(QSize(bLabel_w, bLabel_h))
        self.S_label.setMaximumSize(QSize(bLabel_w, bLabel_h))
        self.S_lineedit = QLineEdit(self)
        self.S_lineedit.setText('1/5')
        self.S_lineedit.setPlaceholderText('1/5')
        self.S_lineedit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        band_box.setSpacing(1)
        band_box.addWidget(self.choose_sys_freq_label, 0, 0, 1, 3)
        band_box.addWidget(self.G_label, 0, 3, 1, 1)
        band_box.addWidget(self.G_lineedit, 0, 4, 1, 2)
        band_box.addWidget(self.R_label, 0, 7, 1, 1)
        band_box.addWidget(self.R_lineedit, 0, 8, 1, 2)


        band_box.addWidget(self.C_label, 1, 0, 1, 1)
        band_box.addWidget(self.C_lineedit, 1, 1, 1, 2)
        band_box.addWidget(self.R_label, 1, 0, 1, 1)
        band_box.addWidget(self.R_lineedit, 1, 1, 1, 2)
        band_box.addWidget(self.E_label, 1, 3, 1, 1)
        band_box.addWidget(self.E_lineedit, 1, 4, 1, 2)
        band_box.addWidget(self.J_label, 1, 7, 1, 1)
        band_box.addWidget(self.J_lineedit, 1, 8, 1, 2)


        band_box.addWidget(self.I_label, 2, 0, 1, 1)
        band_box.addWidget(self.I_lineedit, 2, 1, 1, 2)
        band_box.addWidget(self.S_label, 2, 3, 1, 1)
        band_box.addWidget(self.S_lineedit, 2, 4, 1, 2)
        band_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        band_wg = QFrame()
        band_wg.setFrameShape(QFrame.Box)
        band_wg.setLayout(band_box)


        bnt_box = QHBoxLayout()
        spacerItem = QSpacerItem(QSpacerItem_w, QSpacerItem_h, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bnt_box.addItem(spacerItem)
        self.sure_but = QPushButton('OK', self)
        self.sure_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.sure_but.clicked.connect(self.sure_function)

        self.cancel_but = QPushButton('Cancel', self)
        self.cancel_but.setMinimumSize(QSize(zPushButton_w, zPushButton_h))
        self.cancel_but.clicked.connect(self.cancel_function)

        bnt_box.setSpacing(1)
        bnt_box.addWidget(self.sure_but)
        bnt_box.addWidget(self.cancel_but)
        bnt_wg = QWidget()
        bnt_wg.setLayout(bnt_box)

        frame_box = QGridLayout()
        frame_box.addWidget(set_wg, 0, 0)
        frame_box.addWidget(sys_wg, 1, 0)
        frame_box.addWidget(band_wg, 2, 0)
        frame_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)
        frame_wg = QFrame()
        frame_wg.setFrameShape(QFrame.Box)
        # frame_wg.setStyleSheet('border-radius: 10px; border: 1px solid rgb(100, 100, 189)')
        frame_wg.setLayout(frame_box)

        option_box = QVBoxLayout(self)
        option_box.setSpacing(0)
        option_box.addWidget(frame_wg)
        option_box.addWidget(bnt_wg)
        # spacerItem_V = QSpacerItem(1, 2, QSizePolicy.Minimum, QSizePolicy.Minimum)
        # option_box.addItem(spacerItem_V)
        option_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin, Pagemargin)

        mainFrame = QWidget()
        mainFrame.setLayout(option_box)
        self.setCentralWidget(mainFrame)


    def sure_function(self):
        height_angle = self.height_angle_lineedit.text()
        carrier_noise = self.carrier_noise_lineedit.text()
        pos_height_angle = self.pos_height_angle_lineedit.text()
        pos_carrier_noise = self.pos_carrier_noise_lineedit.text()
        iono_correction = self.iono_correction_combox.currentText()
        trop_correction = self.trop_correction_combox.currentText()
        motion_model = self.motion_mode_combox.currentText()
        continuous_epoch = self.continuous_epoch_lineedit.text()
        seted_sys = []
        for sys in ['G', 'C', 'R', 'E', 'I', 'J', 'S']:
            exec("if self.{}_checkbox.isChecked() == True: seted_sys.append(sys)".format(sys))
        G_band = self.G_lineedit.text()
        C_band = self.C_lineedit.text()
        R_band = self.R_lineedit.text()
        E_band = self.E_lineedit.text()
        J_band = self.J_lineedit.text()
        I_band = self.I_lineedit.text()
        S_band = self.S_lineedit.text()

        if height_angle != '':
            self.conf_qc['elmin'] = str(height_angle)
        if carrier_noise != '':
            self.conf_qc['cnrmin'] = str(carrier_noise)

        if pos_height_angle != '':
            self.conf_qc['pos_elcut'] = str(pos_height_angle)
        if pos_carrier_noise != '':
            self.conf_qc['pos_cnrcut'] = str(pos_carrier_noise)

        if iono_correction[0:2] == 'ON':
            self.conf_qc['ionoopt'] = str(1)
        else:
            self.conf_qc['ionoopt'] = str(0)
        if trop_correction[0:2] == 'ON':
            self.conf_qc['tropopt'] = str(1)
        else:
            self.conf_qc['tropopt'] = str(0)

        if motion_model[0] == '0':
            self.conf_qc['pos_kin'] = str(0)
        else:
            self.conf_qc['pos_kin'] = str(1)

        if continuous_epoch != '':
            self.conf_qc['int_pcs'] = str(continuous_epoch)

        if len(seted_sys) != 0:
            self.conf_gen['satsys'] = ''.join(seted_sys)

        if G_band != '':
            self.conf_gen['gps_band'] = G_band.replace('/', ' ')
        if C_band != '':
            self.conf_gen['bds_band'] = C_band.replace('/', ' ')
        if R_band != '':
            self.conf_gen['glo_band'] = R_band.replace('/', ' ')
        if E_band != '':
            self.conf_gen['gal_band'] = E_band.replace('/', ' ')
        if J_band != '':
            self.conf_gen['qzs_band'] = J_band.replace('/', ' ')
        if I_band != '':
            self.conf_gen['irn_band'] = I_band.replace('/', ' ')
        if S_band != '':
            self.conf_gen['sbs_band'] = S_band.replace('/', ' ')

        self._signal.emit(self.conf_gen, self.conf_qc)

        # close window
        self.close()

    def cancel_function(self):
        self.close()

if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    # QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    import qdarkstyle
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt5'))
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    print(dpi)
    ratio = dpi/96
    win = Data_Preprocessing_Setup(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    # font.setPointSize(14)
    font.setPixelSize(14*ratio)
    app.setFont(font)
    win.show()
    sys.exit(app.exec_())