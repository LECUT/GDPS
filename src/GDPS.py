from GUI_Conversion_Obs import *
from GUI_Conversion_Nav import *
from GUI_Conversion_Met import *
from GUI_Edit_CutData import *
from GUI_Edit_ExtraData import *
from GUI_Edit_CombData_ import *
from GUI_Tool_CoorConv import *
from GUI_Tool_TimeConv import *
from GUI_Help import *
import global_var
from tool import PPP
# import resources_rcinstall
from PyQt5 import QtGui
from OpenGL import GL
from PyQt5 import QtGui
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
from multiprocessing import Pool, freeze_support

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

# GDPS
curdir = os.getcwd() # program work path

class GDPS(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        global_var._init()
        self.ratio = ratio
        self.setWindowTitle('GDPS')
        self.move(50, 20)
        # self.resize(500, 250)
        self.setMinimumSize(QSize(620*self.ratio, 420*self.ratio))
        # self.setFixedSize(620*self.ratio, 400*self.ratio)
        self.setWindowIcon(QtGui.QIcon(':/icon/logo.ico'))
        self.setIconSize(QSize(36, 36))
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width())/2, (screen.height() - size.height())/2)
        Code_Envir = os.getcwd()
        global_var.set_value('code_environment', Code_Envir)
        self.setup_ui()

    def setup_ui(self):
        bg_box = QHBoxLayout()
        self.background_label = QLabel('')
        self.background_label.setMinimumSize(QSize(100*self.ratio, 100*self.ratio))
        self.background_label.setScaledContents(True)
        bg_box.addWidget(self.background_label)
        self.background_label.setPixmap(QPixmap(":/backgorund/background.png").scaled(self.background_label.width(), self.background_label.height()))
        self.background_label.setPixmap(QPixmap(":/backgorund/background.png"))
        bg_box.setContentsMargins(0, 0, 0, 0)
        bg_wg = QWidget()
        bg_wg.setMinimumSize(QSize(0, 0))
        bg_wg.setLayout(bg_box)

        self.status = self.statusBar()
        self.status.setStyleSheet("background-color:rgb(255, 255, 255)")

        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.status_bar_show_msg)
        timer.start()

        #-----------------------------------------------------------------------------------------
        self.menubar = self.menuBar()

        #  Version conversion
        self.convert = self.menubar.addMenu("Translate")
        self.convert.setContentsMargins(0, 0, 0, 0)
        version_obs  = self.convert.addAction(QIcon(':/icon/convert.ico'), "Observed Data")
        version_obs.triggered.connect(self.convert_1)
        version_nav  = self.convert.addAction(QIcon(':/icon/convert.ico'), "Ephemeris Data")
        version_nav.triggered.connect(self.convert_2)
        version_met  = self.convert.addAction(QIcon(':/icon/convert.ico'), "Meteorological Data")
        version_met.triggered.connect(self.convert_3)

        #  data edit
        self.edit = self.menubar.addMenu("Edit")
        edit_seg  = self.edit.addAction(QIcon(':/icon/cut.ico'), "Segmentaion")
        edit_seg.triggered.connect(self.edit_1)
        edit_ext  = self.edit.addAction(QIcon(':/icon/extract.ico'), "Extract")
        edit_ext.triggered.connect(self.edit_2)
        edit_com  = self.edit.addAction(QIcon(':/icon/merge.ico'), "Splicing")
        edit_com.triggered.connect(self.edit_3)

        # data estimate
        self.estimate = self.menubar.addAction("Quality-Check")
        self.estimate.triggered.connect(self.estimate_0)

        #   tool
        self.tool  = self.menubar.addMenu("Tools")
        online_ppp = self.tool.addMenu(QIcon(':/icon/web.ico'),"Online PPP")
        ppp_Net = online_ppp.addAction("Net_Diff (China)")
        ppp_Net.triggered.connect(self.tool_101)
        # ppp_APPS   = online_ppp.addAction("APPS (USA)")
        # ppp_APPS.triggered.connect(self.tool_104)
        ppp_OPUS = online_ppp.addAction("OPUS (USA)")
        ppp_OPUS.triggered.connect(self.tool_108)
        ppp_RTX = online_ppp.addAction("RTX-PP (USA)")
        ppp_RTX.triggered.connect(self.tool_103)
        ppp_AUSPOS = online_ppp.addAction("AUSPOS (Australia)")
        ppp_AUSPOS.triggered.connect(self.tool_107)
        ppp_CSRS   = online_ppp.addAction("CSRS-PPP (Canda)")
        ppp_CSRS.triggered.connect(self.tool_102)
        ppp_GAPS   = online_ppp.addAction("GAPS (Canda)")
        ppp_GAPS.triggered.connect(self.tool_106)
        ppp_magic  = online_ppp.addAction("magicGNSS (Spain)")
        ppp_magic.triggered.connect(self.tool_105)

        Coordinate = self.tool.addAction(QIcon(':/icon/coordinate.ico'), "Coordinate Transformation")
        Coordinate.triggered.connect(self.tool_2)
        Time = self.tool.addAction(QIcon(':/icon/time.ico'), "Time Transformation")
        Time.triggered.connect(self.tool_3)

        # help
        self.help = self.menubar.addMenu("Help")
        explain = self.help.addAction(QIcon(':/icon/document.ico'), "Document")
        explain.triggered.connect(self.help_1)
        about = self.help.addAction(QIcon(':/icon/about.ico'), "About")
        about.triggered.connect(self.help_2)

        # ***************************************************
        self.stacked_layout = QStackedWidget()

        self.stacked_layout.addWidget(bg_wg)
        self.stacked_layout.addWidget(Obs_RINEX_Conversion(self.ratio))
        self.stacked_layout.addWidget(Nav_RINEX_Conversion(self.ratio))
        self.stacked_layout.addWidget(Met_RINEX_Conversion(self.ratio))
        self.stacked_layout.addWidget(Data_Cut(self.ratio))
        self.stacked_layout.addWidget(Data_Extract(self.ratio))
        self.stacked_layout.addWidget(Data_Combine(self.ratio))
        from GUI_Quality_Check import Data_Preprocessing
        self.stacked_layout.addWidget(Data_Preprocessing(self.ratio, curdir))

        self.stacked_layout.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.stacked_layout.adjustSize()
        self.adjustSize()
        self.stacked_layout.setCurrentIndex(0)

        self.setCentralWidget(self.stacked_layout)


    def status_bar_show_msg(self):
        self.status.showMessage("East China University of Technology", 0)

    def updateSizes(self):
        QApplication.processEvents()
        self.adjustSize()

    def convert_1(self):
        self.stacked_layout.setCurrentIndex(1)
        logger.error('Obs conversion.')

    def convert_2(self):
        self.stacked_layout.setCurrentIndex(2)
        logger.error('Nav conversion.')

    def convert_3(self):
        self.stacked_layout.setCurrentIndex(3)
        logger.error('Met conversion.')

    def edit_1(self):
        self.stacked_layout.setCurrentIndex(4)
        logger.error('Data segmentaion.')

    def edit_2(self):
        self.stacked_layout.setCurrentIndex(5)
        logger.error('Data extract.')

    def edit_3(self):
        self.stacked_layout.setCurrentIndex(6)
        logger.error('Data splicing.')

    def estimate_0(self):
        self.stacked_layout.setCurrentIndex(7)
        logger.error('Quality checking.')

    def tool_101(self):
        self.s = PPP.Net_Diff_PPP(self.ratio)
        self.s.show()
        logger.error('Net_Diff online.')

    def tool_102(self):
        self.s = PPP.CSRS_PPP(self.ratio)
        self.s.show()
        logger.error('CSRS_PPP online.')

    def tool_103(self):
        self.s = PPP.RTX_PPP(self.ratio)
        self.s.show()
        logger.error('RTX_PPP online.')

    def tool_104(self):
        self.s = PPP.APPS_PPP(self.ratio)
        self.s.show()
        logger.error('APPS_PPP online.')

    def tool_105(self):
        self.s = PPP.magicGNSS_PPP(self.ratio)
        self.s.show()
        logger.error('magicGNSS_PPP online.')

    def tool_106(self):
        self.s = PPP.GAPS_PPP(self.ratio)
        self.s.show()
        logger.error('GAPS_PPP online.')

    def tool_107(self):
        self.s = PPP.AUSPOS_PPP(self.ratio)
        self.s.show()
        logger.error('AUSPOS_PPP online.')

    def tool_108(self):
        self.s = PPP.OPUS_PPP(self.ratio)
        self.s.show()
        logger.error('OPUS_PPP online.')

    def tool_2(self):
        self.s = XYZconvertBLH(self.ratio)
        self.s.show()
        logger.error('Coordinate transformation.')

    def tool_3(self):
        self.s = Time_convertion(self.ratio)
        self.s.show()
        logger.error('Time transformation.')

    def help_1(self):
        self.s = Helps(self.ratio)
        self.s.show()
        logger.error('Software help.')

    def help_2(self):
        self.s = Software_About(self.ratio)
        self.s.show()
        logger.error('Software about.')

# help
class Helps(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.setWindowTitle('Help')
        self.browser = QWebEngineView()
        global curdir
        url = os.path.join(curdir, 'tutorial/User_Manual.html')
        self.browser.setUrl(QUrl.fromLocalFile(url))
        self.setCentralWidget(self.browser)


def on_exit():
    logger.info('Program ended.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting the program.")
    import sys
    freeze_support()
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    ratio = dpi/96
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(12*ratio)
    app.setFont(font)
    win = GDPS(ratio)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())
