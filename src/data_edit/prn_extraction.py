#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Extract file data based on PRN                     * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import re


def PRN_Extraction_Function(input_file_content, PRN_list):
    raw_rinex_text_list = input_file_content
    type_of_observ_judge = True
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        if line_text[60:80].strip() == '# / TYPES OF OBSERV':
            if type_of_observ_judge:
                input_file_code_num = int(line_text[:10].strip())
                type_of_observ_judge = False
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    raw_header_record = raw_rinex_text_list[:end_header_rows + 1]
    raw_data_record = raw_rinex_text_list[end_header_rows + 1:]
    copy_raw_data_record = raw_data_record[:]
    copy_raw_data_record_02 = raw_data_record[:]
    list_copy_raw_data_record = iter(copy_raw_data_record)
    all_record_prn_list = []
    if raw_data_record[0][0] == '>':  # version 3.x~4.x
        for line in list_copy_raw_data_record:
            if line[0] != '>':
                all_record_prn_list.append(line[:3].replace(' ', '0'))
    else:  # version 2.x
        for line in list_copy_raw_data_record:
            if len(line[:27].split()) > 5:
                the_moment_site_satellite_num = int(line[30:32])
                all_monment_prn_list = line[32:].split('\n')[0]
                all_monment_prn_list = "".join(re.findall('[A-Z]..', all_monment_prn_list)).replace(' ', '0')
                divisible_moment_satellite = the_moment_site_satellite_num % 12
                if divisible_moment_satellite == 0:
                    record_satellite_row = the_moment_site_satellite_num // 12 - 1
                else:
                    record_satellite_row = the_moment_site_satellite_num // 12
                skip_record_num_1 = record_satellite_row
                while skip_record_num_1 > 0:
                    all_monment_prn_list += str(next(list_copy_raw_data_record).split('\n')[0].strip()).replace(' ',
                                                                                                                '0')
                    skip_record_num_1 -= 1
                all_monment_prn_list = re.findall(r'.{3}', all_monment_prn_list)
                all_record_prn_list.extend(all_monment_prn_list)
    all_record_prn_list = list(set(all_record_prn_list))
    all_record_prn_list.sort()
    extracted_data_record_list = []
    iter_data_record_list = iter(copy_raw_data_record_02)
    if raw_data_record[0][0] != '>':
        moment_satellite_max_num = 12
        for line in iter_data_record_list:
            if len(line[:32].split()) == 8:
                record_all_satellite_list = ''
                the_moment_site_satellite_num = int(line[30:32])
                record_all_satellite_list += line[32:].split('\n')[0]
                record_all_satellite_list = "".join(re.findall('[A-Z]..', record_all_satellite_list)).replace(' ',
                                                                                                              '0')
                divisible_moment_satellite = the_moment_site_satellite_num % moment_satellite_max_num
                if divisible_moment_satellite == 0:
                    record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num - 1
                else:
                    record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num
                skip_record_num_2 = record_satellite_row
                while skip_record_num_2 > 0:
                    record_all_satellite_list += str(next(iter_data_record_list).split('\n')[0].strip()).replace(
                        ' ', '0')
                    skip_record_num_2 -= 1
                record_all_satellite_list = re.findall(r'.{3}', record_all_satellite_list)
                copy_record_all_satellite_list = record_all_satellite_list[:]
                satellite_observe_data_list = []
                divisible_satellite_PRN_recode_info = input_file_code_num % 5
                if divisible_satellite_PRN_recode_info == 0:
                    record_satellite_row = input_file_code_num // 5
                else:
                    record_satellite_row = input_file_code_num // 5 + 1
                stable_record_satellite_row = record_satellite_row
                for i in range(the_moment_site_satellite_num):
                    record_satellite_row = stable_record_satellite_row
                    one_PRN_recode_info = []
                    while record_satellite_row > 0:
                        temp_PRN_line_info = next(iter_data_record_list)
                        one_PRN_recode_info.append(temp_PRN_line_info)
                        record_satellite_row -= 1
                    satellite_observe_data_list.append(one_PRN_recode_info)
                delete_record_data_list = []
                delete_num = 0
                for prn in copy_record_all_satellite_list:
                    if prn not in PRN_list:
                        delete_record_data_list.append(delete_num)
                        record_all_satellite_list.remove(prn)
                    delete_num += 1
                div_12prn_list = [record_all_satellite_list[i:i + 12] for i in
                                  range(0, len(record_all_satellite_list), 12)]
                for i in reversed(delete_record_data_list):
                    satellite_observe_data_list.pop(i)
                if len(satellite_observe_data_list) != 0:
                    first_line_judge = True
                    for i in div_12prn_list:
                        if first_line_judge:
                            temp_time_prn = line[:30] + str(len(record_all_satellite_list)).rjust(2, ' ') + ''.join \
                                (i) + '\n'
                            first_line_judge = False
                        else:
                            temp_time_prn = ' ' * 32 + ''.join(i) + '\n'
                        extracted_data_record_list.append(temp_time_prn)
                    for i in satellite_observe_data_list:
                        for j in i:
                            extracted_data_record_list.append(j)

    elif raw_data_record[0][0] == '>':  # version 3.x~4.x
        extracted_data_record_list = []
        moment_satellite_max_num = 12
        iter_data_record_list = iter(copy_raw_data_record_02)
        for line in iter_data_record_list:
            if len(line[:32].split()) == 8:
                moment_prn_num = int(line[32:35].strip())
                moment_prn_data_list = []
                while moment_prn_num > 0:
                    moment_prn_data_list.append(next(iter_data_record_list))
                    moment_prn_num -= 1
                delete_prn_data_num_list = []
                delete_prn_data_num = 0
                for i in moment_prn_data_list:
                    if i[:3].replace(' ', '0') not in PRN_list:
                        delete_prn_data_num_list.append(delete_prn_data_num)
                    delete_prn_data_num += 1
                for i in reversed(delete_prn_data_num_list):
                    moment_prn_data_list.pop(i)
                if len(moment_prn_data_list) != 0:
                    time_prntime = line[:32] + str(len(moment_prn_data_list)).rjust(3, ' ') + '\n'
                    extracted_data_record_list.append(time_prntime)
                    for i in moment_prn_data_list:
                        extracted_data_record_list.append(i)

    raw_header_record_ = raw_header_record.copy()
    for j in range(len(raw_header_record[:]) - 1, -1, -1):
        line_ = raw_header_record_[j]
        if "PRN / # OF OBS" in line_[60:]:
            del raw_header_record_[j]
        if '# OF SATELLITES' in line_[60:]:
            del raw_header_record_[j]

    extracted_content = raw_header_record_ + extracted_data_record_list
    return extracted_content
