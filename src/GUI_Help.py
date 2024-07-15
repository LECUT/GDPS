'''
Author: huweijian 1494170841@qq.com
Date: 2024-04-25 10:02:22
LastEditors: huweijian 1494170841@qq.com
LastEditTime: 2024-05-23 14:44:57
FilePath: \src\GUI_Help.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
import resources_rc
import sys
import os

""" about gui """
curdir = os.getcwd() # program work path

class Software_About(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        # self.setWindowFlags(Qt.MSWindowsFixedSizeDialogHint)
        # self.setFixedSize(500, 300)
        self.setFixedSize(400*self.ratio, 220*self.ratio)
        # self.setFixedSize(500*dpi/100, 260*dpi/100)
        self.setWindowTitle("About")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width())/1.8), int((screen.height() - size.height())/2))
        self.setup_ui()

    def setup_ui(self):
        Pagemargin_row = 10*self.ratio
        Pagemargin_col = 30*self.ratio
        #********************************************************************

        self.title_label = QLabel('GNSS Data Pre-processing Software (GDPS)')
        self.title_label.setAlignment(Qt.AlignCenter)

        self.version_label   = QLabel('Version: 1.0')
        self.version_label.setAlignment(Qt.AlignCenter)

        self.developer_label = QLabel('Research Groups       : L-Team')
        # self.developer_label.setAlignment(Qt.AlignCenter)

        self.agenccy_label   = QLabel('Research Institutions: East China University of Technology (ECUT)')
        # self.agenccy_label.setAlignment(Qt.AlignCenter)

        self.emeil_label     = QLabel('E-mail                         : lglu66@163.com')
        # self.emeil_label.setAlignment(Qt.AlignCenter)

        self.copyright_label = QLabel('Copyright © 2023 ECUT')
        # self.copyright_label.setAlignment(Qt.AlignCenter)

        gride = QGridLayout()
        gride.setSpacing(Pagemargin_row)
        gride.addWidget(self.title_label, 0, 0, 2, 1)
        gride.addWidget(self.version_label, 1, 0, 2, 1)
        gride.addWidget(self.developer_label, 3, 0, 1, 1)
        gride.addWidget(self.agenccy_label, 4, 0, 1, 1)
        gride.addWidget(self.emeil_label, 5, 0, 1, 1)
        gride.addWidget(self.copyright_label, 6, 0, 1, 1)
        gride.setContentsMargins(Pagemargin_row, Pagemargin_col, Pagemargin_row, Pagemargin_col)

        mainFrame = QWidget()
        mainFrame.setLayout(gride)
        self.setCentralWidget(mainFrame)

    def resizeEvent(self, event: QResizeEvent): # set background
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(QPixmap(':/backgorund/aboutground.jpg').scaled(self.size(), Qt.IgnoreAspectRatio)))
        self.setPalette(palette)


if __name__ == '__main__':
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    print(dpi)
    ratio = dpi/96
    win = Software_About(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(12*ratio)
    # font.setPointSize(11)
    app.setFont(font)
    win.show()
    sys.exit(app.exec_())