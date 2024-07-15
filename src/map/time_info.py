import re
import datetime

def isFloat(x):
    """ if char to float """
    try:
        float(x)
        return True
    except ValueError:
        return False

def str2time(str_line):
    """ str to datetime """
    ep = str_line.split()
    if len(ep[0]) == 2:
        year = int(ep[0])
        if year <= 79:
            year += 2000
        else:
            year += 1900
    else:
        year = int(ep[0])

    month = int(ep[1])
    day = int(ep[2])
    hour = int(ep[3])
    minute = int(ep[4])
    sec = int(float(ep[5]))

    time = datetime.datetime(year, month, day, hour, minute, sec)
    return time

def obs_time(obsfile):
    # obsfile = 'E:/working/data_process/data/WUH200CHN_R_20220010000_01D_30S_MO.rnx'
    with open(obsfile, 'rt', encoding='gbk') as f:
        data = f.readlines()
    f.close()

    # Dfine variable
    H_first_time = None
    H_last_time = None
    interval = None

    for i in range(len(data)):
        if 'RINEX VERSION / TYPE' in data[i]:
            rinex_ver = float(data[i][0:10])
            rinex_type = data[i][20]

        elif 'INTERVAL' in data[i]:
            if isFloat(data[i][1:44]):
                interval = float(data[i][1:44])
            else:
                interval = None

        elif 'TIME OF FIRST OBS' in data[i]:
            H_first_time = str2time(data[i][0:43])

        elif 'TIME OF LAST OBS' in data[i]:
            H_last_time = str2time(data[i][0:43])

        elif 'END OF HEADER' in data[i]:
            if rinex_ver <= 2.99:
                first_time = str2time(data[i+1][0:0+27])
            else:
                first_time = str2time(data[i+1][2:2+27])
            break

    if H_first_time == None or H_last_time == None:
        for i in range(len(data)-1, -1, -1):
            try:
                last_time = str2time(re.findall(r'\s\d{2,4}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', data[i])[0])
                break
            except Exception as e:
                continue
    else:
        first_time = H_first_time
        last_time = H_last_time

    return first_time, last_time, interval

def obs_time_h(obsfile):
    # obsfile = 'E:/working/data_process/data/abpo0010.22o'
    with open(obsfile, 'rt', encoding='gbk') as f:
        data = f.read()
    f.close()
    data_ = data.split('\n')

    H_first_time = None
    H_last_time = None
    interval = None

    for i in range(len(data)):
        if 'RINEX VERSION / TYPE' in data_[i]:
            rinex_ver = float(data_[i][0:10])
            rinex_type = data_[i][20]

        elif 'INTERVAL' in data_[i]:
            if isFloat(data_[i][1:44]):
                interval = float(data_[i][1:44])
            else:
                interval = None

        elif 'TIME OF FIRST OBS' in data_[i]:
            H_first_time = str2time(data_[i][0:43])

        elif 'TIME OF LAST OBS' in data_[i]:
            H_last_time = str2time(data_[i][0:43])

        elif 'END OF HEADER' in data_[i]:
            if rinex_ver <= 2.99:
                first_time = str2time(data_[i+1][0:0+27])
            else:
                first_time = str2time(data_[i+1][2:2+27])
            break
    if H_first_time == None and H_last_time == None:
        if rinex_ver <= 2.99:
            Epoch = re.findall(r'\s\d{2}\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+\s{1,2}\d+.\d{7}', data)
        else:
            Epoch = re.findall(r'>\s\d{4}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}\s{1,2}\d{1,2}.\d{7}', data)
        first_time = str2time(Epoch[0][1:])
        last_time = str2time(Epoch[-1][1:])
    else:
        first_time = H_first_time
        last_time = H_last_time

    return first_time, last_time, interval