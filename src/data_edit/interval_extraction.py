#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Extract file data based on interval                * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *


def Interval_Extraction_Function(input_file_content, sampling_interval_num):
    raw_rinex_text_list = input_file_content
    interval_judge = False
    type_of_observ_judge = True
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        if line_text[60:80].strip() == '# / TYPES OF OBSERV':
            if type_of_observ_judge:
                input_file_code_num = int(line_text[:10].strip())
                type_of_observ_judge = False
        if line_text[60:80].strip() == 'INTERVAL':
            interval_location = i
            interval_judge = True
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    raw_header_record = raw_rinex_text_list[:end_header_rows + 1]
    raw_data_record = raw_rinex_text_list[end_header_rows + 1:]
    ture_judge = True
    for i in raw_data_record:
        if len(i[:27].split()) > 5:
            if ture_judge:
                first_time_list = i[:27].split()
                ture_judge = False
            else:
                second_time_list = i[:27].split()
                break
    if len(first_time_list[0]) == 2:
        start_year = 2000 + int(first_time_list[0])
        start_month = int(first_time_list[1])
        start_day = int(first_time_list[2])
        start_hour = int(first_time_list[3])
        start_monter = int(first_time_list[4])
        start_second = int(float(first_time_list[5]))
    else:
        start_year = int(first_time_list[1])
        start_month = int(first_time_list[2])
        start_day = int(first_time_list[3])
        start_hour = int(first_time_list[4])
        start_monter = int(first_time_list[5])
        start_second = int(float(first_time_list[6]))
    if len(second_time_list[0]) == 2:
        last_year = 2000 + int(second_time_list[0])
        last_month = int(second_time_list[1])
        last_day = int(second_time_list[2])
        last_hour = int(second_time_list[3])
        last_monter = int(second_time_list[4])
        last_second = int(float(second_time_list[5]))
    else:
        last_year = int(second_time_list[1])
        last_month = int(second_time_list[2])
        last_day = int(second_time_list[3])
        last_hour = int(second_time_list[4])
        last_monter = int(second_time_list[5])
        last_second = int(float(second_time_list[6]))
    first_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
    second_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
    interval = (second_time - first_time).total_seconds()
    if interval_judge:
        sampling_interval_num = format(sampling_interval_num, ".3f")
        raw_header_record[interval_location] = sampling_interval_num.rjust(9, ' ') + ' ' + '                                                  INTERVAL\n'
    interval_division = int(float(sampling_interval_num) / interval)  # int 2
    extracted_data_record_list = []
    iter_data_record_list = iter(raw_data_record)
    if raw_data_record[0][0] != '>':  # version 2.x
        moment_satellite_max_num = 12
        for line in iter_data_record_list:
            skip_interval = interval_division - 1
            if len(line[:32].split()) == 8:
                extracted_data_record_list.append(line)
                the_moment_site_satellite_num = int(line[30:32])
                divisible_moment_satellite = the_moment_site_satellite_num % moment_satellite_max_num
                if divisible_moment_satellite == 0:
                    record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num - 1
                else:
                    record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num
                skip_record_num_2 = record_satellite_row
                while skip_record_num_2 > 0:
                    extracted_data_record_list.append(next(iter_data_record_list))
                    skip_record_num_2 -= 1
                divisible_satellite_PRN_recode_info = input_file_code_num % 5
                if divisible_satellite_PRN_recode_info == 0:
                    record_satellite_row = input_file_code_num // 5
                else:
                    record_satellite_row = input_file_code_num // 5 + 1
                stable_record_satellite_row = record_satellite_row
                for i in range(the_moment_site_satellite_num):
                    temp_satellite_row = stable_record_satellite_row
                    while temp_satellite_row > 0:
                        extracted_data_record_list.append(next(iter_data_record_list))
                        temp_satellite_row -= 1
                    pass
                while skip_interval > 0:
                    next_line_text = next(iter_data_record_list)
                    next_moment_site_satellite_num = int(next_line_text[30:32])
                    next_divisible_moment_satellite = next_moment_site_satellite_num % moment_satellite_max_num
                    if next_divisible_moment_satellite == 0:
                        next_record_satellite_row = next_moment_site_satellite_num // moment_satellite_max_num - 1
                    else:
                        next_record_satellite_row = next_moment_site_satellite_num // moment_satellite_max_num
                    skip_record_num_3 = next_record_satellite_row
                    while skip_record_num_3 > 0:
                        next(iter_data_record_list)
                        skip_record_num_3 -= 1
                    for i in range(next_moment_site_satellite_num):
                        temp_satellite_row = stable_record_satellite_row
                        while temp_satellite_row > 0:
                            next(iter_data_record_list)
                            temp_satellite_row -= 1
                    skip_interval -= 1
    elif raw_data_record[0][0] == '>':  # > version 3.x
        for line in iter_data_record_list:
            skip_interval = interval_division - 1
            if len(line[:32].split()) == 8:
                moment_prn_num = int(line[32:35].strip())
                extracted_data_record_list.append(line)
                while moment_prn_num > 0:
                    extracted_data_record_list.append(next(iter_data_record_list))
                    moment_prn_num -= 1
                while skip_interval > 0:
                    next_line_text = next(iter_data_record_list)
                    next_moment_prn_num = int(next_line_text[32:35].strip())
                    while next_moment_prn_num > 0:
                        next(iter_data_record_list)
                        next_moment_prn_num -= 1
                    skip_interval -= 1

    raw_header_record_ = raw_header_record.copy()
    for j in range(len(raw_header_record[:]) - 1, -1, -1):
        line_ = raw_header_record_[j]
        if "PRN / # OF OBS" in line_[60:]:
            del raw_header_record_[j]
        if '# OF SATELLITES' in line_[60:]:
            del raw_header_record_[j]
    extracted_content = raw_header_record_ + extracted_data_record_list
    return extracted_content
