from .rtkcmn import uGNSS, rCST, sat2prn, timediff, MAX_NFREQ, gpst2utc, time2gpst
import numpy as np
from .meas import gfmeas_h, mwmeas_h, muphmeas, ionpmeas, ccmeas, gfifmeas, gfmeas
from math import sqrt
from .str2typ import arc_dtr, arc_dtr_h, arc_dtr_h1, lomp, lomp_h, logfif, logfif_h, cal_sat_sys, cal_sat_sys_m, calcsThres
from .sat_column import GNSS_col
import datetime

def data_tirm(obs):
    # obs struct to np.array
    epoch = []  # epoch matrix
    sat_num = []  # sat matrix (contain repeat sat)
    P_mat = np.full([uGNSS.MAXSAT, len(obs), MAX_NFREQ], np.nan) # Pseudo Range matrix
    L_mat = np.full([uGNSS.MAXSAT, len(obs), MAX_NFREQ], np.nan) # carrier phase matrix
    CNR_mat = np.full([uGNSS.MAXSAT, len(obs), MAX_NFREQ], np.nan) # Signal Strength matrix
    frq_mat = np.full([uGNSS.MAXSAT, MAX_NFREQ], np.nan) # frequency matrix
    for i in range(len(obs)):
        epoch.append(obs[i].t.time + obs[i].t.sec)
        for j in np.argsort(obs[i].sat):
            sat = obs[i].sat[j]
            # sys, prn = sat2prn(sat)
            fre = np.where((obs[i].freq[j] == 0), np.nan, obs[i].freq[j])
            P_mat[sat-1, i, :] = obs[i].P[j]
            L_mat[sat-1, i, :] = obs[i].L[j]
            CNR_mat[sat-1, i, :] = obs[i].S[j]
            # 0 to NAN
            P_mat[sat-1, i, :] = np.where((P_mat[sat-1, i, :] == 0.0), np.nan, P_mat[sat-1, i, :])
            L_mat[sat-1, i, :] = np.where((L_mat[sat-1, i, :] == 0.0), np.nan, L_mat[sat-1, i, :])
            CNR_mat[sat-1, i, :] = np.where((CNR_mat[sat-1, i, :] == 0.0), np.nan, CNR_mat[sat-1, i, :])
            frq_mat[sat-1, :] = fre
            sat_num.append(sat)
    sat_idx = sorted(list(set(sat_num)))

    # summary
    cnr_time = CNR_mat.copy()
    cnr_sat, cnr_sys = cal_sat_sys_m(CNR_mat, 'mean')
    cnr_qc = dict(zip(['time', 'sat', 'sys'], [cnr_time, cnr_sat, cnr_sys]))
    return P_mat, L_mat, frq_mat, sat_idx, epoch, cnr_qc


def data_visibility(P_mat, L_mat):
    mask = np.logical_and(~np.isnan(P_mat), ~np.isnan(L_mat))
    data_visible = np.where(mask, 1, 0)
    return data_visible

def pseudorange_gross(P_mat, sat_idx):
    C1P1_K1 = 30
    P1P2_K2 = 60 # set threshold
    # dCP = np.full((P_mat.shape[0], P_mat.shape[1], P_mat.shape[2]), np.nan) # The first type of threshold
    dPP = np.full((P_mat.shape[0], P_mat.shape[1], P_mat.shape[2]), np.nan) # The first type of threshold
    gro_slip = np.zeros([P_mat.shape[0], P_mat.shape[1], P_mat.shape[2]], dtype=int) # gross flag matrix
    P_mat_ = P_mat.copy()
    for sat in sat_idx:
        one_dPP = np.tile(P_mat_[sat-1, :, 0], (P_mat.shape[2], 1)).T
        dPP[sat-1, :, :] = one_dPP - P_mat_[sat-1, :, :]

        dPP_abs = np.absolute(dPP[sat-1, :, :]) # abs
        gro_idx = np.zeros([P_mat.shape[1], P_mat.shape[2]], dtype=int)
        gro_id = np.where(dPP_abs > P1P2_K2)
        gro_idx[gro_id] = 1
        gro_slip[sat-1, :, :] = gro_idx  # gross flag
        L1_idx = np.sum(gro_idx, axis=1)
        gro_slip[sat-1, :, 0][L1_idx>0] = 1 # gross flag
        # delete gross
        P_mat[sat-1, :, :][gro_slip[sat-1, :, :]>0] = np.nan

    return gro_slip, P_mat

