#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Observation Data RINEX Conversion                  * |
#            <From 2.11 to 2.12>                                * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *
import re


def OBS_RINEX211_to_RINEX212(file_path, target_version):
    print('RINEX-2.12 Convert to RINEX-', target_version)
    raw_header_info = []
    with open(file_path, 'r') as f:
        raw_rinex_text_list = f.readlines()
    copy_raw_rinex_text_list = raw_rinex_text_list[:]
    converted_save_list = []
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        temp_info_list = [line_text[0:20], line_text[20:40], line_text[40:60], line_text[60:80]]
        raw_header_info = raw_header_info + [temp_info_list]
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    type_of_observe_num = True
    raw_type_of_observe = []
    for deal_row in range(end_header_rows + 1):
        add_dealed_list = []
        current_row_list = raw_rinex_text_list[deal_row].strip('\n')
        header_label = current_row_list[60:80].rstrip()
        if header_label == 'RINEX VERSION / TYPE':
            add_dealed_list.append([current_row_list.replace('2.11', target_version)])
        elif header_label == 'PGM / RUN BY / DATE':
            PGM = 'GRDC'
            utct = datetime.utcnow()
            utctm = f"0{utct.month}" if utct.month < 10 else f"{utct.month}"
            utctd = f"0{utct.day}" if utct.day < 10 else f"{utct.day}"
            utcth = f"0{utct.hour}" if utct.hour < 10 else f"{utct.hour}"
            utctmi = f"0{utct.minute}" if utct.minute < 10 else f"{utct.minute}"
            utcts = f"0{utct.second}" if utct.second < 10 else f"{utct.second}"
            utctout = f"{utct.year}{utctm}{utctd} {utcth}{utctmi}{utcts} UTC "
            add_comment = PGM + ' ' * 16 + 'VERSION CONVERSION' + ' ' * 2 + utctout + "COMMENT"
            add_dealed_list.append([current_row_list])
            add_dealed_list.append([add_comment])
        elif header_label == '# / TYPES OF OBSERV':
            if type_of_observe_num:
                sys_obs_type_insert_num = len(converted_save_list)
                input_file_code_num = int(current_row_list.split()[0])
                type_of_observe_num = False
            raw_type_of_observe.append(current_row_list)
        else:
            add_dealed_list.append([current_row_list])
        converted_save_list.extend(add_dealed_list)
    all_type_of_observe_code = []
    for one_row_of_type_observe in raw_type_of_observe:
        temp_type_of_observe_list = (one_row_of_type_observe.split('#')[0]).split()
        for one_observe_code in temp_type_of_observe_list:
            if len(one_observe_code) == 2:
                if one_observe_code.isdigit():
                    pass
                else:
                    all_type_of_observe_code.append(one_observe_code)
    all_sys_list = []
    data_record_content = str(copy_raw_rinex_text_list[end_header_rows + 1:])
    if 'G' in data_record_content:
        all_sys_list.append('G')
    elif 'R' in data_record_content:
        all_sys_list.append('R')
    elif 'E' in data_record_content:
        all_sys_list.append('E')
    elif 'S' in data_record_content:
        all_sys_list.append('S')
    rinex211_to_rinex212_code = {'G': {'C1': 'CA',
                                       'P1': 'P1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'C2': 'CC',
                                       'P2': 'P2', 'L2': 'L2', 'D2': 'D2', 'S2': 'S2',
                                       'P5': 'P5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5'},
                                 'R': {'C1': 'CA',
                                       'P1': 'P1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'C2': 'CD',
                                       'P2': 'P2', 'L2': 'L2', 'D2': 'D2', 'S2': 'S2'},
                                 'E': {'C1': 'C1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'C5': 'C5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5',
                                       'C7': 'C7', 'L7': 'L7', 'D7': 'D7', 'S7': 'S7',
                                       'C8': 'C8', 'L8': 'L8', 'D8': 'D8', 'S8': 'S8',
                                       'C6': 'C6', 'L6': 'L6', 'D6': 'D6', 'S6': 'S6'},
                                 'S': {'C1': 'C1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'C5': 'C5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5'}}
    rinex211_location = {'G': {'CA': 'C1', 'LA': 'L1', 'DA': 'D1', 'SA': 'S1',
                               'P1': 'P1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                               'CC': 'C2', 'LC': 'L2', 'DC': 'D2', 'SC': 'S2',
                               'P2': 'P2', 'L2': 'L2', 'D2': 'D2', 'S2': 'S2',
                               'P5': 'P5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5'},
                         'R': {'CA': 'C1', 'LA': 'L1', 'DA': 'D1', 'SA': 'S1',
                               'P1': 'P1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                               'CD': 'C2', 'LD': 'L2', 'DD': 'D2', 'SD': 'S2',
                               'P2': 'P2', 'L2': 'L2', 'D2': 'D2', 'S2': 'S2'},
                         'E': {'C1': 'C1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                               'C5': 'C5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5',
                               'C7': 'C7', 'L7': 'L7', 'D7': 'D7', 'S7': 'S7',
                               'C8': 'C8', 'L8': 'L8', 'D8': 'D8', 'S8': 'S8',
                               'C6': 'C6', 'L6': 'L6', 'D6': 'D6', 'S6': 'S6'},
                         'S': {'C1': 'C1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                               'C5': 'C5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5'}}
    repe_conv_observe_code = []
    sign_conv_observe_code = []
    code_conv_relation_list = []
    code_location_dic = {}
    for j in all_sys_list:
        temp_conv_observe_code = []
        for i in all_type_of_observe_code:
            conv_code = rinex211_to_rinex212_code[j][i]
            temp_conv_observe_code.append(conv_code)
            if j == 'G':
                if conv_code == 'CA':
                    if 'L1' in all_type_of_observe_code:
                        temp_conv_observe_code.append('LA')
                    if 'D1' in all_type_of_observe_code:
                        temp_conv_observe_code.append('DA')
                    if 'S1' in all_type_of_observe_code:
                        temp_conv_observe_code.append('SA')
                elif conv_code == 'CC':
                    if 'L2' in all_type_of_observe_code:
                        temp_conv_observe_code.append('LC')
                    if 'D2' in all_type_of_observe_code:
                        temp_conv_observe_code.append('DC')
                    if 'S2' in all_type_of_observe_code:
                        temp_conv_observe_code.append('SC')
            elif j == 'R':
                if conv_code == 'CA':
                    if 'L1' in all_type_of_observe_code:
                        temp_conv_observe_code.append('LA')
                    if 'D1' in all_type_of_observe_code:
                        temp_conv_observe_code.append('DA')
                    if 'S1' in all_type_of_observe_code:
                        temp_conv_observe_code.append('SA')
                elif conv_code == 'CD':
                    if 'L2' in all_type_of_observe_code:
                        temp_conv_observe_code.append('LD')
                    if 'D2' in all_type_of_observe_code:
                        temp_conv_observe_code.append('DD')
                    if 'S2' in all_type_of_observe_code:
                        temp_conv_observe_code.append('SD')
        if j == 'G' or j == 'R':
            if 'P1' not in temp_conv_observe_code:
                try:
                    temp_conv_observe_code.remove('L1')
                    temp_conv_observe_code.remove('D1')
                    temp_conv_observe_code.remove('S1')
                except:
                    pass
            elif 'P2' not in temp_conv_observe_code:
                try:
                    temp_conv_observe_code.remove('L2')
                    temp_conv_observe_code.remove('D2')
                    temp_conv_observe_code.remove('S2')
                except:
                    pass
        temp_dic = {}
        for k in temp_conv_observe_code:
            initial_location = all_type_of_observe_code.index(rinex211_location[j][k])
            temp_dic[k] = initial_location
            temp_list = [j, rinex211_location[j][k], k]
            code_conv_relation_list.append(temp_list)
        code_location_dic[j] = temp_dic
        repe_conv_observe_code += temp_conv_observe_code
    for i in repe_conv_observe_code:
        if i not in sign_conv_observe_code:
            sign_conv_observe_code.append(i)
    divide_step = 9
    temp_list = [sign_conv_observe_code[i:i + divide_step] for i in
                 range(0, len(sign_conv_observe_code), divide_step)]
    for i, k in zip(range(len(temp_list)), temp_list):
        for j in range(len(k)):
            temp_list[i][j] = ' ' * 4 + temp_list[i][j]
        for x in range(9 - len(k)):
            temp_list[i].append(' ' * 6)
        temp_list[i].append('# / TYPES OF OBSERV')
        if i == 0:
            temp_list[i].insert(0, ' ' * (6 - len(str(len(sign_conv_observe_code)))) + str(
                len(sign_conv_observe_code)))
        else:
            temp_list[i].insert(0, ' ' * 6)
    for i in reversed(temp_list):
        line_text = ''.join(i)
        converted_save_list.insert(sys_obs_type_insert_num, [line_text])
    temp_comment_list = ['       CODE CONVERSION DETAILS:                             COMMENT']
    for code_conv in code_conv_relation_list:
        conv_detail = '  ' + code_conv[0] + '    ' + code_conv[1] + ' -> ' + code_conv[2] + ' ' * 45 + 'COMMENT'
        temp_comment_list.append(conv_detail)
    converted_save_list.insert(sys_obs_type_insert_num, temp_comment_list)
    iter_search_for_satellite = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for line in iter_search_for_satellite:
        record_all_satellite_list = ''
        the_moment_site_satellite_time = line[:30]
        the_moment_site_satellite_num = int(line[30:32])
        record_all_satellite_list += line[32:].split('\n')[0]
        record_all_satellite_list = "".join(re.findall('[A-Z]..', record_all_satellite_list)).replace(' ', '0')
        divisible_moment_satellite = the_moment_site_satellite_num % 12
        if divisible_moment_satellite == 0:
            record_satellite_row = the_moment_site_satellite_num // 12 - 1
        else:
            record_satellite_row = the_moment_site_satellite_num // 12
        skip_record_num = record_satellite_row
        while skip_record_num > 0:
            record_all_satellite_list += str(next(iter_search_for_satellite).split('\n')[0].strip()).replace(' ',
                                                                                                             '0')
            skip_record_num -= 1
        record_all_satellite_list = re.findall(r'.{3}', record_all_satellite_list)
        divide_12_PRN_list = [record_all_satellite_list[i:i + 12] for i in
                              range(0, len(record_all_satellite_list), 12)]
        divide_12_PRN_str_list = []
        for i in divide_12_PRN_list:
            divide_12_PRN_str_list.append(''.join(i))
        prn_num = (str(len(record_all_satellite_list))).rjust(2, ' ')
        heard_time_PRN = the_moment_site_satellite_time + prn_num + divide_12_PRN_str_list[0]
        converted_save_list.append([heard_time_PRN])
        if len(divide_12_PRN_str_list) > 1:
            for i in divide_12_PRN_str_list[1:]:
                temp_line = ' ' * 32 + i
                converted_save_list.append([temp_line])
        divisible_satellite_PRN_recode_info = input_file_code_num % 5
        if divisible_satellite_PRN_recode_info == 0:
            record_satellite_row = input_file_code_num // 5
        else:
            record_satellite_row = input_file_code_num // 5 + 1
        for PRN in record_all_satellite_list:
            skip_record_num_2 = record_satellite_row
            one_PRN_recode_data = ''
            while skip_record_num_2 > 0:
                line_text = next(iter_search_for_satellite).split('\n')[0]
                if skip_record_num_2 != 1:
                    if len(line_text) != 80:
                        line_text += ' ' * (80 - len(line_text))
                elif skip_record_num_2 == 1:
                    all_recode_data_long = 16 * input_file_code_num
                    last_line_theoretical_long = all_recode_data_long - (record_satellite_row - 1) * 80
                    line_text += ' ' * (last_line_theoretical_long - len(line_text))
                one_PRN_recode_data += line_text
                skip_record_num_2 -= 1
            one_PRN_recode_data_list = re.findall(r'.{16}', one_PRN_recode_data)
            conv_one_prn_data = ''
            for conv_code in sign_conv_observe_code:
                code_location = code_location_dic[PRN[0]][conv_code]
                conv_one_prn_data += one_PRN_recode_data_list[code_location]
            conv_one_prn_data_list = cut_list(conv_one_prn_data, 16)
            conv_one_line_PRN_data_list = cut_list(conv_one_prn_data_list, 5)
            for str_5_list in conv_one_line_PRN_data_list:
                converted_save_list.append([''.join(str_5_list)])
    else:
        for _ in range(record_satellite_row):
            next(iter_search_for_satellite, None)
    return converted_save_list



# function: Split the list into lists with a length of 3
# input parameter: 1.list  2.length
# output parameter: 1.list
# input example: [1,2,3,4,5,6,7,8,9,10,11]  3
# output example: [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11]]
def cut_list(lists, cut_len):
    res_data = []
    if len(lists) > cut_len:
        for i in range(int(len(lists) / cut_len)):
            cut_a = lists[cut_len * i:cut_len * (i + 1)]
            res_data.append(cut_a)
        last_data = lists[int(len(lists) / cut_len) * cut_len:]
        if last_data:
            res_data.append(last_data)
    else:
        res_data.append(lists)
    return res_data
