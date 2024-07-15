import numpy as np
from numpy.linalg import norm, lstsq
from .rtkcmn import rCST, ecef2pos, geodist, satazel, ionmodel, tropmodel, \
     Sol, uGNSS, timeadd, sat2prn, dops_h, xyz2enu, covecef, timediff, time2gpst,\
     chisqr, dops, Sat_, freqpos, rcvstds
from quality_check import rtkcmn as gn
from .ephemeris_h import satposs
import copy
import math
# Filsh test
from scipy.stats import f
# distribution
import scipy.stats as stats

NX =        4+4           # num of estimated parameters, pos + clock
NX_dop =    4           # num of estimated parameters, velocity + clock_drift
NX_F =      7           # /*PVA, dt*/
MAXITR =    10          #  max number of iteration or point pos
ERR_ION =   5.0         #  ionospheric delay Std (m)
ERR_TROP =  3.0         #  tropspheric delay Std (m)
ERR_SAAS =  0.3         #  Saastamoinen model error Std (m)
ERR_BRDCI = 0.5         #  broadcast ionosphere model error factor
ERR_CBIAS = 0.3         #  code bias error Std (m)
REL_HUMI =  0.7         #  relative humidity for Saastamoinen model
MIN_EL = np.deg2rad(5)  #  min elevation for measurement
MAX_GDOP =  30          #  max GDOP

VAR_POS =  30.0**2      # /* initial variance of receiver pos (m^2) */
VAR_VEL =  10.0**2      # /* initial variance of receiver vel ((m/s)^2) */
VAR_ACC =  10.0**2      # /* initial variance of receiver acc ((m/ss)^2) */


EFACT_GPS = 1.0                 # /* error factor: GPS */
EFACT_GLO = 1.5                 # /* error factor: GLONASS */
EFACT_GAL = 1.0                 # /* error factor: Galileo */
EFACT_QZS = 1.0                 # /* error factor: QZSS */
EFACT_BDS = 1.0                 # /* error factor: BeiDou */
EFACT_IRN = 1.5                 # /* error factor: IRNSS */
EFACT_SBS = 3.0                 # /* error factor: SBAS */

# variation of measurement
def varerr(nav, sys, el, snr):
    fact = 1.0
    if sys == uGNSS.GPS:
        fact *= EFACT_GPS
    elif sys == uGNSS.GLO:
        fact *= EFACT_GLO
    elif sys == uGNSS.GAL:
        fact *= EFACT_GAL
    elif sys == uGNSS.QZS:
        fact *= EFACT_QZS
    elif sys == uGNSS.SBS:
        fact *= EFACT_SBS
    elif sys == uGNSS.BDS:
        fact *= EFACT_BDS
    elif sys == uGNSS.IRN:
        fact *= EFACT_IRN
    else:
        fact *= EFACT_GPS

    s_el = np.sin(el)
    if s_el <= 0.0:
        return 0.0

    if snr <= 0:
        return 0.0

    a = 0.3
    b = 0.3
    var = a**2 + (b / s_el)**2

    var *= fact
    return var

# get tgd
def gettgd(sat, tgd, type=0):
    
    sys, _ = sat2prn(sat)
    if sys == uGNSS.GLO:
        return tgd[0]*rCST.CLIGHT
    else:
        return tgd[type]*rCST.CLIGHT
    
