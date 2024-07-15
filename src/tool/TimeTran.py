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

import datetime

"""GL to JD"""
def GL2JD(year, month, day, hour, minute, second):
    if month <= 2:
       year = year - 1
       month = month + 12
    JD = int(365.25*year) + int(30.6001 * (month + 1)) + day + 1720981.5 + hour/24.0 + minute/1440.0 + second/86400.0
    return JD

def JD2GL(JD):
    a = int(JD + 0.5)
    b = a + 1537
    c = int((b - 122.1) / 365.25)
    d = int(365.25 * c)
    e = int((b - d) / 30.6)
    day = b - d - int(30.6001 * e)
    month = e - 1 - 12 * int(e / 14)
    year = c - 4715 - int((7 + month) / 10)
    hour = int(24 * (JD + 0.5 - int(JD + 0.5)))
    minute = int(60 * (24 * (JD + 0.5 - int(JD + 0.5)) - hour))
    second = int(60 * (60 * (24 * (JD + 0.5 - int(JD + 0.5)) - hour) -minute))+1
    return year, month, day, hour, minute, second

"""JD to MJD"""
def JD2MJD(JD):
    MJD = JD - 2400000.5
    return MJD

def MJD2JD(MJD):
    JD = MJD + 2400000.5
    return JD

"""JD to GPSt"""
def JD2GPST(JD):
    julday = int(JD)
    juldaySec = (JD - julday) * 60.0 * 60.0 * 24
    gps_week = int((JD - 2444244.5) / 7)
    day_of_week = int((JD - 2444244.5)%7)
    second_of_week = round(((julday - 2444244) % 7 + (juldaySec / (60.0 * 60.0 * 24) - 0.5)) * 86400)
    # print(gps_week, second_of_week)
    return gps_week, second_of_week, day_of_week

def GPST2JD(week, sec):
    JD = week * 7 + sec / 86400 + 2444244.5
    return JD

"""GPST to UTC"""
def GPST2UTC(week, sec):
    JD = GPST2JD(week, sec)
    Year, Month, Day, Hour, Minute, Second = JD2GL(JD)
    leapseconds = getGPSLeaps(Year, Month)
    time = datetime.datetime(Year, Month, Day, Hour, Minute, Second)
    time = time + datetime.timedelta(seconds=-leapseconds)
    return time.year, time.month, time.day, time.hour, time.minute, time.second

def UTC2GPST(year, month, day, hour, minute, second):
    leapseconds = getGPSLeaps(year, month)
    time = datetime.datetime(year, month, day, hour, minute, second)
    time = time + datetime.timedelta(seconds=leapseconds)
    if time.month <= 2:
        JD = int(365.25*(time.year - 1)) + int(30.6001*(time.month + 1 + 12)) + time.day + 1720981.5 + time.hour/24.0 + \
             time.minute/1440.0 + time.second/86400.0
    else:
        JD = int(365.25*time.year) + int(30.6001*(time.month + 1)) + time.day + 1720981.5 + time.hour/24.0 + \
             time.minute/1440.0 + time.second/86400.0
    gps_week, second_of_week, day_of_week = JD2GPST(JD)
    return gps_week, second_of_week, day_of_week

def GPST2date(week, sec):
    JD = GPST2JD(week, sec)
    year, month, day, hour, minute, second = JD2GL(JD)
    time = datetime.datetime(year, month, day, hour, minute, second)
    return time.year, time.month, time.day, time.hour, time.minute, time.second

def date2GPST(year, month, day, hour, minute, second):
    time = datetime.datetime(year, month, day, hour, minute, second)
    if time.month <= 2:
        JD = int(365.25 * (time.year-1)) + int(30.6001 * (time.month + 1 + 12)) + time.day + 1720981.5 + time.hour / 24.0 + \
        time.minute / 1440.0 + time.second / 86400.0
    else:
        JD = int(365.25*time.year) + int(30.6001*(time.month + 1)) + time.day + 1720981.5 + time.hour/24.0 + \
             time.minute/1440.0 + time.second/86400.0
    gps_week, second_of_week, day_of_week = JD2GPST(JD)
    return gps_week, second_of_week, day_of_week

def getGPSLeaps(year, month):
    if year <= 1981 & month <= 7:
        return 0
    elif year <= 1982 & month <= 7:
        return 1
    elif year <= 1983 & month <= 7:
        return 2
    elif year <= 1985 & month <= 7:
        return 3
    elif year <= 1988 & month <= 1:
        return 4
    elif year <= 1990 & month <= 1:
        return 5
    elif year <= 1991 & month <= 1:
        return 6
    elif year <= 1992 & month <= 7:
        return 7
    elif year <= 1993 & month <= 7:
        return 8
    elif year <= 1994 & month <= 7:
        return 9
    elif year <= 1996 & month <= 1:
        return 10
    elif year <= 1997 & month <= 7:
        return 11
    elif year <= 1999 & month <= 1:
        return 12
    elif year <= 2006 & month <= 1:
        return 13
    elif year <= 2009 & month <= 1:
        return 14
    elif year <= 2012 & month <= 7:
        return 15
    elif year <= 2015 & month <= 7:
        return 16
    elif year <= 2017 & month <= 1:
        return 17
    else:
        return 18

