from .rtkcmn import MAX_NFREQ, rCST, ecef2pos, uGNSS, sat2prn
import pandas as pd
import numpy as np
from .meas import obs_ideal, obs_exist, obs_exist_h, obs_full, obs_full_h
from .sat_column import GNSS_col
from numpy.linalg import norm
from .ephemeris_h import satposs_qc
from quality_check import rtkcmn as gn

def data_inte(Tcount, Acount):
    # satellite
    tcount_ = Tcount.copy()
    acount_ = Acount.copy()
    tcount_nan = np.where((tcount_ == 0.0), np.nan, tcount_)
    acount_nan = np.where((acount_ == 0.0), np.nan, acount_)
    acount_n = pd.DataFrame(acount_nan)
    tcount_n = pd.DataFrame(tcount_nan)
    data_ratio = acount_n/tcount_n
    inte_sat = data_ratio
    # system
    inte_sys = np.full([uGNSS.GNSSMAX, Tcount.shape[1]], np.nan)
    expt_sys = np.full([uGNSS.GNSSMAX, Tcount.shape[1]], np.nan)
    have_sys = np.full([uGNSS.GNSSMAX, Tcount.shape[1]], np.nan)

    inte_sys[uGNSS.GPS] = acount_n.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)
    inte_sys[uGNSS.GLO] = acount_n.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)
    inte_sys[uGNSS.BDS] = acount_n.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)
    inte_sys[uGNSS.GAL] = acount_n.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)
    inte_sys[uGNSS.QZS] = acount_n.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)
    inte_sys[uGNSS.SBS] = acount_n.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)
    inte_sys[uGNSS.IRN] = acount_n.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)/tcount_n.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)

    expt_sys[uGNSS.GPS] = tcount_n.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)
    expt_sys[uGNSS.GLO] = tcount_n.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)
    expt_sys[uGNSS.BDS] = tcount_n.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)
    expt_sys[uGNSS.GAL] = tcount_n.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)
    expt_sys[uGNSS.QZS] = tcount_n.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)
    expt_sys[uGNSS.IRN] = tcount_n.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)
    expt_sys[uGNSS.SBS] = tcount_n.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)

    have_sys[uGNSS.GPS] = acount_n.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)
    have_sys[uGNSS.GLO] = acount_n.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)
    have_sys[uGNSS.BDS] = acount_n.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)
    have_sys[uGNSS.GAL] = acount_n.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)
    have_sys[uGNSS.QZS] = acount_n.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)
    have_sys[uGNSS.SBS] = acount_n.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)
    have_sys[uGNSS.IRN] = acount_n.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)


    inte_sys = pd.DataFrame(inte_sys)
    expt_sys = pd.DataFrame(expt_sys)
    have_sys = pd.DataFrame(have_sys)
    inte_sys.replace(0, np.nan, inplace=True)
    expt_sys.replace(0, np.nan, inplace=True)
    have_sys.replace(0, np.nan, inplace=True)
    inte_qc = dict(zip(['sat', 'sys', 'expt', 'have'], [inte_sat.values, inte_sys.values, expt_sys.values, have_sys.values]))
    return inte_qc

def data_full(Pcount, Lcount):
    # satellite
    Pcount_ = Pcount.copy()
    Lcount_ = Lcount.copy()
    Pcount_nan = np.where((Pcount_ == 0.0), np.nan, Pcount_)
    Lcount_nan = np.where((Lcount_ == 0.0), np.nan, Lcount_)
    data_max = pd.DataFrame(np.maximum(Pcount_nan, Lcount_nan))
    data_min = pd.DataFrame(np.minimum(Pcount_nan, Lcount_nan))
    ful_sat = data_min/data_max

    ful_sys = np.full([uGNSS.GNSSMAX, Pcount.shape[1]], np.nan)
    min_sys = np.full([uGNSS.GNSSMAX, Pcount.shape[1]], np.nan)
    max_sys = np.full([uGNSS.GNSSMAX, Pcount.shape[1]], np.nan)
    ful_sys[uGNSS.GPS] = data_min.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)
    ful_sys[uGNSS.GLO] = data_min.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)
    ful_sys[uGNSS.BDS] = data_min.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)
    ful_sys[uGNSS.GAL] = data_min.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)
    ful_sys[uGNSS.QZS] = data_min.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)
    ful_sys[uGNSS.IRN] = data_min.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)
    ful_sys[uGNSS.SBS] = data_min.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)/data_max.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)

    min_sys[uGNSS.GPS] = data_min.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)
    min_sys[uGNSS.GLO] = data_min.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)
    min_sys[uGNSS.BDS] = data_min.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)
    min_sys[uGNSS.GAL] = data_min.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)
    min_sys[uGNSS.QZS] = data_min.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)
    min_sys[uGNSS.IRN] = data_min.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)
    min_sys[uGNSS.SBS] = data_min.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)

    max_sys[uGNSS.GPS] = data_max.loc[GNSS_col.GPS[0]:GNSS_col.GPS[1]-1, :].sum(axis=0)
    max_sys[uGNSS.GLO] = data_max.loc[GNSS_col.GLO[0]:GNSS_col.GLO[1]-1, :].sum(axis=0)
    max_sys[uGNSS.BDS] = data_max.loc[GNSS_col.BDS[0]:GNSS_col.BDS[1]-1, :].sum(axis=0)
    max_sys[uGNSS.GAL] = data_max.loc[GNSS_col.GAL[0]:GNSS_col.GAL[1]-1, :].sum(axis=0)
    max_sys[uGNSS.QZS] = data_max.loc[GNSS_col.QZS[0]:GNSS_col.QZS[1]-1, :].sum(axis=0)
    max_sys[uGNSS.IRN] = data_max.loc[GNSS_col.IRN[0]:GNSS_col.IRN[1]-1, :].sum(axis=0)
    max_sys[uGNSS.SBS] = data_max.loc[GNSS_col.SBS[0]:GNSS_col.SBS[1]-1, :].sum(axis=0)


    ful_sys = pd.DataFrame(ful_sys)
    min_sys = pd.DataFrame(min_sys)
    max_sys = pd.DataFrame(max_sys)
    ful_sys.replace(0, np.nan, inplace=True)
    min_sys.replace(0, np.nan, inplace=True)
    max_sys.replace(0, np.nan, inplace=True)
    ful_qc = dict(zip(['sat', 'sys', 'min', 'max'], [ful_sat.values, ful_sys.values, min_sys.values, max_sys.values]))
    return ful_qc