# /* psendorange with code bias correction -------------------------------------*/
def prange(nav, obs, i, tgd, cfg):
    # eph, stat = seleph(nav, obs.t, obs.sat[i])
    sys, prn = sat2prn(obs.sat[i])
    band_pos = cfg.pos_banpos()[sys]
    # band_pos = freqpos[sys].index(band_type)

    b1 = np.zeros(obs.P.shape[1])
    P1 = obs.P[i, band_pos]
    Vmea = 0.0
    if P1 == 0:
        return 0, Vmea

    Vmea = (ERR_CBIAS)**2
    tgd1 = gettgd(obs.sat[i], tgd[i], 0)
    tgd2 = gettgd(obs.sat[i], tgd[i], 1)
    if sys == uGNSS.GPS or sys == uGNSS.QZS:
        gamma = (gn.FREQL1/gn.FREQL2)**2
        b1[0] = tgd1
        b1[1] = gamma*tgd1

    elif sys == uGNSS.GLO:  # GLO
        glok = [1, -4, 5, 6, 1, -4, 5, 6, -2, -7, 0, -1, -2, -7, 0, -1, 4, -3, 3, 2, 4, -3, 3, 2, -5, -6, 0]
        gamma = ((gn.FREQ1_GLO+glok[prn-1]*0.56250E6)/(gn.FREQ2_GLO+glok[prn-1]*0.43750E6))**2
        tgd1_ = tgd1/(gamma-1)
        b1[0] = tgd1_
        b1[1] = gamma*tgd1_

    elif sys == uGNSS.GAL:  # GAL
        gamma = (gn.FREQL5/gn.FREQL1)**2
        b1[0] = gamma*tgd1
        b1[1] = tgd1
        b1[2] = gamma*tgd1 + (1-gamma)*tgd2

    elif sys == uGNSS.BDS:  # BDS
        if prn > 18:
            b1[0] = tgd1
            b1[1] = 0
        else:
            b1[0] = tgd1
            b1[1] = tgd2

    elif sys == uGNSS.IRN:  # IRN
        gamma = (gn.FREQs/gn.FREQL5)**2
        b1[0] = tgd1*gamma
        b1[1] = tgd1
    return P1 - b1[band_pos], Vmea

# /* pseudorange residuals -----------------------------------------------------*/
def rescode(iter, obs, nav, rs, dts, Vars, svh, tgd, x, gross_idx, cfg):
    ns = len(obs.sat)  # measurements
    # trace(4, 'rescode : n=%d\n' % ns)
    v = np.zeros(ns+NX-3)
    H = np.zeros((ns+NX-3, NX))
    mask = np.zeros(NX-3) # clk states
    azv = np.zeros(ns)
    elv = np.zeros(ns)
    azt = np.zeros(ns) # DOP
    elt = np.zeros(ns)
    cnr = np.zeros(ns) # C/N0
    var = np.zeros(ns+NX-3)
    vsat = np.zeros(ns, dtype=int)
    resp = np.zeros(ns)
    satpos = np.zeros(ns)
    
    rr = x[0:3].copy()
    dtr = x[3].copy()
    pos = ecef2pos(rr)

    rcvstds(nav, obs) # decode stdevs from receiver
    
    nv = 0
    ns = 0
    for i, _ in enumerate(obs.sat):
        sys, prn = sat2prn(obs.sat[i])

        if norm(rs[i, :]) < rCST.RE_WGS84:
            continue

        if gn.satexclude(obs.sat[i], Vars[i], svh[i], nav) == 1:
            continue

        # geometric distance and elevation mask and C/N0 mask
        r, e = geodist(rs[i][0:3], rr)
        az, el = satazel(pos, e)
        # save az el data
        azv[i] = az
        elv[i] = el

        if r < 0 or el < np.deg2rad(cfg.pos_elcut()) or obs.S[i, cfg.pos_banpos()[sys]] < cfg.pos_cnrcut():
            continue

        if gross_idx[i] == 1:
            continue

        # psendorange with code bias correction
        P, Vmea = prange(nav, obs, i, tgd, cfg)

        if P == 0:
            continue

        if iter > 0:
            # # ionospheric correction
            if cfg.ionoopt() == 0:
                dion = 0
                dion_var = 5**2
            elif cfg.ionoopt() == 1:
                dion = ionmodel(obs.t, pos, az, el, nav.ion_gps)
                dion_var = (0.5*dion)**2
                freq = gn.sat2freq(obs.freq[i], 0)
                dion *= (gn.FREQL1/freq)**2
            else:
                print('SPP not surpport this ionospheric correction option!!!')
            # tropospheric correction
            if cfg.tropopt() == 0:
                dtrp = 0
                dtrop_var = 3**2
            elif cfg.tropopt() == 1:
                trop_hs, trop_wet, _ = tropmodel(obs.t, pos, el, REL_HUMI)
                # mapfh, mapfw = tropmapf(obs.t, pos, el)
                mapfh = 1
                mapfw = 1
                dtrp = mapfh * trop_hs + mapfw * trop_wet
                dtrop_var = (0.3/(np.sin(el)+0.01))**2
            else:
                print('SPP not surpport this tropspheric correction option!!!')
        else:
            dion = dtrp = 0
            dion_var = 5**2
            dtrop_var = 3**2

        # DOP ELE AZI
        azt[nv] = az
        elt[nv] = el

        # pseudorange residual
        v[nv] = P-(r+dtr-rCST.CLIGHT*dts[i][0]+dion+dtrp)

        # design matrix 
        H[nv, 0:3] = -e
        H[nv, 3] = 1
        # time system offset and receiver bias correction
        if sys == uGNSS.GLO:
            v[nv] -= x[4]
            H[nv, 4] = 1.0
            mask[1] = 1
        elif sys == uGNSS.GAL:
            v[nv] -= x[5]
            H[nv, 5] = 1.0
            mask[2] = 1
        elif sys == uGNSS.BDS:
            v[nv] -= x[6]
            H[nv, 6] = 1.0
            mask[3] = 1
        elif sys == uGNSS.IRN:
            v[nv] -= x[7]
            H[nv, 7] = 1.0
            mask[4] = 1
        else:
            mask[0] = 1
            
        # azv[i] = az
        # elv[i] = el
        cnr[nv] = obs.S[i][0]
        VARr = varerr(nav, sys, el, obs.S[i][cfg.pos_banpos()[sys]])
        vcc = VARr + Vars[i] + dion_var + dtrop_var + Vmea
        var[nv] = vcc
        resp[nv] = v[nv]
        satpos[nv] = i
        # if satellite is used flag
        vsat[i] = 1
        nv += 1
        ns += 1

    # constraint to avoid rank-deficient
    for i in range(NX-3):
        if mask[i] == 0:
            v[nv] = 0.0
            H[nv, i+3] = 1
            var[nv] = 0.01
            nv += 1

    v = v[0:nv]
    H = H[0:nv, :]
    var = var[0:nv]
    P = np.zeros((H.shape[0], H.shape[0]))
    for i in range(nv):
        P[i, i] = 1/var[i]
    # DOP ELE AZI
    elt = elt[0:ns]
    azt = azt[0:ns]
    satpos = satpos[0:ns]

    if iter > 1 and ns > 4:
        v, H, P, satpos, vsat, gross_idx = robust_code_IQR(v, H, P, ns, vsat, satpos, gross_idx)
        nv = len(v)
        ns = np.count_nonzero(vsat == 1)
    return v, H, azv, elv, azt, elt, var, vsat, resp, nv, ns, P, satpos, gross_idx

