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
#        <From 2.11/2.12 to 3.00/3.01/3.02/3.03/3.04/3.05/4.00> * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *
import re


def OBS_RINEX2_to_RINEX3(file_path, target_version):
    print('RINEX-2.11 Convert to RINEX-', target_version)
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
            if '2.12' in current_row_list:
                print('RINEX-2.12 Convert to RINEX-', target_version)
                add_dealed_list.append([current_row_list.replace('2.12', target_version)])
            else:
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
    if target_version == '3.00':
        rinex2_to_rinex3_codeconv = {'G': {'P1': 'C1W', 'L1': 'L1W', 'D1': 'D1W', 'S1': 'S1W',
                                           'CA': 'C1C', 'LA': 'L1C', 'DA': 'D1C', 'SA': 'S1C',
                                           'CB': 'C1C', 'LB': 'L1C', 'DB': 'D1C', 'SB': 'S1C',
                                           'C1': 'C1C',
                                           'P2': 'C2W', 'L2': 'L2W', 'D2': 'D2W', 'S2': 'S2W',
                                           'C2': 'C2C',
                                           'CC': 'C2C', 'LC': 'L2C', 'DC': 'D2C', 'SC': 'S2C',
                                           'C5': 'C5X', 'L5': 'L5X', 'D5': 'D5X', 'S5': 'S5X'},
                                     'R': {'P1': 'C1P', 'P2': 'C2P',
                                           'C1': 'C1C', 'C2': 'C2C',
                                           'CA': 'C1C', 'CD': 'C2C',
                                           'L1': 'L1P', 'L2': 'L2P',
                                           'D1': 'D1P', 'D2': 'D2P',
                                           'S1': 'S1P', 'S2': 'S2P',
                                           'LA': 'L1C', 'LD': 'L2C',
                                           'DA': 'D1C', 'DD': 'D2C',
                                           'SA': 'S1C', 'SD': 'S2C'},
                                     'E': {'C1': 'C1X', 'C5': 'C5X', 'C7': 'C7X', 'C8': 'C8X', 'C6': 'C6X',
                                           'L1': 'L1X', 'L5': 'L5X', 'L7': 'L7X', 'L8': 'L8X', 'L6': 'L6X',
                                           'D1': 'D1X', 'D5': 'D5X', 'D7': 'D7X', 'D8': 'D8X', 'D6': 'D6X',
                                           'S1': 'S1X', 'S5': 'S5X', 'S7': 'S7X', 'S8': 'S8X', 'S6': 'S6X'},
                                     'S': {'C1': 'C1C', 'L1': 'L1C', 'D1': 'D1C', 'S1': 'S1C',
                                           'C5': 'C5X', 'L5': 'L5X', 'D5': 'D5X', 'S5': 'S5X'}}
    elif target_version == '3.01':
        rinex2_to_rinex3_codeconv = {'G': {'P1': 'C1W', 'P2': 'C2W',
                                           'CA': 'C1C', 'C2': 'C2C',
                                           'CB': 'C1C', 'CD': 'C1C',
                                           'C1': 'C1C',              'C5': 'C5X',
                                           'L1': 'L1W', 'L2': 'L2W', 'L5': 'L5X',
                                           'D1': 'D1W', 'D2': 'D2W', 'D5': 'D5X',
                                           'S1': 'S1W', 'S2': 'S2W', 'S5': 'S5X',
                                           'LA': 'L1C', 'LC': 'L2C',
                                           'DA': 'D1C', 'DC': 'D2C',
                                           'SA': 'S1C', 'SC': 'S2C',
                                           'LB': 'L1C',
                                           'DB': 'D1C',
                                           'SB': 'S1C'},
                                     'R': {'P1': 'C1P', 'P2': 'C2P',
                                           'C1': 'C1C', 'C2': 'C2C',
                                           'CA': 'C1C', 'CD': 'C2C',
                                           'L1': 'L1P', 'L2': 'L2P',
                                           'D1': 'D1P', 'D2': 'D2P',
                                           'S1': 'S1P', 'S2': 'S2P',
                                           'LA': 'L1C', 'LD': 'L2C',
                                           'DA': 'D1C', 'DD': 'D2C',
                                           'SA': 'S1C', 'SD': 'S2C'},
                                     'E': {'C1': 'C1X', 'C5': 'C5X', 'C7': 'C7X', 'C8': 'C8X', 'C6': 'C6X',
                                           'L1': 'L1X', 'L5': 'L5X', 'L7': 'L7X', 'L8': 'L8X', 'L6': 'L6X',
                                           'D1': 'D1X', 'D5': 'D5X', 'D7': 'D7X', 'D8': 'D8X', 'D6': 'D6X',
                                           'S1': 'S1X', 'S5': 'S5X', 'S7': 'S7X', 'S8': 'S8X', 'S6': 'S6X'},
                                     'S': {'C1': 'C1C', 'L1': 'L1C', 'D1': 'D1C', 'S1': 'S1C',
                                           'C5': 'C5X', 'L5': 'L5X', 'D5': 'D5X', 'S5': 'S5X'},
                                     'C': {'C2': 'C1X', 'L2': 'L1X', 'D2': 'D1X', 'S2': 'S1X',
                                           'C7': 'C7X', 'L7': 'L7X', 'D7': 'D7X', 'S7': 'S7X',
                                           'C6': 'C6X', 'L6': 'L6X', 'D6': 'D6X', 'S6': 'S6X'}}
    elif target_version == '3.02':
        rinex2_to_rinex3_codeconv = {'G': {'P1': 'C1W', 'P2': 'C2W',
                                           'CA': 'C1C', 'C2': 'C2C',
                                           'CB': 'C1C', 'CD': 'C1C',
                                           'C1': 'C1C',              'C5': 'C5X',
                                           'L1': 'L1W', 'L2': 'L2W', 'L5': 'L5X',
                                           'D1': 'D1W', 'D2': 'D2W', 'D5': 'D5X',
                                           'S1': 'S1W', 'S2': 'S2W', 'S5': 'S5X',
                                           'LA': 'L1C', 'LC': 'L2C',
                                           'DA': 'D1C', 'DC': 'D2C',
                                           'SA': 'S1C', 'SC': 'S2C',
                                           'LB': 'L1C',
                                           'DB': 'D1C',
                                           'SB': 'S1C'},
                                     'R': {'P1': 'C1P', 'P2': 'C2P',
                                           'C1': 'C1C', 'C2': 'C2C',
                                           'CA': 'C1C', 'CD': 'C2C',
                                           'L1': 'L1P', 'L2': 'L2P',
                                           'D1': 'D1P', 'D2': 'D2P',
                                           'S1': 'S1P', 'S2': 'S2P',
                                           'LA': 'L1C', 'LD': 'L2C',
                                           'DA': 'D1C', 'DD': 'D2C',
                                           'SA': 'S1C', 'SD': 'S2C'},
                                     'E': {'C1': 'C1X', 'C5': 'C5X', 'C7': 'C7X', 'C8': 'C8X', 'C6': 'C6X',
                                           'L1': 'L1X', 'L5': 'L5X', 'L7': 'L7X', 'L8': 'L8X', 'L6': 'L6X',
                                           'D1': 'D1X', 'D5': 'D5X', 'D7': 'D7X', 'D8': 'D8X', 'D6': 'D6X',
                                           'S1': 'S1X', 'S5': 'S5X', 'S7': 'S7X', 'S8': 'S8X', 'S6': 'S6X'},
                                     'S': {'C1': 'C1C', 'L1': 'L1C', 'D1': 'D1C', 'S1': 'S1C',
                                           'C5': 'C5X', 'L5': 'L5X', 'D5': 'D5X', 'S5': 'S5X'},
                                     'C': {'C2': 'C1X', 'L2': 'L1X', 'D2': 'D1X', 'S2': 'S1X',
                                           'C7': 'C7X', 'L7': 'L7X', 'D7': 'D7X', 'S7': 'S7X',
                                           'C6': 'C6X', 'L6': 'L6X', 'D6': 'D6X', 'S6': 'S6X'}}
    else:
        rinex2_to_rinex3_codeconv = {'G': {'P1': 'C1W', 'P2': 'C2W',
                                           'CA': 'C1C', 'C2': 'C2C',
                                           'CB': 'C1C', 'CD': 'C1C',
                                           'C1': 'C1C',              'C5': 'C5X',
                                           'L1': 'L1W', 'L2': 'L2W', 'L5': 'L5X',
                                           'D1': 'D1W', 'D2': 'D2W', 'D5': 'D5X',
                                           'S1': 'S1W', 'S2': 'S2W', 'S5': 'S5X',
                                           'LA': 'L1C', 'LC': 'L2C',
                                           'DA': 'D1C', 'DC': 'D2C',
                                           'SA': 'S1C', 'SC': 'S2C',
                                           'LB': 'L1C',
                                           'DB': 'D1C',
                                           'SB': 'S1C'},
                                     'R': {'P1': 'C1P', 'P2': 'C2P',
                                           'C1': 'C1C', 'C2': 'C2C',
                                           'CA': 'C1C', 'CD': 'C2C',
                                           'L1': 'L1P', 'L2': 'L2P',
                                           'D1': 'D1P', 'D2': 'D2P',
                                           'S1': 'S1P', 'S2': 'S2P',
                                           'LA': 'L1C', 'LD': 'L2C',
                                           'DA': 'D1C', 'DD': 'D2C',
                                           'SA': 'S1C', 'SD': 'S2C'},
                                     'E': {'C1': 'C1X', 'C5': 'C5X', 'C7': 'C7X', 'C8': 'C8X', 'C6': 'C6X',
                                           'L1': 'L1X', 'L5': 'L5X', 'L7': 'L7X', 'L8': 'L8X', 'L6': 'L6X',
                                           'D1': 'D1X', 'D5': 'D5X', 'D7': 'D7X', 'D8': 'D8X', 'D6': 'D6X',
                                           'S1': 'S1X', 'S5': 'S5X', 'S7': 'S7X', 'S8': 'S8X', 'S6': 'S6X'},
                                     'S': {'C1': 'C1C', 'L1': 'L1C', 'D1': 'D1C', 'S1': 'S1C',
                                           'C5': 'C5X', 'L5': 'L5X', 'D5': 'D5X', 'S5': 'S5X'},
                                     'C': {'C2': 'C2X', 'L2': 'L2X', 'D2': 'D2X', 'S2': 'S2X',
                                           'C7': 'C7X', 'L7': 'L7X', 'D7': 'D7X', 'S7': 'S7X',
                                           'C6': 'C6X', 'L6': 'L6X', 'D6': 'D6X', 'S6': 'S6X'}}
    all_satellite_system_list = []
    iter_search_for_satellite = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for line in iter_search_for_satellite:
        record_all_satellite_list = ''
        the_moment_site_satellite_num = int(line[30:32])
        record_all_satellite_list += line[32:].split('\n')[0]
        record_all_satellite_list = "".join(re.findall('[A-Z]..', record_all_satellite_list)).replace(' ', '0')
        divisible_moment_satellite = the_moment_site_satellite_num % 12
        if divisible_moment_satellite == 0:
            record_satellite_row = the_moment_site_satellite_num // 12 - 1
        else:
            record_satellite_row = the_moment_site_satellite_num // 12
        skip_record_num_1 = record_satellite_row
        while skip_record_num_1 > 0:
            record_all_satellite_list += str(next(iter_search_for_satellite).split('\n')[0].strip()).replace(' ', '0')
            skip_record_num_1 -= 1
            pass
        record_all_satellite_list = re.findall(r'.{3}', record_all_satellite_list)
        for single_satellite_system in record_all_satellite_list:
            if single_satellite_system[0] not in all_satellite_system_list:
                all_satellite_system_list.append(single_satellite_system[0])
        divisible_satellite_PRN_recode_info = input_file_code_num % 5
        if divisible_satellite_PRN_recode_info == 0:
            record_satellite_row = input_file_code_num // 5
        else:
            record_satellite_row = input_file_code_num // 5 + 1
        for _ in range(the_moment_site_satellite_num * record_satellite_row):  # skip next 3 items
            next(iter_search_for_satellite, None)
    raw_converted_code = []
    raw_converted_code_details = []
    convert_code_location = []
    for satellite_system in all_satellite_system_list:
        temp_list = []
        temp_location = []
        temp_list.append(satellite_system)
        temp_location.append(satellite_system)
        location_num = 0
        for observe_code in all_type_of_observe_code:
            location_num += 1
            try:
                single_converted_code = rinex2_to_rinex3_codeconv[satellite_system][observe_code]
                temp_list.append(single_converted_code)
                temp_location.append(location_num)
                recode_details = satellite_system + '   ' + observe_code + ' --> ' + single_converted_code
                raw_converted_code_details.append(recode_details)
            except:
                pass
        raw_converted_code.append(temp_list)
        convert_code_location.append(temp_location)

    finnal_insert_text = []
    for i in raw_converted_code:
        temp_list = []
        if len(i[1:]) <= 13:
            line_code = ''
            for j in i[1:]:
                line_code += ' ' + j
            if len(str(len(i[1:]))) < 2:
                temp_code_num = ' ' + str(len(i[1:]))
            else:
                temp_code_num = str(len(i[1:]))
            line_code = i[0] + '   ' + temp_code_num + line_code + (
                    54 - len(line_code)) * ' ' + 'SYS / # / OBS TYPES'
            temp_list.append(line_code)
            finnal_insert_text.append(temp_list)
        else:
            line_code = ''
            for j in i[1:14]:
                line_code += ' ' + j
            temp_code_num = str(len(i[1:]))
            line_code = i[0] + '   ' + temp_code_num + line_code + '  ' + 'SYS / # / OBS TYPES'
            finnal_insert_text.append([line_code])
            second_end_code_list = cut_list(i[14:], 13)
            for k12 in second_end_code_list:
                line_code = ''
                for j12 in k12:
                    line_code += ' ' + j12
                line_code = ' ' * 6 + line_code + (54 - len(line_code)) * ' ' + 'SYS / # / OBS TYPES'
                finnal_insert_text.append([line_code])
            pass
    finnal_insert_text.append(['                                                            COMMENT'])
    finnal_insert_text.append(['RINEX 2.11 -> 3.xx CODE CONVERSION DETAILS:                 COMMENT'])
    finnal_insert_text.append(['-------------------------------------------                 COMMENT'])
    for i in raw_converted_code_details:
        temp_list = []
        temp_list.append('      ' + i + '                                        COMMENT')
        finnal_insert_text.append(temp_list)
    finnal_insert_text.append(['-------------------------------------------                 COMMENT'])
    finnal_insert_text.append(['                                                            COMMENT'])
    for i in reversed(finnal_insert_text):
        converted_save_list.insert(sys_obs_type_insert_num, i)
    moment_satellite_max_num = 12
    now_deal_row = 0
    null_string = ' ' * 16
    all_satellite_system_list = []
    iter_copy_raw_rinex_text_list = iter(copy_raw_rinex_text_list[end_header_rows + 1:])
    for line in iter_copy_raw_rinex_text_list:
        now_deal_row += 1
        if len(line[:32].split()) == 8:
            add_dealed_list = []
            moment_time = '> 20' + line[1:32]
            add_dealed_list.append([moment_time])
            converted_save_list.extend(add_dealed_list)
            record_all_satellite_list = ''
            the_moment_site_satellite_num = int(line[30:32])
            record_all_satellite_list += line[32:].split('\n')[0]
            record_all_satellite_list = "".join(re.findall('[A-Z]..', record_all_satellite_list)).replace(' ', '0')
            divisible_moment_satellite = the_moment_site_satellite_num % moment_satellite_max_num
            if divisible_moment_satellite == 0:
                record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num - 1
            else:
                record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num
            skip_record_num_2 = record_satellite_row
            while skip_record_num_2 > 0:
                record_all_satellite_list += str(next(iter_copy_raw_rinex_text_list).split('\n')[0].strip()).replace \
                    (' ', '0')
                skip_record_num_2 -= 1
                pass
            record_all_satellite_list = re.findall(r'.{3}', record_all_satellite_list)
            for single_satellite_system in record_all_satellite_list:
                if single_satellite_system[0] not in all_satellite_system_list:
                    all_satellite_system_list.append(single_satellite_system[0])
            satellite_observe_data_list = []
            divisible_satellite_PRN_recode_info = input_file_code_num % 5
            if divisible_satellite_PRN_recode_info == 0:
                record_satellite_row = input_file_code_num // 5
            else:
                record_satellite_row = input_file_code_num // 5 + 1
            stable_record_satellite_row = record_satellite_row
            for i in range(the_moment_site_satellite_num):
                record_satellite_row = stable_record_satellite_row
                one_PRN_recode_info = ''
                while record_satellite_row > 0:
                    temp_PRN_line_info = str(next(iter_copy_raw_rinex_text_list).split('\n')[0])
                    if len(temp_PRN_line_info) < 80:
                        temp_PRN_line_info = temp_PRN_line_info + (80 - len(temp_PRN_line_info)) * ' '
                    one_PRN_recode_info += temp_PRN_line_info
                    record_satellite_row -= 1
                satellite_observe_data_list.append(one_PRN_recode_info)
            for PRN, record_info in zip(record_all_satellite_list, satellite_observe_data_list):
                record_info_list = re.findall(r'.{16}', record_info)
                for one_satellite_convert_loation in convert_code_location:
                    if PRN[0] in one_satellite_convert_loation:
                        temp_line_text = ''
                        for location in one_satellite_convert_loation[1:]:
                            temp_line_text += record_info_list[location - 1]
                        add_dealed_list = []
                        add_dealed_list.append([PRN + temp_line_text])
                        converted_save_list.extend(add_dealed_list)
                        break
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