"""BDT to JD"""
def BDT2JD(week, sec):
    JD = week * 7 + sec / 86400 + 2453736.5
    return JD

def JD2BDT(JD):
    julday = int(JD)
    juldaySec = (JD - julday) * 60.0 * 60.0 * 24
    bd_week = int((JD - 2453736.5)/7)
    day_of_week = int((JD - 2453736.5)%7)
    second_of_week = round(((julday - 2453736) % 7 + (juldaySec/(60.0 * 60.0 * 24) - 0.5)) * 86400)
    # print(bd_week, second_of_week)
    return bd_week, second_of_week, day_of_week

"""BDT to UTC"""
def BDT2UTC(week, sec):
    JD = BDT2JD(week, sec)
    year, month, day, hour, minute, second = JD2GL(JD)
    leaps = getBDLeaps(year, month)
    time = datetime.datetime(year, month, day, hour, minute, second)
    time = time + datetime.timedelta(seconds=-leaps)
    return time.year, time.month, time.day, time.hour, time.minute, time.second

def UTC2BDT(year, month, day, hour, minute, second):
    leaps = getBDLeaps(year, month)
    time = datetime.datetime(year, month, day, hour, minute, second)
    time = time + datetime.timedelta(seconds=leaps)
    if time.month <= 2:
        JD = int(365.25 * (time.year-1)) + int(30.6001 * (time.month + 1 + 12)) + time.day + 1720981.5 + time.hour / 24.0 + \
        time.minute / 1440.0 + time.second / 86400.0
    else:
        JD = int(365.25*time.year) + int(30.6001*(time.month + 1)) + time.day + 1720981.5 + time.hour/24.0 + \
             time.minute/1440.0 + time.second/86400.0
    bds_week, second_of_week, day_of_week = JD2BDT(JD)
    return bds_week, second_of_week, day_of_week

def BDT2date(self):
    JD = self.BDT2JD()
    year, month, day, hour, minute, second = self.JD2GL(JD)
    time = datetime.datetime(year, month, day, hour, minute, second)
    return time.year, time.month, time.day, time.hour, time.minute, time.second

def date2BDT(year, month, day, hour, minute, second):
    time = datetime.datetime(year, month, day, hour, minute, second)
    if time.month <= 2:
        JD = int(365.25 * (time.year-1)) + int(30.6001 * (time.month + 1 + 12)) + time.day + 1720981.5 + time.hour / 24.0 + \
        time.minute / 1440.0 + time.second / 86400.0
    else:
        JD = int(365.25*time.year) + int(30.6001*(time.month + 1)) + time.day + 1720981.5 + time.hour/24.0 + \
             time.minute/1440.0 + time.second/86400.0
    bds_week, second_of_week, day_of_week = JD2BDT(JD)
    return bds_week, second_of_week, day_of_week

def getBDLeaps(year, month):
    if year <= 2006 & month <= 1:
        raise ValueError("BD Time started at 2006")
    elif year <= 2009 & month <= 1:
        return 0
    elif year <= 2012 & month <= 7:
        return 1
    elif year <= 2015 & month <= 7:
        return 2
    elif year <= 2017 & month <= 1:
        return 3
    else:
        return 4

"""BDT to GPST"""
def GPST2BDT(week, sec):
    year, month, day, hour, minute, second = GPST2UTC(week, sec)
    bds_week, second_of_week, day_of_week = UTC2BDT(year, month, day, hour, minute, second)
    return bds_week, second_of_week, day_of_week

def BDT2GPST(week, sec):
    year, month, day, hour, minute, second = BDT2UTC(week, sec)
    bds_week, second_of_week, day_of_week = UTC2GPST(year, month, day, hour, minute, second)
    return bds_week, second_of_week, day_of_week

"""time to doy"""
def date2doy(year, month, day, hour, minute, second):
    """Convert date to day of year, return int doy"""
    if year % 4 == 0 and year % 400 != 0:
        doy = day
        day_month = [0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        doy = doy + sum(day_month[0:month])
        doysec = hour*3600 + minute*60 + second
    else:
        doy = day
        day_month = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        doy = doy + sum(day_month[0:month])
        doysec = hour*3600 + minute*60 + second
    return doy, doysec