# robust
def robust_code(v0, H0, P0, ns, vsat, satpos):
    nv0 = np.size(H0, 0)
    n1 = np.size(H0, 1)
    exc = np.zeros(nv0)
    n = 0
    MAX_DISTANCE = 10
    v = np.zeros(nv0)
    H = np.zeros([nv0, n1])
    P = np.zeros([nv0, nv0])
    ave_distance = np.zeros(nv0)
    for i in range(ns):
        vi = np.abs(v0[i])
        if vi < MAX_DISTANCE:
            continue
        v_other = np.abs(v0[0:ns])
        v_other = np.delete(v_other, (i), axis=0)
        ave_v = np.sum(abs(v_other))/(ns-1)
        ave_distance[i] = np.sum(np.abs(vi-v_other))/(ns-1)
        if ave_distance[i] > 3*ave_v and ave_distance[i] > 10:
            exc[i] = 1

    for i in range(nv0):
        if exc[i] == 1:
            vsat[int(satpos[i])] = 0
            continue
        v[n] = v0[i]
        H[n, :] = H0[i, :]
        P[n, n] = P0[i, i]
        n = n + 1

    if n < nv0:
        v = v[0:n]
        H = H[0:n, :]
        P = P[0:n, 0:n]
    return v, H, P, vsat


