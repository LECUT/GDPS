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
#            <From 4.00 to 2.00/2.11>                           * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import datetime


def NAV_rinex4_to_rinex2(input_file_path, target_version, output_location):
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
    global GP_info_list, GL_info_list, GA_info_list, BD_info_list, QZ_info_list, IR_info_list, SB_info_list
    GP_info_list = [[], []]
    GL_info_list = [[], []]
    GA_info_list = [[], []]
    BD_info_list = [[], []]
    QZ_info_list = [[], []]
    IR_info_list = [[], []]
    SB_info_list = [[], []]
    for i in raw_header_info:
        if i[1].strip() == 'RINEX VERSION / TYPE':
            if target_version == '2':
                lines_text = '     2              NAVIGATION DATA                         RINEX VERSION / TYPE'
            elif target_version == '2.11':
                lines_text = '     2.11           NAVIGATION DATA                         RINEX VERSION / TYPE'
        else:
            lines_text = i[0] + i[1]
        GP_info_list[0].append(lines_text)
        GL_info_list[0].append(lines_text)
        GA_info_list[0].append(lines_text)
        BD_info_list[0].append(lines_text)
        QZ_info_list[0].append(lines_text)
        IR_info_list[0].append(lines_text)
        SB_info_list[0].append(lines_text)
    global GP_temp_data_list, GL_temp_data_list, GA_temp_data_list, BD_temp_data_list, QZ_temp_data_list, IR_temp_data_list, SB_temp_data_list, GP_time_list, GL_time_list, GA_time_list, BD_time_list, QZ_time_list, IR_time_list, SB_time_list
    GP_temp_data_list = []
    GL_temp_data_list = []
    GA_temp_data_list = []
    BD_temp_data_list = []
    QZ_temp_data_list = []
    IR_temp_data_list = []
    SB_temp_data_list = []
    GP_time_list = []
    GL_time_list = []
    GA_time_list = []
    BD_time_list = []
    QZ_time_list = []
    IR_time_list = []
    SB_time_list = []
    data_system_convert_dic = {'G': 'GP', 'R': 'GL', 'E': 'GA', 'C': 'BD', 'J': 'QZ', 'I': 'IR', 'S': 'SB'}
    iter_copy_raw_rinex_text_list = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for row_line in iter_copy_raw_rinex_text_list:
        temp_list = []
        line = next(iter_copy_raw_rinex_text_list).split('\n')[0]
        moment_time = line[4:8] + '-' + line[9:11].strip().rjust(2, '0') + '-' + line[12:14].strip().rjust(2, '0') + ' ' + line[15:17].strip().rjust \
            (2, '0') + ':' + line[18:20].strip().rjust(2, '0') + ':' + line[21:23].strip().rjust(2, '0')
        var_time_name = data_system_convert_dic[line[0]] + '_time_list'
        temp_time_value = globals()[var_time_name]
        if moment_time not in temp_time_value:
            temp_time_value.append(moment_time)
        hh = moment_time[11:13].lstrip('0').rjust(2, ' ') if moment_time[11:13] != '00' else ' 0'
        mm = moment_time[14:16].lstrip('0').rjust(2, ' ') if moment_time[14:16] != '00' else ' 0'
        ss = moment_time[17:19].lstrip('0').rjust(2, ' ') if moment_time[17:19] != '00' else ' 0'
        first_line_list = [moment_time, line[1:3].lstrip('0').rjust(2, ' ') +'  ' +line[6:8] +'  ' +moment_time[5:7].lstrip('0').rjust(2, ' ') +'  ' +moment_time[8:10].lstrip('0').rjust(2, ' ' ) +'  ' +hh +'  ' +mm +'  ' +ss +'.0 ' +' ' +line[23:].upper().replace('E', 'D')]
        temp_list += first_line_list
        if line[0] in ['G', 'E', 'C', 'J', 'I']:
            skip_line_num = 7
        elif line[0] in ['R']:
            skip_line_num = 4
        elif line[0] in ['S']:
            skip_line_num = 3
        while skip_line_num > 0:
            converd_line0 = '   ' + (next(iter_copy_raw_rinex_text_list).split('\n')[0][4:].upper()).replace('E', 'D')
            temp_list.append(converd_line0)
            skip_line_num -= 1
        if line[0] == 'R':
            del(temp_list[-1])
        var_name = data_system_convert_dic[line[0]] + '_temp_data_list'
        temp_value = globals()[var_name]
        temp_value.append(temp_list)
    input_file_name = input_file_path.split('/')[-1]
    file_suffix_dic = {'GP': 'n', 'GL': 'g', 'GA': 'l', 'BD': 'f', 'IR': 'i', 'QZ': 'q', 'SB': 'h'}
    for system in ['GP', 'GL', 'GA', 'BD', 'QZ', 'IR', 'SB']:
        var_name_GP_temp_data_list = system + '_temp_data_list'
        temp_value_GP_temp_data_list = globals()[var_name_GP_temp_data_list]
        if len(temp_value_GP_temp_data_list) != 0:
            var_name_GP_time_list = system + '_time_list'
            temp_value_GP_time_list = globals()[var_name_GP_time_list]
            sort_GP_time_list = sorted(temp_value_GP_time_list, key=lambda date: datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp())
            var_name_GP_info_list = system + '_info_list'
            temp_value_GP_info_list = globals()[var_name_GP_info_list]
            for point_time in sort_GP_time_list:
                for i in temp_value_GP_temp_data_list:
                    if i[0] == point_time:
                        temp_value_GP_info_list.append(i[1:])
            new_file_name = input_file_name[0:4].lower() + input_file_name[16:20] + '.' + input_file_name[14:16] + file_suffix_dic[system]
            with open(output_location + new_file_name, 'w', encoding='utf-8') as f:
                for i in temp_value_GP_info_list:
                    for j in i:
                        f.write(str(j))
                        f.write('\n')
