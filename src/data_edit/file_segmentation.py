#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Split files by equal observation time              * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
from datetime import *
import gnsscal
import re


def File_Segmentation_Function(input_file_path, cut_time_long):
    cut_time_long = float(cut_time_long)
    input_file_name = input_file_path.split('/')[-1]
    input_path = input_file_path.replace(input_file_name, '')
    with open(input_file_path, 'r') as f:
        raw_rinex_text_list = f.readlines()
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

    for i in raw_data_record:
        if len(i[:27].split()) > 5:
            first_time_list = i[:27].split()
            break
    for j in reversed(raw_data_record):
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
    first_time = datetime(start_year, start_month, start_day, start_hour, start_monter, start_second)
    last_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
    start_time_list = [first_time]
    test_judge = True
    while test_judge:
        first_time = first_time + timedelta(hours=cut_time_long)
        if first_time <= last_time:
            start_time_list.append(first_time)
        else:
            test_judge = False
    figure_letter_dic = {}
    for x, y in ((x + 1, chr(ord('a') + x)) for x in range(26)):
        figure_letter_dic.update({x: y})
    start_info_list01 = []
    for i in start_time_list:
        year_doy = gnsscal.date2yrdoy(i.date())
        add_list = (
            str(year_doy[0]), str(year_doy[1]).zfill(3), figure_letter_dic[int(i.hour) + 1]+str(i.minute).zfill(2), str(i.hour).zfill(2),
            str(i.minute).zfill(2))
        start_info_list01.append([i, add_list])
    marker_name = input_file_name[:4].lower()
    start_info_list02 = []

    try:
        version = float(str(raw_header_info[0][0])[4:10])
    except ValueError:
        version = None
    if version <= 2.99:
        for i in start_info_list01:
            new_file_name = marker_name + i[1][1] + i[1][2] + '.' + i[1][0][2:] + 'o'
            i.insert(0, new_file_name)
            start_info_list02.append(i)
    elif version > 2.99:
        for i in start_info_list01:
            new_file_name = input_file_name[:12] + i[1][0] + i[1][1] + i[1][3] + i[1][4] + '_' + str(int(cut_time_long)).zfill(2) + 'H' + input_file_name[27:]
            i.insert(0, new_file_name)
            start_info_list02.append(i)
    else:
        return

    cut_datetime_list = []
    if raw_data_record[0][0] == '>':
        for i in start_info_list02:
            cut_datetime = str(i[1].year)[2:] + str(i[1].month).zfill(2).rjust(3, ' ') + str(i[1].day).zfill(
                2).rjust(3, ' ') + str(
                i[1].hour).zfill(2).rjust(3, ' ') + str(i[1].minute).zfill(2).rjust(3, ' ') + str(
                i[1].second).rjust(3, ' ')
            cut_datetime_list.append(cut_datetime)
    else:
        for i in start_info_list02:
            cut_datetime = str(i[1].year)[2:] + str(i[1].month).rjust(3, ' ') + str(i[1].day).rjust(3, ' ') + str(
                i[1].hour).rjust(3, ' ') + str(i[1].minute).rjust(3, ' ') + str(i[1].second).rjust(3, ' ')
            cut_datetime_list.append(cut_datetime)
    num = 0
    record_num_list = []
    for i in cut_datetime_list:
        for j in raw_data_record[num:]:
            if re.search(r'\s\d{2}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', j) or re.search(r'>\s\d{4}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}.\d{7}', j):
                if version > 2.99:
                    time_a = [float(x) for x in i.split()]
                    time_b = [float(x) for x in j[4:].split()[0:6]]
                else:
                    time_a = [float(x) for x in i.split()]
                    time_b = [float(x) for x in j[1:].split()[0:6]]
                if time_a == time_b:
                    record_num_list.append(num)
                    break
            num += 1
    cut_raw_data_record = []
    for i, j in zip(range(len(record_num_list)), record_num_list):
        if i < (len(record_num_list) - 1):
            add_raw_data_record = raw_data_record[j: record_num_list[i + 1]]
            cut_raw_data_record.append(add_raw_data_record)
        elif i == (len(record_num_list) - 1):
            add_raw_data_record = raw_data_record[j:]
            cut_raw_data_record.append(add_raw_data_record)
    num = 0
    for i in cut_raw_data_record:
        for j in reversed(i):
            if len(j[:27].split()) > 5:
                last_time_list = j[:27].split()
                break
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
        last_time = datetime(last_year, last_month, last_day, last_hour, last_monter, last_second)
        start_info_list02[num].append(last_time)
        num += 1
    time_of_first_obs_location = ''
    time_of_last_obs_location = ''
    for i in raw_header_record:
        if 'TIME OF FIRST OBS' in i:
            time_of_first_obs_location = raw_header_record.index(i)
        elif 'TIME OF LAST OBS' in i:
            time_of_last_obs_location = raw_header_record.index(i)
    cut_raw_header_record = []
    for i in start_info_list02:
        if time_of_first_obs_location != '':
            raw_header_record[time_of_first_obs_location] = '  ' + str(i[1].year) + '    ' + str(i[1].month).rjust(2, ' ') \
                                                            + '    ' + str(i[1].day).rjust(2, ' ') + '    ' \
                                                            + str(i[1].hour).rjust(2, ' ') + '    ' + str(i[1].minute).rjust(2, ' ') \
                                                            + '   ' + str(i[1].second).rjust(2, ' ') + \
                                                            raw_header_record[time_of_first_obs_location][35:]
        if time_of_last_obs_location != '':
            raw_header_record[time_of_last_obs_location] = '  ' + str(i[3].year) + '    ' + str(i[3].month).rjust(2, ' ') \
                                                           + '    ' + str(i[3].day).rjust(2, ' ') + '    ' \
                                                           + str(i[3].hour).rjust(2, ' ') + '    ' + str(i[3].minute).rjust(2, ' ') \
                                                           + '   ' + str(i[3].second).rjust(2, ' ') + \
                                                           raw_header_record[time_of_last_obs_location][35:]

        raw_header_record_ = raw_header_record.copy()
        for j in range(len(raw_header_record[:])-1, -1, -1):
            line_ = raw_header_record_[j]
            if "PRN / # OF OBS" in line_[60:]:
                del raw_header_record_[j]
            if '# OF SATELLITES' in line_[60:]:
                del raw_header_record_[j]

        cut_raw_header_record.append(raw_header_record_[:])

    for i, j, k in zip(start_info_list02, cut_raw_header_record, cut_raw_data_record):
        out_file_path = input_path + i[0]
        with open(out_file_path, 'w', encoding='utf-8') as f:
            for header_data in j:
                f.write(str(header_data))
            for record_data in k:
                f.write(str(record_data))
