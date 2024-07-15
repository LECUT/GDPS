#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Convert X/Y/Z coordinate to B/L/H coordinate       * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import math

def XYZ_to_BLH(datum, X, Y, Z):
    if datum == 'WGS-84':
        a = 6378137.0
        b = 6356752.3142
    elif datum == 'CGCS2000':
        a = 6378137.0
        b = 6356752.3141
    e2 = (a ** 2 - b ** 2) / (a ** 2)
    e = math.sqrt(e2)
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
    B = round(B, 8)
    B_int = int(B)
    B_float = B % B_int
    B_DD = B_int
    B_MM = int(B_float * 3600 // 60)
    B_SS = float(B_float * 3600 % 60)
    B_SS = format(B_SS, '.3f')
    B = str(B_DD) + '°' + str(B_MM) + '′' + str(B_SS) + '″'
    L = round(L, 8)
    L_int = int(L)
    L_float = L % L_int
    L_DD = L_int
    L_MM = int(L_float * 3600 // 60)
    L_SS = float(L_float * 3600 % 60)
    L_SS = format(L_SS, '.3f')
    L = str(L_DD) + '°' + str(L_MM) + '′' + str(L_SS) + '″'
    H = format(H, '.4f')
    cacilated_BLH = [B, L, str(H)]
    return cacilated_BLH
