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
#            <From 3.00/3.01/3.02/3.03/3.04 to 3.05/4.00/4.01>  * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *
import re


def OBS_RINEX30X_to_RINEX305400(file_path, target_version):
    raw_header_info = []
    with open(file_path, 'r') as f:
        raw_rinex_text_list = f.readlines()
    copy_raw_rinex_text_list = raw_rinex_text_list[:]
    input_file_version = raw_rinex_text_list[0][5:9].strip()
    print('RINEX-', input_file_version, ' Convert to RINEX-', target_version)
    converted_save_list = []
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
            add_dealed_list.append([current_row_list.replace(input_file_version, target_version)])
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
    raw_rinex_obs_type_mess = []
    raw_rinex_obs_type_sort = []
    for i in raw_header_info:
        if i[-1].rstrip() == 'SYS / # / OBS TYPES':
            raw_rinex_obs_type_mess += [i]
    for i in raw_rinex_obs_type_mess:
        raw_header_info.remove(i)
    for i in raw_rinex_obs_type_mess:
        if i[0][0:1] != ' ':
            raw_rinex_obs_type_sort += [[i[0] + i[1] + i[2]]]
        else:
            raw_rinex_obs_type_sort[-1] = raw_rinex_obs_type_sort[-1] + [i[0] + i[1] + i[2]]
        if len(raw_rinex_obs_type_sort[-1]) != 1:
            temp_list = ''
            for j in raw_rinex_obs_type_sort[-1]:
                temp_list += j
            raw_rinex_obs_type_sort[-1] = [temp_list]
    raw_rinex_obs_type_sort_01 = []
    for i in raw_rinex_obs_type_sort:
        temp_list = i[0].split()
        raw_rinex_obs_type_sort_01 += [[temp_list[0], temp_list[2:]]]

    code_of_rine305_GPS_delete = ['C1R', 'L1R', 'D1R', 'S1R',
                                  'C2R', 'L2R', 'D2R', 'S2R']

    code_of_rine305_NavIC_delete = ['C1D', 'L1D', 'D1D', 'S1D',
                                    'C1P', 'L1P', 'D1P', 'S1P',
                                    'C1X', 'L1X', 'D1X', 'S1X']

    converted_rinex305_obs_type_list = []
    converted_rinex305_obs_type_None_list = []
    for i in raw_rinex_obs_type_sort_01:
        temp_list = []
        temp_none_list = []
        if i[0] == 'G':
            if float(target_version) < 4.01:
                for j in i[1]:
                    if j not in code_of_rine305_GPS_delete:
                        temp_list.append(j)
                        temp_none_list.append(j)
                    else:
                        temp_none_list.append(None)
                converted_rinex305_obs_type_list.append([i[0], temp_list])
                converted_rinex305_obs_type_None_list.append([i[0], temp_none_list])
            else:
                converted_rinex305_obs_type_list.append(i)
                converted_rinex305_obs_type_None_list.append(i)
        elif i[0] == 'C':
            if input_file_version == '3.02':
                BDS_temp_code = [m.replace('1I', '2I') if '1I' in m else m for m in i[1]]
                BDS_temp_code = [m.replace('1Q', '2Q') if '1Q' in m else m for m in BDS_temp_code]
                BDS_temp_code = [m.replace('1X', '2X') if '1X' in m else m for m in BDS_temp_code]
            else:
                BDS_temp_code = [m.replace('1A', '1Z') if '1A' in m else m for m in i[1]]
                BDS_temp_code = [m.replace('6A', '6Z') if '6A' in m else m for m in BDS_temp_code]
            for j in BDS_temp_code:
                if j not in temp_list:
                    temp_list.append(j)
                    temp_none_list.append(j)
                else:
                    temp_none_list.append(None)
            converted_rinex305_obs_type_list.append([i[0], temp_list])
            converted_rinex305_obs_type_None_list.append([i[0], temp_none_list])
        elif i[0] == 'I':
            if float(target_version) < 4.01:
                for j in i[1]:
                    if j not in code_of_rine305_NavIC_delete:
                        temp_list.append(j)
                        temp_none_list.append(j)
                    else:
                        temp_none_list.append(None)
                converted_rinex305_obs_type_list.append([i[0], temp_list])
                converted_rinex305_obs_type_None_list.append([i[0], temp_none_list])
            else:
                converted_rinex305_obs_type_list.append(i)
                converted_rinex305_obs_type_None_list.append(i)
        else:
            converted_rinex305_obs_type_list.append(i)
            converted_rinex305_obs_type_None_list.append(i)


    finnal_insert_text = []
    for i in converted_rinex305_obs_type_list:
        temp_list = []
        if len(i[1]) <= 13 and len(i[1]) > 0:
            line_code = ''
            for j in i[1]:
                line_code += ' ' + j
            if len(str(len(i[1]))) < 2:
                temp_code_num = ' ' + str(len(i[1]))
            else:
                temp_code_num = str(len(i[1]))
            line_code = i[0] + '   ' + temp_code_num + line_code + (
                    54 - len(line_code)) * ' ' + 'SYS / # / OBS TYPES'
            temp_list.append(line_code)
            finnal_insert_text.append(temp_list)
        elif len(i[1]) > 13:
            line_code = ''
            for j in i[1][0:13]:
                line_code += ' ' + j
            temp_code_num = str(len(i[1]))
            line_code = i[0] + '   ' + temp_code_num + line_code + '  ' + 'SYS / # / OBS TYPES'
            finnal_insert_text.append([line_code])
            second_end_code_list = cut_list(i[1][13:], 13)
            for k12 in second_end_code_list:
                line_code = ''
                for j12 in k12:
                    line_code += ' ' + j12
                line_code = ' ' * 6 + line_code + (54 - len(line_code)) * ' ' + 'SYS / # / OBS TYPES'
                finnal_insert_text.append([line_code])
        else:
            continue
    for i in reversed(finnal_insert_text):
        converted_save_list.insert(sys_obs_type_insert_num, i)
    now_deal_row = end_header_rows + 1
    for line in copy_raw_rinex_text_list[end_header_rows + 1:]:
        now_deal_row += 1
        line = line.split('\n')[0]
        temp_list = []
        if line.startswith('>'):
            try:
                moment_time_info = line[:-3]
                new_file_moment_satellites_num = 0
                for j in raw_rinex_text_list[(now_deal_row):(now_deal_row + int(line[32:35]))]:
                    moment_satellites_list = []
                    if j[0] in ['G', 'R', 'E', 'S', 'C', 'J', 'I']:
                        j = j.split('\n')[0]
                        moment_satellites_list.append(j[0:3])
                        for sys_code in raw_rinex_obs_type_sort_01:
                            if j[0] == sys_code[0]:
                                temp_line = j + (len(sys_code[1])*16 - len(j[3:]))*' '
                                break
                        divided_temp_line = re.findall(r'.{16}', temp_line[3:])
                        temp_num = 0
                        for i in converted_rinex305_obs_type_None_list:
                            if j[0] == i[0]:
                                for k in i[1]:
                                    if k:
                                        moment_satellites_list.append(divided_temp_line[temp_num])
                                    temp_num += 1
                                break
                        if i[1].count(None) == len(i[1]):
                            continue
                        new_file_moment_satellites_num += 1
                        temp_list.append([''.join(moment_satellites_list)])

                if new_file_moment_satellites_num <= 9:
                    recoad_PRN_num_str = '  ' + str(new_file_moment_satellites_num)
                elif new_file_moment_satellites_num >= 100:
                    recoad_PRN_num_str = str(new_file_moment_satellites_num)
                else:
                    recoad_PRN_num_str = ' ' + str(new_file_moment_satellites_num)

                moment_time_info_ = list(moment_time_info)
                moment_time_info_[32: 35] = recoad_PRN_num_str
                new_time_recoad_info = ''.join(moment_time_info_)
                temp_list.insert(0, [new_time_recoad_info])
                converted_save_list.extend(temp_list)
            except:
                pass
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
