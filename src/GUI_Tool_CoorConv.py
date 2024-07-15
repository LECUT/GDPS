from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys
import re
import os
import pandas as pd
import numpy as np
from tool import xyz_to_blh
from tool import blh_to_xyz
from tool import CoordTran
import resources_rc

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

# work path
curdir = os.getcwd() # program work path

#  Coordinate Transfer
class XYZconvertBLH(QWidget):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Coordinate Transformation")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setFixedSize(500*self.ratio, 400*self.ratio)
        self.input_path = ''
        self.output_path = ''
        self.setup_ui()

    def setup_ui(self):
        zlabel_w       = 100*self.ratio
        zlabel_h       = 25*self.ratio
        label_w        = 30*self.ratio
        label_h        = 25*self.ratio
        blabel_w       = 5*self.ratio
        blabel_h       = 5*self.ratio
        clabel_w       = 50*self.ratio
        clabel_h       = 25*self.ratio
        LineEdit_w     = 100*self.ratio
        LineEdit_h     = 25*self.ratio
        ComboBox_w     = 80*self.ratio
        ComboBox_h     = 25*self.ratio
        RadioButton_w  = 50*self.ratio
        RadioButton_h  = 25*self.ratio
        PushButton_w   = 80*self.ratio
        PushButton_h   = 25*self.ratio
        Spacing        = 5*self.ratio

        xybh_box = QGridLayout()


        # **********************************************
        self.X_label = QLabel('X')
        self.X_label.setAlignment(Qt.AlignCenter)
        self.X_label.setMinimumSize(QSize(label_w, label_h))
        self.X_label.setMaximumSize(QSize(label_w, label_h))

        self.X_edit = QLineEdit('-2408693.2691')
        self.X_edit.setAlignment(Qt.AlignCenter)
        self.X_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.X_unit = QLabel('m')
        self.X_unit.setMinimumSize(QSize(label_w, label_h))
        self.X_unit.setMaximumSize(QSize(label_w, label_h))

        #**********************************************
        self.Y_label = QLabel('Y:')
        self.Y_label.setAlignment(Qt.AlignCenter)
        self.Y_label.setMinimumSize(QSize(label_w, label_h))
        self.Y_label.setMaximumSize(QSize(label_w, label_h))

        self.Y_edit = QLineEdit('4698102.8463')
        self.Y_edit.setAlignment(Qt.AlignCenter)
        self.Y_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.Y_unit = QLabel('m')
        self.Y_unit.setMinimumSize(QSize(label_w, label_h))
        self.Y_unit.setMaximumSize(QSize(label_w, label_h))

        #**********************************************
        self.Z_label = QLabel('Z')
        self.Z_label.setAlignment(Qt.AlignCenter)
        self.Z_label.setMinimumSize(QSize(label_w, label_h))
        self.Z_label.setMaximumSize(QSize(label_w, label_h))

        self.Z_edit = QLineEdit('3566697.2810')
        self.Z_edit.setAlignment(Qt.AlignCenter)
        self.Z_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.Z_unit = QLabel('m')
        self.Z_unit.setMinimumSize(QSize(label_w, label_h))
        self.Z_unit.setMaximumSize(QSize(label_w, label_h))

        #**********************************************
        self.B_label = QLabel('B')
        self.B_label.setAlignment(Qt.AlignCenter)
        self.B_label.setMinimumSize(QSize(label_w, label_h))
        self.B_label.setMaximumSize(QSize(label_w, label_h))

        self.B_edit = QLineEdit()
        self.B_edit.setAlignment(Qt.AlignCenter)
        self.B_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.B_unit = QLabel('°')
        self.B_unit.setMinimumSize(QSize(label_w, label_h))
        self.B_unit.setMaximumSize(QSize(label_w, label_h))

        #**********************************************
        self.L_label = QLabel('L')
        self.L_label.setAlignment(Qt.AlignCenter)
        self.L_label.setMinimumSize(QSize(label_w, label_h))
        self.L_label.setMaximumSize(QSize(label_w, label_h))

        self.L_edit = QLineEdit()
        self.L_edit.setAlignment(Qt.AlignCenter)
        self.L_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.L_unit = QLabel('°')
        self.L_unit.setMinimumSize(QSize(label_w, label_h))
        self.L_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.H_label = QLabel('H')
        self.H_label.setAlignment(Qt.AlignCenter)
        self.H_label.setMinimumSize(QSize(label_w, label_h))
        self.H_label.setMaximumSize(QSize(label_w, label_h))

        self.H_edit = QLineEdit()
        self.H_edit.setAlignment(Qt.AlignCenter)
        self.H_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.H_unit = QLabel('m')
        self.H_unit.setMinimumSize(QSize(label_w, label_h))
        self.H_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.refX_label = QLabel('X_ref')
        self.refX_label.setAlignment(Qt.AlignCenter)
        self.refX_label.setMinimumSize(QSize(label_w, label_h))
        self.refX_label.setMaximumSize(QSize(label_w, label_h))

        self.refX_edit = QLineEdit('-2408693.1743')
        self.refX_edit.setAlignment(Qt.AlignCenter)
        self.refX_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.refX_unit = QLabel('m')
        self.refX_unit.setMinimumSize(QSize(label_w, label_h))
        self.refX_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.refY_label = QLabel('Y_ref')
        self.refY_label.setAlignment(Qt.AlignCenter)
        self.refY_label.setMinimumSize(QSize(label_w, label_h))
        self.refY_label.setMaximumSize(QSize(label_w, label_h))

        self.refY_edit = QLineEdit('4698102.7549')
        self.refY_edit.setAlignment(Qt.AlignCenter)
        self.refY_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.refY_unit = QLabel('m')
        self.refY_unit.setMinimumSize(QSize(label_w, label_h))
        self.refY_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.refZ_label = QLabel('Z_ref')
        self.refZ_label.setAlignment(Qt.AlignCenter)
        self.refZ_label.setMinimumSize(QSize(label_w, label_h))
        self.refZ_label.setMaximumSize(QSize(label_w, label_h))

        self.refZ_edit = QLineEdit('3566697.1705')
        self.refZ_edit.setAlignment(Qt.AlignCenter)
        self.refZ_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.refZ_unit = QLabel('m')
        self.refZ_unit.setMinimumSize(QSize(label_w, label_h))
        self.refZ_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.N_label = QLabel('N')
        self.N_label.setAlignment(Qt.AlignCenter)
        self.N_label.setMinimumSize(QSize(label_w, label_h))
        self.N_label.setMaximumSize(QSize(label_w, label_h))

        self.N_edit = QLineEdit()
        self.N_edit.setAlignment(Qt.AlignCenter)
        self.N_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.N_unit = QLabel('m')
        self.N_unit.setMinimumSize(QSize(label_w, label_h))
        self.N_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.E_label = QLabel('E')
        self.E_label.setAlignment(Qt.AlignCenter)
        self.E_label.setMinimumSize(QSize(label_w, label_h))
        self.E_label.setMaximumSize(QSize(label_w, label_h))

        self.E_edit = QLineEdit()
        self.E_edit.setAlignment(Qt.AlignCenter)
        self.E_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.E_unit = QLabel('m')
        self.E_unit.setMinimumSize(QSize(label_w, label_h))
        self.E_unit.setMaximumSize(QSize(label_w, label_h))

        # **********************************************
        self.U_label = QLabel('U')
        self.U_label.setAlignment(Qt.AlignCenter)
        self.U_label.setMinimumSize(QSize(label_w, label_h))
        self.U_label.setMaximumSize(QSize(label_w, label_h))

        self.U_edit = QLineEdit()
        self.U_edit.setAlignment(Qt.AlignCenter)
        self.U_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.U_unit = QLabel('m')
        self.U_unit.setMinimumSize(QSize(label_w, label_h))
        self.U_unit.setMaximumSize(QSize(label_w, label_h))


        self.choose_coordinatelabel = QLabel('Coordinate:')
        self.choose_coordinatelabel.setMinimumSize(QSize(clabel_w, clabel_h))

        self.choose_coordinate = QComboBox()
        self.choose_coordinate.setEditable(True)
        ledit = self.choose_coordinate.lineEdit()
        ledit.setAlignment(Qt.AlignCenter)

        b = ['WGS84', 'CGCS2000']
        self.choose_coordinate.addItems(b)
        self.choose_coordinate.setCurrentText('WGS84')
        self.choose_coordinate.setMinimumSize(QSize(ComboBox_w, ComboBox_h))

        self.one_hand_rbtn = QRadioButton('One-Hand')
        self.one_hand_rbtn.setMinimumSize(QSize(RadioButton_w, RadioButton_h))
        self.one_hand_rbtn.setChecked(True)

        self.clear_button = QPushButton('Clean')
        self.clear_button.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.clear_button.clicked.connect(self.clear_view)

        self.batch_file_rbtn = QRadioButton('Batch File')
        self.batch_file_rbtn.setMinimumSize(QSize(RadioButton_w, RadioButton_h))
        self.batch_file_rbtn.setChecked(False)

        self.file_format = QLabel("<a href=https://www.baidu.com>Input Format</a>")
        self.file_format.setMinimumSize(QSize(clabel_w, clabel_h))
        self.file_format.setOpenExternalLinks(False)
        self.file_format.linkActivated.connect(self.fileformat)

        self.xyzblh_input_file_button = QPushButton('Import')
        self.xyzblh_input_file_button.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.xyzblh_input_file_button.clicked.connect(self.input_file)

        self.xyzblh_output_file_button = QPushButton('Output')
        self.xyzblh_output_file_button.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.xyzblh_output_file_button.clicked.connect(self.output_file)

        self.xyzblh_output_file_name = QLineEdit()
        self.xyzblh_output_file_name.setAlignment(Qt.AlignCenter)
        self.xyzblh_output_file_button.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.xyzblh_output_file_name.setPlaceholderText("Enter Converted Filename")

        self.xyz2blh_btn = QPushButton('XYZ --> BLH')
        self.xyz2blh_btn.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.xyz2blh_btn.clicked.connect(self.XYZ_to_BLH)

        self.blh2xyz_btn = QPushButton('BLH --> XYZ')
        self.blh2xyz_btn.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.blh2xyz_btn.clicked.connect(self.BLH_to_XYZ)

        self.xyz2neu_btn = QPushButton('XYZ --> NEU')
        self.xyz2neu_btn.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.xyz2neu_btn.clicked.connect(self.XYZ_to_NEU)

        self.neu2xyz_btn = QPushButton('NEU --> XYZ')
        self.neu2xyz_btn.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.neu2xyz_btn.clicked.connect(self.NEU_to_XYZ)


        blank_label = QLabel('')
        blank_label.setMinimumSize(QSize(blabel_w, blabel_h))
        blank_label.setMaximumSize(QSize(blabel_w, blabel_h))

        xybh_box.addWidget(blank_label, 0, 0)

        xybh_box.addWidget(self.X_label, 1, 0, 1, 1)
        xybh_box.addWidget(self.X_edit, 1, 1, 1, 2)
        xybh_box.addWidget(self.X_unit, 1, 3, 1, 1)
        xybh_box.addWidget(blank_label, 1, 4, 1, 1)
        xybh_box.addWidget(self.B_label, 1, 5, 1, 1)
        xybh_box.addWidget(self.B_edit, 1, 6, 1, 2)
        xybh_box.addWidget(self.B_unit, 1, 8, 1, 1)

        xybh_box.addWidget(self.Y_label, 2, 0, 1, 1)
        xybh_box.addWidget(self.Y_edit, 2, 1, 1, 2)
        xybh_box.addWidget(self.Y_unit, 2, 3, 1, 1)
        xybh_box.addWidget(blank_label, 2, 4, 1, 1)
        xybh_box.addWidget(self.L_label, 2, 5, 1, 1)
        xybh_box.addWidget(self.L_edit, 2, 6, 1, 2)
        xybh_box.addWidget(self.L_unit, 2, 8, 1, 1)

        xybh_box.addWidget(self.Z_label, 3, 0, 1, 1)
        xybh_box.addWidget(self.Z_edit, 3, 1, 1, 2)
        xybh_box.addWidget(self.Z_unit, 3, 3, 1, 1)
        xybh_box.addWidget(blank_label, 3, 4, 1, 1)
        xybh_box.addWidget(self.H_label, 3, 5, 1, 1)
        xybh_box.addWidget(self.H_edit, 3, 6, 1, 2)
        xybh_box.addWidget(self.H_unit, 3, 8, 1, 1)
        xybh_box.addWidget(blank_label, 3, 9, 1, 1)

        xybh_box.addWidget(blank_label, 4, 0)
        xybh_box.addWidget(self.refX_label, 5, 0, 1, 1)
        xybh_box.addWidget(self.refX_edit, 5, 1, 1, 2)
        xybh_box.addWidget(self.refX_unit, 5, 3, 1, 1)
        xybh_box.addWidget(blank_label, 5, 4, 1, 1)
        xybh_box.addWidget(self.N_label, 5, 5, 1, 1)
        xybh_box.addWidget(self.N_edit, 5, 6, 1, 2)
        xybh_box.addWidget(self.N_unit, 5, 8, 1, 1)

        xybh_box.addWidget(self.refY_label, 6, 0, 1, 1)
        xybh_box.addWidget(self.refY_edit, 6, 1, 1, 2)
        xybh_box.addWidget(self.refY_unit, 6, 3, 1, 1)
        xybh_box.addWidget(blank_label, 6, 4, 1, 1)
        xybh_box.addWidget(self.E_label, 6, 5, 1, 1)
        xybh_box.addWidget(self.E_edit, 6, 6, 1, 2)
        xybh_box.addWidget(self.E_unit, 6, 8, 1, 1)

        xybh_box.addWidget(self.refZ_label, 7, 0, 1, 1)
        xybh_box.addWidget(self.refZ_edit, 7, 1, 1, 2)
        xybh_box.addWidget(self.refZ_unit, 7, 3, 1, 1)
        xybh_box.addWidget(blank_label, 7, 4, 1, 1)
        xybh_box.addWidget(self.U_label, 7, 5, 1, 1)
        xybh_box.addWidget(self.U_edit, 7, 6, 1, 2)
        xybh_box.addWidget(self.U_unit, 7, 8, 1, 1)
        xybh_box.addWidget(blank_label, 7, 9, 1, 1)


        xybh_wg = QWidget()
        xybh_wg.setLayout(xybh_box)

        set_box = QGridLayout()
        set_box.addWidget(self.choose_coordinatelabel, 0, 0, 1, 1)
        set_box.addWidget(self.choose_coordinate, 0, 1, 1, 3)

        set_box.addWidget(self.one_hand_rbtn, 1, 0, 1, 1)
        set_box.addWidget(self.clear_button, 1, 1, 1, 3)

        set_box.addWidget(self.batch_file_rbtn, 2, 0, 1, 1)
        set_box.addWidget(self.xyzblh_input_file_button, 2, 1, 1, 3)

        set_box.addWidget(self.file_format, 3, 0, 1, 1)
        set_box.addWidget(self.xyzblh_output_file_button, 3, 1, 1, 3)

        bnt_box = QVBoxLayout()
        bnt_box.setSpacing(Spacing)
        bnt_box.addWidget(self.xyzblh_output_file_name)
        bnt_box.addWidget(self.xyz2blh_btn)
        bnt_box.addWidget(self.blh2xyz_btn)
        bnt_box.addWidget(self.xyz2neu_btn)
        bnt_box.addWidget(self.neu2xyz_btn)

        bnt_wg = QWidget()
        bnt_wg.setLayout(bnt_box)

        set_box.addWidget(bnt_wg, 0, 5, 4, 4)

        set_wg = QWidget()
        set_wg.setLayout(set_box)

        main_box = QVBoxLayout()
        main_box.addWidget(xybh_wg)
        main_box.addWidget(set_wg)
        self.setLayout(main_box)


    def fileformat(self):
        file_path = './Lib/file format/coordinate_format.txt'
        self.s = View_FileFormat(file_path, self.ratio)
        self.s.show()

    def clear_view(self):
        self.X_edit.setText('')
        self.Y_edit.setText('')
        self.Z_edit.setText('')
        self.B_edit.setText('')
        self.L_edit.setText('')
        self.H_edit.setText('')
        self.refX_edit.setText('')
        self.refY_edit.setText('')
        self.refZ_edit.setText('')
        self.N_edit.setText('')
        self.E_edit.setText('')
        self.U_edit.setText('')

    # input file
    def input_file(self):
       self.input_path, _ = QFileDialog.getOpenFileName(self, 'Select File', curdir, "txt(*.txt)")
       if self.input_path == '':
           QMessageBox.information(self, 'Prompt', 'Cancel Load')
       else:
           self.xyzblh_output_file_name.setText(os.path.basename(self.input_path))
           os.chdir(os.path.dirname(self.input_path))
           QMessageBox.information(self, 'Prompt', 'Success Load')
       return self.input_path

    # output file
    def output_file(self):
       self.output_path = QFileDialog.getExistingDirectory(self, 'Select File', './')
       if self.output_path == '':
           QMessageBox.information(self, 'Prompt', 'Cancel Load')
       else:
           QMessageBox.information(self, 'Prompt', 'Select Output')
       return self.output_path

    def XYZ_to_BLH(self):
        coordinate_system = self.choose_coordinate.currentText()
        if self.one_hand_rbtn.isChecked() == True:
            if self.X_edit.text() == '' or self.Y_edit.text() == '' or self.Z_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input XYZ')
            else:
                x = float(self.X_edit.text())
                y = float(self.Y_edit.text())
                z = float(self.Z_edit.text())

                blh = CoordTran.XYZ_BLH(coordinate_system, [x, y, z])
                self.B_edit.setText('{:.9f}'.format(blh[0]))
                self.L_edit.setText('{:.9f}'.format(blh[1]))
                self.H_edit.setText('{:.9f}'.format(blh[2]))

        elif self.batch_file_rbtn.isChecked() == True:

            if self.input_path == '' or self.output_path == '' or self.xyzblh_output_file_name.text() == '':
                QMessageBox.information(self, 'Prompt', 'Check Set')
            else:
                try:
                    output = os.path.join(self.output_path, self.xyzblh_output_file_name.text())
                    data = pd.read_csv(self.input_path, sep='\s+')
                    data = np.array([data['X(m)'], data['Y(m)'], data['Z(m)']]).T

                    fmt_head = '{:^13s} {:^12s} {:^12} {:^12s} {:^13s} {:^12s}\n'
                    fmt_data = '{:^13.4f} {:^12.4f} {:^12.4f} {:^12.9f} {:^13.9f} {:^12.9f}\n'

                    fid = open(output, 'w+', encoding='utf-8')
                    fid.write(fmt_head.format("X(m)", "Y(m)", "Z(m)", "B(°)", "L(°)", "H(m)"))

                    for i in range(data.shape[0]):
                        xyz = data[i, :]
                        blh = CoordTran.XYZ_BLH(coordinate_system, xyz)
                        fid.write(fmt_data.format(xyz[0], xyz[1], xyz[2], blh[0], blh[1], blh[2]))

                    fid.write('\n')
                    fid.close()

                    QMessageBox.information(self, 'Prompt', 'Successful conversion')
                except Exception as e:
                    QMessageBox.information(self, 'Prompt', 'Format Error')

    def BLH_to_XYZ(self):
        coordinate_system = self.choose_coordinate.currentText()
        if self.one_hand_rbtn.isChecked() == True:
            if self.B_edit.text() == '' or self.L_edit.text() == '' or self.H_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input BLH')
            else:
                B = float(self.B_edit.text())
                L = float(self.L_edit.text())
                H = float(self.H_edit.text())

                xyz = CoordTran.BLH_XYZ(coordinate_system, [B, L, H])
                self.X_edit.setText('{:.4f}'.format(xyz[0]))
                self.Y_edit.setText('{:.4f}'.format(xyz[1]))
                self.Z_edit.setText('{:.4f}'.format(xyz[2]))

        elif self.batch_file_rbtn.isChecked() == True:
            if self.input_path == '' or self.output_path == '' or self.xyzblh_output_file_name.text() == '':
                QMessageBox.information(self, 'Prompt', 'Check Set')
            else:
                try:
                    output = os.path.join(self.output_path, self.xyzblh_output_file_name.text())
                    data = pd.read_csv(self.input_path, sep='\s+')
                    data = np.array([data['B(°)'], data['L(°)'], data['H(m)']]).T

                    fmt_head = '{:^12s} {:^13s} {:^12s} {:^13s} {:^12s} {:^12}\n'
                    fmt_data = '{:^12.9f} {:^13.9f} {:^12.9f} {:^13.4f} {:^12.4f} {:^12.4f}\n'

                    fid = open(output, 'w+', encoding='utf-8')
                    fid.write(fmt_head.format("B(°)", "L(°)", "H(m)", "X(m)", "Y(m)", "Z(m)"))

                    for i in range(data.shape[0]):
                        blh = data[i, :]
                        xyz = CoordTran.BLH_XYZ(coordinate_system, blh)
                        fid.write(fmt_data.format(blh[0], blh[1], blh[2], xyz[0], xyz[1], xyz[2]))

                    fid.write('\n')
                    fid.close()
                    QMessageBox.information(self, 'Prompt', 'Successful conversion')
                except Exception as e:
                    QMessageBox.information(self, 'Prompt', 'Format Error')


    def XYZ_to_NEU(self):
        coordinate_system = self.choose_coordinate.currentText()
        if self.one_hand_rbtn.isChecked() == True:
            if self.X_edit.text() == '' or self.Y_edit.text() == '' or self.Z_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input XYZ')
            elif self.refX_edit.text() == '' or self.refY_edit.text() == '' or self.refZ_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input XYZ_ref')
            else:
                x = float(self.X_edit.text())
                y = float(self.Y_edit.text())
                z = float(self.Z_edit.text())

                x_ref = float(self.refX_edit.text())
                y_ref = float(self.refY_edit.text())
                z_ref = float(self.refZ_edit.text())

                neu = CoordTran.XYZ_NEU(coordinate_system, [x_ref, y_ref, z_ref], [x, y, z])
                self.N_edit.setText('{:.4f}'.format(neu[0]))
                self.E_edit.setText('{:.4f}'.format(neu[1]))
                self.U_edit.setText('{:.4f}'.format(neu[2]))

        elif self.batch_file_rbtn.isChecked() == True:
            if self.refX_edit.text() == '' or self.refY_edit.text() == '' or self.refZ_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input XYZ_ref')
            else:
                try:
                    output = os.path.join(self.output_path, self.xyzblh_output_file_name.text())
                    x_ref = float(self.refX_edit.text())
                    y_ref = float(self.refY_edit.text())
                    z_ref = float(self.refZ_edit.text())
                    xyz_ref = np.array([x_ref, y_ref, z_ref])

                    data = pd.read_csv(self.input_path, sep='\s+')
                    data = np.array([data['X(m)'], data['Y(m)'], data['Z(m)']]).T

                    fmt_head = '{:^13s} {:^12s} {:^12} {:^10s} {:^10s} {:^10s}\n'
                    fmt_data = '{:^13.4f} {:^12.4f} {:^12.4f} {:^10.6f} {:^10.6f} {:^10.6f}\n'

                    fid = open(output, 'w+', encoding='utf-8')
                    fid.write(fmt_head.format("X(m)", "Y(m)", "Z(m)", "N(m)", "E(m)", "U(m)"))

                    for i in range(data.shape[0]):
                        xyz = data[i, :]
                        neu = CoordTran.XYZ_NEU(coordinate_system, xyz_ref, xyz)
                        fid.write(fmt_data.format(xyz[0], xyz[1], xyz[2], neu[0], neu[1], neu[2]))

                    fid.write('\n')
                    fid.close()
                    QMessageBox.information(self, 'Prompt', 'Successful conversion')
                except Exception as e:
                    QMessageBox.information(self, 'Prompt', 'Format Error')


    def NEU_to_XYZ(self):
        coordinate_system = self.choose_coordinate.currentText()
        if self.one_hand_rbtn.isChecked() == True:
            if self.refX_edit.text() == '' or self.refY_edit.text() == '' or self.refZ_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input XYZ_ref')
            else:
                N = float(self.N_edit.text())
                E = float(self.E_edit.text())
                U = float(self.U_edit.text())

                x_ref = float(self.refX_edit.text())
                y_ref = float(self.refY_edit.text())
                z_ref = float(self.refZ_edit.text())

                xyz = CoordTran.NEU_XYZ(coordinate_system, [x_ref, y_ref, z_ref], [N, E, U])
                self.X_edit.setText('{:.4f}'.format(xyz[0]))
                self.Y_edit.setText('{:.4f}'.format(xyz[1]))
                self.Z_edit.setText('{:.4f}'.format(xyz[2]))

        elif self.batch_file_rbtn.isChecked() == True:
            if self.refX_edit.text() == '' or self.refY_edit.text() == '' or self.refZ_edit.text() == '':
                QMessageBox.information(self, 'Prompt', 'Please Input XYZ_ref')
            else:
                try:
                    output = os.path.join(self.output_path, self.xyzblh_output_file_name.text())
                    data = pd.read_csv(self.input_path, sep='\s+')
                    data = np.array([data['N(°)'], data['E(°)'], data['U(m)']]).T

                    fmt_head = '{:^10s} {:^10s} {:^10s} {:^13s} {:^12s} {:^12}\n'
                    fmt_data = '{:^10.6f} {:^10.6f} {:^10.6f} {:^13.4f} {:^12.4f} {:^12.4f}\n'

                    fid = open(output, 'w+', encoding='utf-8')
                    fid.write(fmt_head.format("N(m)", "E(m)", "U(m)", "X(m)", "Y(m)", "Z(m)"))

                    for i in range(data.shape[0]):
                        neu = data[i, :]
                        xyz = CoordTran.NEU_XYZ(coordinate_system, neu)
                        fid.write(fmt_data.format(neu[0], neu[1], neu[2], xyz[0], xyz[1], xyz[2]))

                    fid.write('\n')
                    fid.close()
                    QMessageBox.information(self, 'Prompt', 'Successful conversion')
                except Exception as e:
                    QMessageBox.information(self, 'Prompt', 'Format Error')


#  view file data
class View_FileFormat(QWidget):
    def __init__(self, converted_file, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("File Format")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.resize(500*ratio, 400*ratio)
        self.setup_ui(converted_file)

    def setup_ui(self, converted_file):
        layout = QVBoxLayout()
        self.textEdit = QTextEdit()
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textEdit.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.textEdit)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        with open(converted_file, 'r', encoding='utf-8') as f:
            msg = f.read()
            self.textEdit.setPlainText(msg)
        f.close()

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
    win = XYZconvertBLH(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(12*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())