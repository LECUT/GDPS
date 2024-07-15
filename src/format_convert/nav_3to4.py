#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Navigation Data RINEX Conversion                   * |
#            <From 3.00/3.01/3.02/3.03/3.04/3.05 to 4.00>       * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------


def NAV_rinex3_to_rinex4(input_file_path, target_version):
    with open(input_file_path, 'r') as f:
        raw_rinex_text_list = f.readlines()
    copy_raw_rinex_text_list = raw_rinex_text_list[:]
    raw_header_info = []
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        temp_info_list = [line_text[0:60], line_text[60:80]]
        raw_header_info = raw_header_info + [temp_info_list]
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    converd_list = []
    for i in raw_header_info:
        temp_list = []
        if i[1].strip() == 'RINEX VERSION / TYPE':
            lines_text = '     {} '.format(target_version) + i[0][10:60] + i[1]
            temp_list.append(lines_text)
        elif i[1].strip() in ['IONOSPHERIC CORR', 'TIME SYSTEM CORR']:
            pass
        else:
            lines_text = i[0] + i[1]
            temp_list.append(lines_text)
        if len(temp_list) != 0:
            converd_list.append(temp_list)
    iter_copy_raw_rinex_text_list = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for row_line in iter_copy_raw_rinex_text_list:
        temp_list = []
        system = row_line.split('\n')[0][0].upper()
        PRN = row_line.split('\n')[0][0] + row_line.split('\n')[0][1:3].strip().rjust(2, '0')
        eph_nav_message_type = 'LNAV'
        if system == 'G' or system == 'J' or system == 'I':
            eph_nav_message_type = 'LNAV'
        elif system == 'E':
            eph_nav_message_type = 'INAV'
        elif system == 'R':
            eph_nav_message_type = 'FDMA'
        elif system == 'S':
            eph_nav_message_type = 'SBAS L1'
        elif system == 'C':
            BDS_PRN_Num = PRN[1:]
            if BDS_PRN_Num in ['01', '02', '03', '04', '05', '59', '60', '61']:
                eph_nav_message_type = 'D2'
            else:
                eph_nav_message_type = 'D1'
        else:
            pass
        Rinex4_record_heard_line = '> EPH ' + PRN + ' ' + eph_nav_message_type
        temp_list.append(Rinex4_record_heard_line)
        temp_list.append(row_line.split('\n')[0])
        if system in ['G', 'E', 'C', 'J', 'I']:
            skip_line_num = 7
        elif system in ['R', 'S']:
            skip_line_num = 3
        while skip_line_num > 0:
            temp_list.append(next(iter_copy_raw_rinex_text_list).split('\n')[0])
            skip_line_num -= 1
        if system == 'R' and len(temp_list) != 6:
            temp_list.append('                         .999999999999e+09 1.500000000000e+01                   ')
        converd_list.append(temp_list)
    return converd_list
