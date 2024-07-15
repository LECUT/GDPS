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
#            <From 2.12 to 2.11>                                * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *
import re


def OBS_RINEX212_to_RINEX211(file_path, target_version):
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
            add_dealed_list.append([current_row_list.replace('2.12', target_version)])
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
    if 'R' in data_record_content:
        all_sys_list.append('R')
    if 'E' in data_record_content:
        all_sys_list.append('E')
    if 'S' in data_record_content:
        all_sys_list.append('S')
    rinex212_to_rinex211_code = {'G': {'P1': 'P1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'CA': 'C1', 'LA': 'L1', 'DA': 'D1', 'SA': 'S1',
                                       'CB': 'C1', 'LB': 'L1', 'DB': 'D1', 'SB': 'S1',
                                       'C2': 'C2',
                                       'P2': 'P2', 'L2': 'L2', 'D2': 'D2', 'S2': 'S2',
                                       'CC': 'C2', 'LC': 'L2', 'DC': 'D2', 'SC': 'S2',
                                       'P5': 'P5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5'},
                                 'R': {'P1': 'P1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'CA': 'C1', 'LA': 'L1', 'DA': 'D1', 'SA': 'S1',
                                       'P2': 'P2', 'L2': 'L2', 'D2': 'D2', 'S2': 'S2',
                                       'CD': 'C2', 'LD': 'L2', 'DD': 'D2', 'SD': 'S2', },
                                 'E': {'C1': 'C1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'C5': 'C5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5',
                                       'C7': 'C7', 'L7': 'L7', 'D7': 'D7', 'S7': 'S7',
                                       'C8': 'C8', 'L8': 'L8', 'D8': 'D8', 'S8': 'S8',
                                       'C6': 'C6', 'L6': 'L6', 'D6': 'D6', 'S6': 'S6'},
                                 'S': {'C1': 'C1', 'L1': 'L1', 'D1': 'D1', 'S1': 'S1',
                                       'C5': 'C5', 'L5': 'L5', 'D5': 'D5', 'S5': 'S5'}}
    code_convert_details_01 = []
    conv_code = []
    for i in all_sys_list:
        code_local_num = 0
        for j in all_type_of_observe_code:
            temp_dic = {}
            if j in rinex212_to_rinex211_code[i[0]]:
                converted_code_value = rinex212_to_rinex211_code[i][j]
                if converted_code_value not in conv_code:
                    conv_code.append(converted_code_value)
                single_code_convert_detail = [i, j, converted_code_value,
                                              list(rinex212_to_rinex211_code[i].keys()).index(j), code_local_num]
                code_convert_details_01.append(single_code_convert_detail)
            code_local_num += 1
    code_convert_details_02 = []
    for system in all_sys_list:
        temp_list = [system]
        for i in code_convert_details_01:
            if i[0] == system:
                i.remove(system)
                temp_list.append(i)
        code_convert_details_02.append(temp_list)
    code_convert_details_03 = []
    for i in code_convert_details_02:
        code_convert_details_03_son = [i[0]]
        temp_list_01 = []
        for j in i[1:]:
            if j[1] not in temp_list_01:
                temp_list_01.append(j[1])
        for x in temp_list_01:
            temp_list_02 = []
            for y in i[1:]:
                if y[1] == x:
                    temp_list_02.append(y)
            if len(temp_list_02) > 1:
                sorted_temp_list_02 = sorted(temp_list_02, key=(lambda x: x[2]))
                code_convert_details_03_son.append(sorted_temp_list_02[0])
            else:
                code_convert_details_03_son.append(temp_list_02[0])
        code_convert_details_03.append(code_convert_details_03_son)
    converted_code_dic = {}
    code_convert_details = []
    for i in code_convert_details_03:
        temp_dic = {}
        for j in i[1:]:
            temp_dic.update({j[1]: j[3]})
            single_code_convert_detail = [i[0], j[0], j[1]]
            code_convert_details.append(single_code_convert_detail)
        converted_code_dic.update({i[0]: temp_dic})
    divide_step = 9
    temp_list = [conv_code[i:i + divide_step] for i in
                 range(0, len(conv_code), divide_step)]
    for i, k in zip(range(len(temp_list)), temp_list):
        for j in range(len(k)):
            temp_list[i][j] = ' ' * 4 + temp_list[i][j]
        for x in range(9 - len(k)):
            temp_list[i].append(' ' * 6)
        temp_list[i].append('# / TYPES OF OBSERV')
        if i == 0:
            temp_list[i].insert(0, ' ' * (6 - len(str(len(conv_code)))) + str(len(conv_code)))
        else:
            temp_list[i].insert(0, ' ' * 6)
    for i in reversed(temp_list):
        line_text = ''.join(i)
        converted_save_list.insert(sys_obs_type_insert_num, [line_text])
    temp_comment_list = ['       CODE CONVERSION DETAILS:                             COMMENT']
    for code_conv in code_convert_details:
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
        record_all_satellite_list_copy = record_all_satellite_list[:]
        for one_PRN in record_all_satellite_list[::-1]:
            if one_PRN[0] not in ['G', 'E', 'R', 'S']:
                record_all_satellite_list.remove(one_PRN)
        num = 0
        for one_PRN in record_all_satellite_list_copy:
            if one_PRN[0] not in ['G', 'E', 'R', 'S']:
                record_all_satellite_list_copy.remove(one_PRN)
                record_all_satellite_list_copy.insert(num, None)
            num += 1
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
        for PRN in record_all_satellite_list_copy:
            if PRN:
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
                for code in conv_code:
                    code_location = converted_code_dic[PRN[0]][code]
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
