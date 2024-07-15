#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Weijian Hu  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Converted from MM/DD/YY to Julian day              * |
# * Input    Year, Month, Day, Hour, Minute, Second             * |
# * Output   Julian Day                                         * |
# *                                                             * |
# * Author   Weijian Hu, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import math
from tool import TimeTran as TimeT


def JulianDay_MJD(datetime_strftime):
    year = int(datetime_strftime[0:4])
    month = int(str(datetime_strftime[5:7]))
    day = int(str(datetime_strftime[8:10]))
    hour = int(str(datetime_strftime[11:13]))
    minute = int(str(datetime_strftime[14:16]))
    second = int(str(datetime_strftime[17:19]))

    JD = TimeT.GL2JD(year, month, day, hour, minute, second)
    MJD = TimeT.JD2MJD(JD)
    return JD, MJD

