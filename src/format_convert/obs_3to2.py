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
#        <From 3.00/3.01/3.02/3.03/3.04/3.05/4.00 to 2.11/2.12> * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *


def OBS_RINEX3_to_RINEX2(file_path, target_version):
    raw_header_info = []
    with open(file_path, 'r') as f:
        raw_rinex_text_list = f.readlines()
    copy_raw_rinex_text_list = raw_rinex_text_list[:]
    input_file_version = raw_rinex_text_list[0][5:9].strip()
    if target_version == '2.12':
        print('RINEX-', input_file_version, ' Convert to RINEX-2.12')
    else:
        print('RINEX-', input_file_version, ' Convert to RINEX-2.11')
    converted_save_list = []
    time_moment_type = "{:>3}{:>3}{:>3}{:>3}{:>3}{:>11}{:>3}{:>3}{:<36}"
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        temp_info_list = [line_text[0:20], line_text[20:40], line_text[40:60], line_text[60:80]]
        raw_header_info = raw_header_info + [temp_info_list]
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    glonass_frq = True
    for deal_row in range(end_header_rows + 1):
        add_dealed_list = []
        current_row_list = raw_rinex_text_list[deal_row].strip('\n')
        header_label = current_row_list[60:80].rstrip()
        if header_label == 'RINEX VERSION / TYPE':
            if target_version == '2.12':
                add_dealed_list.append([current_row_list.replace(input_file_version, "2.12")])
            else:
                add_dealed_list.append([current_row_list.replace(input_file_version, "2.11")])
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
        elif header_label == 'SYS / # / OBS TYPES':
            sys_obs_type_insert_num = len(converted_save_list)
        elif header_label == 'SYS / PHASE SHIFTS':
            pass
        elif header_label == 'GLONASS COD/PHS/BIS':
            add_dealed_list.append(['GLONASS COD/PHS/BIS was droped after version conversion.    COMMENT'])
        elif header_label == 'SIGNAL STRENGTH UNIT':
            add_dealed_list.append(['SIGNAL STRENGTH UNIT | ' + current_row_list[0:22] + '               COMMENT'])
        elif header_label == 'GLONASS SLOT / FRQ #':
            if glonass_frq:
                add_dealed_list.append(['GLONASS SLOT / FRQ # was droped after version conversion.   COMMENT'])
                glonass_frq = False
        else:
            add_dealed_list.append([current_row_list])

        converted_save_list.extend(add_dealed_list)
    raw_rinex302_obs_type_mess = []
    raw_rinex302_obs_type_sort = []
    for i in raw_header_info:
        if i[-1].rstrip() == 'SYS / # / OBS TYPES':
            raw_rinex302_obs_type_mess += [i]
    for i in raw_rinex302_obs_type_mess:
        raw_header_info.remove(i)
    for i in raw_rinex302_obs_type_mess:
        if i[0][0:1] != ' ':
            raw_rinex302_obs_type_sort += [[i[0] + i[1] + i[2]]]
        else:
            raw_rinex302_obs_type_sort[-1] = raw_rinex302_obs_type_sort[-1] + [i[0] + i[1] + i[2]]
        if len(raw_rinex302_obs_type_sort[-1]) != 1:
            temp_list = ''
            for j in raw_rinex302_obs_type_sort[-1]:
                temp_list += j
            raw_rinex302_obs_type_sort[-1] = [temp_list]

    raw_rinex302_obs_type_sort_01 = []
    for i in raw_rinex302_obs_type_sort:
        temp_list = i[0].split()
        raw_rinex302_obs_type_sort_01 += [[temp_list[0], temp_list[1], temp_list[2:len(temp_list)]]]
    if target_version == '2.11':
        rinex_2_all_code = ['L1', 'L2', 'L5', 'L6', 'L7', 'L8',
                            'P1', 'P2',
                            'C1', 'C2', 'C5', 'C6', 'C7', 'C8',
                            'D1', 'D2', 'D5', 'D6', 'D7', 'D8',
                            'S1', 'S2', 'S5', 'S6', 'S7', 'S8']
        rinex302_to_rinex211_code = {'G': {'C1P': 'P1', 'L1P': 'L1', 'D1P': 'D1', 'S1P': 'S1',
                                           'C1W': 'P1', 'L1W': 'L1', 'D1W': 'D1', 'S1W': 'S1',
                                           'C1Y': 'P1', 'L1Y': 'L1', 'D1Y': 'D1', 'S1Y': 'S1',
                                           'C1M': 'P1', 'L1M': 'L1', 'D1M': 'D1', 'S1M': 'S1',
                                           'L1N': 'L1', 'D1N': 'D1', 'S1N': 'S1',
                                           'C1C': 'C1', 'L1C': 'L1', 'D1C': 'D1', 'S1C': 'S1',
                                           'C1S': 'C1', 'L1S': 'L1', 'D1S': 'D1', 'S1S': 'S1',
                                           'C1L': 'C1', 'L1L': 'L1', 'D1L': 'D1', 'S1L': 'S1',
                                           'C1X': 'C1', 'L1X': 'L1', 'D1X': 'D1', 'S1X': 'S1',
                                           'C1R': 'C1', 'L1R': 'L1', 'D1R': 'D1', 'S1R': 'S1',
                                           'C2P': 'P2', 'L2P': 'L2', 'D2P': 'D2', 'S2P': 'S2',
                                           'C2W': 'P2', 'L2W': 'L2', 'D2W': 'D2', 'S2W': 'S2',
                                           'C2Y': 'P2', 'L2Y': 'L2', 'D2Y': 'D2', 'S2Y': 'S2',
                                           'C2M': 'P2', 'L2M': 'L2', 'D2M': 'D2', 'S2M': 'S2',
                                           'L2N': 'L2', 'D2N': 'D2', 'S2N': 'S2',
                                           'C2C': 'C2', 'L2C': 'L2', 'D2C': 'D2', 'S2C': 'S2',
                                           'C2D': 'C2', 'L2D': 'L2', 'D2D': 'D2', 'S2D': 'S2',
                                           'C2S': 'C2', 'L2S': 'L2', 'D2S': 'D2', 'S2S': 'S2',
                                           'C2L': 'C2', 'L2L': 'L2', 'D2L': 'D2', 'S2L': 'S2',
                                           'C2X': 'C2', 'L2X': 'L2', 'D2X': 'D2', 'S2X': 'S2',
                                           'C2R': 'C2', 'L2R': 'L2', 'D2R': 'D2', 'S2R': 'S2',
                                           'C5I': 'C5', 'L5I': 'L5', 'D5I': 'D5', 'S5I': 'S5',
                                           'C5Q': 'C5', 'L5Q': 'L5', 'D5Q': 'D5', 'S5Q': 'S5',
                                           'C5X': 'C5', 'L5X': 'L5', 'D5X': 'D5', 'S5X': 'S5'},
                                     'R': {'C1P': 'P1', 'L1P': 'L1', 'D1P': 'D1', 'S1P': 'S1',
                                           'C1C': 'C1', 'L1C': 'L1', 'D1C': 'D1', 'S1C': 'S1',
                                           'C2P': 'P2', 'L2P': 'L2', 'D2P': 'D2', 'S2P': 'S2',
                                           'C2C': 'C2', 'L2C': 'L2', 'D2C': 'D2', 'S2C': 'S2'},
                                     'E': {'C1A': 'C1', 'L1A': 'L1', 'D1A': 'D1', 'S1A': 'S1',
                                           'C1B': 'C1', 'L1B': 'L1', 'D1B': 'D1', 'S1B': 'S1',
                                           'C1X': 'C1', 'L1X': 'L1', 'D1X': 'D1', 'S1X': 'S1',
                                           'C1Z': 'C1', 'L1Z': 'L1', 'D1Z': 'D1', 'S1Z': 'S1',
                                           'C1C': 'C1', 'L1C': 'L1', 'D1C': 'D1', 'S1C': 'S1',
                                           'C5I': 'C5', 'L5I': 'L5', 'D5I': 'D5', 'S5I': 'S5',
                                           'C5Q': 'C5', 'L5Q': 'L5', 'D5Q': 'D5', 'S5Q': 'S5',
                                           'C5X': 'C5', 'L5X': 'L5', 'D5X': 'D5', 'S5X': 'S5',
                                           'C6A': 'C6', 'L6A': 'L6', 'D6A': 'D6', 'S6A': 'S6',
                                           'C6B': 'C6', 'L6B': 'L6', 'D6B': 'D6', 'S6B': 'S6',
                                           'C6C': 'C6', 'L6C': 'L6', 'D6C': 'D6', 'S6C': 'S6',
                                           'C6X': 'C6', 'L6X': 'L6', 'D6X': 'D6', 'S6X': 'S6',
                                           'C6Z': 'C6', 'L6Z': 'L6', 'D6Z': 'D6', 'S6Z': 'S6',
                                           'C7I': 'C7', 'L7I': 'L7', 'D7I': 'D7', 'S7I': 'S7',
                                           'C7Q': 'C7', 'L7Q': 'L7', 'D7Q': 'D7', 'S7Q': 'S7',
                                           'C7X': 'C7', 'L7X': 'L7', 'D7X': 'D7', 'S7X': 'S7',
                                           'C8I': 'C8', 'L8I': 'L8', 'D8I': 'D8', 'S8I': 'S8',
                                           'C8Q': 'C8', 'L8Q': 'L8', 'D8Q': 'D8', 'S8Q': 'S8',
                                           'C8X': 'C8', 'L8X': 'L8', 'D8X': 'D8', 'S8X': 'S8'},
                                     'S': {'C1C': 'C1', 'L1C': 'L1', 'D1C': 'D1', 'S1C': 'S1',
                                           'C5I': 'C5', 'L5I': 'L5', 'D5I': 'D5', 'S5I': 'S5',
                                           'C5Q': 'C5', 'L5Q': 'L5', 'D5Q': 'D5', 'S5Q': 'S5',
                                           'C5X': 'C5', 'L5X': 'L5', 'D5X': 'D5', 'S5X': 'S5'}}
    elif target_version == '2.12':
        rinex_2_all_code = ['CA', 'CB', 'CC', 'CD', 'C1', 'C2', 'C3', 'C5', 'C6', 'C7', 'C8',
                            'P1', 'P2',
                            'LA', 'LB', 'LC', 'LD', 'L1', 'L2', 'L3', 'L5', 'L6', 'L7', 'L8',
                            'DA', 'DB', 'DC', 'DD', 'D1', 'D2', 'D3', 'D5', 'D6', 'D7', 'D8',
                            'SA', 'SB', 'SC', 'SD', 'S1', 'S2', 'S3', 'S5', 'S6', 'S7', 'S8']
        rinex302_to_rinex211_code = {'G': {'C1P': 'P1', 'L1P': 'L1', 'D1P': 'D1', 'S1P': 'S1',
                                           'C1W': 'P1', 'L1W': 'L1', 'D1W': 'D1', 'S1W': 'S1',
                                           'C1Y': 'P1', 'L1Y': 'L1', 'D1Y': 'D1', 'S1Y': 'S1',
                                           'C1M': 'P1', 'L1M': 'L1', 'D1M': 'D1', 'S1M': 'S1',
                                           'L1N': 'L1', 'D1N': 'D1', 'S1N': 'S1',
                                           'C1C': 'CA', 'L1C': 'LA', 'D1C': 'DA', 'S1C': 'SA',
                                           'C1S': 'CB', 'L1S': 'LB', 'D1S': 'DB', 'S1S': 'SB',
                                           'C1L': 'CB', 'L1L': 'LB', 'D1L': 'DB', 'S1L': 'SB',
                                           'C1X': 'CB', 'L1X': 'LB', 'D1X': 'DB', 'S1X': 'SB',
                                           'C1R': 'CB', 'L1R': 'LB', 'D1R': 'DB', 'S1R': 'SB',
                                           'C2P': 'P2', 'L2P': 'L2', 'D2P': 'D2', 'S2P': 'S2',
                                           'C2W': 'P2', 'L2W': 'L2', 'D2W': 'D2', 'S2W': 'S2',
                                           'C2Y': 'P2', 'L2Y': 'L2', 'D2Y': 'D2', 'S2Y': 'S2',
                                           'C2M': 'P2', 'L2M': 'L2', 'D2M': 'D2', 'S2M': 'S2',
                                           'L2N': 'L2', 'D2N': 'D2', 'S2N': 'S2',
                                           'C2C': 'C2', 'L2C': 'L2', 'D2C': 'D2', 'S2C': 'S2',
                                           'C2D': 'CC', 'L2D': 'LC', 'D2D': 'DC', 'S2D': 'SC',
                                           'C2S': 'CC', 'L2S': 'LC', 'D2S': 'DC', 'S2S': 'SC',
                                           'C2L': 'CC', 'L2L': 'LC', 'D2L': 'DC', 'S2L': 'SC',
                                           'C2X': 'CC', 'L2X': 'LC', 'D2X': 'DC', 'S2X': 'SC',
                                           'C2R': 'CC', 'L2R': 'LC', 'D2R': 'DC', 'S2R': 'SC',
                                           'C5I': 'C5', 'L5I': 'L5', 'D5I': 'D5', 'S5I': 'S5',
                                           'C5Q': 'C5', 'L5Q': 'L5', 'D5Q': 'D5', 'S5Q': 'S5',
                                           'C5X': 'C5', 'L5X': 'L5', 'D5X': 'D5', 'S5X': 'S5'},
                                     'R': {'C1P': 'P1', 'L1P': 'L1', 'D1P': 'D1', 'S1P': 'S1',
                                           'C1C': 'CA', 'L1C': 'LA', 'D1C': 'DA', 'S1C': 'SA',
                                           'C2P': 'P2', 'L2P': 'L2', 'D2P': 'D2', 'S2P': 'S2',
                                           'C2C': 'CD', 'L2C': 'LD', 'D2C': 'DD', 'S2C': 'SD',
                                           'C3I': 'C3', 'L3I': 'L3', 'D3I': 'D3', 'S3I': 'S3',
                                           'C3Q': 'C3', 'L3Q': 'L3', 'D3Q': 'D3', 'S3Q': 'S3',
                                           'C3X': 'C3', 'L3X': 'L3', 'D3X': 'D3', 'S3X': 'S3'},
                                     'E': {'C1A': 'C1', 'L1A': 'L1', 'D1A': 'D1', 'S1A': 'S1',
                                           'C1B': 'C1', 'L1B': 'L1', 'D1B': 'D1', 'S1B': 'S1',
                                           'C1C': 'C1', 'L1C': 'L1', 'D1C': 'D1', 'S1C': 'S1',
                                           'C1X': 'C1', 'L1X': 'L1', 'D1X': 'D1', 'S1X': 'S1',
                                           'C1Z': 'C1', 'L1Z': 'L1', 'D1Z': 'D1', 'S1Z': 'S1',
                                           'C5I': 'C5', 'L5I': 'L5', 'D5I': 'D5', 'S5I': 'S5',
                                           'C5Q': 'C5', 'L5Q': 'L5', 'D5Q': 'D5', 'S5Q': 'S5',
                                           'C5X': 'C5', 'L5X': 'L5', 'D5X': 'D5', 'S5X': 'S5',
                                           'C6A': 'C6', 'L6A': 'L6', 'D6A': 'D6', 'S6A': 'S6',
                                           'C6B': 'C6', 'L6B': 'L6', 'D6B': 'D6', 'S6B': 'S6',
                                           'C6C': 'C6', 'L6C': 'L6', 'D6C': 'D6', 'S6C': 'S6',
                                           'C6X': 'C6', 'L6X': 'L6', 'D6X': 'D6', 'S6X': 'S6',
                                           'C6Z': 'C6', 'L6Z': 'L6', 'D6Z': 'D6', 'S6Z': 'S6',
                                           'C7I': 'C7', 'L7I': 'L7', 'D7I': 'D7', 'S7I': 'S7',
                                           'C7Q': 'C7', 'L7Q': 'L7', 'D7Q': 'D7', 'S7Q': 'S7',
                                           'C7X': 'C7', 'L7X': 'L7', 'D7X': 'D7', 'S7X': 'S7',
                                           'C8I': 'C8', 'L8I': 'L8', 'D8I': 'D8', 'S8I': 'S8',
                                           'C8Q': 'C8', 'L8Q': 'L8', 'D8Q': 'D8', 'S8Q': 'S8',
                                           'C8X': 'C8', 'L8X': 'L8', 'D8X': 'D8', 'S8X': 'S8'},
                                     'S': {'C1C': 'C1', 'L1C': 'L1', 'D1C': 'D1', 'S1C': 'S1',
                                           'C5I': 'C5', 'L5I': 'L5', 'D5I': 'D5', 'S5I': 'S5',
                                           'C5Q': 'C5', 'L5Q': 'L5', 'D5Q': 'D5', 'S5Q': 'S5',
                                           'C5X': 'C5', 'L5X': 'L5', 'D5X': 'D5', 'S5X': 'S5'},
                                     'C': {'C2I': 'C1', 'L2I': 'L1', 'D2I': 'D1', 'S2I': 'S1',
                                           'C2Q': 'C1', 'L2Q': 'L1', 'D2Q': 'D1', 'S2Q': 'S1',
                                           'C2X': 'C1', 'L2X': 'L1', 'D2X': 'D1', 'S2X': 'S1',
                                           'C1I': 'C1', 'L1I': 'L1', 'D1I': 'D1', 'S1I': 'S1',
                                           'C1Q': 'C1', 'L1Q': 'L1', 'D1Q': 'D1', 'S1Q': 'S1',
                                           'C1X': 'C1', 'L1X': 'L1', 'D1X': 'D1', 'S1X': 'S1',
                                           'C7I': 'C7', 'L7I': 'L7', 'D7I': 'D7', 'S7I': 'S7',
                                           'C7Q': 'C7', 'L7Q': 'L7', 'D7Q': 'D7', 'S7Q': 'S7',
                                           'C7X': 'C7', 'L7X': 'L7', 'D7X': 'D7', 'S7X': 'S7',
                                           'C7D': 'C7', 'L7D': 'L7', 'D7D': 'D7', 'S7D': 'S7',
                                           'C7P': 'C7', 'L7P': 'L7', 'D7P': 'D7', 'S7P': 'S7',
                                           'C7Z': 'C7', 'L7Z': 'L7', 'D7Z': 'D7', 'S7Z': 'S7',
                                           'C6I': 'C6', 'L6I': 'L6', 'D6I': 'D6', 'S6I': 'S6',
                                           'C6Q': 'C6', 'L6Q': 'L6', 'D6Q': 'D6', 'S6Q': 'S6',
                                           'C6X': 'C6', 'L6X': 'L6', 'D6X': 'D6', 'S6X': 'S6',
                                           'C6D': 'C6', 'L6D': 'L6', 'D6D': 'D6', 'S6D': 'S6',
                                           'C6P': 'C6', 'L6P': 'L6', 'D6P': 'D6', 'S6P': 'S6',
                                           'C6Z': 'C6', 'L6Z': 'L6', 'D6Z': 'D6', 'S6Z': 'S6'}}
    del_list = []
    for i in raw_rinex302_obs_type_sort_01:
        if i[0] not in rinex302_to_rinex211_code.keys():
            del_list += [i]
    for j in del_list:
        raw_rinex302_obs_type_sort_01.remove(j)
    code_convert_details_01 = []
    for i in raw_rinex302_obs_type_sort_01:
        code_local_num = 0
        temp_dic = {}
        for j in i[2]:
            if j in rinex302_to_rinex211_code[i[0]]:
                converted_code_value = rinex302_to_rinex211_code[i[0]][j]
                single_code_convert_detail = [i[0], j, converted_code_value,
                                              list(rinex302_to_rinex211_code[i[0]].keys()).index(j), code_local_num]
                code_convert_details_01.append(single_code_convert_detail)
            code_local_num += 1
    code_convert_details_01_all_system = []
    for i in code_convert_details_01:
        if i[0] not in code_convert_details_01_all_system:
            code_convert_details_01_all_system.append(i[0])
    code_convert_details_02 = []
    for system in code_convert_details_01_all_system:
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
    code_convert_details_result = []
    same_system_code_conert = same_sys_code_convert_cutList(code_convert_details)
    same_system_code_conert_deduplication = []
    for an in same_system_code_conert:
        temp_list = []
        temp_code = []
        for bn in an:
            if bn[2] not in temp_code:
                temp_list.append(bn)
                temp_code.append(bn[2])
        same_system_code_conert_deduplication.append(temp_list)
    for j in same_system_code_conert_deduplication:
        code_convert_details_result.append(['                                                            COMMENT'])
        for i in j:
            temp_string = ' ' * 6 + i[0] + ' ' * 4 + i[1] + ' -> ' + i[2] + ' ' * 40 + 'COMMENT'
            code_convert_details_result.append([temp_string])
    temp_comment_list = ['                                                            COMMENT',
                         '       CODE CONVERSION DETAILS:                             COMMENT',
                         '-------------------------------------------                 COMMENT']
    for i in [temp_comment_list[0], temp_comment_list[2]]:
        converted_save_list.insert(sys_obs_type_insert_num, [i])
    for i in reversed(code_convert_details_result):
        converted_save_list.insert(sys_obs_type_insert_num, i)
    for i in reversed(temp_comment_list):
        converted_save_list.insert(sys_obs_type_insert_num, [i])
    temp_list = []
    for k1, v1 in converted_code_dic.items():
        for k2 in v1.keys():
            if k2 not in temp_list:
                temp_list.append(k2)
    type_of_observ_code_list = sorted(temp_list, key=lambda x: rinex_2_all_code.index(x))
    divide_step = 9
    temp_list = [type_of_observ_code_list[i:i + divide_step] for i in
                 range(0, len(type_of_observ_code_list), divide_step)]
    for i, k in zip(range(len(temp_list)), temp_list):
        for j in range(len(k)):
            temp_list[i][j] = ' ' * 4 + temp_list[i][j]
        for x in range(9 - len(k)):
            temp_list[i].append(' ' * 6)
        temp_list[i].append('# / TYPES OF OBSERV')
        if i == 0:
            temp_list[i].insert(0, ' ' * (6 - len(str(len(type_of_observ_code_list)))) + str
                (len(type_of_observ_code_list)))
        else:
            temp_list[i].insert(0, ' ' * 6)
    for i in reversed(temp_list):
        converted_save_list.insert(sys_obs_type_insert_num, i)
    now_deal_row = end_header_rows + 1
    null_string = ' ' * 16
    for line in copy_raw_rinex_text_list[end_header_rows + 1:]:
        line = line.split('\n')[0]
        if line.startswith('>'):
            moment_satellites_num = 0
            moment_satellites_list = []
            for j in raw_rinex_text_list[(now_deal_row + 1):(now_deal_row + int(line[33:35]) + 1)]:
                if j[0] in rinex302_to_rinex211_code.keys():
                    moment_satellites_list.append(j[0:3])
                    moment_satellites_num += 1
            old_moment_list = line.split()
            new_moment_list_time = [old_moment_list[1][-2:], str(int(old_moment_list[2])),
                                    str(int(old_moment_list[3])), str(int(old_moment_list[4])),
                                    str(int(old_moment_list[5])), old_moment_list[6], old_moment_list[7],
                                    str(len(moment_satellites_list))]
            divide_step = 12
            divide_step_spae = ''
            divide_moment_satellites_list = [moment_satellites_list[i:i + divide_step] for i in
                                             range(0, len(moment_satellites_list), divide_step)]
            if len(divide_moment_satellites_list) == 1:
                combin1 = new_moment_list_time + [divide_step_spae.join(divide_moment_satellites_list[0])]
                combin2 = [time_moment_type.format(combin1[0], combin1[1], combin1[2], combin1[3], combin1[4],
                                                   combin1[5], combin1[6], combin1[7], combin1[8])]
                converted_save_list.append(combin2)
            else:
                combin1 = new_moment_list_time + [divide_step_spae.join(divide_moment_satellites_list[0])]
                combin2 = [time_moment_type.format(combin1[0], combin1[1], combin1[2], combin1[3], combin1[4],
                                                   combin1[5], combin1[6], combin1[7], combin1[8])]
                converted_save_list.append(combin2)
                for satellite in divide_moment_satellites_list[1:]:
                    combin1 = ['', '', '', '', '', '', '', '' ] +[divide_step_spae.join(satellite)]
                    combin2 = [time_moment_type.format(combin1[0], combin1[1], combin1[2], combin1[3], combin1[4],
                                                       combin1[5], combin1[6], combin1[7], combin1[8])]
                    converted_save_list.append(combin2)
                    pass
        else:
            if line[0] in rinex302_to_rinex211_code.keys():
                add_space_num = 16 - (len(line) - 3) % 16 if (len(line) - 3) % 16 != 0 else 0
                line = line + ' ' * add_space_num
                line_3_end = line[3:]
                raw_record_data_list = [line_3_end[i:i + 16] for i in range(0, len(line_3_end), 16)]
                temp_list = []
                for i in type_of_observ_code_list:
                    if i in converted_code_dic[line[0]].keys():
                        try:
                            temp_list.append(raw_record_data_list[converted_code_dic[line[0]][i]])
                        except:
                            temp_list.append(null_string)
                    else:
                        temp_list.append(null_string)
                divide_temp_list = [temp_list[n:n + 5] for n in range(0, len(temp_list), 5)]
                converted_save_list.extend(divide_temp_list)
                pass
        now_deal_row += 1
    return converted_save_list



# function: Based on the first element combination list
# input parameter: 1.list
# output parameter: 1.list
# input example: [['G', 'C1C', 'C1'], ['G', 'L1C', 'L1'], ['E', 'D1C', 'D1'], ['E', 'S1C', 'S1'], ['S', 'S1C', 'S1']]
# output example: [[['G', 'C1C', 'C1'], ['G', 'L1C', 'L1']], [['E', 'D1C', 'D1'], ['E', 'S1C', 'S1']], [['S', 'S1C', 'S1']]]
def same_sys_code_convert_cutList(orList):
    newList = []
    n = 0
    for k in range(len(orList)):
        if orList[k][0] == orList[-1][0]:
            newList.append(orList[n:])
            break
        if orList[k][0] != orList[k + 1][0]:
            subList = orList[n:k + 1]
            newList.append(subList)
            n = k + 1
    return newList
