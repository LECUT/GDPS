#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Online PPP services                                * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from PyQt5.QtWebEngineWidgets import *
from PyQt5.Qt import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QObject, pyqtSlot, QUrl, QVariant
import resources_rc


# Net_Diff PPP
class Net_Diff_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('Net_Diff')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('http://202.127.29.4/shao_gnss_ac/'))
        self.setCentralWidget(self.browser)


#  CSRS-PPP PPP
class CSRS_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('CSRS-PPP')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://webapp.geod.nrcan.gc.ca/geod/tools-outils/ppp.php?locale=en/'))
        self.setCentralWidget(self.browser)


#  RTX-PP PPP
class RTX_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('RTX-PP')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://www.trimblertx.com/UploadForm.aspx/'))
        self.setCentralWidget(self.browser)


#  JPL APPS PPP
class APPS_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('APPS')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://pppx.gdgps.net/'))
        self.setCentralWidget(self.browser)


#  GMV magicGNSS PPP
class magicGNSS_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('magicGNSS')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://magicgnss.gmv.com/'))
        self.setCentralWidget(self.browser)


#  GAPS PPP
class GAPS_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('GAPS')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('http://gaps.gge.unb.ca/'))
        self.setCentralWidget(self.browser)


#  AUSPOS PPP
class AUSPOS_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('AUSPOS')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://www.ga.gov.au/scientific-topics/positioning-navigation/geodesy/auspos'))
        self.setCentralWidget(self.browser)


#  OPUS PPP
class OPUS_PPP(QMainWindow):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle('OPUS')
        self.resize(500*self.ratio, 400*self.ratio)
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        self.browser = QWebEngineView()
        self.browser.load(QUrl('https://www.ngs.noaa.gov/OPUS/'))
        self.setCentralWidget(self.browser)