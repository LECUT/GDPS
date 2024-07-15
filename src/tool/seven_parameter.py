#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Calculate Seven Parameters                         * |
# * Input    coordinate_list: [[x1,y1,z1,x2,y2,z2], [...], ...] * |
# * Output   seven_parameters: [∆x,∆y,∆z,m,α,β,γ]            * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import numpy as np


def Calculate_Seven_Parameters(coordinate_list):
    hangshu = len(coordinate_list) * 3
    lieshu = 7
    B_matria = np.zeros(shape=(hangshu, lieshu))
    L_matria = np.zeros(shape=(hangshu, 1))
    for i in range(len(coordinate_list)):
        B_matria[i * 3, 0] = 1
        B_matria[i * 3, 1] = 0
        B_matria[i * 3, 2] = 0
        B_matria[i * 3, 3] = 0
        B_matria[i * 3, 4] = -coordinate_list[i][2]
        B_matria[i * 3, 5] = coordinate_list[i][1]
        B_matria[i * 3, 6] = coordinate_list[i][0]
        B_matria[i * 3 + 1, 0] = 0
        B_matria[i * 3 + 1, 1] = 1
        B_matria[i * 3 + 1, 2] = 0
        B_matria[i * 3 + 1, 3] = coordinate_list[i][2]
        B_matria[i * 3 + 1, 4] = 0
        B_matria[i * 3 + 1, 5] = -coordinate_list[i][0]
        B_matria[i * 3 + 1, 6] = coordinate_list[i][1]
        B_matria[i * 3 + 2, 0] = 0
        B_matria[i * 3 + 2, 1] = 0
        B_matria[i * 3 + 2, 2] = 1
        B_matria[i * 3 + 2, 3] = -coordinate_list[i][1]
        B_matria[i * 3 + 2, 4] = coordinate_list[i][0]
        B_matria[i * 3 + 2, 5] = 0
        B_matria[i * 3 + 2, 6] = coordinate_list[i][2]
        L_matria[i * 3, 0] = coordinate_list[i][3] - coordinate_list[i][0]
        L_matria[i * 3 + 1, 0] = coordinate_list[i][4] - coordinate_list[i][1]
        L_matria[i * 3 + 2, 0] = coordinate_list[i][5] - coordinate_list[i][2]
        pass
    BT = np.transpose(B_matria)
    BTB = np.dot(BT, B_matria)
    BTB_inv = np.linalg.inv(BTB)
    BTL_li = np.dot(BTB_inv, BT)
    seven_parameters = np.dot(BTL_li, L_matria)
    return seven_parameters

