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
# * Input    Initial X/Y/Z coordinate: [x0,y0,z0]               * |
#            seven_parameters: [∆x,∆y,∆z,α,β,γ,m]            * |
# * Output   After X/Y/Z coordinate: [x1,y1,z1]                 * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import numpy as np


def CoorSys_Convert(x0, y0, z0, seven_parameters):
    translata_x = seven_parameters[0]
    translata_y = seven_parameters[1]
    translata_z = seven_parameters[2]
    rota_angle1 = (seven_parameters[3] * 3.141592653589793) / (3600 * 180)
    rota_angle2 = (seven_parameters[4] * 3.141592653589793) / (3600 * 180)
    rota_angle3 = (seven_parameters[5] * 3.141592653589793) / (3600 * 180)
    m_proportion = seven_parameters[6] * 0.000001
    old_xyz_list = [x0, y0, z0]
    old_xyz_list_T = np.transpose(old_xyz_list)
    d_list = [translata_x, translata_y, translata_z]
    d_list_T = np.transpose(d_list)
    k_list = [[0, -z0, y0, x0], [z0, 0, -x0, y0], [-y0, x0, 0, z0]]
    para_list = [rota_angle1, rota_angle2, rota_angle3, m_proportion]
    para_list_T = np.transpose(para_list)
    K_para_list = np.dot(k_list, para_list_T)
    new_xyz = old_xyz_list_T + d_list_T + K_para_list
    new_xyz = np.round(new_xyz, decimals=4)
    return new_xyz