# robust
def robust_code_3s(v0, H0, P0, ns, vsat, satpos0, gross_idx):
    vec_x = np.linalg.inv(H0.T@P0@H0)@H0.T@P0@v0
    vec_v = H0@vec_x - v0

    nv0 = np.size(H0, 0)
    n1 = np.size(H0, 1)
    exc = np.zeros(nv0)

    v = np.zeros(nv0)
    H = np.zeros([nv0, n1])
    P = np.zeros([nv0, nv0])

    Zgama_square = 0
    vec_v_mean = np.mean(vec_v[0:ns])
    for i in range(ns):
        Zgama_square =  Zgama_square + ((vec_v[i] - vec_v_mean)**2/(ns-1))
    Zgama = np.sqrt(Zgama_square)

    vec_v_abs = abs(vec_v[0:ns])

    for i in range(ns):
        if vec_v_abs[i] > 3*Zgama and vec_v_abs[i] > 10:
            exc[i] = 1

    n = 0
    for i in range(nv0):
        if exc[i] == 1:
            vsat[int(satpos0[i])] = 0
            gross_idx[int(satpos0[i])] = 1
            continue
        v[n] = v0[i]
        H[n, :] = H0[i, :]
        P[n, n] = P0[i, i]
        n = n + 1

    if n < nv0:
        v = v[0:n]
        H = H[0:n, :]
        P = P[0:n, 0:n]

    satpos = np.delete(satpos0, np.where(exc == 1)[0], axis=0)
    return v, H, P, satpos, vsat, gross_idx

# robust
def robust_code_IQR(v0, H0, P0, ns, vsat, satpos0, gross_idx):
    vec_x = np.linalg.inv(H0.T@P0@H0)@H0.T@P0@v0
    vec_v = H0@vec_x - v0

    nv0 = np.size(H0, 0)
    n1 = np.size(H0, 1)
    exc = np.zeros(nv0)

    v = np.zeros(nv0)
    H = np.zeros([nv0, n1])
    P = np.zeros([nv0, nv0])

    vec_v_abs = abs(vec_v[0:ns])
    Q1 = np.percentile(vec_v_abs[0:ns], 25)
    Q3 = np.percentile(vec_v_abs[0:ns], 75)
    IQR = Q3 - Q1

    threshold = 1.5*IQR

    for i in range(ns):
        if (vec_v_abs[i] > Q3 + threshold) and (vec_v_abs[i] > 10):
            exc[i] = 1

    n = 0
    for i in range(nv0):
        if exc[i] == 1:
            vsat[int(satpos0[i])] = 0
            gross_idx[int(satpos0[i])] = 1
            continue
        v[n] = v0[i]
        H[n, :] = H0[i, :]
        P[n, n] = P0[i, i]
        n = n + 1

    if n < nv0:
        v = v[0:n]
        H = H[0:n, :]
        P = P[0:n, 0:n]

    satpos = np.delete(satpos0, np.where(exc == 1)[0], axis=0)
    return v, H, P, satpos, vsat, gross_idx

def LU(A):
    import numpy as np
    import scipy.linalg
    P, L, U = scipy.linalg.lu(A)
    A_inv = np.linalg.inv(U).dot(np.linalg.inv(L)).dot(np.linalg.inv(P))
    return A_inv

# estimate position and clock errors with standard precision
def estpos(obs, nav, rs, dts, svh, tgd, sta, Vars, sol, cfg):
    
    x = np.zeros(NX)
    # x[0:3] = sta.pos
    # sol = Sol()
    if sta.pos[0] != 0 and sol.rr[0] ==0:
        x[0:3] = sta.pos[0:3]
    else:
        x[0:3] = sol.rr[0:3]
    sol = copy.deepcopy(Sol())

    # trace(3, 'estpos  : n=%d\n' % len(rs))
    gross_idx = np.zeros(len(obs.sat))
    for iter in range(MAXITR):
        # iter = 0
        sat_ = Sat_() # temporary data
        v, H, az, el, az_dop, el_dop, var, vsat, resp, nv, ns, P, satpos, gross_idx = rescode(iter, obs, nav, rs[:, 0:3], dts, Vars, svh, tgd, x, gross_idx, cfg)
        sat_.vsat = vsat
        sat_.az = az
        sat_.el = el
        sat_.resp = resp
        # new add
        sat_.v = v
        sat_.ns = ns
        sat_.satpos = satpos
        sat_.H = H
        sat_.Q= np.linalg.inv(P)
        if nv < NX:
            # trace(3, 'estpos: lack of valid sats nsat=%d nv=%d\n' %
            #       (len(obs.sat), nv))
            sol.stat = -1
            stat_v = -1
            return sol, vsat, stat_v, sat_

        v_p = v.copy()
        H_p = H.copy()
        P_ = P.copy()
        try:
            dx = np.linalg.inv(H_p.T @ P_ @ H_p) @ H_p.T @ P_ @ v_p
            Q = np.linalg.inv(H_p.T@P_@H_p)
        except Exception as e:
            dx = np.linalg.pinv(H_p.T @ P_ @ H_p) @ H_p.T @ P_ @ v_p
            Q = np.linalg.pinv(H_p.T@P_@H_p)

        x += dx
        if np.dot(dx, dx) < 1e-4:
            break
    else: # exceeded max iterations
        sol.stat = gn.SOLQ_NONE

    sol.t = timeadd(obs.t, -x[3]/rCST.CLIGHT)
    # clock
    sol.dtr = x[3:]/rCST.CLIGHT
    # position + velity
    sol.rr[0:3] = x[0:3]
    sol.rr[3:6] = np.zeros(3)
    # variance and covariance
    sol.qr[0] = Q[0, 0]
    sol.qr[1] = Q[1, 1]
    sol.qr[2] = Q[2, 2]
    sol.qr[3] = Q[0, 1]
    sol.qr[4] = Q[1, 2]
    sol.qr[5] = Q[0, 2]
    # DOP
    sol.dop = dops(az_dop, el_dop, 0)
    # sat number
    sol.ns = ns

    # /* validate solution */
    stat_v = valsol(v, P, vsat, az, el) # n: the number of satellites；nv: the number of equations; nx:parameter
    # stat_v = 1
    # epoch is normal
    if stat_v == 1:
        sol.stat = gn.SOLQ_SINGLE

    return sol, vsat, stat_v, sat_