def clk_jmp2(P_mat, L_mat, frq_mat, obs, sta, epoch, cfg):
    k1 = 290000 # SURPEME threshold
    k2 = 1e-5 # SURPEME threshold
    clk_slip = np.zeros([P_mat.shape[1], P_mat.shape[0]], dtype=int)
    for i in range(1, len(obs)):
        s = np.zeros([1, obs[i].P.shape[1]])
        validGnss = 0
        cjGnss = 0 # satellite number
        clkJump = 0 # clkJump number
        # Skip when CNR_mat is not continuous
        if np.ceil(epoch[i] - epoch[i-1]) != sta.interval:
            continue
        # // Receiver clock slip detect
        for j in np.argsort(obs[i].sat):
            sat = obs[i].sat[j]

            IocL_pre = gfmeas(L_mat[sat-1, i, :], frq_mat[sat-1, :], sat)
            IocL_crt = gfmeas(L_mat[sat-1, i-1, :], frq_mat[sat-1, :], sat)

            if np.abs(IocL_pre[0, 0] - IocL_crt[0, 0]) < 0.1:
                fre = np.where((obs[i].freq[j] == 0), np.nan, obs[i].freq[j])
                dC_mat = P_mat[sat-1, i, :] - P_mat[sat-1, i-1, :]
                dL_mat = L_mat[sat-1, i, :] - L_mat[sat-1, i-1, :]
                dCL_mat = dC_mat - dL_mat*rCST.CLIGHT/fre
                if dCL_mat[0] == np.nan:
                    continue
                validGnss = validGnss + 1
                if abs(dCL_mat[0]) >= k1:
                    dCL_mat_ = np.where((dCL_mat == np.nan), 0, dCL_mat)
                    s = s + dCL_mat_
                    cjGnss += 1

        # / Receiver clock slip repaire
        if cjGnss != 0 and cjGnss == validGnss:
            m_s = s/cjGnss/rCST.CLIGHT*1000.0
            m_s_int = np.round(m_s)
            m_s_abs = np.abs(m_s - m_s_int)
            if m_s_abs[0] <= k2:
                clkJump = m_s_int[0]
                clk_slip[:, i] = np.ones([clk_slip[:, i].shape[0], 1])
            else:
                clkJump = 0

            # P_mat[:, i, :] = P_mat[:, i, :]+np.ones([P_mat[:, i, :].shape[0], P_mat[:, i, :].shape[1]])*clkJump*rCST.CLIGHT/1000.0
            L_mat[:, i, :] = L_mat[:, i, :]+np.ones([L_mat[:, i, :].shape[0], L_mat[:, i, :].shape[1]])*clkJump*rCST.CLIGHT/1000.0*frq_mat[:, i, :]/rCST.CLIGHT

    return clk_slip, L_mat

def cs_mian(P_mat, L_mat, frq_mat, sat_idx, sta, ele, epoch, cfg):
    time_mat = np.full([len(epoch), 1], np.nan).astype(datetime.datetime)
    for i in range(len(epoch)):
        sec_t = epoch[i]
        time_mat[i, 0] = datetime.datetime.fromtimestamp(sec_t, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    dt = sta.interval
    sig0 = sqrt(2*(0.0027**2 + 0.0017**2)) # meter
    dl = 0.4*dt/3600 # meter/hour
    # Turn on cycle detect
    CSMw = 1 # MW flag
    CSGf = 1 # GF flag
    sat_slip = np.zeros([L_mat.shape[0], L_mat.shape[1], L_mat.shape[2]], dtype=int)
    for sat in sat_idx:
        sys, prn = sat2prn(sat)
        if sys == uGNSS.GPS:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 1, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 2, sta, ele, epoch, cfg)
        elif sys == uGNSS.GLO:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 1, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 2, sta, ele, epoch, cfg)
        elif sys == uGNSS.BDS:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 3, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 1, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 2, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 4, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 5, 3, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 6, sta, ele, epoch, cfg)
        elif sys == uGNSS.GAL:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 2, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 1, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 3, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 4, sta, ele, epoch, cfg)
        elif sys == uGNSS.QZS:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 1, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 2, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 3, sta, ele, epoch, cfg)
        elif sys == uGNSS.SBS:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 0, 1, sta, ele, epoch, cfg)

        elif sys == uGNSS.IRN:
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 1, 0, sta, ele, epoch, cfg)
            sat_slip, L_mat = cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, 2, 0, sta, ele, epoch, cfg)

    return sat_slip, L_mat

