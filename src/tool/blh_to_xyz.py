#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Convert B/L/H coordinate to X/Y/Z coordinate       * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import math


def BLH_to_XYZ(coordinate_system, b0, b1, b2, l0, l1, l2, H_DMS):
    if coordinate_system == 'BJZ54':
        a = 6378245.0
        b = 6356863.0187730473
    elif coordinate_system == 'XiAn80':
        a = 6378140.0
        b = 6356755.2881575287
    elif coordinate_system == 'WGS-84':
        a = 6378137.0
        b = 6356752.3142
    elif coordinate_system == 'CGCS2000':
        a = 6378137.0
        b = 6356752.3141
    B = b0 + b1 / 60.000 + b2 / 3600.000
    B = float(B) / (180 / math.pi)
    L = l0 + l1 / 60.000 + l2 / 3600.000
    L = float(L) / (180 / math.pi)
    H = float(H_DMS)
    c = (a * a) / b
    alfa = (a - b) / a
    e = math.sqrt(2 * alfa - alfa * alfa)
    W = math.sqrt(1.0 - e * e * math.sin(B) * math.sin(B))
    N = a / W
    X = (N + H) * math.cos(B) * math.cos(L)
    Y = (N + H) * math.cos(B) * math.sin(L)
    Z = (N * (1.0 - e * e) + H) * math.sin(B)
    x = str(format(X, '.4f'))
    y = str(format(Y, '.4f'))
    z = str(format(Z, '.4f'))
    caculate_xyz = [x, y, z]
    return caculate_xyz