# /* validate solution ---------------------------------------------------------*/
def valsol(v, P, vsat, az, el):
    v_ = v.copy()
    stat = 1
    nx = NX

    # /* Chi-square validation of residuals */
    nv = len(v_)
    var = np.linalg.inv(P)
    v_t = v_/np.diagonal(np.sqrt(var))
    vv = np.dot(v_t, v_t)
    if nv > nx and vv > chisqr[nv-nx-1]:
        stat = 0
        return stat

    # /* large GDOP check */
    ns = 0
    n = len(vsat)
    azs = np.zeros(len(az))
    els = np.zeros(len(el))
    for i in range(n):
        if vsat[i] == 0:
            continue
        azs[ns] = az[i]
        els[ns] = el[i]
        ns += 1
    azs = azs[0:ns]
    els = els[0:ns]
    dop = dops(azs, els, 0)
    if dop[0] <= 0.0 or dop[0] > MAX_GDOP:
        stat = 0
        return stat
    return stat


def w_test(v, H, Q, ns, vsat, sat_pos, obs, nav, rs, dts, svh, sol, sta, Vars, tgd, cfg):
    Q_inv = np.linalg.inv(Q)
    Pa = H@np.linalg.inv(H.T@Q_inv@H)@H.T@Q_inv
    Pa_ = np.eye(Q.shape[0]) - Pa
    Q_e = Pa_@Q@Pa_.T

    alpha = 0.01
    n = ns
    out_index = []
    e = v[0:n]
    Q_inv_ = Q_inv[0:n, 0:n]
    Q_e_ = Q_e[0:n, 0:n]
    w = np.zeros(n)
    for i in range(n):
        c = np.zeros((n, 1))
        c[i] = 1
        w[i] = np.fabs((c.T@Q_inv_@e)/math.sqrt(c.T@Q_inv_@Q_e_@Q_inv_@c))

    from scipy.stats import norm
    threshold = norm.ppf(1-alpha/2)
    max_index = np.argmax(w)
    if math.fabs(w[max_index]) >= threshold:
        out_index.append(int(sat_pos[max_index]))
        vsat[int(sat_pos[max_index])] = 0

    # exclude a satellite
    from .rtkcmn import Obs
    obs_tmp = copy.deepcopy(Obs())
    obs_tmp.P = np.delete(obs.P.copy(), out_index, axis=0)
    obs_tmp.L = np.delete(obs.L.copy(), out_index, axis=0)
    obs_tmp.S = np.delete(obs.S.copy(), out_index, axis=0)
    obs_tmp.D = np.delete(obs.D.copy(), out_index, axis=0)
    obs_tmp.freq = np.delete(obs.freq.copy(), out_index, axis=0)
    obs_tmp.sat = np.delete(obs.sat.copy(), out_index, axis=0)
    obs_tmp.lli = np.delete(obs.lli.copy(), out_index, axis=0)
    obs_tmp.Lstd = np.delete(obs.Lstd.copy(), out_index, axis=0)
    obs_tmp.Pstd = np.delete(obs.Pstd.copy(), out_index, axis=0)
    obs_tmp.t = copy.deepcopy(obs.t)

    rs_tmp = np.delete(rs.copy(), out_index, axis=0)
    dts_tmp = np.delete(dts.copy(), out_index, axis=0)
    svh_tmp = np.delete(svh.copy(), out_index, axis=0)
    tgd_tmp = np.delete(tgd.copy(), out_index, axis=0)
    Vars_tmp = np.delete(Vars.copy(), out_index, axis=0)

    sol_tmp = copy.deepcopy(sol)

    # lsq
    sol_tmp, vsat_tmp, stat_v, sat_tmp = estpos(obs_tmp, nav, rs_tmp, dts_tmp, svh_tmp, tgd_tmp, sta, Vars_tmp, sol_tmp, cfg)
    # estpos(obs, nav, rs, dts, svh, tgd, sta, Vars, sol, cfg)

    return sol_tmp, vsat, stat_v, sat_tmp

