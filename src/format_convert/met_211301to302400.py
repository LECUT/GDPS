#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Meteorological Data RINEX Conversion               * |
#            <From 2.11/3.00/3.01 to 3.02/3.03/3.04/3.05/4.00>  * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------


def MET_RINEX211301_to_RINEX302400(input_file_path, target_version):
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
            lines_text = ' ' * 5 + target_version + (15 - len(target_version)) * ' ' + i[0][20:60] + i[1]
        elif i[1].strip() == 'DOI' or i[1].strip() == 'LICENSE OF USE' or i[1].strip() == 'STATION INFORMATION':
            pass
        else:
            lines_text = i[0] + i[1]
        temp_list.append(lines_text)
        converd_list.append(temp_list)
    iter_copy_raw_rinex_text_list = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for row_line in iter_copy_raw_rinex_text_list:
        lines_text = row_line.split('\n')[0]
        if len(lines_text[1:3].strip()) == 2:
            add_lines_text = ' 20' + lines_text[1:]
        elif len(lines_text[1:3].strip()) == 1:
            add_lines_text = ' 200' + lines_text[2:]
        converd_list.append([add_lines_text])
    return converd_list

