#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Extract file data based on time                    * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *


def Time_Extraction_Function(input_file_content, start_time, end_time):
    start_time = start_time
    end_time = end_time
    raw_rinex_text_list = input_file_content
    raw_header_info = []
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        temp_info_list = [line_text[0:60], line_text[60:80]]
        raw_header_info = raw_header_info + [temp_info_list]
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
    interval = (second_time - first_time)
    if raw_data_record[0][0] == '>':
        print(type(end_time.year), end_time.year)
        print(type(end_time.month), end_time.month)
        print(type(end_time.day), end_time.day)
        print(type(end_time.hour), end_time.hour)
        print(type(end_time.minute), end_time.minute)
        print(type(end_time.second), end_time.second)
        end_time_str = str(end_time.year)[2:] + str(end_time.month).zfill(2).rjust(3, ' ') + str(end_time.day).zfill(
            2).rjust(3, ' ') + str(end_time.hour).zfill(2).rjust(3, ' ') + str(end_time.minute).zfill(2).rjust(3,
                                                                                                               ' ') + str(
            end_time.second).rjust(3, ' ')
    else:
        end_time_str = str(end_time.year)[2:] + str(end_time.month).rjust(3, ' ') + str(end_time.day).rjust(3,
                                                                                                            ' ') + str(
            end_time.hour).rjust(3, ' ') + str(end_time.minute).rjust(3, ' ') + str(end_time.second).rjust(3, ' ')
    end_time_addIntervel_judge = False
    for i in raw_data_record:
        if len(i[:27].split()) > 5:
            if end_time_str in i:
                end_time_addIntervel_judge = True
                break
    if end_time_addIntervel_judge:
        raw_time_list = [start_time, end_time + interval]
    else:
        raw_time_list = [start_time, end_time]

    try:
        version = float(str(raw_header_info[0][0])[4:10])
    except ValueError:
        version = None

    start_time_judge = True
    end_time_judge = True
    record_num_list = []
    num = 0
    try:
        for i in raw_data_record:
            import re
            if version <= 2.99:
                if re.search(r'\s\d{2}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', i):
                    record_time_list = i[:27].split()
            else:
                if re.search(r'>\s\d{4}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}.\d{7}', i):
                    record_time_list = i[:27].split()

            # if len(i[:27].split()) > 5:
            #     record_time_list = i[:27].split()
            if len(record_time_list[0]) == 2:
                record_year = 2000 + int(record_time_list[0])
                record_month = int(record_time_list[1])
                record_day = int(record_time_list[2])
                record_hour = int(record_time_list[3])
                record_monter = int(record_time_list[4])
                record_second = int(float(record_time_list[5]))
            else:
                record_year = int(record_time_list[1])
                record_month = int(record_time_list[2])
                record_day = int(record_time_list[3])
                record_hour = int(record_time_list[4])
                record_monter = int(record_time_list[5])
                record_second = int(float(record_time_list[6]))
            record_time = datetime(record_year, record_month, record_day, record_hour, record_monter, record_second)
            if start_time_judge:
                if raw_time_list[0] <= record_time:
                    record_num_list.append(num)
                    start_time_judge = False
            if end_time_judge:
                if raw_time_list[1] <= record_time:
                    record_num_list.append(num)
                    end_time_judge = False
            num += 1
    except Exception as e:
        print(e)
    if len(record_num_list) == 1:
        record_num_list.append(num)
    cut_raw_data_record = raw_data_record[record_num_list[0]: record_num_list[1]]

    for i in cut_raw_data_record:
        if len(i[:27].split()) > 5:
            first_time_list = i[:27].split()
            break
    for j in reversed(cut_raw_data_record):
        if len(j[:27].split()) > 5:
            last_time_list = j[:27].split()
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

    if len(last_time_list[0]) == 2:
        last_year = 2000 + int(last_time_list[0])
        last_month = int(last_time_list[1])
        last_day = int(last_time_list[2])
        last_hour = int(last_time_list[3])
        last_monter = int(last_time_list[4])
        last_second = int(float(last_time_list[5]))
    else:
        last_year = int(last_time_list[1])
        last_month = int(last_time_list[2])
        last_day = int(last_time_list[3])
        last_hour = int(last_time_list[4])
        last_monter = int(last_time_list[5])
        last_second = int(float(last_time_list[6]))
    extracted_first_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
    extracted_last_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
    raw_time_list = [extracted_first_time, extracted_last_time]
    time_of_first_obs_location = ''
    time_of_last_obs_location = ''
    for i in raw_header_record:
        if 'TIME OF FIRST OBS' in i:
            time_of_first_obs_location = raw_header_record.index(i)
        elif 'TIME OF LAST OBS' in i:
            time_of_last_obs_location = raw_header_record.index(i)
    if time_of_first_obs_location != '':
        raw_header_record[time_of_first_obs_location] = '  ' + str(raw_time_list[0].year) + '    ' + str(
            raw_time_list[0].month).rjust(2, ' ') \
                                                        + '    ' + str(raw_time_list[0].day).rjust(2, ' ') + '    ' \
                                                        + str(raw_time_list[0].hour).rjust(2, ' ') + '    ' + str(
            raw_time_list[0].minute).rjust(2, ' ') \
                                                        + '   ' + str(raw_time_list[0].second).rjust(2, ' ') + \
                                                        raw_header_record[time_of_first_obs_location][35:]
    if time_of_last_obs_location != '':
        raw_header_record[time_of_last_obs_location] = '  ' + str(raw_time_list[1].year) + '    ' + str(
            raw_time_list[1].month).rjust(2, ' ') \
                                                       + '    ' + str(raw_time_list[1].day).rjust(2, ' ') + '    ' \
                                                       + str(raw_time_list[1].hour).rjust(2, ' ') + '    ' + str(
            raw_time_list[1].minute).rjust(2, ' ') \
                                                       + '   ' + str(raw_time_list[1].second).rjust(2, ' ') + \
                                                       raw_header_record[time_of_last_obs_location][35:]

    raw_header_record_ = raw_header_record.copy()
    for i in range(len(raw_header_record_)-1, -1, -1):
        line_ = raw_header_record_[i]
        if "PRN / # OF OBS" in line_[60:]:
            del raw_header_record_[i]
        if '# OF SATELLITES' in line_[60:]:
            del raw_header_record_[i]

    time_extracted_list = raw_header_record_ + cut_raw_data_record
    return time_extracted_list