# estimate position and clock errors with standard precision
# %receiver autonomous integrity monitoring, failure detection and exclution
# %only detect and exclude a faulty satellite
def raim_fde(obs, nav, rs, dts, svh, sol, sat_, sta, Vars, tgd, cfg):
    stat = 0
    rms_max = 100
    nobs = len(obs.sat)
    # obs_tmp = obs
    # rs_tmp = rs.copy()
    # dts_tmp = dts.copy()
    # svh_tmp = svh.copy()
    for i in range(nobs):
        # exclude a satellite
        from .rtkcmn import Obs
        obs_tmp = copy.deepcopy(Obs())
        obs_tmp.P    = np.delete(obs.P.copy(), (i), axis=0)
        obs_tmp.L    = np.delete(obs.L.copy(), (i), axis=0)
        obs_tmp.S    = np.delete(obs.S.copy(), (i), axis=0)
        obs_tmp.D    = np.delete(obs.D.copy(), (i), axis=0)
        obs_tmp.freq = np.delete(obs.freq.copy(), (i), axis=0)
        obs_tmp.sat  = np.delete(obs.sat.copy(), (i), axis=0)
        obs_tmp.lli  = np.delete(obs.lli.copy(), (i), axis=0)
        obs_tmp.Lstd = np.delete(obs.Lstd.copy(), (i), axis=0)
        obs_tmp.Pstd = np.delete(obs.Pstd.copy(), (i), axis=0)
        obs_tmp.t = copy.deepcopy(obs.t)

        rs_tmp       = np.delete(rs.copy(), (i), axis=0)
        dts_tmp      = np.delete(dts.copy(), (i), axis=0)
        svh_tmp      = np.delete(svh.copy(), (i), axis=0)
        tgd_tmp      = np.delete(tgd.copy(), (i), axis=0)
        Vars_tmp     = np.delete(Vars.copy(), (i), axis=0)

        sol_tmp = copy.deepcopy(sol)

        # lsq
        sol_tmp, vsat_tmp, stat_v, sat_tmp = estpos(obs_tmp, nav, rs_tmp, dts_tmp, svh_tmp, tgd_tmp, sta, Vars_tmp, sol_tmp, cfg)
        #estpos(obs, nav, rs, dts, svh, tgd, sta, Vars, sol, cfg)

        if stat_v == 0:
            continue

        resp_tmp = sat_tmp.resp
        rms = 0
        nvsat = 0
        for j in range(nobs-1):
            if vsat_tmp[j] == 0:
                continue
            rms = rms + resp_tmp[j]**2
            nvsat = nvsat + 1
        if nvsat < 5:
            continue
        rms_ave = np.sqrt(rms/nvsat)
        if rms_ave > rms_max:
            continue

        # save result
        m = 0
        for j in range(nobs):
            if j == i:
                continue
            sat_.az[j] = sat_tmp.az[m]
            sat_.el[j] = sat_tmp.el[m]
            sat_.vsat[j] = sat_tmp.vsat[m]
            sat_.resp[j] = sat_tmp.resp[m]
            m = m + 1
        stat = 1
        sol = sol_tmp
        rms_max = rms_ave
        sat_.vsat[i] = 0

    return sol, sat_, stat

