from .rtkcmn import epoch2time, isFloat, uGNSS
import numpy as np
from .sat_column import GNSS_col
import copy

import warnings
warnings.filterwarnings(action='ignore', message='Mean of empty slice')

def str2time(str_line):
    """ UTC to GPST """
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
    sec = float(ep[5])

    toc = epoch2time([year, month, day, hour, minute, sec])
    return toc


def cut(obj, sec, num):
    """ 数据信息转换 """
    obj = obj.replace('D', 'E')
    data = np.zeros(num)
    k = 0
    for i in range(0, len(obj), sec):
        k = k + 1
        if isFloat(obj[i:i+sec]):
            data[k-1] = float(obj[i:i+sec])
        # else:
        #     data[k-1] = 0.0
        if k >= num:
            break
    return data

def line2buff(line, MAXRNXLEN):
    line_del = line.replace('\n', '').replace('\r', '')  # delete line breaks
    buff = ' '*MAXRNXLEN
    buff = list(buff)
    buff[0:len(line_del)] = line_del
    buff = ''.join(buff)
    return buff

def uraindex(value):
    import numpy as np
    ura_eph = np.array([2.4, 3.4, 4.85, 6.85, 9.65, 13.65, 24.0, 48.0, 96.0, 192.0, 384.0, 768.0, 1536.0, 3072.0, 6144.0, 0.0])
    for i in range(16):
        if ura_eph[i] >= value:
            ind = i
            break
    return i

def sisa_index(value):
    if value < 0.0 or value > 6.0:
        ind = 255
        return ind
    elif value <= 0.5:
        ind = np.fix(value/0.01)
        return ind
    elif value <= 1:
        ind = np.fix((value-0.5)/0.02)+50
        return ind
    elif value <= 2:
        ind = np.fix((value-1.0)/0.04)+75
        return ind
    else:
        ind = np.fix(np.fix(value-2.0)/0.16+100)
        return ind

# detect continuous time period
# Interval discontinuity is not considered
def arc_dtr(data, sta, epoch, cfg):
    # data = mw + gfl
    st = np.zeros([data.shape[0], 1])
    new_st = st
    all_mg = data.copy()
    new_st[~np.isnan(all_mg)] = 1
    row = np.where(new_st == 1)
    row = np.array(row)[0]
    brk = np.where(np.diff(row) != 1)
    brk = np.array(brk)[0]
    frs = np.hstack((np.array([0]), brk+1))
    lst = np.hstack((brk, np.array([len(row)-1])))
    als = np.vstack((frs, lst)).T
    als_ = als.copy()
    if als_.shape[0] > 1:
        for t in range(als_.shape[0]-1, -1, -1):
            if (als_[t, 1] - als_[t, 0]) < cfg.short_limit():
                als_ = np.delete(als_, (t), axis=0)
    else:
        if row.size != 0:
            if (als_[0, 1]-als_[0, 0]) < cfg.short_limit():
                als_ = np.delete(als_, (0), axis=0)
    als = als_
    arn = np.full([als.shape[0], 2], np.nan)
    if np.all(lst == 0) or lst.size == 0 or row.size == 0:
        ark = arn
    else:
        for j in range(als.shape[0]):
            arn[j, 0] = row[als[j, 0]]
            arn[j, 1] = row[als[j, 1]]
        ark = arn
    return ark

