from .rtkcmn import time2gpst, gpst2utc, sat2id, sat2prn, ecef2pos, rCST
import pandas as pd
import numpy as np
import datetime
import os

def save_path(filepath):
    difectory = os.path.dirname(filepath)
    file = os.path.splitext(filepath)[0].split("/")[-1]
    if os.path.exists(difectory+'/result/'):
        pass
    else:
        os.mkdir(difectory+'/result/')
    dirStr = difectory+'/result/'+ file
    return dirStr

def save_sol(tepoch_sol, dirStr, file_list):
    solfile = dirStr + '.pos'
    file_list['sol'].append(os.path.basename(solfile))
    solhdr = 'GNSS       Date     Time        X(m)            Y(m)          Z(m)         B(deg)    L(deg)      H(m)     Q   NS     GDOP      PDOP        HDOP        VDOP\n'
    systype = dict(zip(['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS', 'NavIC', 'MIX'], ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'SBS',  'NavIC', 'MIX']))
    with open(solfile, 'w') as outfile:
        outfile.write(solhdr)
        for sys, data in tepoch_sol.items():
            if data ==None:
                continue
            if len(data) == 0:
                continue
            for s in data:
                if s == []:
                    continue
                if s.stat == -1:
                    continue
                llh = ecef2pos(s.rr[0:3])
                time = datetime.datetime.fromtimestamp(np.round(s.t.time+s.t.sec), tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
                fmt = '%-5s %s %14.5f %14.5f %14.5f %10.4f %10.4f %10.4f %3d %3d %10.4f %10.4f %10.4f %10.4f\n'
                outfile.write(fmt % (systype[sys], time, s.rr[0], s.rr[1], s.rr[2], llh[0]/rCST.D2R, llh[1]/rCST.D2R, llh[2], s.stat, s.ns, s.dop[0], s.dop[1], s.dop[2], s.dop[3]))
            outfile.write('\n')
        outfile.close()

def save_ele(ele, qc_time, dirStr, file_list, sat_idx):
    elefile = dirStr + '.ele'
    file_list['ele'].append(os.path.basename(elefile))
    ele_ = ele.copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    with open(elefile, 'w') as outfile:
        head_str = '{:^20}'.format('Date       Time   ') + ' '.join('{:>7}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        data = np.round(ele_[:, np.array(sat_idx)-1], 3)
        data_str = ['{} '.format(qc_time[j, 0]) + ' '.join('{:7.3f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
        outfile.write('\n'.join(data_str))
        outfile.close()

def save_azi(azi, qc_time, dirStr, file_list, sat_idx):
    azifile = dirStr + '.azi'
    file_list['azi'].append(os.path.basename(azifile))
    azi_ = azi.copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    with open(azifile, 'w') as outfile:
        head_str = '{:^20}'.format('Date       Time   ') + ' '.join('{:>7}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        data = np.round(azi_[:, np.array(sat_idx)-1], 3)
        data_str = ['{} '.format(qc_time[j, 0]) + ' '.join('{:7.3f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
        outfile.write('\n'.join(data_str))
        outfile.close()


def save_inte(qc_inte, dirStr, file_list, sat_idx):
    intefile = dirStr + '.inte'
    file_list['inte'].append(os.path.basename(intefile))
    inte_ = np.round(qc_inte['sat'], 6).T
    sat_np = np.array(sat_idx)-1
    T_data = inte_[:, sat_np].copy()
    fmt_c = '%-20s'+' %-8s'*len(sat_idx) # - -represents left alignment
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    row_index = np.array(['Band', 'L1/G1/E1/B1/L1/L1/L5', 'L2/G2/E5b/B2/L2/L5/S',   'L5/G3/E5a/B2a/L5', 'E6/L6/B3', 'E5/B2(a+b)', 'B1C', 'B2b'])
    row_index = row_index.reshape((len(row_index), 1))
    prn_id = np.array(prn_id).reshape((1, len(prn_id)))
    arr = np.vstack((prn_id, T_data))
    arr = np.hstack((row_index, arr))
    np.savetxt(intefile, arr, fmt=fmt_c, delimiter=' ')

def save_full(qc_full, dirStr, file_list, sat_idx):
    intefile = dirStr + '.satu'
    file_list['satu'].append(os.path.basename(intefile))
    full_ = np.round(qc_full['sat'], 6).T
    sat_np = np.array(sat_idx)-1
    T_data = full_[:, sat_np].copy()
    fmt_c = '%-20s'+' %-8s'*len(sat_idx) # - -represents left alignment
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    row_index = np.array(['Band', 'L1/G1/E1/B1/L1/L1/L5', 'L2/G2/E5b/B2/L2/L5/S',   'L5/G3/E5a/B2a/L5', 'E6/L6/B3', 'E5/B2(a+b)', 'B1C', 'B2b'])
    row_index = row_index.reshape((len(row_index), 1))
    prn_id = np.array(prn_id).reshape((1, len(prn_id)))
    arr = np.vstack((prn_id, T_data))
    arr = np.hstack((row_index, arr))
    np.savetxt(intefile, arr, fmt=fmt_c, delimiter=' ')

def save_CNR(qc_cnr, qc_time, dirStr, file_list, sat_idx):
    cnrfile = dirStr + '.cnr'
    file_list['CN0'].append(os.path.basename(cnrfile))
    cnr_ = qc_cnr['time'].T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    band_type = ['CNRS1 ', 'CNRS2 ', 'CNRS3 ', 'CNRS4 ', 'CNRS5 ', 'CNRS6 ', 'CNRS7 ']
    with open(cnrfile, 'w') as outfile:
        head_str = 'GNSSx ' + '{:^20}'.format('Date       Time   ') + ' '.join('{:>5}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        for i in range(cnr_.shape[0]):
            data = np.round(cnr_[i, :, np.array(sat_idx)-1].T, 3)
            data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:5.3}'.format(num) for num in data[j]) for j in range(data.shape[0])]
            data_str = '\n'.join(data_str)
            outfile.write(data_str + '\n')
            outfile.write('\n')
        outfile.close()

def save_mp(qc_mp, qc_time, dirStr, file_list, sat_idx):
    mpfile = dirStr + '.pmp'
    file_list['MP'].append(os.path.basename(mpfile))
    mp_ = qc_mp['time'].T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    band_type = ['MPM1 ', 'MPM2 ', 'MPM3 ', 'MPM4 ', 'MPM5 ', 'MPM6 ', 'MPM7 ']
    with open(mpfile, 'w') as outfile:
        head_str = 'GNSSx ' + '{:^20}'.format('Date       Time  ') + ' '.join('{:>7}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        for i in range(mp_.shape[0]):
            data = np.round(mp_[i, :, np.array(sat_idx)-1].T, 4)
            data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:7.4f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
            data_str = '\n'.join(data_str)
            outfile.write(data_str + '\n')
            outfile.write('\n')
        outfile.close()

def save_gfif(qc_gfif, qc_time, dirStr, file_list, sat_idx):
    gfiffile = dirStr + '.lmp'
    file_list['GFIF'].append(os.path.basename(gfiffile))
    gfif_ = qc_gfif['time']
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    with open(gfiffile, 'w') as outfile:
        head_str = '{:^20}'.format('Date       Time   ') + ' '.join('{:>8}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        data = np.round(gfif_[:, np.array(sat_idx)-1], 5)
        data_str = ['{} '.format(qc_time[j, 0]) + ' '.join('{:8.5f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
        data_str = '\n'.join(data_str)
        outfile.write(data_str + '\n')
        outfile.close()

def save_iod(qc_iod, qc_time, dirStr, file_list, sat_idx):
    iodfile = dirStr + '.iod'
    file_list['iod'].append(os.path.basename(iodfile))
    iod_ = qc_iod['time'].T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    band_type = ['IODI1 ', 'IODI2 ', 'IODI3 ', 'IODI4 ', 'IODI5 ', 'IODI6 ', 'IODI7 ']
    with open(iodfile, 'w') as outfile:
        head_str = 'GNSSx ' + '{:^20}'.format('Date       Time   ') + ' '.join('{:>7}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        for i in range(iod_.shape[0]):
            data = np.round(iod_[i, :, np.array(sat_idx)-1].T, 4).copy()
            data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:7.4f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
            data_str = '\n'.join(data_str)
            outfile.write(data_str + '\n')
            outfile.write('\n')
        outfile.close()

def save_pnoise(qc_pnoise, qc_time, dirStr, file_list, sat_idx):
    pnoisefile = dirStr + '.pnoise'
    file_list['Pnoise'].append(os.path.basename(pnoisefile))
    pnoise_ = qc_pnoise['time'].T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_ ))
    band_type = ['PNSN1 ', 'PNSN2 ', 'PNSN3 ', 'PNSN4 ', 'PNSN5 ', 'PNSN6 ', 'PNSN7 ']
    with open(pnoisefile, 'w') as outfile:
        head_str = 'GNSSx ' + '{:^20}'.format('Date       Time   ') + ' '.join('{:>7}'.format(prn) for prn in prn_id)
        outfile.write(head_str+'\n')
        for i in range(pnoise_.shape[0]):
            data = np.round(pnoise_[i, :, np.array(sat_idx)-1].T, 4).copy()
            data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:7.4f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
            data_str = '\n'.join(data_str)
            outfile.write(data_str + '\n')
            outfile.write('\n')
        outfile.close()

def save_cnoise(qc_lnoise, qc_time, dirStr, file_list, sat_idx):
    cnoisefile = dirStr + '.lnoise'
    file_list['Cnoise'].append(os.path.basename(cnoisefile))
    pnoise_ = qc_lnoise['time'].T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    band_type = ['CNSN1 ', 'CNSN2 ', 'CNSN3 ', 'CNSN4 ', 'CNSN5 ', 'CNSN6 ', 'PNSN7 ']
    with open(cnoisefile, 'w') as outfile:
        head_str = 'GNSSx ' + '{:^20}'.format('Date       Time   ') + ' '.join('{:>7}'.format(prn) for prn in prn_id)
        outfile.write(head_str + '\n')
        for i in range(pnoise_.shape[0]):
            data = np.round(pnoise_[i, :, np.array(sat_idx) - 1].T, 4).copy()
            data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:7.4f}'.format(num) for num in data[j]) for j in range(data.shape[0])]
            data_str = '\n'.join(data_str)
            outfile.write(data_str + '\n')
            outfile.write('\n')
        outfile.close()


def save_summary(dirStr, qc_time, tepoch_sol, ele, azi, qc_inte, qc_full, qc_cnr, qc_csr, qc_mp, qc_gfif, qc_iod, qc_pnoise, qc_lnoise, sat_idx):
    outputFile = dirStr + '.sum'
    ## -- HEADER
    fid = open(outputFile, 'w+')
    fid.write('# GDPS [2.0] Jul 20 2023 09:46:14 (Rev: 3738)\n')
    fid.write('\n')
    # Summary statistics
    fid.write('Quality Check Summary by GDPS software\n')

    fid.write('# ---------------------------------------------------------- #\n')
    fid.write('|GNSS  |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('L1  ', 'L2  ', 'L3  ', 'L4  ', 'L5  ', 'L6  ', 'L7  '))
    fid.write('|GPS   |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('L1  ', 'L2  ', 'L5  ', '----', '----', '----', '----'))
    fid.write('|GLO   |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('G1  ', 'G2  ', 'G3  ', '----', '----', '----', '----'))
    fid.write('|BDS   |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('B1  ', 'B2  ', 'B2a ', 'B3  ', 'B2ab', 'B1C ', 'B2b '))
    fid.write('|GAL   |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('E1  ', 'E5b ', 'E5a ', 'E6  ', 'E5ab', '----', '----'))
    fid.write('|QZS   |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('L1  ', 'L2  ', 'L5  ', 'L6  ', '----', '----', '----'))
    fid.write('|SBS   |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('L1  ', 'L5  ', '----', '----', '----', '----', '----'))
    fid.write('|NavIC |{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|{:>7}|\n'.format('L5  ', 'S   ', 'L1  ', '----', '----', '----', '----'))

    fid.write('# ---------------------------------------------------------- #\n')
    fid.write('\n')

    # Data body
    fid.write('# --------------- Data Integrity Rate -------------------- #' + '\n')
    sys_type = ['GPS   ','GLO   ',  'BDS   ', 'GAL   ', 'QZS   ', 'SBS   ', 'NavIC ']
    head_ = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
    head_inte = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_inte = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_inte['sys'][j]) for j in range(qc_inte['sys'].shape[0])]
    data_inte = '\n'.join(data_inte)
    fid.write(head_inte + '\n')
    fid.write(data_inte + '\n')
    fid.write('\n')

    fid.write('# ---------------- Data saturation rate -------------------- #' + '\n')
    head_full = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_full = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_full['sys'][j]) for j in range(qc_full['sys'].shape[0])]
    data_full = '\n'.join(data_full)
    fid.write(head_full + '\n')
    fid.write(data_full + '\n')
    fid.write('\n')

    fid.write('# ----------------------- C/N0 --------------------------- #' + '\n')
    head_cnr = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_cnr = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_cnr['sys'][j]) for j in range(qc_cnr['sys'].shape[0])]
    data_cnr = '\n'.join(data_cnr)
    fid.write(head_cnr + '\n')
    fid.write(data_cnr + '\n')
    fid.write('\n')

    fid.write('# ------------------------ CSR --------------------------- #' + '\n')
    head_csr = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_csr = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_csr['sys'][j]) for j in range(qc_csr['sys'].shape[0])]
    data_csr = '\n'.join(data_csr)
    fid.write(head_csr + '\n')
    fid.write(data_csr + '\n')
    fid.write('\n')

    fid.write('# -------------- Pseudorange Multipath ------------------ #' + '\n')
    head_mp = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_mp = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_mp['sys'][j]) for j in range(qc_mp['sys'].shape[0])]
    data_mp = '\n'.join(data_mp)
    fid.write(head_mp + '\n')
    fid.write(data_mp + '\n')
    fid.write('\n')

    fid.write('# ----------- Carrier Phase Multipath ------------------ #' + '\n')
    data_gfif = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_gfif['sys'][j]) for j in range(qc_gfif['sys'].shape[0])]
    data_gfif = '\n'.join(data_gfif)
    fid.write(data_gfif + '\n')
    fid.write('\n')

    fid.write('# ------------- Ionospheric Delay Rate ------------------ #' + '\n')
    head_iod = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_iod = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_iod['sys'][j]) for j in range(qc_iod['sys'].shape[0])]
    data_iod = '\n'.join(data_iod)
    fid.write(head_iod + '\n')
    fid.write(data_iod + '\n')
    fid.write('\n')

    fid.write('# ---------------- Pseudorange Noise ---------------- #' + '\n')
    head_pnoise = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_pnoise = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_pnoise['sys'][j]) for j in range(qc_pnoise['sys'].shape[0])]
    data_pnoise = '\n'.join(data_pnoise)
    fid.write(head_pnoise + '\n')
    fid.write(data_pnoise + '\n')
    fid.write('\n')

    fid.write('# --------------- Carrier Phase Noise ------------------- #' + '\n')
    head_cnoise = '      ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_cnoise = [sys_type[j] + ' '.join('{:7.4f}'.format(num) for num in qc_lnoise['sys'][j]) for j in range(qc_lnoise['sys'].shape[0])]
    data_cnoise = '\n'.join(data_cnoise)
    fid.write(head_cnoise + '\n')
    fid.write(data_cnoise + '\n')
    fid.write('\n')

    fid.write('# ------------------- C/N0 of Sat ---------------------- #' + '\n')
    head_scnr = '    ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_ = qc_cnr['sat'][np.array(sat_idx)-1, :].copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    data_scnr = [prn_id[j]+ ' ' + ' '.join('{:7.4f}'.format(num) for num in data_[j]) for j in range(data_.shape[0])]
    data_scnr = '\n'.join(data_scnr)
    fid.write(head_scnr + '\n')
    fid.write(data_scnr + '\n')
    fid.write('\n')

    fid.write('# ------------------- CSR of Sat ----------------------- #' + '\n')
    head_scsr = '    ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_ = qc_csr['sat'][np.array(sat_idx)-1, :].copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    data_scsr = [prn_id[j]+ ' ' + ' '.join('{:7.4f}'.format(num) for num in data_[j]) for j in range(data_.shape[0])]
    data_scsr = '\n'.join(data_scsr)
    fid.write(head_scsr + '\n')
    fid.write(data_scsr + '\n')
    fid.write('\n')

    fid.write('# -------------- Code Multipath of Sat ------------------ #' + '\n')
    head_smp = '    ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_ = qc_mp['sat'][np.array(sat_idx)-1, :].copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    data_smp = [prn_id[j]+ ' ' + ' '.join('{:7.4f}'.format(num) for num in data_[j]) for j in range(data_.shape[0])]
    data_smp = '\n'.join(data_smp)
    fid.write(head_smp + '\n')
    fid.write(data_smp + '\n')
    fid.write('\n')

    fid.write('# ---------- Ionospheric Delay Rate of Sat -------------- #' + '\n')
    head_siod = '    ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_ = qc_iod['sat'][np.array(sat_idx)-1, :].copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    data_siod = [prn_id[j]+ ' ' + ' '.join('{:7.4f}'.format(num) for num in data_[j]) for j in range(data_.shape[0])]
    data_siod = '\n'.join(data_siod)
    fid.write(head_siod + '\n')
    fid.write(data_siod + '\n')
    fid.write('\n')

    fid.write('# ------------ Pseudorange Noise of Sat ----------------- #' + '\n')
    head_spnoise = '    ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_ = qc_pnoise['sat'][np.array(sat_idx)-1, :].copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    data_spnoise = [prn_id[j]+ ' ' + ' '.join('{:7.4f}'.format(num) for num in data_[j]) for j in range(data_.shape[0])]
    data_spnoise = '\n'.join(data_spnoise)
    fid.write(head_spnoise + '\n')
    fid.write(data_spnoise + '\n')
    fid.write('\n')

    fid.write('# ----------- Carrier Phase Noise of Sat ---------------- #' + '\n')
    head_scnoise = '    ' + ' '.join('{:>7}'.format(band) for band in head_)
    data_ = qc_lnoise['sat'][np.array(sat_idx)-1, :].copy()
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    data_scnoise = [prn_id[j]+ ' ' + ' '.join('{:7.4f}'.format(num) for num in data_[j]) for j in range(data_.shape[0])]
    data_scnoise = '\n'.join(data_scnoise)
    fid.write(head_scnoise + '\n')
    fid.write(data_scnoise + '\n')
    fid.write('\n')
    fid.close()