def cal_csr(cycle_slip, have_sys):
    slip_num = np.sum(cycle_slip, axis=1)
    slip_num_nan = np.where((slip_num == 0.0), np.nan, slip_num)
    have_sys_nan = np.where((have_sys == 0.0), np.nan, have_sys)
    csr_sat = slip_num_nan*1000/have_sys_nan

    csr_sys = np.full([uGNSS.GNSSMAX, have_sys.shape[1]], np.nan)
    csr_sys[uGNSS.GPS] = np.sum(slip_num[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :], axis=0)
    csr_sys[uGNSS.GLO] = np.sum(slip_num[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :], axis=0)
    csr_sys[uGNSS.BDS] = np.sum(slip_num[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :], axis=0)
    csr_sys[uGNSS.GAL] = np.sum(slip_num[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :], axis=0)
    csr_sys[uGNSS.QZS] = np.sum(slip_num[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :], axis=0)
    csr_sys[uGNSS.SBS] = np.sum(slip_num[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :], axis=0)
    csr_sys[uGNSS.IRN] = np.sum(slip_num[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :], axis=0)*1000/np.sum(have_sys[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :], axis=0)

    csr = dict(zip(['sat', 'sys'], [csr_sat, csr_sys]))
    return csr

# MW+GF
def cs_detect(P_mat, L_mat, frq_mat, sat, CSMw, CSGf, sig0, dl, sat_slip, L1, L2, sta, ele, epoch, cfg):
    gfl = gfmeas_h(L_mat[sat-1, :, :], frq_mat[sat-1, :], L1, L2)
    mw = mwmeas_h(L_mat[sat-1, :, :], P_mat[sat-1, :, :], frq_mat[sat-1, :], L1, L2)
    m_mw = np.full(P_mat.shape[1], np.nan)
    sigma = np.full(P_mat.shape[1], np.nan)
    s_gf = np.full(P_mat.shape[1], np.nan)

    aa = gfl.reshape(P_mat.shape[1], 1)
    aa1 = mw.reshape(P_mat.shape[1], 1)

    if np.isnan(np.abs(mw) + np.abs(gfl)).all():
        return sat_slip, L_mat

    ark = arc_dtr_h(np.abs(mw) + np.abs(gfl), sta, epoch, cfg)
    if not np.isnan(ark).any():
        for t in range(ark.shape[0]):
            st = int(ark[t, 0])
            fn = int(ark[t, 1])

            for k in range(st+1, fn+1):
                dmwc = 0
                dgfc = 0
                if CSMw == 1:
                    if np.isnan(mw[k]) or np.isnan(mw[k-1]):
                        continue

                    if k == (st+1):
                        mmw = np.mean(mw[st:k])
                        smw = 0.25
                    elif k < (st+30):
                        mmw = np.mean(mw[st:k])
                        smw = np.std(mw[st:k])
                    else:
                        mmw = np.mean(mw[k-30:k])
                        smw = np.std(mw[k-30:k])
                    dmw = mmw - mw[k]
                    if abs(dmw) > (4*smw):
                        dmwc = 1
                        if k < fn:
                            if abs(mw[k+1]-mw[k]) > 1:
                                L_mat[sat-1, k, L1] = np.nan
                                L_mat[sat-1, k, L2] = np.nan

                                sat_slip[sat-1, k, L1] = 0
                                sat_slip[sat-1, k, L2] = 0

                                mw[k] = np.nan
                                gfl[k] = np.nan
                                st = k+1
                                continue

                if CSGf == 1:
                    if np.isnan(gfl[k]) or np.isnan(gfl[k-1]):
                        continue
                    if k > st+1:
                        dgf1 = gfl[k-1] - gfl[k]
                        dgf2 = gfl[k-2] - gfl[k-1]
                        dgf = dgf1 - dgf2
                    else:
                        dgf = gfl[k-1] - gfl[k]

                    elv = ele[k, sat-1]
                    me = 1 + (10*np.exp(-elv/10))
                    smg = sig0*me
                    s_gf[k] = ((4*smg)+dl)
                    if abs(dgf) > s_gf[k]:
                        dgfc = 1
                        if k < fn:
                            if abs(mw[k+1]-mw[k]) > 1:
                                L_mat[sat-1, k, L1] = np.nan
                                L_mat[sat-1, k, L2] = np.nan

                                sat_slip[sat-1, k, L1] = 0
                                sat_slip[sat-1, k, L2] = 0

                                mw[k] = np.nan
                                gfl[k] = np.nan
                                st = k+1
                                continue


                if (dmwc == 1) or (dgfc == 1):
                    one = mw[k-1] - mw[k]
                    two = gfl[k-1] - gfl[k]
                    A = np.array([[1, -1], [rCST.CLIGHT/frq_mat[sat-1, L1], -rCST.CLIGHT/frq_mat[sat-1, L2]]])
                    L = np.array([one, two]).reshape(2, 1)
                    Dn = np.linalg.pinv(A) @ L

                    Dn1 = round(Dn[0, 0])
                    Dn2 = round(Dn[1, 0])

                    if (Dn1 != 0) or (Dn2 != 0):
                        # Search starts
                        min_residuals=999999
                        cycleL1 = 0
                        cycleL2 = 0
                        for integer_cycle_L1 in range(round(Dn1-5),round(Dn1+5)+1, 1):
                            for integer_cycle_L2 in range(round(Dn2-5),round(Dn2+5)+1, 1):

                                new_L1 = L_mat[sat-1, k, L1] + integer_cycle_L1
                                new_L2 = L_mat[sat-1, k, L2] + integer_cycle_L2

                                f1 = frq_mat[sat-1, L1]
                                f2 = frq_mat[sat-1, L2]

                                lamwl = rCST.CLIGHT/(f1 - f2)
                                lwl = (new_L1 - new_L2)*rCST.CLIGHT/(f1 - f2)
                                pnl = (f1*P_mat[sat-1, k, L1] + f2*P_mat[sat-1, k, L2])/(f1 + f2)
                                new_mw = (lwl - pnl)/lamwl

                                new_gfl = (new_L1/f1 - new_L2/f2)*rCST.CLIGHT

                                if k < (st + 30):
                                    nm_mw = np.mean(mw[st:k]) + (new_mw-np.mean(mw[st:k]))/(k-st+1)
                                else:
                                    nm_mw = np.mean(mw[k-29:k]) + (new_mw-np.mean(mw[k-29:k]))/(30)

                                residual_temp = (nm_mw - mmw)**2+(gfl[k-1] - new_gfl)**2

                                if residual_temp < min_residuals: # the "best" cycle-slip candidate shoule yield the smallest residuals
                                    min_residuals = residual_temp
                                    cycleL1 = integer_cycle_L1
                                    cycleL2 = integer_cycle_L2

                        if (cycleL1 != 0) or (cycleL2 != 0):
                            if cycleL1 != 0:
                                sat_slip[sat-1, k, L1] = 1
                            if cycleL2 != 0:
                                sat_slip[sat-1, k, L2] = 1
                            st = k

    return sat_slip, L_mat

