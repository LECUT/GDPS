from PyQt5.Qt import *
from PyQt5.QtWidgets import QApplication
import sys
from tool import julian_day
from tool import week_doy
import resources_rc

# Set up logging object
from loger import get_module_logger
import logging
logger = get_module_logger(__name__)

class Time_convertion(QWidget):
    def __init__(self, ratio):
        super().__init__()
        self.ratio = ratio
        self.setWindowTitle("Time Transformation")
        self.setWindowIcon(QIcon(':/icon/logo.ico'))
        # self.resize(350, 150)
        self.setFixedSize(500*self.ratio, 300*self.ratio)
        self.setup_ui()

    def setup_ui(self):

        label_w         = 90*self.ratio
        label_h         = 25*self.ratio
        blabel_w        = 40*self.ratio
        blabel_h        = 10*self.ratio
        LineEdit_w      = 70*self.ratio
        LineEdit_h      = 25*self.ratio
        QDateTimeEdit_w = 140*self.ratio
        QDateTimeEdit_h = 25*self.ratio
        PushButton_w    = 70*self.ratio
        PushButton_h    = 25*self.ratio
        Pagemargin      = 10*self.ratio
        Pagemargin_row  = 30*self.ratio

        convert_box = QGridLayout()
        self.ymd_label = QLabel('YY-MM-DD')
        self.ymd_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.ymd_label.setMinimumSize(QSize(label_w, label_h))
        self.ymd_label.setMaximumSize(QSize(label_w, label_h))

        self.convert_btn = QPushButton('Convert')
        self.convert_btn.setMinimumSize(QSize(PushButton_w, PushButton_h))
        self.convert_btn.clicked.connect(self.Time_0)
        self.convert_btn.clicked.connect(self.Time_1)

        self.JD_label = QLabel('JD:')
        self.JD_label.setAlignment(Qt.AlignCenter)
        self.JD_label.setMinimumSize(QSize(label_w, label_h))
        self.JD_label.setMaximumSize(QSize(label_w, label_h))

        self.JD_edit = QLineEdit()
        self.JD_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.JD_edit.setMinimumSize(QSize(label_w, label_h))

        self.MJD_label = QLabel('MJD:')
        self.MJD_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.MJD_label.setMinimumSize(QSize(label_w, label_h))
        self.MJD_label.setMaximumSize(QSize(label_w, label_h))

        self.MJD_edit = QLineEdit()
        self.MJD_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.MJD_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.year_label = QLabel('Year:')
        self.year_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.year_label.setMinimumSize(QSize(label_w, label_h))
        self.year_label.setMaximumSize(QSize(label_w, label_h))

        self.year_edit = QLineEdit()
        self.year_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.year_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.doy_label = QLabel('DOY:')
        self.doy_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.doy_label.setMinimumSize(QSize(label_w, label_h))
        self.doy_label.setMaximumSize(QSize(label_w, label_h))

        self.doy_edit = QLineEdit()
        self.doy_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.doy_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.GPSweek_label = QLabel('GPSweek:')
        self.GPSweek_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.GPSweek_label.setMinimumSize(QSize(label_w, label_h))
        self.GPSweek_label.setMaximumSize(QSize(label_w, label_h))

        self.GPSweek_edit = QLineEdit()
        self.GPSweek_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.GPSweek_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))


        self.GPSday_label = QLabel('GPSday:')
        self.GPSday_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.GPSday_label.setMinimumSize(QSize(label_w, label_h))
        self.GPSday_label.setMaximumSize(QSize(label_w, label_h))

        self.GPSday_edit = QLineEdit()
        self.GPSday_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.GPSday_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.GPSsec_label = QLabel('GPSsec:')
        self.GPSsec_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.GPSsec_label.setMinimumSize(QSize(label_w, label_h))
        self.GPSsec_label.setMaximumSize(QSize(label_w, label_h))

        self.GPSsec_edit = QLineEdit()
        self.GPSsec_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.GPSsec_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))


        self.BDSweek_label = QLabel('BDSweek:')
        self.BDSweek_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.BDSweek_label.setMinimumSize(QSize(label_w, label_h))
        self.BDSweek_label.setMaximumSize(QSize(label_w, label_h))

        self.BDSweek_edit = QLineEdit()
        self.BDSweek_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.BDSweek_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))


        self.BDSday_label = QLabel('BDSday:')
        self.BDSday_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.BDSday_label.setMinimumSize(QSize(label_w, label_h))
        self.BDSday_label.setMaximumSize(QSize(label_w, label_h))

        self.BDSday_edit = QLineEdit()
        self.BDSday_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.BDSday_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))

        self.BDSsec_label = QLabel('BDSsec:')
        self.BDSsec_label.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.BDSsec_label.setMinimumSize(QSize(label_w, label_h))
        self.BDSsec_label.setMaximumSize(QSize(label_w, label_h))

        self.BDSsec_edit = QLineEdit()
        self.BDSsec_edit.setAlignment(Qt.AlignVCenter | Qt.AlignCenter)
        self.BDSsec_edit.setMinimumSize(QSize(LineEdit_w, LineEdit_h))


        self.dateEdit = QDateTimeEdit(QDateTime.currentDateTime())
        self.dateEdit.setAlignment(Qt.AlignVCenter|Qt.AlignCenter)
        self.dateEdit.setMinimumSize(QSize(QDateTimeEdit_w, QDateTimeEdit_h))
        self.dateEdit.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        self.dateEdit.setMinimumDate(QDate.currentDate().addDays(-365*12))
        self.dateEdit.setMaximumDate(QDate.currentDate().addDays(365*12))
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.dateTimeChanged.connect(self.onDateTimeChanged)

        blank_label = QLabel('')
        blank_label.setMaximumSize(QSize(blabel_w, blabel_h))
        convert_box.addWidget(blank_label, 0, 0)
        convert_box.addWidget(self.ymd_label, 1, 0, 1, 1)
        convert_box.addWidget(self.dateEdit, 1, 1, 1, 2)
        convert_box.addWidget(self.convert_btn, 1, 3, 1, 1)
        convert_box.addWidget(blank_label, 2, 0)
        convert_box.addWidget(self.JD_label, 3, 0, 1, 1)
        convert_box.addWidget(self.JD_edit, 3, 1, 1, 1)
        convert_box.addWidget(self.MJD_label, 3, 2, 1, 1)
        convert_box.addWidget(self.MJD_edit, 3, 3, 1, 1)
        convert_box.addWidget(self.year_label, 4, 0, 1, 1)
        convert_box.addWidget(self.year_edit, 4, 1, 1, 1)
        convert_box.addWidget(self.doy_label, 4, 2, 1, 1)
        convert_box.addWidget(self.doy_edit, 4, 3, 1, 1)
        convert_box.addWidget(blank_label, 5, 0)

        convert_box.addWidget(self.GPSweek_label, 6, 0, 1, 1)
        convert_box.addWidget(self.GPSweek_edit, 6, 1, 1, 1)
        convert_box.addWidget(self.BDSweek_label, 6, 2, 1, 1)
        convert_box.addWidget(self.BDSweek_edit, 6, 3, 1, 1)
        convert_box.addWidget(self.GPSday_label, 7, 0, 1, 1)
        convert_box.addWidget(self.GPSday_edit, 7, 1, 1, 1)
        convert_box.addWidget(self.BDSday_label, 7, 2, 1, 1)
        convert_box.addWidget(self.BDSday_edit, 7, 3, 1, 1)
        convert_box.addWidget(self.GPSsec_label, 8, 0, 1, 1)
        convert_box.addWidget(self.GPSsec_edit, 8, 1, 1, 1)
        convert_box.addWidget(self.BDSsec_label, 8, 2, 1, 1)
        convert_box.addWidget(self.BDSsec_edit, 8, 3, 1, 1)
        convert_box.addWidget(blank_label, 9, 0)
        convert_box.setContentsMargins(Pagemargin, Pagemargin, Pagemargin_row, Pagemargin)

        self.setLayout(convert_box)

    def onDateTimeChanged(self, dateTime):
        time_format = dateTime.toString(Qt.ISODate)
        global data_time
        data_time = time_format.replace("T", "_")

    def Time_0(self):
        global time_yearmothday
        time_yearmothday = self.dateEdit.text()
        time_yearmothday = time_yearmothday.replace("-", "/")
        JD, MJD = julian_day.JulianDay_MJD(time_yearmothday)
        julday = int(JD)
        julday = format(julday, '.2f')
        MJD = format(MJD, '.2f')
        self.JD_edit.setText(str(julday))
        self.MJD_edit.setText(str(MJD))

    def Time_1(self):
        global time_yearmothday
        week_doy_day = week_doy.Week_Doy_Day(time_yearmothday)
        self.GPSweek_edit.setText(str(week_doy_day[0]))
        self.GPSday_edit.setText(str(week_doy_day[1]))
        self.GPSsec_edit.setText(str(week_doy_day[2]))
        self.BDSweek_edit.setText(str(week_doy_day[3]))
        self.BDSday_edit.setText(str(week_doy_day[4]))
        self.BDSsec_edit.setText(str(week_doy_day[5]))
        self.year_edit.setText(str(week_doy_day[6]))
        self.doy_edit.setText(str(week_doy_day[7]))

def on_exit():
    logger.info('Program ended.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger.info("Starting the program.")
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch()
    ratio = dpi/96
    win = Time_convertion(ratio)
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPixelSize(12*ratio)
    app.setFont(font)
    win.show()
    app.aboutToQuit.connect(on_exit)
    sys.exit(app.exec_())