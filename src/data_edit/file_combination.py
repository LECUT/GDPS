#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Splicing multiple files into a single file         * |
#             in chronological order                            * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import datetime
import math
import re

def File_Combination_Function(input_file_path_list):
    all_info_list = []
    try:
        input_file_path_list.remove('/')
    except ValueError:
        pass

    raw_GLONASS_SLOT = []
    for one_input_path in input_file_path_list:
        with open(one_input_path, 'r') as f:
            raw_rinex_text_list = f.readlines()
        raw_header_info = []
        for i in range(len(raw_rinex_text_list)):
            line_text = raw_rinex_text_list[i].strip('\n')
            temp_info_list = [line_text[:60], line_text[60:]]
            raw_header_info = raw_header_info + [temp_info_list]
            if 'GLONASS SLOT / FRQ #' in line_text:
                raw_GLONASS_SLOT.append([line_text[0:4], list(filter(str.strip, [line_text[i:i+7] for i in range(4, 60-7, 7)])), line_text[60:]])
            if 'END OF HEADER' in line_text:
                end_header_rows = i
                break
        raw_header_record = raw_rinex_text_list[:end_header_rows + 1]
        raw_data_record = raw_rinex_text_list[end_header_rows + 1:]
        for i in raw_header_info:
            if i[1].strip() == 'RINEX VERSION / TYPE':
                RINEX_version = i[0][:10].strip()
            elif i[1].strip() == 'MARKER NAME':
                Station_name = i[0][:10].strip()


        ture_judge = True
        for i in raw_data_record:
            if re.search(r'\s\d{2}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', i) or re.search(r'>\s\d{4}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}.\d{7}', i):
                if ture_judge:
                    first_time_list = i[:27].split()
                    ture_judge = False
                else:
                    second_time_list = i[:27].split()
                    break
        for i in reversed(raw_data_record):
            if re.search(r'\s\d{2}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', i) or re.search(r'>\s\d{4}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}.\d{7}', i):
                end_time_list = i[:27].split()
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
            second_year = 2000 + int(second_time_list[0])
            second_month = int(second_time_list[1])
            second_day = int(second_time_list[2])
            second_hour = int(second_time_list[3])
            second_monter = int(second_time_list[4])
            second_second = int(float(second_time_list[5]))
        else:
            second_year = int(second_time_list[1])
            second_month = int(second_time_list[2])
            second_day = int(second_time_list[3])
            second_hour = int(second_time_list[4])
            second_monter = int(second_time_list[5])
            second_second = int(float(second_time_list[6]))
        if len(end_time_list[0]) == 2:
            last_year = 2000 + int(end_time_list[0])
            last_month = int(end_time_list[1])
            last_day = int(end_time_list[2])
            last_hour = int(end_time_list[3])
            last_monter = int(end_time_list[4])
            last_second = int(float(end_time_list[5]))
        else:
            last_year = int(end_time_list[1])
            last_month = int(end_time_list[2])
            last_day = int(end_time_list[3])
            last_hour = int(end_time_list[4])
            last_monter = int(end_time_list[5])
            last_second = int(float(end_time_list[6]))
        first_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
        second_time = datetime(second_year, second_month, second_day, second_hour, second_monter, second_second)
        end_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
        interval = (second_time - first_time)
        all_info_list.append([one_input_path, [RINEX_version, Station_name, interval, first_time, end_time]])

    if len(raw_GLONASS_SLOT) > 0:
        GLONASS_Slot_tmp = []
        for i in range(len(input_file_path_list)):
            GLONASS_Slot_tmp.extend(raw_GLONASS_SLOT[i][1])
        GLONASS_Slot_repeat = list(set(GLONASS_Slot_tmp))
        GLONASS_Slot = []
        n = math.ceil(len(GLONASS_Slot_repeat)/8)
        tmp = ''.join(GLONASS_Slot_repeat).ljust(56*n)
        for i in range(n):
            tmp_ = tmp[56*i:56*(i+1)]
            if i == 0:
                line_slot = ' '+ str(len(GLONASS_Slot_repeat)) + ' ' + tmp_ + 'GLONASS SLOT / FRQ #' + '\n'
            else:
                line_slot = '  ' + '  ' + tmp_ + 'GLONASS SLOT / FRQ #' + '\n'
            GLONASS_Slot.append(line_slot)

    record_one_version = []
    record_one_station = []
    record_one_interval = []
    for i in all_info_list:
        if i[1][0] not in record_one_version:
            record_one_version.append(i[1][0])
        if i[1][1] not in record_one_station:
            record_one_station.append(i[1][1])
        if i[1][2] not in record_one_interval:
            record_one_interval.append(i[1][2])
    if len(record_one_version) != 1:
        print('Version number is inconsistent')
        return
    if len(record_one_station) != 1:
        print('The station names are inconsistent')
        return

    all_info_list.sort(key=lambda x: x[1][3])
    first_time = all_info_list[0][1][3]
    last_time = all_info_list[-1][1][4]
    with open(all_info_list[0][0], 'r') as f:
        raw_rinex_text_list = f.readlines()
    raw_header_info = []
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    raw_header_record = raw_rinex_text_list[:end_header_rows + 1]
    time_of_first_obs_location = ''
    time_of_last_obs_location = ''
    for i in raw_header_record:
        if 'TIME OF FIRST OBS' in i:
            time_of_first_obs_location = raw_header_record.index(i)
        elif 'TIME OF LAST OBS' in i:
            time_of_last_obs_location = raw_header_record.index(i)
    if time_of_first_obs_location != '':
        raw_header_record[time_of_first_obs_location] = '  ' + str(first_time.year) + '    ' + str(
            first_time.month).rjust(2, ' ') \
                                                        + '    ' + str(first_time.day).rjust(2, ' ') + '    ' \
                                                        + str(first_time.hour).rjust(2, ' ') + '    ' + str(
            first_time.minute).rjust(2, ' ') \
                                                        + '   ' + str(first_time.second).rjust(2, ' ') + \
                                                        raw_header_record[time_of_first_obs_location][35:]
    if time_of_last_obs_location != '':
        raw_header_record[time_of_last_obs_location] = '  ' + str(last_time.year) + '    ' + str(
            last_time.month).rjust(2, ' ') \
                                                       + '    ' + str(last_time.day).rjust(2, ' ') + '    ' \
                                                       + str(last_time.hour).rjust(2, ' ') + '    ' + str(
            last_time.minute).rjust(2, ' ') \
                                                       + '   ' + str(last_time.second).rjust(2, ' ') + \
                                                       raw_header_record[time_of_last_obs_location][35:]
    raw_header_record_ = raw_header_record.copy()
    if len(raw_GLONASS_SLOT) > 0:
        GLONASS_Slot_location = ''
        for i in range(len(raw_header_record_)-1, -1, -1):
            line_ = raw_header_record_[i]
            if "PRN / # OF OBS" in line_[60:]:
                del raw_header_record_[i]
            if '# OF SATELLITES' in line_[60:]:
                del raw_header_record_[i]
            if 'GLONASS SLOT / FRQ #' in line_:
                GLONASS_Slot_location = raw_header_record_.index(line_)
                del raw_header_record_[i]

        # raw_header_record_ = list(reversed(raw_header_record_))
        if GLONASS_Slot_location != '':
            raw_header_record_[GLONASS_Slot_location:GLONASS_Slot_location] = GLONASS_Slot

    all_data_record_list = []
    for one_input_path in all_info_list:
        with open(one_input_path[0], 'r') as f:
            raw_rinex_text_list = f.readlines()
        for i in range(len(raw_rinex_text_list)):
            line_text = raw_rinex_text_list[i].strip('\n')
            if 'END OF HEADER' in line_text:
                end_header_rows = i
                break
        all_data_record_list.extend(raw_rinex_text_list[end_header_rows + 1:])
    combination_list = raw_header_record_ + all_data_record_list
    return combination_list