def cal_multipath(P_mat, L_mat, frq_mat, sat_idx, sta, epoch, cycle_slip, cfg):
    mp = np.full((P_mat.shape[0], P_mat.shape[1], P_mat.shape[2]), np.nan) # MP
    for sat in sat_idx:
        sys, _ = sat2prn(sat)
        mpl, cycles = muphmeas(L_mat[sat-1, :, :], P_mat[sat-1, :, :], frq_mat[sat-1, :], sat, cycle_slip[sat-1, :, :])
        # aa1 = mpl.reshape(L_mat.shape[1], 1)
        for fq in range(P_mat.shape[2]):
            # ark = arc_dtr_h(mpl[:, fq].copy(), sta, epoch, cfg)
            if np.isnan(mpl[:, fq]).all():
                continue
            ark = arc_dtr_h1(mpl[:, fq].copy(), sta, epoch, cycles[ :, fq], cfg)
            if np.isnan(ark).any():
                continue
            for t in range(ark.shape[0]):
                st = int(ark[t, 0])
                fn = int(ark[t, 1])
                mp[sat-1, st:fn+1, fq] = lomp(mpl[st:fn+1, fq].copy())

    # summary
    mp_time = mp.copy()
    mp_sat, mp_sys = cal_sat_sys_m(mp, 'rms')
    mp_qc = dict(zip(['time', 'sat', 'sys'], [mp_time, mp_sat, mp_sys]))
    return mp_qc

