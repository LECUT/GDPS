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
#            <From 2.00/2.11 to 4.00>                           * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------


def Nav_rinex2_to_rinex4(input_file_path, target_version):
    FileName_system_dic = {'n': 'G', 'g': 'R', 'l': 'E', 'h': 'S', 'i': 'I', 'f': 'C', 'q': 'J'}
    if input_file_path[-1] in FileName_system_dic.keys():
        system = FileName_system_dic[input_file_path[-1]]
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
    heard_info_ion_corr_dic = {'G': 'GPS', 'R': 'GLONASS', 'E': 'GALILEO', 'C': 'BDS', 'S': 'SBAS', 'I': 'IRNSS',
                               'J': 'QZSS'}
    converd_list = []
    for i in raw_header_info:
        temp_list = []
        if i[1].strip() == 'RINEX VERSION / TYPE':
            lines_text = ' ' * 5 + target_version + (15 - len(target_version)) * ' ' + i[0][20:40] + system + ' ' * 19 + i[1]
        elif i[1].strip() == 'ION ALPHA' or i[1].strip() == 'ION BETA' or i[1].strip() == 'DELTA-UTC: A0,A1,T,W':
            pass
        else:
            lines_text = i[0] + i[1]
        temp_list.append(lines_text)
        converd_list.append(temp_list)
    PRN_list = []
    record_info = []
    iter_copy_raw_rinex_text_list = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for row_line in iter_copy_raw_rinex_text_list:
        temp_list = []
        line = row_line.split('\n')[0].split()
        converd_system = system + line[0].rjust(2, '0')
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
            BDS_PRN_Num = converd_system[1:]
            if BDS_PRN_Num in ['01', '02', '03', '04', '05', '59', '60', '61']:
                eph_nav_message_type = 'D2'
            else:
                eph_nav_message_type = 'D1'
        else:
            pass
        Rinex4_record_heard_line = '> EPH ' + converd_system + ' ' + eph_nav_message_type
        temp_list.append(Rinex4_record_heard_line)
        if converd_system not in PRN_list:
            PRN_list.append(converd_system)
        converd_line0 = converd_system + ' ' + '20' + line[1] + ' ' + line[2].rjust(2, '0') + ' ' + line[3].rjust(2, '0') + ' ' + line[4].rjust(2, '0') + ' ' + line[5].rjust(2, '0') + ' ' + line[6][0] + line[6][2] + \
                            (row_line[22:79].upper()).replace('D', 'E')
        temp_list.append(converd_line0)
        if system in ['G', 'E', 'C', 'J', 'I']:
            skip_line_num = 7
        elif system in ['R', 'S']:
            skip_line_num = 3
        while skip_line_num > 0:
            converd_line0 = ' ' * 4 + (next(iter_copy_raw_rinex_text_list).split('\n')[0][3:].upper()).replace('D', 'E')
            temp_list.append(converd_line0)
            skip_line_num -= 1
        if system == 'R':
            temp_list.append('                         .999999999999e+09 1.500000000000e+01                   ')
        record_info.append(temp_list)
    sort_record_info = []
    PRN_list.sort()
    for PRN in PRN_list:
        for data in record_info:
            if data[1][0:3] == PRN:
                sort_record_info.append(data)
    converd_list += sort_record_info
    return converd_list