# detect continuous time period
# Interval discontinuity is considered
def arc_dtr_h(data, sta, epoch, cfg):
    # data = mw + gfl
    epoch_ = np.array(epoch)
    epoch_ep = np.abs(np.diff(epoch_ - epoch_[0])) - sta.interval
    J = np.where(epoch_ep > 0.001)[0]

    st = np.zeros([data.shape[0], 1])
    new_st = st
    all_mg = data.copy()
    new_st[~np.isnan(all_mg)] = 1
    row = np.where(new_st == 1)
    row = np.array(row)[0]
    brk = np.where(np.diff(row) != 1)
    brk = np.array(brk)[0]
    frs = np.hstack((np.array([0]), brk+1))
    lst = np.hstack((brk, np.array([len(row)-1])))
    als = np.vstack((frs, lst)).T
    als_ = als.copy()
    if als_.shape[0] > 1:
        for t in range(als_.shape[0]-1, -1, -1):
            if (als_[t, 1] - als_[t, 0]) < cfg.short_limit():
                als_ = np.delete(als_, (t), axis=0)
    else:
        if row.size != 0:
            if (als_[0, 1]-als_[0, 0]) < cfg.short_limit():
                als_ = np.delete(als_, (0), axis=0)
    als = als_
    arn = np.full([als.shape[0], 2], np.nan)
    if np.all(lst == 0) or lst.size == 0 or row.size == 0:
        ark = arn
    else:
        for j in range(als.shape[0]):
            arn[j, 0] = row[als[j, 0]]
            arn[j, 1] = row[als[j, 1]]
        ark = arn
    arc = ark.copy()

    if len(J) > 0:
        DSR = 0
        for j in range(len(J)):
            for t in range(DSR, ark.shape[0]):
                st = ark[t, 0]
                fn = ark[t, 1]
                if J[j] > st and J[j] < fn:
                    if t == 0:
                        ark = np.vstack(np.array([st, J[j]], [J[j]+1, fn]), ark[1:, :])
                        break
                    else:
                        ark = np.vstack(ark[0:t-1, :], np.array([st, J[j]], [J[j]+1, fn]), ark[t+1:, :])
                        DSR = t + 1
                        break
        ark_ = ark.copy()
        LS = np.where((ark[:, 1]-ark[:, 0])<cfg.short_limit())[0]
        if len(LS) > 0:
            for t in range(len(LS)-1, -1, -1):
                ark_ = np.delete(ark_, (t), axis=0)
        arc = ark_.copy()
    return arc

# Interval discontinuity is considered
# considered cycle jump
def arc_dtr_h1(data, sta, epoch, slip, cfg):
    # data = mw + gfl
    epoch_ = np.array(epoch)
    epoch_ep = np.abs(np.diff(epoch_ - epoch_[0])) - sta.interval
    J = np.where(epoch_ep > 0.001)[0].astype(int)
    S = np.where(slip > 0)[0]

    st = np.zeros([data.shape[0], 1])
    new_st = st
    all_mg = data.copy()
    new_st[~np.isnan(all_mg)] = 1
    row = np.where(new_st == 1)
    row = np.array(row)[0]
    brk = np.where(np.diff(row) != 1)
    brk = np.array(brk)[0]
    frs = np.hstack((np.array([0]), brk+1))
    lst = np.hstack((brk, np.array([len(row)-1])))
    als = np.vstack((frs, lst)).T
    als_ = als.copy()
    if als_.shape[0] > 1:
        for t in range(als_.shape[0]-1, -1, -1):
            if (als_[t, 1] - als_[t, 0]) < cfg.short_limit():
                als_ = np.delete(als_, (t), axis=0)
    else:
        if row.size != 0:
            if (als_[0, 1]-als_[0, 0]) < cfg.short_limit():
                als_ = np.delete(als_, (0), axis=0)
    als = als_
    arn = np.full([als.shape[0], 2], np.nan)
    if np.all(lst == 0) or lst.size == 0 or row.size == 0:
        ark = arn
    else:
        for j in range(als.shape[0]):
            arn[j, 0] = row[als[j, 0]]
            arn[j, 1] = row[als[j, 1]]
        ark = arn
    arc = ark.copy().astype(int)

    if len(J) > 0:
        DSR = 0
        for j in range(len(J)):
            for t in range(DSR, ark.shape[0]):
                st = ark[t, 0]
                fn = ark[t, 1]
                if J[j] > st and J[j] < fn:
                    if t == 0:
                        ark = np.vstack((np.array([(st, J[j]), (J[j]+1, fn)]), ark[1:, :]))
                        break
                    else:
                        try:
                            ark = np.vstack((ark[0:t, :], np.array([(st, J[j]), (J[j]+1, fn)]), ark[t+1:, :]))
                        except Exception as e:
                            print(e)
                        DSR = t + 1
                        break
        ark_ = ark.copy()
        LS = np.where((ark[:, 1]-ark[:, 0])<cfg.short_limit())[0]
        if len(LS) > 0:
            for t in range(len(LS)-1, -1, -1):
                ark_ = np.delete(ark_, LS[t], axis=0)
        arc = ark_.copy().astype(int)

    # week cycle
    ark_s = arc.copy().astype(int)
    if len(S) > 0:
        DSR = 0
        for j in range(len(S)):
            for t in range(DSR, ark_s.shape[0]):
                st = ark_s[t, 0]
                fn = ark_s[t, 1]
                if S[j] > st and S[j] < fn:
                    if t == 0:
                        ark_s = np.vstack((np.array([(st, S[j]-1), (S[j], fn)]), ark_s[1:, :]))
                        break
                    else:
                        ark_s = np.vstack((ark_s[0:t, :], np.array([(st, S[j]-1), (S[j], fn)]), ark_s[t+1:, :]))
                        DSR = t + 1
                        break
                elif fn == S[j]:
                    if t == 0:
                        ark_s = np.vstack((np.array([(st, S[j]-1), (S[j], fn)]), ark_s[1:, :]))
                        break
                    else:
                        ark_s = np.vstack((ark_s[0:t, :], np.array([(st, S[j]-1), (S[j], fn)]), ark_s[t+1:, :]))
                        DSR = t + 1
                        break
        ark_s_ = ark_s.copy()
        LS = np.where((ark_s_[:, 1]-ark_s_[:, 0])<cfg.short_limit())[0]
        if len(LS) > 0:
            for t in range(len(LS)-1, -1, -1):
                ark_s_ = np.delete(ark_s_, LS[t], axis=0)
        arc = ark_s_.copy().astype(int)

    return arc