def cal_iondelay(L_mat, frq_mat, sat_idx, sta, epoch, cycle_slip, cfg):
    iod_delay = np.full([L_mat.shape[0], L_mat.shape[1], L_mat.shape[2]], np.nan) # iod
    for sat in sat_idx:
        sys, prn = sat2prn(sat)
        ionl, cycles = ionpmeas(L_mat[sat-1, :, :], frq_mat[sat-1, :], sat, cycle_slip[sat-1, :, :])
        for fq in range(L_mat.shape[2]):
            if np.isnan(ionl[:, fq]).all():
                continue

            ark = arc_dtr_h1(ionl[:, fq].copy(), sta, epoch, cycles[ :, fq], cfg)
            if np.isnan(ark).any():
                continue
            for t in range(ark.shape[0]):
                st = int(ark[t, 0])
                fn = int(ark[t, 1])

                iod_ = np.diff(ionl[st:fn+1, fq], axis=0)/sta.interval

                I_tmp = iod_.copy()
                three_simga = 3*np.nanstd(I_tmp)
                iod_[np.abs(I_tmp) > three_simga] = np.nan

                # iod_[np.abs(iod_) > 1] = np.nan

                iod_delay[sat-1, st, fq] = 0.0
                iod_delay[sat-1, st+1:fn+1, fq] = iod_

    # summary
    iod_time = iod_delay.copy()
    iod_sat, iod_sys = cal_sat_sys_m(iod_delay, 'rms')
    iod_qc = dict(zip(['time', 'sat', 'sys'], [iod_time, iod_sat, iod_sys]))
    return iod_qc

def cal_gfif(L_mat, frq_mat, sat_idx, sta, epoch, cycle_slip, cfg):
    gfif = np.full([L_mat.shape[1], L_mat.shape[0]], np.nan) # GFIF
    for sat in sat_idx:
        gfifl, band_sel = gfifmeas(L_mat[sat-1, :, :], frq_mat[sat-1, :], sat)
        # gfifl = gfifl.reshape(len(gfifl), 1)
        if band_sel == []:
            continue
        if np.isnan(gfifl).all():
            continue
        ark = arc_dtr_h1(gfifl.copy(), sta, epoch, np.sum(cycle_slip[sat-1, :, band_sel], axis=0), cfg)
        # ark = arc_dtr_h(gfifl.copy(), sta, epoch, cfg)
        if np.isnan(ark).any():
            continue
        for t in range(ark.shape[0]):
            st = int(ark[t, 0])
            fn = int(ark[t, 1])
            gfif[st:fn+1, sat-1] = logfif(gfifl[st:fn+1].copy())

    # summary
    gfif_time = gfif.copy()
    gfif_sat, gfif_sys = cal_sat_sys(gfif, 'rms')
    gfif_qc = dict(zip(['time', 'sat', 'sys'], [gfif_time, gfif_sat, gfif_sys]))
    return gfif_qc

