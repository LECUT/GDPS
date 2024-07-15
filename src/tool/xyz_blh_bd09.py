#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Coordinate transformation:                         * |
#            1. XYZ to BLH                                      * |
#            2. BLH to BD09 (BLH --> GCJ02 --> BD09)            * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import math


def XYZ_to_BLH(X, Y, Z):
    a = 6378137.0
    b = 6356752.3142
    e2 = (a ** 2 - b ** 2) / (a ** 2)
    e = math.sqrt(e2)
    # Calculate the value of L
    if X == 0 and Y > 0:
        L = 90
    elif X == 0 and Y < 0:
        L = -90
    elif X < 0 and Y > 0:
        L = math.atan(Y / X)
        L = L * 180.0 / 3.141592653589793
        L = L + 180
    elif X < 0 and Y <= 0:
        L = math.atan(Y / X)
        L = L * 180.0 / 3.141592653589793
        L = L - 180
    else:
        L = math.atan(Y / X)
        L = L * 180.0 / 3.141592653589793
    b0 = math.atan(Z / math.sqrt(X ** 2 + Y ** 2))
    N_temp = a / math.sqrt((1 - e2 * math.sin(b0) * math.sin(b0)))
    b1 = math.atan((Z + N_temp * e2 * math.sin(b0)) / math.sqrt(X ** 2 + Y ** 2))
    while abs(b0 - b1) > 1e-10:
        b0 = b1
        N_temp = a / math.sqrt(1 - e2 * math.sin(b0) * math.sin(b0))
        b1 = math.atan((Z + N_temp * e2 * math.sin(b0)) / math.sqrt(X ** 2 + Y ** 2))
    B = b1
    N = a / math.sqrt(1 - e2 * math.sin(B) ** 2)
    H = (math.sqrt(X ** 2 + Y ** 2) / math.cos(B)) - N
    B = math.degrees(B)
    return [B, L, H]

pi = math.pi
a = 6378245.0  # semi-major axis
es = 0.00669342162296594323  # sqrt(Eccentricity)
x_pi = 3.14159265358979324 * 3000.0 / 180.0
def BLH_to_BD09(lat, lng, hig):
    """
    BLH_to_BD09
    :param lng: WGS84 longitude
    :param lat: WGS84 dimension
    :return: BD09 (longitude, dimension)
    """
    lng2, lat2 = WGS84_to_GCJ02(lng, lat)
    lng3, lat3 = GCJ02_to_BD09(lng2, lat2)
    return [lat3, lng3]

def WGS84_to_GCJ02(lng, lat):
    """
    WGS84_to_GCJ02
    :param lng: WGS84 longitude
    :param lat: WGS84 dimension
    :return: GCJ02 (longitude, dimension)
    """
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - es * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - es)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    gcj_lng = lat + dlat
    gcj_lat = lng + dlng
    return gcj_lng, gcj_lat

def GCJ02_to_BD09(gcj_lng, gcj_lat):
    """
    GCJ02_to_BD09
    :param lng: GCJ02 longitude
    :param lat: GCJ02 dimension
    :return: BD09 (longitude, dimension)
    """
    z = math.sqrt(gcj_lng * gcj_lng + gcj_lat * gcj_lat) + 0.00002 * math.sin(gcj_lat * x_pi)
    theta = math.atan2(gcj_lat, gcj_lng) + 0.000003 * math.cos(gcj_lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lng, bd_lat

def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret

def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret

