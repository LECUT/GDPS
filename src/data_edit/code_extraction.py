#-*- coding:utf-8 -*-
# ----------------------------------------------------------------
# *                                                             * |
# * History                                                     * |
# *   -1.0 Liang Qiao  2023-05-05 created                       * |
# *                                                             * |
# * Copyright (c) 2023, East China University of Technology.    * |
# *                     All rights reserved.                    * |
# *                                                             * |
# * Brief    Extract file data based on observation code        * |
# *                                                             * |
# * Author   Liang Qiao, East China University of Technology    * |
# * Date     2023-05-05                                         * |
# * Description     python 3.*                                  * |
# *                                                             * |
# ----------------------------------------------------------------
import re


def Code_Extraction_Function(input_file_content, ObservationCode_list):
    raw_rinex_text_list = input_file_content
    remove_type_of_observe_list = []
    test_judge = True
    type_of_observ_judge = True
    for i in range(len(raw_rinex_text_list)):
        line_text = raw_rinex_text_list[i].strip('\n')
        if '# / TYPES OF OBSERV' in line_text:
            test_judge = False
            if type_of_observ_judge:
                input_file_code_num = int(line_text[:10].strip())
                type_of_observ_judge = False
        if 'SYS / # / OBS TYPES' in line_text:
            test_judge = False
        if test_judge:
            remove_type_of_observe_list.append(raw_rinex_text_list[i])
        test_judge = True
        if 'END OF HEADER' in line_text:
            end_header_rows = i
            break
    raw_header_record = raw_rinex_text_list[:end_header_rows + 1]
    raw_data_record = raw_rinex_text_list[end_header_rows + 1:]
    type_of_observe_num = True
    raw_type_of_observe = []
    num = 0
    for deal_row in range(end_header_rows):
        add_dealed_list = []
        current_row_list = raw_rinex_text_list[deal_row].strip('\n')
        header_label = current_row_list[60:80].strip()
        if header_label == 'RINEX VERSION / TYPE':
            rinex_version = current_row_list[:10].strip()
        elif header_label == '# / TYPES OF OBSERV':  # version 1.x
            if type_of_observe_num:
                sys_obs_type_insert_num = num
                type_of_observe_num = False
            raw_type_of_observe.append(current_row_list)
        elif header_label == 'SYS / # / OBS TYPES':  # version 3.x~4.x
            if type_of_observe_num:
                sys_obs_type_insert_num = num
                type_of_observe_num = False
            raw_type_of_observe.append(current_row_list[:60])
        num += 1
    sys_obscode_list = []
    if raw_data_record[0][0] == '>':  # version 3.x~4.x
        raw_one_sys_obs_list = []  # [['G   18 C1C L1C D1C S1C C1W S1W    S2L C5Q L5Q D5Q S5Q          '], ...]
        for i in raw_type_of_observe:
            if i[0] != ' ':
                raw_one_sys_obs_list += [i]
            else:
                raw_one_sys_obs_list[-1] = raw_one_sys_obs_list[-1] + [i]
            if len(raw_one_sys_obs_list[-1]) != 1:
                temp_list = ''
                for j in raw_one_sys_obs_list[-1]:
                    temp_list += j
                raw_one_sys_obs_list[-1] = [temp_list]
        sys_obscode_list = []  # [['G', ['C1C', 'L1C']], ['R', ['C1C']]]
        for i in raw_one_sys_obs_list:
            temp_list = i[0].split()
            temp_list01 = temp_list[2:len(temp_list)]
            temp_list01.insert(0, temp_list[0])
            sys_obscode_list.append(temp_list01)
            pass
    else:  # version 2.x
        copy_raw_data_record = raw_data_record[:]
        list_copy_raw_data_record = iter(copy_raw_data_record)
        all_record_prn_list = []
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
        all_record_sys_list = [i[0] for i in all_record_prn_list]
        all_record_sys_list = list(set(all_record_sys_list))
        all_record_sys_list.sort()
        all_type_of_observe_code = []
        for one_row_of_type_observe in raw_type_of_observe:
            temp_type_of_observe_list = (one_row_of_type_observe.split('#')[0]).split()
            for one_observe_code in temp_type_of_observe_list:
                if len(one_observe_code) == 2:
                    if one_observe_code.isdigit():
                        pass
                    else:
                        all_type_of_observe_code.append(one_observe_code)
        for sys in all_record_sys_list:
            temp_list = all_type_of_observe_code[:]
            temp_list.insert(0, sys)
            sys_obscode_list.append(temp_list)
    if raw_data_record[0][0] == '>':  # version 3.x~4.x
        if len(ObservationCode_list) == 1:
            remove_type_of_observe_list[0] = remove_type_of_observe_list[0][:40] + ObservationCode_list[0][
                0] + '                   RINEX VERSION / TYPE\n'
        elif len(ObservationCode_list) > 1:
            remove_type_of_observe_list[0] = remove_type_of_observe_list[0][:40] + 'M                    RINEX VERSION / TYPE\n'
        temp_list = []
        for deal_list in ObservationCode_list:
            obscode_13cut_list = [deal_list[1:][i:i + 13] for i in
                                  range(0, len(deal_list[1:]), 13)]
            temp_judge = True
            for i in obscode_13cut_list:
                if temp_judge:
                    temp_line0 = deal_list[0] + ' ' * 3 + str(len(deal_list[1:])).rjust(2, ' ') + ' ' + ' '.join(i)
                    temp_line1 = temp_line0 + (60 - len(temp_line0)) * ' ' + 'SYS / # / OBS TYPES\n'
                    temp_judge = False
                else:
                    temp_line0 = ' ' * 7 + ' '.join(i)
                    temp_line1 = temp_line0 + (60 - len(temp_line0)) * ' ' + 'SYS / # / OBS TYPES\n'
                temp_list.append(temp_line1)
            pass
        pass
    else:  # version 2.x
        temp_sys_list = []
        temp_code_list = []
        for i in ObservationCode_list:
            temp_sys_list.append(i[0])
            temp_code_list.extend(i[1:])
        temp_code_list = list(set(temp_code_list))
        temp_code_list.sort()
        deal_list = [temp_sys_list, temp_code_list]
        if len(deal_list[0]) == 1:
            remove_type_of_observe_list[0] = remove_type_of_observe_list[0][:40] + deal_list[0][0] + '                   RINEX VERSION / TYPE'
        elif len(deal_list[0]) > 1:
            remove_type_of_observe_list[0] = remove_type_of_observe_list[0][:40] + 'M                    RINEX VERSION / TYPE'
        obscode_9cut_list = [deal_list[1][i:i + 9] for i in range(0, len(deal_list[1]), 9)]
        temp_list = []
        temp_judge = True
        for i in obscode_9cut_list:
            if temp_judge:
                temp_line0 = ' ' * 4 + str(len(deal_list[1])).rjust(2, ' ') + ' ' * 4 + '    '.join(i)
                temp_line1 = temp_line0 + (60 - len(temp_line0)) * ' ' + '# / TYPES OF OBSERV\n'
                temp_judge = False
            else:
                temp_line0 = ' ' * 10 + '    '.join(i)
                temp_line1 = temp_line0 + (60 - len(temp_line0)) * ' ' + '# / TYPES OF OBSERV\n'
            temp_list.append(temp_line1)
        pass
    for i in reversed(temp_list):
        remove_type_of_observe_list.insert(sys_obs_type_insert_num, i)
    copy_raw_data_record_02 = raw_data_record[:]
    extracted_data_record_list = []
    iter_data_record_list = iter(copy_raw_data_record_02)
    if raw_data_record[0][0] == '>':
        extrect_code_location = []
        for extrect_list in ObservationCode_list:
            for inherent_list in sys_obscode_list:
                if extrect_list[0] == inherent_list[0]:
                    temp_list = [extrect_list[0]]
                    for obs_code in extrect_list[1:]:
                        if obs_code in inherent_list:
                            temp_list.append(inherent_list.index(obs_code) - 1)
                    extrect_code_location.append(temp_list)
        extrect_code_location_dic = {}
        for i in extrect_code_location:
            extrect_code_location_dic[i[0]] = i[1:]
        for line in iter_data_record_list:
            if len(line[:32].split()) == 8:
                time_PRNnum_line = line
                moment_prn_num = int(line[32:35].strip())
                moment_prn_data_list = []
                sys_obscode_num_dic = {}
                for sys in ObservationCode_list:
                    sys_obscode_num_dic[sys[0]] = len(sys[1:])
                temp_list = []
                while moment_prn_num > 0:
                    moment_prn_data_line = next(iter_data_record_list).split('\n')[0]
                    if moment_prn_data_line[0] in extrect_code_location_dic.keys():
                        standard_long = 3 + 16 * int(sys_obscode_num_dic[moment_prn_data_line[0]])
                        standard_moment_prn_data_line = moment_prn_data_line + ' ' * (
                                standard_long - len(moment_prn_data_line))
                        add_line = moment_prn_data_line[:3]
                        for code_location in extrect_code_location_dic[moment_prn_data_line[0]]:
                            start_location = 3 + code_location * 16
                            end_location = 3 + code_location * 16 + 16
                            add_line += standard_moment_prn_data_line[start_location:end_location]
                        add_line += '\n'
                        temp_list.append(add_line.lstrip())
                    moment_prn_num -= 1
                new_time_PRNnum_line = time_PRNnum_line[:32] + str(len(temp_list)).rjust(3, ' ') + '\n'
                extracted_data_record_list.append(new_time_PRNnum_line)
                for new_data_record in temp_list:
                    extracted_data_record_list.append(new_data_record)
            pass
        pass
    else:  # version 2.x
        temp_sys_list = []
        temp_code_list = []
        for i in ObservationCode_list:
            temp_sys_list.append(i[0])
            temp_code_list.extend(i[1:])
        temp_code_list = list(set(temp_code_list))
        temp_code_list.sort()
        deal_ObservationCode_list = [temp_sys_list,
                                     temp_code_list]
        extrect_code_location = [deal_ObservationCode_list[0], []]
        for extrect_obs_code in deal_ObservationCode_list[1]:
            if extrect_obs_code in sys_obscode_list[0][1:]:
                extrect_code_location[1].append(sys_obscode_list[0].index(extrect_obs_code) - 1)
        moment_satellite_max_num = 12
        for line in iter_data_record_list:
            if len(line[:32].split()) == 8:
                record_all_satellite_list = ''
                the_moment_site_satellite_num = int(line[30:32])
                record_all_satellite_list += line[32:].split('\n')[0]
                record_all_satellite_list = "".join(re.findall('[A-Z]..', record_all_satellite_list)).replace(' ',  '0')
                divisible_moment_satellite = the_moment_site_satellite_num % moment_satellite_max_num
                if divisible_moment_satellite == 0:
                    record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num - 1
                else:
                    record_satellite_row = the_moment_site_satellite_num // moment_satellite_max_num
                skip_record_num_2 = record_satellite_row
                while skip_record_num_2 > 0:
                    record_all_satellite_list += str(next(iter_data_record_list).split('\n')[0].strip()).replace(' ', '0')
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
                    one_PRN_recode_line = ''
                    while record_satellite_row > 0:
                        temp_PRN_line_info = next(iter_data_record_list).split('\n')[0]
                        temp_PRN_line_info = temp_PRN_line_info + ' ' * (80 - len(temp_PRN_line_info))  # ' '
                        one_PRN_recode_line += temp_PRN_line_info
                        record_satellite_row -= 1
                    satellite_observe_data_list.append(one_PRN_recode_line)
                extract_data_list = []
                for raw_data_line in satellite_observe_data_list:
                    extract_data_line = ''
                    for extract_location in extrect_code_location[1]:
                        start_location = extract_location * 16
                        end_location = extract_location * 16 + 16
                        extract_data_line += raw_data_line[start_location:end_location]
                    extract_data_list.append(extract_data_line)
                temp_num = 0
                extract_prn = []
                delete_prn_location_list = []
                for prn in record_all_satellite_list:
                    if prn[0] in extrect_code_location[0]:
                        extract_prn.append(prn)
                    else:
                        delete_prn_location_list.append(temp_num)
                    temp_num += 1
                div_12prn_list = [extract_prn[i:i + 12] for i in range(0, len(extract_prn), 12)]  # a group of 12
                first_line_judge = True
                for i in div_12prn_list:
                    if first_line_judge:
                        temp_time_prn = line[:30] + str(len(extract_prn)) + ''.join(i) + '\n'
                        first_line_judge = False
                    else:
                        temp_time_prn = ' ' * 32 + ''.join(i) + '\n'
                    extracted_data_record_list.append(temp_time_prn)
                for delete_num in reversed(delete_prn_location_list):
                    extract_data_list.pop(delete_num)
                for long_text in extract_data_list:
                    div_80_list = [long_text[i:i + 80] for i in range(0, len(long_text), 80)]  # a group of 12
                    for one_row_text in div_80_list:
                        temp_row_text = one_row_text.rstrip() + '\n'
                        extracted_data_record_list.append(temp_row_text)
                    pass
                pass
    extracted_content = remove_type_of_observe_list + extracted_data_record_list
    return extracted_content