def save_cycle(cycle_slip, qc_time, sat_idx, dirStr, file_list):
    outputFile = dirStr + '.cycleslip'
    file_list['cycle'].append(os.path.basename(outputFile))
    fid = open(outputFile, 'w+')
    ## -- HEADER
    cycle_ = cycle_slip.T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    band_type = ['CYCLE1 ', 'CYCLE2 ', 'CYCLE3 ', 'CYCLE4 ', 'CYCLE5 ', 'CYCLE6 ', 'CYCLE7 ']
    head_str = 'GNSSx  ' + '{:^20}'.format('Date       Time   ') + ' '.join('{:>3}'.format(prn) for prn in prn_id)
    fid.write(head_str + '\n')
    for i in range(cycle_.shape[0]):
        data = cycle_[i, :, np.array(sat_idx) - 1].T
        data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:3d}'.format(num) for num in data[j]) for j in range(data.shape[0])]
        data_str = '\n'.join(data_str)
        fid.write(data_str + '\n')
        fid.write('\n')
    fid.close()

def save_clkjump(clk_slip, qc_time, sat_idx, dirStr, file_list):
    outputFile = dirStr + '.clkjump'
    file_list['clkjump'].append(os.path.basename(outputFile))
    fid = open(outputFile, 'w+')
    ## -- HEADER
    jump_ = clk_slip
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    head_str = '{:^20}'.format('Date       Time   ') + ' '.join('{:>3}'.format(prn) for prn in prn_id)
    fid.write(head_str + '\n')
    data = jump_[:, np.array(sat_idx) - 1]
    data_str = ['{} '.format(qc_time[j, 0]) + ' '.join('{:3d}'.format(num) for num in data[j]) for j in range(data.shape[0])]
    data_str = '\n'.join(data_str)
    fid.write(data_str + '\n')
    fid.write('\n')
    fid.close()

