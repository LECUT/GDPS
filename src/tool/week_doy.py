#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Weijian Hu  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    MM/DD/YY Convert to Week / Day of Week / DOY       * |
# * Input    Year, Month, Day, Hour, Minute, Second             * |
# * Output   [GPS Week, Second of Week                          * |
#             BDS Week, Day of Week,                            * |
#             Year, DOY]                                        * |
# *                                                             * |
# * Author   Weijian Hu, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from tool import TimeTran as Timet
import datetime


# /* datetime GNSS Time --------------------------------------------------------
# * convert bdatetime to GNSS Time
# * args   : '2023/08/04 11:12:02'
# * return : [GPSWeek, GPSsec, BDSWeek, GPSday, Year, Doy]
# *-----------------------------------------------------------------------------*/
def Week_Doy_Day(datetime_strftime):
    time_info = []
    year    = int(datetime_strftime[0:4])
    month   = int(str(datetime_strftime[5:7]))
    day     = int(str(datetime_strftime[8:10]))
    hour    = int(str(datetime_strftime[11:13]))
    minute  = int(str(datetime_strftime[14:16]))
    second  = int(str(datetime_strftime[17:19]))

    GPS_week, GPS_sec, GPS_day = Timet.date2GPST(year, month, day, hour, minute, second)  # GPSweek GPSsec
    Gweek_sec = GPS_day*86400 + hour*3600 + minute*60 + second

    BDS_week, BDS_sec, BDS_day = Timet.date2BDT(year, month, day, hour, minute, second)  # BDSweek BDSsec
    Cweek_sec = BDS_day*86400 + hour*3600 + minute*60 + second - 14

    doy, doysec = Timet.date2doy(year, month, day, hour, minute, second)

    time_info.append(GPS_week)
    time_info.append(GPS_day)
    time_info.append(Gweek_sec)
    time_info.append(BDS_week)
    time_info.append(BDS_day)
    time_info.append(Cweek_sec)
    time_info.append(year)
    time_info.append(doy)
    return time_info