# robust
def robust_dop(v0, H0, P0):
    nv0 = np.size(H0, 0)
    n1 = np.size(H0, 1)
    exc = np.zeros(nv0)
    n = 0
    MAX_DISTANCE = 0.2
    v = np.zeros(nv0)
    H = np.zeros([nv0, n1])
    P = np.zeros([nv0, nv0])
    ave_distance = np.zeros(nv0)
    for i in range(nv0):
        vi = np.abs(v0[i])
        if vi < MAX_DISTANCE:
            continue
        v_other = np.abs(v0)
        v_other = np.delete(v_other, (i), axis=0)
        ave_v = np.sum(abs(v_other))/(nv0-1)
        ave_distance[i] = np.sum(np.abs(vi-v_other))/(nv0-1)
        if ave_distance[i] > 3*ave_v and ave_distance[i] > 10:
            exc[i] = 1

    for i in range(nv0):
        if exc[i] == 1:
            continue
        v[n] = v0[i]
        H[n, :] = H0[i, :]
        P[n, n] = P0[i, i]
        n = n + 1

    if n < nv0:
        v = v[0:n]
        H = H[0:n, :]
        P = P[0:n, 0:n]
    return v, H, P

# calculate code residuals
def resdop(obs, nav, rs, dts, svh, rr, x, vsat): # rr:sol result, x:receiver speed
    
    ns = len(obs.sat)  # measurements

    v = np.zeros(ns+NX_dop-3)
    H = np.zeros((ns+NX_dop-3, NX_dop))
    var = np.zeros(ns+NX_dop-3)
    # sig = np.zeros(ns+NX_dop-3)

    pos = ecef2pos(rr[0:3])
    E = xyz2enu(pos)

    rcvstds(nav, obs)  # decode stdevs from receiver

    nv = 0
    for i in np.argsort(obs.sat):
        sys = sat2prn(obs.sat[i])[0]
        freq = obs.freq[i][0]
        # if sys != uGNSS.GPS:
        #     continue

        if obs.D[i][0] == 0.0 or freq == 0 or vsat[i] == 0 or norm(rs[i][3:6]) <= 0.0:
            continue

        # geometric distance and elevation mask
        r, e = geodist(rs[i][0:3], rr[0:3])
        if r < 0:
            continue
        az, el = satazel(pos, e)

        # /* satellite velocity relative to receiver in ECEF */
        vs = rs[i][3:6] - x[0:3]

        # /* range rate with earth rotation correction */
        rate = np.dot(vs, e)+rCST.OMGE/rCST.CLIGHT*(rs[i][4]*rr[0]+rs[i][1]*x[0]-rs[i][3]*rr[1]-rs[i][0]*x[1])

        # /* Std of range rate error (m/s) */
        # sig = 1.0
        sig = 1

        # /* range rate residual (m/s) */
        v[nv] = (-obs.D[i][0]*rCST.CLIGHT/freq-(rate+x[3]-rCST.CLIGHT*dts[i][1]))/sig # dts[1] = 0.0

        # design matrix
        H[nv, 0:3] = -e
        H[nv, 3] = 1

        # variance
        var[nv] = 0.05**2

        nv += 1

    # # constraint to avoid rank-deficient
    # for i in range(NX_dop - 3):
    #     v[nv] = 0.0
    #     H[nv, i+4] = 1
    #     var[nv] = 0.01
    #     nv += 1

    v = v[0:nv]
    H = H[0:nv, :]
    var = var[0:nv]
    P = np.zeros((H.shape[0], H.shape[0]))
    for i in range(nv):
        P[i, i] = 1/var[i]
    # exclude gross errors
    v, H, P = robust_dop(v, H, P)
    nv = len(v)
    return v, H, P, nv

# /* estimate receiver velocity */
def estvel(obs, nav, rs, dts, svh, sol, vsat):
  
    rr = sol.rr
    x = np.zeros(NX_dop)

    for iter in range(MAXITR):
        v, H, P, nv = resdop(obs, nav, rs, dts, svh, rr, x, vsat)
        # nv = len(v)
        if nv < NX_dop:
            return sol, vsat

        dx = np.linalg.inv(H.T @ P @ H) @ H.T @ P @ v

        # # least square estimation
        # dx = lstsq(H, v, rcond=None)[0]
        x += dx
        if np.dot(dx, dx) < 1e-4:
            break

    sol.rr[3:6] = x[0:3]
    sol.dtrd = x[3]
    return sol, vsat