def save_satvs(data_visible, qc_time, sat_idx, dirStr, file_list):
    outputFile = dirStr + '.vis'
    file_list['satvs'].append(os.path.basename(outputFile))
    fid = open(outputFile, 'w+')
    ## -- HEADER
    data_vs = data_visible.T
    prn_id = []
    for sat_ in sat_idx:
        prn_id.append(sat2id(sat_))
    band_type = ['VISIB1 ', 'VISIB2 ', 'VISIB3 ', 'VISIB4 ', 'VISIB5 ', 'VISIB6 ', 'VISIB7 ']
    head_str = 'GNSSx  ' + '{:^20}'.format('Date       Time   ') + ' '.join('{:>3}'.format(prn) for prn in prn_id)
    fid.write(head_str + '\n')
    for i in range(data_vs.shape[0]):
        data = data_vs[i, :, np.array(sat_idx) - 1].T
        data_str = [band_type[i] + '{} '.format(qc_time[j, 0]) + ' '.join('{:3d}'.format(num) for num in data[j]) for j in range(data.shape[0])]
        data_str = '\n'.join(data_str)
        fid.write(data_str + '\n')
        fid.write('\n')
    fid.close()

def save_outsat(sat_idx, dirStr, file_list):
    satfile = dirStr + '.sat'
    file_list['sat'].append(os.path.basename(satfile))
    sat_idx_pd = pd.DataFrame(sat_idx)
    sat_idx_pd.to_csv(satfile, index=False)