# window model 1
def lomp(mp):
    b = 0
    k = 0
    n = 0
    mp_ = mp.copy()
    THRES_SLIP = 2
    for j in range(len(mp)):
        if abs(mp[j] - b) > THRES_SLIP:
            if j > 0:
                for ktmp in range(k, j):
                    mp_[ktmp] = mp_[ktmp] - b
            b = mp_[j]
            n = 1
            k = j
        else:
            n = n + 1
            b = b + (mp_[j] - b)/n
    if n > 0:
        for ktmp in range(k, j+1):
            mp_[ktmp] = mp_[ktmp] - b
    return mp_

# window model 2
def lomp_h(mp):
    mp_ = mp.copy()
    z_mp = np.zeros(len(mp_))
    THRES_SLIP = 2
    b = 0 # mp mean
    k = 0
    for j in range(len(mp_)):
        if j-k < 50:
            if j-k == 0:
                z_mp[j] = mp_[j] - np.mean(mp_[j])
                if abs(mp_[j] - b) > THRES_SLIP:
                    k = j
                b = np.mean(mp_[j])
            else:
                if abs(mp_[j] - b) > THRES_SLIP:
                    k = j
                z_mp[k:j+1] = mp_[k:j+1] - np.mean(mp_[k:j+1])
                b = np.mean(mp_[k:j+1])
        else:
            if abs(mp_[j] - b) > THRES_SLIP:
                k = j
                b = np.mean(mp_[j])
                continue
            z_mp[j] = mp_[j] - np.mean(mp_[j-49:j+1])
            b = np.mean(mp_[j-49:j+1])
    return z_mp


# window model 1
def logfif(gfif):
    b = 0
    k = 0
    n = 0
    gfif_ = gfif.copy()
    THRES_SLIP = 0.1
    for j in range(len(gfif)):
        if abs(gfif[j] - b) > THRES_SLIP:
            if j > 0:
                for ktmp in range(k, j):
                    gfif_[ktmp] = gfif_[ktmp] - b
            b = gfif_[j]
            n = 1
            k = j
        else:
            n = n + 1
            b = b + (gfif_[j] - b)/n
    if n > 0:
        for ktmp in range(k, j+1):
            gfif_[ktmp] = gfif_[ktmp] - b
    return gfif_

# window model 2
def logfif_h(gfif):
    gfif_ = gfif.copy()
    z_gfif = np.zeros(len(gfif_))
    THRES_SLIP = 0.1
    b = 0 # mp mean
    k = 0
    for j in range(len(gfif_)):
        if j-k < 50:
            if j-k == 0:
                z_gfif[j] = gfif_[j]-np.mean(gfif_[j])
                if abs(gfif_[j] - b) > THRES_SLIP:
                    k = j
                b = np.mean(gfif_[j])
            else:
                if abs(gfif_[j] - b) > THRES_SLIP:
                    k = j
                z_gfif[k:j+1] = gfif_[k:j+1] - np.mean(gfif_[k:j+1])
                b = np.mean(gfif_[k:j+1])
        else:
            if abs(gfif_[j] - b) > THRES_SLIP:
                k = j
                b = np.mean(gfif_[j])
                continue
            z_gfif[j] = gfif_[j] - np.mean(gfif_[j-49:j+1])
            b = np.mean(gfif_[j-49:j+1])
    return z_gfif