def cal_pseudons(P_mat, sat_idx, sta, epoch, cycle_slip, cfg):
    dif_num = 3
    pnoise = np.full([P_mat.shape[0], P_mat.shape[2]], np.nan)
    p_noise = np.full([P_mat.shape[0], P_mat.shape[1], P_mat.shape[2]], np.nan)
    for sat in sat_idx:
        for fq in range(P_mat.shape[2]):
            if np.isnan(P_mat[sat-1, :, fq]).all():
                continue
            ark = arc_dtr_h(P_mat[sat-1, :, fq].copy(), sta, epoch, cfg)
            if np.isnan(ark).any():
                continue
            for t in range(ark.shape[0]):
                st = int(ark[t, 0])
                fn = int(ark[t, 1])
                if (fn-st) >= dif_num:
                    satP_mat = P_mat[sat-1, st:fn+1, fq].copy()
                    satP_diff = np.diff(satP_mat, dif_num, axis=0)
                    p_noise[sat-1, st+dif_num:fn+1, fq] = sqrt(1/20)*satP_diff

            # 3σ check
            p_tmp = p_noise[sat-1, :, fq].copy()
            three_simga = 3*np.nanstd(p_tmp)
            p_tmp[np.abs(p_tmp) > three_simga] = np.nan
            # 3σ check
            three_simga = 3*np.nanstd(p_tmp)
            p_tmp[np.abs(p_tmp) > three_simga] = np.nan

            p_noise[sat-1, :, fq] = p_tmp

            satP_diff_nnan_ = p_tmp
            satP_diff_nnan = satP_diff_nnan_[~np.isnan(satP_diff_nnan_)]

            if satP_diff_nnan.shape[0] >= 2:
                pnoise[sat-1, fq] = np.linalg.norm(satP_diff_nnan)/sqrt(satP_diff_nnan.shape[0]-1)

    # summary
    pnoise_time = p_noise.copy()
    pnoise_sat, pnoise_sys = cal_sat_sys(pnoise, 'mean')
    pnoise_qc = dict(zip(['time', 'sat', 'sys'], [pnoise_time, pnoise_sat, pnoise_sys]))
    return pnoise_qc

def cal_carns(L_mat, sat_idx, frq_mat, sta, epoch, cycle_slip, cfg):
    dif_num = 3
    lnoise = np.full([L_mat.shape[0], L_mat.shape[2]], np.nan)
    l_noise = np.full([L_mat.shape[0], L_mat.shape[1], L_mat.shape[2]], np.nan)
    for sat in sat_idx:
        sys, prn = sat2prn(sat)
        for fq in range(L_mat.shape[2]):
            if np.isnan(L_mat[sat-1, :, fq]).all():
                continue
            ark = arc_dtr_h1(L_mat[sat-1, :, fq].copy(), sta, epoch, cycle_slip[sat-1, :, fq], cfg)
            # ark = arc_dtr_h(L_mat[sat-1, :, fq].copy(), sta, epoch, cfg)
            if np.isnan(ark).any():
                continue
            for t in range(ark.shape[0]):
                st = int(ark[t, 0])
                fn = int(ark[t, 1])
                if (fn-st) >= dif_num:
                    satL_mat = L_mat[sat-1, st:fn+1, fq].copy()*rCST.CLIGHT/frq_mat[sat-1, fq]
                    satL_diff = np.diff(satL_mat, dif_num, axis=0)
                    l_noise[sat-1, st+dif_num:fn+1, fq] = sqrt(1/20)*satL_diff

            # cycle check
            l_tmp = l_noise[sat-1, :, fq].copy()
            cycle_simga = 0.5*rCST.CLIGHT/frq_mat[sat-1, fq]
            l_tmp[np.abs(l_tmp) > cycle_simga] = np.nan

            # 3σ check
            three_simga = 3*np.nanstd(l_tmp)
            l_tmp[np.abs(l_tmp) > three_simga] = np.nan
            #
            three_simga = 3*np.nanstd(l_tmp)
            l_tmp[np.abs(l_tmp) > three_simga] = np.nan

            l_noise[sat-1, :, fq] = l_tmp

            satL_diff_nnan_ = l_tmp
            satL_diff_nnan = satL_diff_nnan_[~np.isnan(satL_diff_nnan_)]

            if satL_diff_nnan.shape[0] >= 2:
                lnoise[sat-1, fq] = np.linalg.norm(satL_diff_nnan)/sqrt(satL_diff_nnan.shape[0]-1)

    # summary
    lnoise_time = l_noise.copy()
    lnoise_sat, lnoise_sys = cal_sat_sys(lnoise, 'mean')
    lnoise_qc = dict(zip(['time', 'sat', 'sys'], [lnoise_time, lnoise_sat, lnoise_sys]))
    return lnoise_qc

# GPST to UTC
def cal_time(epoch_t):
    time_mat = np.full([len(epoch_t), 1], np.nan).astype(datetime.datetime)
    for i in range(len(epoch_t)):
        sec_t = epoch_t[i].time + epoch_t[i].sec
        time_mat[i, 0] = datetime.datetime.fromtimestamp(sec_t, tz=datetime.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    time_qc = time_mat
    return time_qc