def save_outlist(file_list, dirStr):
    file_dict = open(dirStr+'.list', 'w+')
    file_dict.write(str(file_list))
    file_dict.close()

def save_file(dirStr, clk_slip, cycle_slip, qc_time, tepoch_sol, ele, azi, qc_inte, qc_full, qc_cnr, qc_csr, qc_mp, qc_gfif, qc_iod, qc_pnoise, qc_lnoise, data_visible, sat_idx):
    file_list = {'sol': [], 'ele': [], 'azi': [], 'inte': [], 'satu': [], 'CN0': [], 'MP': [], 'GFIF': [], 'iod': [], 'Pnoise': [], 'Cnoise': [], 'sat': [], 'cycle': [], 'clkjump': [], 'satvs': []}
    save_sol(tepoch_sol, dirStr, file_list)
    save_ele(ele, qc_time, dirStr, file_list, sat_idx)
    save_azi(azi, qc_time, dirStr, file_list, sat_idx)
    save_inte(qc_inte, dirStr, file_list, sat_idx)
    save_full(qc_full, dirStr, file_list, sat_idx)
    save_CNR(qc_cnr, qc_time, dirStr, file_list, sat_idx)
    save_mp(qc_mp, qc_time, dirStr, file_list, sat_idx)
    save_gfif(qc_gfif, qc_time, dirStr, file_list, sat_idx)
    save_iod(qc_iod, qc_time, dirStr, file_list, sat_idx)
    save_pnoise(qc_pnoise, qc_time, dirStr, file_list, sat_idx)
    save_cnoise(qc_lnoise, qc_time, dirStr, file_list, sat_idx)
    save_summary(dirStr, qc_time, tepoch_sol, ele, azi, qc_inte, qc_full, qc_cnr, qc_csr, qc_mp, qc_gfif, qc_iod, qc_pnoise, qc_lnoise, sat_idx)
    save_cycle(cycle_slip, qc_time, sat_idx, dirStr, file_list)
    save_clkjump(clk_slip, qc_time, sat_idx, dirStr, file_list)
    save_satvs(data_visible, qc_time, sat_idx, dirStr, file_list)
    save_outsat(sat_idx, dirStr, file_list)
    save_outlist(file_list, dirStr)