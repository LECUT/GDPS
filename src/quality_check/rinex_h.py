import numpy as np
from copy import deepcopy
from .rtkcmn import uGNSS, rSIG, Ts, Eph, Geph, Seph, Sta, sigind_t, prn2sat, sat2prn, gpst2time, time2gpst, Obs, Obs_set, Nav, Headinfo, \
                    epoch2time, timediff, timeadd, utc2gpst, adjday, adjweek, bdt2time, bdt2gpst, flt1, isFloat, MAXRNXLEN, MAX_NFREQ

from .str2typ import str2time, cut, line2buff, uraindex, sisa_index
from quality_check import rtkcmn as gn
from .rtkcmn import obs2code, code2idx, getcodepri, freqpris
from math import fabs
import math
from .convcode import convcode
import copy

class rnx_decode:
    def __init__(self):
        self.ver = 0.0

    @classmethod
    def flt(self, u, c=-1):
        if c >= 0:
            if isFloat(u):
                u = u
            else:
                u = '0.0'
        try:
            return float(u.replace("D", "E"))
        except:
            return 0

    @classmethod
    def decode_navh(self, navfile):
        nav = Nav()
        with open(navfile, 'rt') as fnav:
            i = 0
            for line in fnav:
                if 'END OF HEADER' in line:
                    break

                if 'RINEX VERSION / TYPE' in line:
                    nav.ver = float(line[0:10])
                    nav.type = line[19:60].rstrip()

                if 'LEAP SECONDS' in line:
                    nav.leaps = float(line[0:7])

                if float(nav.ver) <= 2.99:
                    if 'ION ALPHA' in line:
                        for k in range(4):
                            nav.ion_gps[k] = self.flt(line[2+k*12:2+(k+1)*12])
                    if 'ION BETA' in line:
                        for k in range(4):
                            nav.ion_gps[k+4] = self.flt(line[2+k*12:2+(k+1)*12])
                    if 'DELTA-UTC: A0,A1,T,W' in line:
                        for k in range(2):
                            nav.utc_gps[k] = self.flt(line[3+k*19:3+(k+1)*19])
                        for k in range(2, 4):
                            nav.utc_gps[k] = self.flt(line[41+(k-2)*9:41+(k-1)*9])
                else:
                    if 'IONOSPHERIC CORR' in line[60:]:
                        if line[0:4] == 'GPSA':
                            for k in range(4):
                                nav.ion_gps[k] = self.flt(line[5+k*12:5+(k+1)*12])
                        if line[0:4] == 'GPSB':
                            for k in range(4):
                                nav.ion_gps[k+4] = self.flt(line[5+k*12:5+(k+1)*12])
                        if line[0:4] == 'GAL ':
                            for k in range(4):
                                nav.ion_gal[k] = self.flt(line[5+k*12:5+(k+1)*12])
                        if line[0:4] == 'QZSA':
                            for k in range(4):
                                nav.ion_qzs[k] = self.flt(line[5+k*12:5+(k+1)*12])
                        if line[0:4] == 'QZSB':
                            for k in range(4):
                                nav.ion_qzs[k+4] = self.flt(line[5+k*12:5+(k+1)*12])
                        if line[0:4] == 'BDSA':
                            for k in range(4):
                                nav.ion_bds[i, k] = self.flt(line[5+k*12:5+(k+1)*12])
                            i += 1
                        if line[0:4] == 'BDSB':
                            for k in range(4):
                                nav.ion_bds[i-24, k+4] = self.flt(line[5+k*12:5+(k+1)*12])
                            i += 1
                        if line[0:4] == 'IRNA':
                            for k in range(4):
                                nav.ion_irn[k] = self.flt(line[5+k*12:5+(k+1)*12])
                        if line[0:4] == 'IRNB':
                            for k in range(4):
                                nav.ion_irn[k+4] = self.flt(line[5+k*12:5+(k+1)*12])
                    if 'TIME SYSTEM CORR' in line[60:]:
                        if line[0:4] == 'GPUT':
                            nav.utc_gps[0] = self.flt(line[5:22])
                            nav.utc_gps[1] = self.flt(line[22:38])
                            nav.utc_gps[2] = self.flt(line[38:45])
                            nav.utc_gps[3] = self.flt(line[45:50])
                        if line[0:4] == 'GLUT':
                            nav.utc_glo[0] = self.flt(line[5:22])
                            nav.utc_glo[1] = self.flt(line[22:38])
                            nav.utc_glo[2] = self.flt(line[38:45])
                            nav.utc_glo[3] = self.flt(line[45:50])
                        if line[0:4] == 'QZUT':
                            nav.utc_qzs[0] = self.flt(line[5:22])
                            nav.utc_qzs[1] = self.flt(line[22:38])
                            nav.utc_qzs[2] = self.flt(line[38:45])
                            nav.utc_qzs[3] = self.flt(line[45:50])
                        if line[0:4] == 'GAUT':
                            nav.utc_gal[0] = self.flt(line[5:22])
                            nav.utc_gal[1] = self.flt(line[22:38])
                            nav.utc_gal[2] = self.flt(line[38:45])
                            nav.utc_gal[3] = self.flt(line[45:50])
                        if line[0:4] == 'BDUT':
                            nav.utc_bds[0] = self.flt(line[5:22])
                            nav.utc_bds[1] = self.flt(line[22:38])
                            nav.utc_bds[2] = self.flt(line[38:45])
                            nav.utc_bds[3] = self.flt(line[45:50])
                        if line[0:4] == 'SBUT':
                            nav.utc_sbs[0] = self.flt(line[5:22])
                            nav.utc_sbs[1] = self.flt(line[22:38])
                            nav.utc_sbs[2] = self.flt(line[38:45])
                            nav.utc_sbs[3] = self.flt(line[45:50])
                        if line[0:4] == 'IRUT':
                            nav.utc_irn[0] = self.flt(line[5:22])
                            nav.utc_irn[1] = self.flt(line[22:38])
                            nav.utc_irn[2] = self.flt(line[38:45])
                            nav.utc_irn[3] = self.flt(line[45:50])
        return nav

    @classmethod
    def decode_navb(self, nav, navfile):
        gnss_tbl = {'G': uGNSS.GPS, 'E': uGNSS.GAL, 'R': uGNSS.GLO, 'J': uGNSS.QZS, 'C': uGNSS.BDS, 'I': uGNSS.IRN, 'S': uGNSS.SBS}
        sp = 3 # local position
        aa = [[], []]
        with open(navfile, 'rt') as fnav:
            for line in fnav:
                if 'END OF HEADER' in line:
                    break

            sat_flag = ''
            for line in fnav:

                if nav.ver > 3.99:
                    if '> EPH' in line:
                        eph_type = line[10:14]
                        line = fnav.readline()
                        # filter data for read rinex 4.00
                        if eph_type == 'CNAV' or eph_type == 'CNV3':
                            for i in range(8):
                                line = fnav.readline()  # 7:10
                            continue
                        elif eph_type == 'CNV1' or eph_type == 'CNV2':
                            for i in range(9):
                                line = fnav.readline()
                            continue

                # record satellite prn
                buff = line2buff(line, MAXRNXLEN)
                data = np.zeros(64)
                satid = buff[0:3].rstrip()
                try:
                    float(satid[1:3])
                except ValueError:
                    continue
                if len(satid) < 3:
                    if 'GPS' in nav.type:
                        sys = gnss_tbl['G']
                        prn = int(satid[1:3])
                    elif 'GLONASS' in nav.type:
                        sys = gnss_tbl['R']
                        prn = int(satid[1:3])
                    elif 'GALILEO' in nav.type:
                        sys = gnss_tbl['E']
                        prn = int(satid[1:3])
                    elif 'BEIDOU' in nav.type:
                        sys = gnss_tbl['C']
                        prn = int(satid[1:3])
                    elif 'QZSS' in nav.type:
                        sys = gnss_tbl['J']
                        prn = int(satid[1:3])
                    elif 'IRNSS' in nav.type:
                        sys = gnss_tbl['I']
                        prn = int(satid[1:3])
                    elif 'SABS' in nav.type:
                        sys = gnss_tbl['S']
                        prn = int(satid[1:3])
                    else:
                        sys = gnss_tbl['G']
                        prn = int(satid[1:3])
                else:
                    try:
                        sys = gnss_tbl[satid[0:1]]
                        prn = int(satid[1:3])
                    except Exception as e:
                        print(e)

                sat = prn2sat(sys, prn)

                # record time
                if nav.ver <= 2.99:
                    toc = str2time(buff[sp:sp+19])
                else:
                    sp = 4
                    toc = str2time(buff[sp:sp+19])

                if sys == uGNSS.GPS or sys == uGNSS.QZS or sys == uGNSS.GAL or sys == uGNSS.BDS or sys == uGNSS.IRN:

                    eph = copy.deepcopy(Eph())
                    # eph = Eph(sat)
                    eph.toc = toc
                    eph.sat = sat

                    data[0:3] = cut(buff[sp+19:], 19, 3)

                    eph_rownum = 7
                    for i in range(eph_rownum):
                        line = fnav.readline()  # 7:10
                        buff = line2buff(line, MAXRNXLEN)
                        data_ = cut(buff[sp:], 19, 4)
                        data[3+i*4:3+(i+1)*4] = data_

                    # if sys == uGNSS.IRN and prn==3:
                    #     aa[0].append(eph.sat)
                    #     aa[1].append(uraindex(data[23]))
                    # if sys != uGNSS.IRN:
                    #     continue

                    # 3 satellite clock parameter
                    eph.f0 = data[0]
                    eph.f1 = data[1]
                    eph.f2 = data[2]

                    # 15 satellite orbit parameter
                    eph.A  = data[10]**2
                    eph.e  = data[8]
                    eph.i0 = data[15]
                    eph.OMG0 = data[13]
                    eph.omg = data[17]
                    eph.M0 = data[6]
                    eph.deln = data[5]
                    eph.OMGd = data[18]
                    eph.idot = data[19]
                    eph.crc = data[16]
                    eph.crs = data[4]
                    eph.cuc = data[7]
                    eph.cus = data[9]
                    eph.cic = data[12]
                    eph.cis = data[14]

                    if sys == uGNSS.GPS or sys == uGNSS.QZS:
                        eph.iode = np.fix(data[3])
                        eph.iodc = np.fix(data[26])
                        eph.toes = data[11]
                        eph.week = np.fix(data[21])
                        eph.toe = adjweek(gpst2time(eph.week, data[11]), toc)
                        eph.tot = adjweek(gpst2time(eph.week, data[27]), toc)

                        eph.code = np.fix(data[20])
                        eph.svh = np.fix(data[24])
                        eph.sva = uraindex(data[23])
                        eph.flag = np.fix(data[22])

                        tgd = np.zeros(6)
                        tgd[0] = data[25]
                        eph.tgd = tgd
                        if sys == uGNSS.GPS:
                            eph.fit = data[28]
                        else:
                            if data[28] == 0:
                                eph.fit = 0
                            else:
                                eph.fit = 2
                    elif sys == uGNSS.GAL:
                        eph.iode = np.fix(data[3])
                        eph.iodc = np.fix(data[26])
                        eph.toes = data[11]
                        eph.week = np.fix(data[21])
                        eph.toe = adjweek(gpst2time(eph.week, data[11]), toc)
                        eph.tot = adjweek(gpst2time(eph.week, data[27]), toc)

                        eph.code = np.fix(data[20])
                        eph.svh = np.fix(data[24])
                        eph.sva = sisa_index(data[23])

                        tgd = np.zeros(6)
                        tgd[0] = data[25]
                        tgd[1] = data[26]
                        eph.tgd = tgd

                    elif sys == uGNSS.BDS:
                        eph.toc = bdt2gpst(eph.toc)
                        eph.iode = np.fix(data[3])
                        eph.iodc = np.fix(data[26])
                        eph.toes = data[11]
                        eph.week = np.fix(data[21])
                        eph.toe = adjweek(bdt2gpst(bdt2time(eph.week, data[11])), toc)
                        eph.tot = adjweek(bdt2gpst(bdt2time(eph.week, data[27])), toc)

                        eph.svh = np.fix(data[24])
                        eph.sva = uraindex(data[23])

                        tgd = np.zeros(6)
                        tgd[0] = data[25]
                        tgd[1] = data[26]
                        eph.tgd = tgd

                    elif sys == uGNSS.IRN:
                        eph.iode = np.fix(data[3])
                        eph.iodc = np.fix(data[26])
                        eph.toes = data[11]
                        eph.week = np.fix(data[21])
                        eph.toe = adjweek(gpst2time(eph.week, data[11]), toc)
                        eph.tot = adjweek(gpst2time(eph.week, data[27]), toc)

                        eph.svh = np.fix(data[24])
                        eph.sva = uraindex(data[23])

                        tgd = np.zeros(6)
                        tgd[0] = data[25]
                        eph.tgd = tgd

                    # if delete sva is None data
                    if eph.sva == None:
                        continue
                    nav.eph.append(eph)

                    if sys == uGNSS.GPS:
                        nav.eph_GPS.append(eph)
                    elif sys == uGNSS.GAL:
                        nav.eph_GAL.append(eph)
                    elif sys == uGNSS.QZS:
                        nav.eph_GPS.append(eph)
                    elif sys == uGNSS.BDS:
                        nav.eph_BDS.append(eph)
                    elif sys == uGNSS.IRN:
                        nav.eph_IRN.append(eph)

                elif sys == uGNSS.GLO:  # GLONASS
                    geph = copy.deepcopy(Geph())
                    geph.sat = sat

                    data[0:3] = cut(buff[sp+19:], 19, 3)

                    # record data
                    geph_rownum = 3
                    if nav.ver > 3.04:
                        geph_rownum = 4
                    for i in range(geph_rownum):
                        line = fnav.readline()  # 7:10
                        buff = line2buff(line, MAXRNXLEN)
                        data_ = cut(buff[sp:], 19, 4)
                        data[3+i*4:3+(i+1)*4] = data_

                    # Toc rounded by 15 min in utc
                    week, tow = time2gpst(toc)
                    toc = gpst2time(week, np.floor((tow + 450.0) / 900.0) * 900)
                    dow = int(np.floor(tow / 86400.0))

                    # time of frame in UTC
                    if float(nav.ver) <= 2.99:
                        tod = data[2]  # /* Tod (v.2) in UTC */
                    else:
                        tod = data[2] % 86400.0  # /* Tow (v.3) in UTC */

                    tof = gpst2time(week, tod+dow*86400.0)
                    tof = adjday(tof, toc)

                    geph.toe = utc2gpst(toc)
                    geph.tof = utc2gpst(tof)

                    # IODE = Tb (7bit), Tb =index of UTC+3H within current day
                    geph.iode = np.fix(((tow + 10800.0) % 86400) / 900.0 + 0.5)
                    geph.taun = -data[0]
                    geph.gamn = data[1]

                    geph.pos = np.array([data[3], data[7], data[11]])*1e3
                    geph.vel = np.array([data[4], data[8], data[12]])*1e3
                    geph.acc = np.array([data[5], data[9], data[13]])*1e3

                    geph.svh = np.fix(data[6])
                    geph.frq = np.fix(data[10])
                    geph.age = np.fix(data[14])

                    # some receiver output>128 for minus frequency number
                    if geph.frq > 128:
                        geph.frq = geph.frq-256

                    nav.geph.append(geph)

                    if sys == uGNSS.GLO:
                        nav.eph_GLO.append(geph)


                elif sys == uGNSS.SBS:  # SBAS
                    seph = copy.deepcopy(Seph())

                    data[0:3] = cut(buff[sp+19:], 19, 3)

                    seph_rownum = 3
                    for i in range(seph_rownum):
                        line = fnav.readline()  # 7:10
                        buff = line2buff(line, MAXRNXLEN)
                        data_ = cut(buff[sp:], 19, 4)
                        data[3+i*4:3+(i+1)*4] = data_

                    # Toc rounded by 15 min in utc
                    week, tow = time2gpst(toc)
                    tof = adjday(gpst2time(week, data[2]), toc)

                    seph.t0 = toc
                    seph.tof = tof
                    seph.af0 = data[0]
                    seph.af1 = data[1]
                    seph.sat = sat

                    seph.pos = np.array([data[3], data[7], data[11]])*1e3
                    seph.vel = np.array([data[4], data[8], data[12]])*1e3
                    seph.acc = np.array([data[5], data[9], data[13]])*1e3

                    seph.svh = np.fix(data[6])
                    seph.sva = uraindex(data[10])

                    if seph.sva == None:
                        continue
                    nav.seph.append(seph)

                    if sys == uGNSS.SBS:
                        nav.eph_SBS.append(seph)

        fnav.close()
        return nav


    @classmethod
    def decode_rnxh(self, rnxfile):
        headinfo = Headinfo()
        headinfo.ver = 2.10
        headinfo.type = ' '
        fobs = open(rnxfile, 'rt')
        for line in fobs:
            if 'RINEX VERSION / TYPE' in line:
                headinfo.ver = float(line[0:10])
                headinfo.type = line[20]
                if line[40] == 'G':
                    headinfo.sys = uGNSS.GPS
                    headinfo.tsys = Ts.SYS_GPS
                elif line[40] == 'R':
                    headinfo.sys = uGNSS.GLO
                    headinfo.tsys = Ts.SYS_GLO
                elif line[40] == 'E':
                    headinfo.sys = uGNSS.GAL
                    headinfo.tsys = Ts.SYS_GAL
                elif line[40] == 'C':
                    headinfo.sys = uGNSS.BDS
                    headinfo.tsys = Ts.SYS_BDS
                elif line[40] == 'J':
                    headinfo.sys = uGNSS.QZS
                    headinfo.tsys = Ts.SYS_QZS
                elif line[40] == 'I':
                    headinfo.sys = uGNSS.IRN
                    headinfo.tsys = Ts.SYS_IRN
                elif line[40] == 'M':
                    headinfo.sys = uGNSS.NONE
                    headinfo.tsys = Ts.SYS_GPS
                break
        fobs.close()
        return headinfo

    @classmethod
    def decode_obsh(self, obsfile, headinfo, cfg):

        self.gnss_tbl = {'G': uGNSS.GPS, 'R': uGNSS.GLO, 'C': uGNSS.BDS, 'E': uGNSS.GAL, 'J': uGNSS.QZS, 'I': uGNSS.IRN, 'S': uGNSS.SBS}

        self.nf     = MAX_NFREQ
        self.sigid  = np.ones((uGNSS.GNSSMAX, gn.MAXOBSTYPE), dtype=int)*rSIG.NONE
        self.typeid = np.ones((uGNSS.GNSSMAX, gn.MAXOBSTYPE), dtype=int)*-1
        self.idx    = np.ones((uGNSS.GNSSMAX, gn.MAXOBSTYPE), dtype=int)*-1
        self.frqi   = np.ones((uGNSS.GNSSMAX, gn.MAXOBSTYPE), dtype=int)*0
        self.pri    = np.ones((uGNSS.GNSSMAX, gn.MAXOBSTYPE), dtype=int)*0
        self.fpos   = np.ones((uGNSS.GNSSMAX, gn.MAXOBSTYPE), dtype=int)*-1
        self.nsig   = np.zeros((uGNSS.GNSSMAX), dtype=int) # channel number
        self.nband  = np.zeros((uGNSS.GNSSMAX), dtype=int)

        sta = Sta()
        fobs = open(obsfile, 'rt')
        for line in fobs:
            if 'END OF HEADER' in line[60:]:
                break
            if len(line) <= 59:
                continue
            if 'RINEX VERSION / TYPE' in line[60:]:
                sta.ver = float(line[4:10])
                Headinfo.ver = float(line[0:10])
                Headinfo.type = line[20]
            elif 'MARKER NAME' in line:
                sta.name = line[0:60].strip()
            elif 'MARKER NUMBER' in line:
                sta.marker = line[0:20].strip()
            elif 'REC # / TYPE / VERS' in line:
                sta.recsno = line[0:20]
                sta.rectype = line[20:40]
                sta.recver = line[40:60]
            elif 'ANT # / TYPE' in line:
                sta.antsno = line[0:20]
                sta.antdes = line[20:40]
            elif 'ANTENNA: DELTA H/E/N' in line:
                sta.dela[0] = float(line[0:14])
                sta.dela[1] = float(line[14:28])
                sta.dela[2] = float(line[28:42])
            elif line[60:79] == 'APPROX POSITION XYZ':
                sta.pos[0] = float(line[0:14])
                sta.pos[1] = float(line[14:28])
                sta.pos[2] = float(line[28:42])
            elif line[60:79] == 'SYS / # / OBS TYPES':
                if line[0] in self.gnss_tbl:
                    sys = self.gnss_tbl[line[0]]
                else:
                    continue
                self.nsig[sys] = int(line[3:7])

                s = line[7:7+4*13]
                if self.nsig[sys] >= 14:
                    for i in range(int(self.nsig[sys]/14)):
                        line2 = fobs.readline()
                        s += line2[7:7+4*13]

                # rinex 3.02 BDS chanel B1:1 to B1:2
                if fabs(sta.ver - 3.02) <= 1e-3:
                    if sys == uGNSS.BDS:
                        s = s.replace('1', '2')

                for k in range(self.nsig[sys]):
                    sig = s[4*k:3+4*k]

                    # Exclude data
                    try:
                        if sys == uGNSS.GPS:
                            if sig[1] not in cfg.gps_band():
                                continue
                        elif sys == uGNSS.GLO:
                            if sig[1] not in cfg.glo_band():
                                continue
                        elif sys == uGNSS.BDS:
                            if sig[1] not in cfg.bds_band():
                                continue
                        elif sys == uGNSS.GAL:
                            if sig[1] not in cfg.gal_band():
                                continue
                        elif sys == uGNSS.QZS:
                            if sig[1] not in cfg.qzs_band():
                                continue
                        elif sys == uGNSS.IRN:
                            if sig[1] not in cfg.irn_band():
                                continue
                        elif sys == uGNSS.SBS:
                            if sig[1] not in cfg.sbs_band():
                                continue
                    except Exception as e:
                        print(e)

                    self.sigid[sys][k] = obs2code(sig[1:3]) # code order
                    if len(sig[1:3]) == 0 or self.sigid[sys][k] == 0: # Skip Save Unknown Code
                        continue
                    self.idx[sys][k] = code2idx(sys, obs2code(sig[1:3]))[0] # Get the priority of frequency
                    self.pri[sys][k] = getcodepri(sys, obs2code(sig[1:3]))
                    if sig[0] == 'C':
                        self.typeid[sys][k] = 0
                    elif sig[0] == 'L':
                        self.typeid[sys][k] = 1
                    elif sig[0] == 'D':
                        self.typeid[sys][k] = 2
                    elif sig[0] == 'S':
                        self.typeid[sys][k] = 3
                    else:
                        continue

                self.nband[sys] = len(np.where(self.typeid[sys]==1)[0])
                # /* assign index for highest priority code */
                # for t in range(uGNSS.GNSSMAX):
                #     for i in range(self.nf):
                #         k = -1
                #         for j in range(self.nsig[t]):
                #             if self.idx[t][j] == i and self.pri[t][j]>0 and (k < 0 or self.pri[t][j] > self.pri[t][k]):
                #                 k = j
                #         for j in range(self.nsig[t]):
                #             if self.sigid[t][j] == self.sigid[t][k]:
                #                 self.fpos[t][j] = i


                for t in range(uGNSS.GNSSMAX):
                    for j in range(self.nsig[t]):
                        if self.pri[t][j] > 0:
                            self.fpos[t][j] = self.idx[t][j]

            elif '# / TYPES OF OBSERV' in line:

                n = int(line[1:6]) # obervation number
                tobs = np.full([uGNSS.GNSSMAX, n], '   ')
                s = line[6:60]
                for i in range(math.ceil(n/9.0)-1):
                    line = fobs.readline()
                    s += line[6:60]

                for k in range(n):
                    str = s[6*k:6+6*k]
                    str = str.strip()
                    if sta.ver <= 2.99:
                        tobs[uGNSS.GPS, k] = convcode(sta.ver, str, uGNSS.GPS)
                        tobs[uGNSS.GLO, k] = convcode(sta.ver, str, uGNSS.GLO)
                        tobs[uGNSS.GAL, k] = convcode(sta.ver, str, uGNSS.GAL)
                        tobs[uGNSS.QZS, k] = convcode(sta.ver, str, uGNSS.QZS)
                        tobs[uGNSS.SBS, k] = convcode(sta.ver, str, uGNSS.SBS)
                        tobs[uGNSS.BDS, k] = convcode(sta.ver, str, uGNSS.BDS)

                for sy in range(uGNSS.GNSSMAX):
                    self.nsig[sy] = n
                    for k in range(self.nsig[sy]):
                        sig = tobs[sy, k]
                        if sig == '' or sig == '   ':
                            continue
                        self.sigid[sy][k] = obs2code(sig[1:3])
                        self.idx[sy][k] = code2idx(sy, obs2code(sig[1:3]))[0] # band priority
                        self.pri[sy][k] = getcodepri(sy, obs2code(sig[1:3]))
                        if sig[0] == 'C':
                            self.typeid[sy][k] = 0
                        elif sig[0] == 'L':
                            self.typeid[sy][k] = 1
                        elif sig[0] == 'D':
                            self.typeid[sy][k] = 2
                        elif sig[0] == 'S':
                            self.typeid[sy][k] = 3
                        else:
                            continue

                    self.nband[sy] = len(np.where(self.typeid[sy] == 1)[0])

                # /* assign index for highest priority code */
                for t in range(uGNSS.GNSSMAX):
                    for i in range(self.nf):
                        k = -1
                        for j in range(self.nsig[t]):
                            if self.idx[t][j] == i and self.pri[t][j] > 0 and (k < 0 or self.pri[t][j] > self.pri[t][k]):
                                k = j
                        for j in range(self.nsig[t]):
                            if self.sigid[t][j] == self.sigid[t][k]:
                                self.fpos[t][j] = i

            elif 'INTERVAL' in line:
                sta.interval = float(line[1:44])
            elif 'TIME OF FIRST OBS' in line:
                if line[49:51] == 'GPS':
                    headinfo.tsys = Ts.SYS_GPS
                elif line[49:51] == 'GLO':
                    headinfo.tsys = Ts.SYS_GLO
                elif line[49:51] == 'GAL':
                    headinfo.tsys = Ts.SYS_GAL
                elif line[49:51] == 'BDT':
                    headinfo.tsys = Ts.SYS_BDS
                elif line[49:51] == 'QZS':
                     headinfo.tsys = Ts.SYS_QZS
                elif line[49:51] == 'IRN':
                     headinfo.tsys = Ts.SYS_IRN
                elif line[49:51] == 'SBS':
                     headinfo.tsys = Ts.SYS_SBS

            elif 'TIME OF Last OBS' in line:
                if line[49:51] == 'GPS':
                    headinfo.tsys = Ts.SYS_GPS
                elif line[49:51] == 'GLO':
                    headinfo.tsys = Ts.SYS_GLO
                elif line[49:51] == 'GAL':
                    headinfo.tsys = Ts.SYS_GAL
                elif line[49:51] == 'BDT':
                    headinfo.tsys = Ts.SYS_BDS
                elif line[49:51] == 'QZS':
                     headinfo.tsys = Ts.SYS_QZS
                elif line[49:51] == 'IRN':
                     headinfo.tsys = Ts.SYS_IRN
                elif line[49:51] == 'SBS':
                     headinfo.tsys = Ts.SYS_SBS

        ind = sigind_t()
        ind.n = self.nsig
        ind.pos = self.fpos
        ind.pri = self.pri
        ind.type = self.typeid
        ind.code = self.sigid
        ind.idx = self.idx
        fobs.close()
        return sta, ind

    @classmethod
    def decode_obsb3(self, obsfile, ind, maxepoch, cfg):
        self.gnss_tbl = {'G': uGNSS.GPS, 'E': uGNSS.GAL, 'R': uGNSS.GLO, 'J': uGNSS.QZS, 'C': uGNSS.BDS, 'I': uGNSS.IRN, 'S': uGNSS.SBS}
        fobs = open(obsfile, 'rt')
        for line in fobs:
            if line[60:73] == 'END OF HEADER':
                break

        obs_list = Obs_set()
        nepoch = 0
        epoch_t = []
        for line in fobs:
            if line == '':
                break
            if line[0] != '>':
                continue
            if line[0] == '>':
                if line[2:6].isdigit():
                    pass
                else:
                    continue

            nsat = int(line[32:35]) # number of obs
            sats = np.zeros(nsat, dtype=int)
            if nsat <= 0:
                continue

            flag = int(line[31]) # % Epoch flag
            if flag >= 3 and flag <= 5:
                continue

            obs = Obs()
            toc = str2time(line[2:2+27])

            # Extract data according to the cfg time_beg and time_end
            if timediff(toc, cfg.time_beg()) < 0 or timediff(toc, cfg.time_end()) > 0:
                continue
            # Extract data according to the cfg interval
            if nepoch != 0:
                if (np.fix(timediff(toc, epoch_t[nepoch-1]))%cfg.interval()) != 0:
                    continue

            epoch_t.append(toc)
            obs.t    = toc
            obs.P    = np.zeros((nsat, gn.MAX_NFREQ))
            obs.L    = np.zeros((nsat, gn.MAX_NFREQ))
            obs.D    = np.zeros((nsat, gn.MAX_NFREQ))
            obs.S    = np.zeros((nsat, gn.MAX_NFREQ))
            obs.lli  = np.zeros((nsat, gn.MAX_NFREQ), dtype=int)
            obs.Pstd = np.zeros((nsat, gn.MAX_NFREQ), dtype=int)
            obs.Lstd = np.zeros((nsat, gn.MAX_NFREQ), dtype=int)
            obs.mag  = np.zeros((nsat, gn.MAX_NFREQ))
            obs.freq = np.zeros((nsat, gn.MAX_NFREQ))
            obs.sat  = np.zeros(nsat, dtype=int)
            obs.sys  = np.ones(nsat, dtype=int)*-1
            pri = np.zeros((nsat, gn.MAX_NFREQ), dtype=int)*-1

            n = 0
            for k in range(nsat):
                line = fobs.readline()
                if line[0] not in self.gnss_tbl:
                    continue
                # exclude sys data
                if line[0] not in cfg.satsys():
                    continue
                sys = self.gnss_tbl[line[0]]
                obs.sys[n] = sys
                if line[1:3].replace(" ", "").isdigit():
                    pass
                else:
                    continue
                prn = int(line[1:3])
                # if sys == uGNSS.QZS:
                #     prn += 192
                obs.sat[n] = prn2sat(sys, prn)
                if obs.sat[n] == 0:
                    continue

                if sys == uGNSS.GLO:
                    # Satellite frequency setting of GLONASS
                    glok = [1, -4, 5, 6, 1, -4, 5, 6, -2, -7, 0, -1, -2, -7, 0, -1, 4, -3, 3, 2, 4, -3, 3, 2, -5, -6, 0]
                    obs.freq[n] = freqpris[sys]
                    obs.freq[n][0] = obs.freq[n][0]+glok[prn-1]*0.56250E6
                    obs.freq[n][1] = obs.freq[n][1]+glok[prn-1]*0.43750E6
                else:
                    obs.freq[n] = freqpris[sys]

                buff = line2buff(line, MAXRNXLEN)
                for i in range(ind.n[sys]):
                    # obs.freq[n, ind.pos[sys][i]] = code2idx(sys, ind.code[sys][i])[1]
                    # if i >= nsig_max:
                    #     break
                    obs_ = buff[16*i+3:16*i+17]
                    # if obs_ == '' or ind.code[sys][i] == 0:
                    #     continue
                    try:
                        obsval = float(obs_)
                    except:
                        obsval = 0.0

                    if ind.pos[sys][i] < 0:
                        continue

                    if ind.type[sys][i] == 0:  # code
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obsval == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        else:
                            continue
                        obs.P[n, ind.pos[sys][i]] = obsval
                        Pstd = line[16*i+16]
                        obs.Pstd[n, ind.pos[sys][i]] = int(Pstd) if Pstd != " " else 0
                    elif ind.type[sys][i] == 1:  # carrier
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obsval == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        else:
                            continue
                        obs.L[n, ind.pos[sys][i]] = obsval
                        lli = line[16*i+15]
                        obs.lli[n, ind.pos[sys][i]] = int(lli) if lli != " " else 0
                        Lstd = line[16*i+16]
                        obs.Lstd[n, ind.pos[sys][i]] = int(Lstd) if Lstd != " " else 0
                    elif ind.type[sys][i] == 3:  # C/N0
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obsval == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        else:
                            continue
                        obs.S[n, ind.pos[sys][i]] = obsval
                    elif ind.type[sys][i] == 2:  # Doppler
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obsval == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        else:
                            continue
                        obs.D[n, ind.pos[sys][i]] = obsval
                n += 1

            obs.P = obs.P[:n, :]
            obs.L = obs.L[:n, :]
            obs.Pstd = obs.Pstd[:n, :]
            obs.Lstd = obs.Lstd[:n, :]
            obs.D = obs.D[:n, :]
            obs.S = obs.S[:n, :]
            obs.lli = obs.lli[:n, :]
            obs.mag = obs.mag[:n, :]
            obs.freq = obs.freq[:n, :]
            obs.sat = obs.sat[:n]
            obs.sys = obs.sys[:n]

            # -------------------------------------------
            import copy
            Mix_obs = [copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs)]
            sys_flag = 0
            try:
                for obs_ in Mix_obs:
                    if sys_flag in obs_.sys:
                        obs_.P    = obs_.P[obs.sys == sys_flag]
                        obs_.L    = obs_.L[obs.sys == sys_flag]
                        obs_.Pstd = obs_.Pstd[obs.sys == sys_flag]
                        obs_.Lstd = obs_.Lstd[obs.sys == sys_flag]
                        obs_.D    = obs_.D[obs.sys == sys_flag]
                        obs_.S    = obs_.S[obs.sys == sys_flag]
                        obs_.lli  = obs_.lli[obs.sys == sys_flag]
                        obs_.mag  = obs_.mag[obs.sys == sys_flag]
                        obs_.freq = obs_.freq[obs.sys == sys_flag]
                        obs_.sat  = obs_.sat[obs.sys == sys_flag]
                        obs_.sys  = obs_.sys[obs.sys == sys_flag]
                        if sys_flag == uGNSS.GPS:
                            obs_list.GPS.append(obs_)
                        elif sys_flag == uGNSS.GLO:
                            obs_list.GLO.append(obs_)
                        elif sys_flag == uGNSS.BDS:
                            obs_list.BDS.append(obs_)
                        elif sys_flag == uGNSS.GAL:
                            obs_list.GAL.append(obs_)
                        elif sys_flag == uGNSS.QZS:
                            obs_list.QZS.append(obs_)
                        elif sys_flag == uGNSS.SBS:
                            obs_list.SBS.append(obs_)
                        elif sys_flag == uGNSS.IRN:
                            obs_list.IRN.append(obs_)
                    sys_flag = sys_flag + 1
            except Exception as e:
                print(e)

            obs_list.GNSS.append(obs)

            nepoch += 1
            if maxepoch != None and nepoch >= maxepoch:
                break
        fobs.close()

        return obs_list, epoch_t

    @classmethod
    def decode_obsb2(self, obsfile, ind, maxepoch, cfg):
        self.gnss_tbl = {'G': uGNSS.GPS, 'E': uGNSS.GAL, 'R': uGNSS.GLO, 'J': uGNSS.QZS, 'C': uGNSS.BDS, 'I': uGNSS.IRN, 'S': uGNSS.SBS}
        a = 0
        fobs = open(obsfile, 'rt')
        for line in fobs:
            if 'END OF HEADER' in line:
                break

        obs_list = Obs_set()
        epoch_t = []
        nepoch = 0
        for line in fobs:
            obs = Obs()
            ns = int(line[30:32]) # number of obs
            sats = np.zeros(ns, dtype=int)
            if ns <= 0:
                continue
            flag = int(line[28]) # % Epoch flag
            if flag >= 3 and flag <= 5:
                continue

            # time
            toc = str2time(line[0:0+27])
            # Extract data according to the cfg time_beg and time_end
            if timediff(toc, cfg.time_beg()) < 0 or timediff(toc, cfg.time_end()) > 0:
                continue
            # Extract data according to the cfg interval
            if nepoch != 0:
                if (np.fix(timediff(toc, epoch_t[nepoch-1]))%cfg.interval()) != 0:
                    continue

            epoch_t.append(toc)
            obs.t = toc
            sat = np.zeros(ns, dtype=int)
            j = 32
            for i in range(ns):  # % record the satellite number
                if j >= 68:
                    line = fobs.readline()
                    j = 32
                satid = line[j:j+3]
                sys = self.gnss_tbl[satid[0]]
                prn = int(satid[1:3])
                sat[i] = prn2sat(sys, prn)
                j = j + 3

            obs.P = np.zeros((ns, gn.MAX_NFREQ))
            obs.L = np.zeros((ns, gn.MAX_NFREQ))
            obs.D = np.zeros((ns, gn.MAX_NFREQ))
            obs.S = np.zeros((ns, gn.MAX_NFREQ))
            obs.lli = np.zeros((ns, gn.MAX_NFREQ), dtype=int)
            obs.Pstd = np.zeros((ns, gn.MAX_NFREQ), dtype=int)
            obs.Lstd = np.zeros((ns, gn.MAX_NFREQ), dtype=int)
            obs.mag = np.zeros((ns, gn.MAX_NFREQ))
            obs.freq = np.zeros((ns, gn.MAX_NFREQ))
            obs.sat = np.zeros(ns, dtype=int)
            obs.sys = np.ones(ns, dtype=int)*-1
            pri = np.zeros((ns, gn.MAX_NFREQ), dtype=int)*-1

            n = 0
            for k in range(sat.shape[0]):
                obs.sat[n] = sat[k]
                if obs.sat[n] == 0:
                    continue
                sys, prn = sat2prn(sat[k])
                obs.sys[n] = sys
                line = fobs.readline().replace('\n', '').replace('\r', '').ljust(80, ' ')
                for j in range(math.ceil(ind.n[sys]/5)-1):
                    linet = fobs.readline().replace('\n', '').replace('\r', '').ljust(80, ' ')
                    line += linet

                if sys == 1:
                    # Satellite frequency setting of GLONASS
                    glok = [1, -4, 5, 6, 1, -4, 5, 6, -2, -7, 0, -1, -2, -7, 0, -1, 4, -3, 3, 2, 4, -3, 3, 2, 0, 0, 0]
                    obs.freq[n] = freqpris[sys]
                    obs.freq[n][0] = obs.freq[n][0]+glok[prn-1]*0.56250E6
                    obs.freq[n][1] = obs.freq[n][1]+glok[prn-1]*0.43750E6
                else:
                    obs.freq[n] = freqpris[sys]

                sys, prn = sat2prn(sat[k])
                for i in range(ind.n[sys]):
                    obs_ = line[16*i:16*i+14].strip()
                    # if obs_ == '' or ind.code[sys][i] == 0:
                    #     continue
                    try:
                        obsval = float(obs_)
                    except:
                        obsval = 0.0

                    if ind.pos[sys][i] < 0:
                        continue

                    if ind.type[sys][i] == 0:  # code
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obs.P[n, ind.pos[sys][i]] == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]

                        obs.P[n, ind.pos[sys][i]] = obsval
                        Pstd = line[16*i+16]
                        obs.Pstd[n, ind.pos[sys][i]] = int(Pstd) if Pstd != " " else 0
                    elif ind.type[sys][i] == 1:  # carrier
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obs.L[n, ind.pos[sys][i]] == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        obs.L[n, ind.pos[sys][i]] = obsval
                        lli = line[16*i+15]
                        obs.lli[n, ind.pos[sys][i]] = int(lli) if lli != " " else 0
                        Lstd = line[16*i+16]
                        obs.Lstd[n, ind.pos[sys][i]] = int(Lstd) if Lstd != " " else 0
                    elif ind.type[sys][i] == 3:  # C/N0
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obs.S[n, ind.pos[sys][i]] == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        obs.S[n, ind.pos[sys][i]] = obsval
                    elif ind.type[sys][i] == 2:  # Doppler
                        if ind.pri[sys][i] >= pri[n, ind.pos[sys][i]]:
                            if obs.D[n, ind.pos[sys][i]] == 0.0:
                                continue
                            pri[n, ind.pos[sys][i]] = ind.pri[sys][i]
                        obs.D[n, ind.pos[sys][i]] = obsval
                n += 1

            obs.P = obs.P[:n, :]
            obs.L = obs.L[:n, :]
            obs.Pstd = obs.Pstd[:n, :]
            obs.Lstd = obs.Lstd[:n, :]
            obs.D = obs.D[:n, :]
            obs.S = obs.S[:n, :]
            obs.lli = obs.lli[:n, :]
            obs.mag = obs.mag[:n, :]
            obs.freq = obs.freq[:n, :]
            obs.sat = obs.sat[:n]
            obs.sys = obs.sys[:n]

            # ----------------------------------------------
            import copy
            Mix_obs = [copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs), copy.deepcopy(obs)]
            sys_flag = 0
            try:
                for obs_ in Mix_obs:
                    if sys_flag in obs_.sys:
                        obs_.P    = obs_.P[obs.sys == sys_flag]
                        obs_.L    = obs_.L[obs.sys == sys_flag]
                        obs_.Pstd = obs_.Pstd[obs.sys == sys_flag]
                        obs_.Lstd = obs_.Lstd[obs.sys == sys_flag]
                        obs_.D    = obs_.D[obs.sys == sys_flag]
                        obs_.S    = obs_.S[obs.sys == sys_flag]
                        obs_.lli  = obs_.lli[obs.sys == sys_flag]
                        obs_.mag  = obs_.mag[obs.sys == sys_flag]
                        obs_.freq = obs_.freq[obs.sys == sys_flag]
                        obs_.sat  = obs_.sat[obs.sys == sys_flag]
                        obs_.sys  = obs_.sys[obs.sys == sys_flag]
                        if sys_flag == uGNSS.GPS:
                            obs_list.GPS.append(obs_)
                        elif sys_flag == uGNSS.GLO:
                            obs_list.GLO.append(obs_)
                        elif sys_flag == uGNSS.BDS:
                            obs_list.BDS.append(obs_)
                        elif sys_flag == uGNSS.GAL:
                            obs_list.GAL.append(obs_)
                        elif sys_flag == uGNSS.QZS:
                            obs_list.QZS.append(obs_)
                        elif sys_flag == uGNSS.SBS:
                            obs_list.SBS.append(obs_)
                        elif sys_flag == uGNSS.IRN:
                            obs_list.IRN.append(obs_)
                    sys_flag = sys_flag + 1
            except Exception as e:
                print(e)

            obs_list.GNSS.append(obs)
            nepoch += 1
            if maxepoch != None and nepoch >= maxepoch:
                break

        fobs.close()
        return obs_list, epoch_t

    @classmethod
    def decode_obs(self, obsfile, cfg):
        headinfo = self.decode_rnxh(obsfile)
        sta, ind = rnx_decode.decode_obsh(obsfile, headinfo, cfg)
        if headinfo.ver <= 2.99:
            obs, epoch_t = self.decode_obsb2(obsfile, ind, None, cfg)
        elif headinfo.ver <= 3.99:
            obs, epoch_t = self.decode_obsb3(obsfile, ind, None, cfg)
        else:
            obs, epoch_t = self.decode_obsb3(obsfile, ind, None, cfg)
        return sta, ind, obs, epoch_t