def ele_azi(obs, tepoch_sol_M, tepoch_sat_cod_M, nav, sta, sat_idx, P_mat, L_mat, cfg):
    ele = np.full([len(obs), uGNSS.MAXSAT], np.nan)  # ele
    azi = np.full([len(obs), uGNSS.MAXSAT], np.nan)  # azi

    inte_Tcount = np.zeros([uGNSS.MAXSAT, MAX_NFREQ])  # ideal number of observation
    inte_Acount = np.zeros([uGNSS.MAXSAT, MAX_NFREQ])  # real number of observation

    full_Pcount = np.zeros([uGNSS.MAXSAT, MAX_NFREQ])  # ideal number of observation
    full_Lcount = np.zeros([uGNSS.MAXSAT, MAX_NFREQ])  # real number of observation

    min_ele = np.deg2rad(cfg.elmin())  # Set the threshold

    motion_model = cfg.pos_kin()

    from .adjnav import adjnav
    eph_mat, geph_mat, seph_mat = adjnav(nav)
    nav.eph_mat = eph_mat
    nav.geph_mat = geph_mat
    nav.seph_mat = seph_mat

    for i in range(len(obs)):
        if len(obs[i].sat) == 0:
            continue
        if  motion_model == 0:
            if tepoch_sol_M[i].stat == 5:
                rr = tepoch_sol_M[i].rr[0:3]
            elif tepoch_sol_M[i].stat == 0:
                rr = tepoch_sol_M[i].rr[0:3]
            else:
                rr = tepoch_sol_M[i].sta_x
        else:
            if tepoch_sol_M[i].stat == 5:
                rr = tepoch_sol_M[i].rr[0:3]
            elif tepoch_sol_M[i].stat == 0:
                rr = tepoch_sol_M[i].rr[0:3]
            else:
                continue

        azv, elv = cs_azel_h(tepoch_sat_cod_M[i].rs, rr, tepoch_sat_cod_M[i].svh, tepoch_sat_cod_M[i].Vars, obs[i].sat, nav)

        for j in np.argsort(obs[i].sat):
            sat = obs[i].sat[j]
            # sys, prn = sat2prn(sat)
            # ele and azi
            az = azv[j]
            el = elv[j]
            azi[i, sat-1] = np.degrees(az)
            ele[i, sat-1] = np.degrees(el)


        for sat in sat_idx:

            sys, prn = sat2prn(sat)
            rs_sat, Vars_sat, svh_sat = satposs_qc(sat, obs[i].t, nav)
            azt, elt = cs_azel_h(rs_sat, rr, [svh_sat], [Vars_sat], [sat], nav)

            if elt >= min_ele:
                inte_Tcount[sat-1] += obs_ideal(sys, prn)
                inte_Acount[sat-1] += obs_exist_h(P_mat[sat-1, i].copy(), L_mat[sat-1, i].copy())

                p_idx, l_idx = obs_full_h(P_mat[sat-1, i].copy(), L_mat[sat-1, i].copy())
                full_Pcount[sat-1] += p_idx
                full_Lcount[sat-1] += l_idx

    return ele, azi, inte_Tcount, inte_Acount, full_Pcount, full_Lcount


def cs_azel_h(rs, rr, svh, Vars, sat_list, nav):
    pos = ecef2pos(rr)
    from .rtkcmn import geodist_h, satazel_h
    # geometric distance and elevation
    r, e = geodist_h(rs[:, 0:3], rr)
    az, el = satazel_h(pos, e)
    # save az el data
    sat_use = ck_rs(rs[:, 0:3], svh, Vars, sat_list, nav)
    azv = np.where((sat_use==0), np.nan, az)
    elv = np.where((sat_use==0), np.nan, el)
    return azv, elv

def ck_rs(rs, svh, Vars, sat_list, nav):
    sat_use = np.zeros(rs.shape[0])
    for i, sat in enumerate(sat_list):
        if norm(rs[i, 0:3]) < rCST.RE_WGS84:
            continue
        # if gn.satexclude(sat, Vars[i], svh[i], nav) == 1:
        #     continue
        sat_use[i] = 1
    return sat_use
