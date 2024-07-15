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
#            <From 2.11/3.00/3.01 to 2.10>                      * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import re


def MET_RINEX211301_to_RINEX210(input_file_path, target_version):
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
    temp_judge = True
    temp_num = 0
    InputFile_type_observ_list = []
    all_type_observ_num = 0
    converd_list = []
    for i in raw_header_info:
        temp_list = []
        if i[1].strip() == 'RINEX VERSION / TYPE':
            lines_text = ' ' * 5 + target_version + (15 - len(target_version)) * ' ' + i[0][20:60] + i[1]
        elif i[1].strip() == '# / TYPES OF OBSERV':
            if temp_judge:
                temp_inset_local = temp_num
                temp_judge = False
            for j in i[0].split():
                if len(j) == 2:
                    InputFile_type_observ_list.append(j)
            all_type_observ_num += 1
        else:
            lines_text = i[0] + i[1]
        temp_num += 1
        temp_list.append(lines_text)
        converd_list.append(temp_list)
    standard_type_observ_list = ['PR', 'TD', 'HR', 'ZW', 'ZD', 'ZT']
    converd_type_observ_list = []
    converd_type_observ_local = []
    temp_num = 0
    for i in InputFile_type_observ_list:
        if i in standard_type_observ_list:
            converd_type_observ_list.append(i)
            converd_type_observ_local.append(temp_num)
        temp_num += 1
    inset_line_1 = ' ' * 5 + str(len(converd_type_observ_list)) + ' ' * 4 + '    '.join(
        str(j) for j in converd_type_observ_list)
    inset_line_2 = inset_line_1 + ' ' * (60 - len(inset_line_1)) + '# / TYPES OF OBSERV'
    converd_list.insert(temp_inset_local, [inset_line_2])
    iter_copy_raw_rinex_text_list = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for row_line in iter_copy_raw_rinex_text_list:
        lines_text = row_line.split('\n')[0]
        moment_time = lines_text[:18]
        record_data_list = re.findall('.{' + str(7) + '}', lines_text[18:])
        record_data_list.append(lines_text[18:][(len(record_data_list) * 7):])
        del (record_data_list[-1])
        if all_type_observ_num != 1:
            lines_text = next(iter_copy_raw_rinex_text_list).split('\n')[0]
            add_second_line_data = re.findall('.{' + str(7) + '}', lines_text[4:])
            add_second_line_data.append(lines_text[4:][(len(add_second_line_data) * 7):])
            del (add_second_line_data[-1])
            record_data_list += add_second_line_data
        recode_line = moment_time
        for i in converd_type_observ_local:
            recode_line += record_data_list[i]
        converd_list.append([recode_line])
    return converd_list