# BDS2 MP correct
def bds2mp_corr(obs, el):
    IGSOCOEF = np.array([[-0.55, -0.40, -0.34, -0.23, -0.15, -0.04, 0.09, 0.19, 0.27, 0.35],  # B1
                         [-0.71, -0.36, -0.33, -0.19, -0.14, -0.03, 0.08, 0.17, 0.24, 0.33],  # B2
                         [-0.27, -0.23, -0.21, -0.15, -0.11, -0.04, 0.05, 0.14, 0.19, 0.32]]) # B3
    MEOCOEF = np.array([[-0.47, -0.38, -0.32, -0.23, -0.11, 0.06, 0.34, 0.69, 0.97, 1.05],  # B1
                        [-0.40, -0.31, -0.26, -0.18, -0.06, 0.09, 0.28, 0.48, 0.64, 0.69],  # B2
                        [-0.22, -0.15, -0.13, -0.10, -0.04, 0.05, 0.14, 0.27, 0.36, 0.47]]) # B3

    nobs = len(obs.sat)
    for i in np.argsort(obs.sat):
        sat = obs.sat[i]
        sys, prn = sat2prn(sat)
        if sys != uGNSS.BDS:
            continue
        if prn < 5:
            continue
        el_ = np.rad2deg(el)
        if el_ <= 0:
            continue
        dmp = np.zeros(3)
        a = el_*0.1
        b = np.fix(a)
        BD2_GEO = np.array([1, 2, 3, 4, 5])
        BD2_IGSO = np.array([6, 7, 8, 9, 10, 13, 16])
        BD2_MEO = np.array([11, 12, 14])
        if prn in BD2_IGSO:
            if b < 0:
                dmp = IGSOCOEF[0:4, 0]
            elif b >= 9:
                dmp = IGSOCOEF[0:4, 9]
            else:
                for j in range(3):
                    dmp[j] = IGSOCOEF[j, b]*(1-a+b) + IGSOCOEF[j, b+1]*(a-b)
        elif prn in BD2_MEO:
            if b < 0:
                dmp = MEOCOEF[0:4, 0]
            elif b >= 9:
                dmp = MEOCOEF[0:4, 9]
            else:
                for j in range(3):
                    dmp[j] = MEOCOEF[j, b]*(1-a+b) + MEOCOEF[j, b+1]*(a-b)
        BD2_frq = np.array([0, 1, 3]) # 0: B1 1:B2 2:B3
        for j in range(len(BD2_frq)):
            obs.P[i, BD2_frq[j]] = obs.P[i, BD2_frq[j]] + dmp[j]
    return obs

def pntpos(obs, nav, sta, sol, cfg):
    from .rtkcmn import Sac
    try:
        rs, Vars, dts, svh, tgd = satposs(obs, nav)
    except Exception as e:
        print(e)
    sac = copy.deepcopy(Sac())
    sac.rs = rs
    sac.Vars = Vars
    sac.svh = svh

    # if len(obs.sat) < 4:
    #     stat_v = 0
    #     vsat = np.zeros(len(obs.sat), dtype=int)
    #     return sol, stat_v, vsat, sac

    sol, vsat, stat_v, sat_ = estpos(obs, nav, rs, dts, svh, tgd, sta, Vars, sol, cfg)
    if stat_v >= 0:
        # if stat_v == 0 and len(obs.sat) >= 6:
        #     sol, sat_, stat_v = raim_fde(obs, nav, rs, dts, svh, sol, sat_, sta, Vars, tgd, cfg)

        if stat_v == 0 and len(obs.sat) > 4:
            sol, vsat, stat_v, sat_ = w_test(sat_.v, sat_.H, sat_.Q, sat_.ns, vsat, sat_.satpos, obs, nav, rs, dts, svh, sol, sta, Vars, tgd, cfg)

        sol, vsat = estvel(obs, nav, rs, dts, svh, sol, vsat)
    return sol, stat_v, vsat, sac