def calcsThres_h(sample):
    # sample = sta.sample
    if sample > 0.0:
        # GF
        if sample <= 1.0:
            csThresGF = 0.05
        elif sample <= 20.0:
            csThresGF = 0.10/20.0*sample+0.05
        elif sample <=60.0:
            csThresGF = 0.15
        elif sample <= 100.0:
            csThresGF = 0.25
        else:
            csThresGF = 0.35
        #MW
        if sample <= 1.0:
            csThresMW = 2.5
        elif sample <= 20.0:
            csThresMW = 2.5/20.0*sample + 2.5
        elif sample <= 60.0:
            csThresMW = 5.0
        else:
            csThresMW = 7.5
    else:
        csThresGF = 0.15
        csThresMW = 5.0
    return csThresGF, csThresMW


def calcsThres(sample):
    # sample = sta.sample
    if sample > 0.0:
        # GF
        if sample <= 1.0:
            csThresGF = 0.05
        elif sample <= 15.0:
            csThresGF = 0.10
        else:
            csThresGF = 0.15
        #MW
        if sample <= 1.0:
            csThresMW = 1.0
        elif sample <= 15.0:
            csThresMW = 1.5
        else:
            csThresMW = 2
    else:
        csThresGF = 0.15
        csThresMW = 2
    return csThresGF, csThresMW

def cal_sat_sys_m(data, cal_type): # data matrix N*N*N of frquency
    if cal_type == 'mean':
        L1 = np.nanmean(data[:, :, 0], axis=1).reshape((data.shape[0], 1))
        L2 = np.nanmean(data[:, :, 1], axis=1).reshape((data.shape[0], 1))
        L3 = np.nanmean(data[:, :, 2], axis=1).reshape((data.shape[0], 1))
        L4 = np.nanmean(data[:, :, 3], axis=1).reshape((data.shape[0], 1))
        L5 = np.nanmean(data[:, :, 4], axis=1).reshape((data.shape[0], 1))
        L6 = np.nanmean(data[:, :, 5], axis=1).reshape((data.shape[0], 1))
        L7 = np.nanmean(data[:, :, 6], axis=1).reshape((data.shape[0], 1))
        data_sat = np.hstack((L1, L2, L3, L4, L5, L6, L7))
        data_sys = np.full([uGNSS.GNSSMAX, data.shape[2]], np.nan)
        data_sys[uGNSS.GPS] = np.nanmean(data_sat[GNSS_col.GPS[0]:GNSS_col.GPS[1], :], axis=0).reshape((1, data.shape[2]))
        data_sys[uGNSS.GLO] = np.nanmean(data_sat[GNSS_col.GLO[0]:GNSS_col.GLO[1], :], axis=0).reshape((1, data.shape[2]))
        data_sys[uGNSS.GAL] = np.nanmean(data_sat[GNSS_col.GAL[0]:GNSS_col.GAL[1], :], axis=0).reshape((1, data.shape[2]))
        data_sys[uGNSS.QZS] = np.nanmean(data_sat[GNSS_col.QZS[0]:GNSS_col.QZS[1], :], axis=0).reshape((1, data.shape[2]))
        data_sys[uGNSS.BDS] = np.nanmean(data_sat[GNSS_col.BDS[0]:GNSS_col.BDS[1], :], axis=0).reshape((1, data.shape[2]))
        data_sys[uGNSS.IRN] = np.nanmean(data_sat[GNSS_col.IRN[0]:GNSS_col.IRN[1], :], axis=0).reshape((1, data.shape[2]))
        data_sys[uGNSS.SBS] = np.nanmean(data_sat[GNSS_col.SBS[0]:GNSS_col.SBS[1], :], axis=0).reshape((1, data.shape[2]))
    elif cal_type == 'rms':
        L1 = np.sqrt(np.nanmean(np.square(data[:, :, 0]), axis=1)).reshape((data.shape[0], 1))
        L2 = np.sqrt(np.nanmean(np.square(data[:, :, 1]), axis=1)).reshape((data.shape[0], 1))
        L3 = np.sqrt(np.nanmean(np.square(data[:, :, 2]), axis=1)).reshape((data.shape[0], 1))
        L4 = np.sqrt(np.nanmean(np.square(data[:, :, 3]), axis=1)).reshape((data.shape[0], 1))
        L5 = np.sqrt(np.nanmean(np.square(data[:, :, 4]), axis=1)).reshape((data.shape[0], 1))
        L6 = np.sqrt(np.nanmean(np.square(data[:, :, 5]), axis=1)).reshape((data.shape[0], 1))
        L7 = np.sqrt(np.nanmean(np.square(data[:, :, 6]), axis=1)).reshape((data.shape[0], 1))
        data_sat = np.hstack((L1, L2, L3, L4, L5, L6, L7))
        data_sys = np.full([uGNSS.GNSSMAX, data.shape[2]], np.nan)
        data_sys[uGNSS.GPS] = np.nanmean(data_sat[GNSS_col.GPS[0]:GNSS_col.GPS[1], :], axis=0)
        data_sys[uGNSS.GLO] = np.nanmean(data_sat[GNSS_col.GLO[0]:GNSS_col.GLO[1], :], axis=0)
        data_sys[uGNSS.GAL] = np.nanmean(data_sat[GNSS_col.GAL[0]:GNSS_col.GAL[1], :], axis=0)
        data_sys[uGNSS.QZS] = np.nanmean(data_sat[GNSS_col.QZS[0]:GNSS_col.QZS[1], :], axis=0)
        data_sys[uGNSS.BDS] = np.nanmean(data_sat[GNSS_col.BDS[0]:GNSS_col.BDS[1], :], axis=0)
        data_sys[uGNSS.IRN] = np.nanmean(data_sat[GNSS_col.IRN[0]:GNSS_col.IRN[1], :], axis=0)
        data_sys[uGNSS.SBS] = np.nanmean(data_sat[GNSS_col.SBS[0]:GNSS_col.SBS[1], :], axis=0)
    return data_sat, data_sys


def cal_sat_sys(data, cal_type): # data matrix N*N*N
    if cal_type == 'mean':
        data_sat = data
        data_sys = np.full([uGNSS.GNSSMAX, data.shape[1]], np.nan)
        data_sys[uGNSS.GPS] = np.nanmean(data_sat[GNSS_col.GPS[0]:GNSS_col.GPS[1], :], axis=0)
        data_sys[uGNSS.GLO] = np.nanmean(data_sat[GNSS_col.GLO[0]:GNSS_col.GLO[1], :], axis=0)
        data_sys[uGNSS.GAL] = np.nanmean(data_sat[GNSS_col.GAL[0]:GNSS_col.GAL[1], :], axis=0)
        data_sys[uGNSS.QZS] = np.nanmean(data_sat[GNSS_col.QZS[0]:GNSS_col.QZS[1], :], axis=0)
        data_sys[uGNSS.BDS] = np.nanmean(data_sat[GNSS_col.BDS[0]:GNSS_col.BDS[1], :], axis=0)
        data_sys[uGNSS.IRN] = np.nanmean(data_sat[GNSS_col.IRN[0]:GNSS_col.IRN[1], :], axis=0)
        data_sys[uGNSS.SBS] = np.nanmean(data_sat[GNSS_col.SBS[0]:GNSS_col.SBS[1], :], axis=0)
    elif cal_type == 'rms':
        data_sat = np.sqrt(np.nanmean(np.square(data[:, :]), axis=0))
        data_sat = data_sat.reshape((len(data_sat), 1))
        data_sys = np.full([uGNSS.GNSSMAX, 1], np.nan)
        data_sys[uGNSS.GPS, 0] = np.nanmean(data_sat[GNSS_col.GPS[0]:GNSS_col.GPS[1], :], axis=0)
        data_sys[uGNSS.GLO, 0] = np.nanmean(data_sat[GNSS_col.GLO[0]:GNSS_col.GLO[1], :], axis=0)
        data_sys[uGNSS.GAL, 0] = np.nanmean(data_sat[GNSS_col.GAL[0]:GNSS_col.GAL[1], :], axis=0)
        data_sys[uGNSS.QZS, 0] = np.nanmean(data_sat[GNSS_col.QZS[0]:GNSS_col.QZS[1], :], axis=0)
        data_sys[uGNSS.BDS, 0] = np.nanmean(data_sat[GNSS_col.BDS[0]:GNSS_col.BDS[1], :], axis=0)
        data_sys[uGNSS.IRN, 0] = np.nanmean(data_sat[GNSS_col.IRN[0]:GNSS_col.IRN[1], :], axis=0)
        data_sys[uGNSS.SBS, 0] = np.nanmean(data_sat[GNSS_col.SBS[0]:GNSS_col.SBS[1], :], axis=0)
    return data_sat, data_sys
