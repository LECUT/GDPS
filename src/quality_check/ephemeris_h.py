import numpy as np
from .rtkcmn import uGNSS, rCST, timediff, timeadd, time2epoch
from .rtkcmn import sat2prn

# ephemeris parameters
MAX_ITER_KEPLER = 30
RTOL_KEPLER = 1e-13
TSTEP = 120 #60.0  # time step for Glonass orbital calcs
ERREPH_GLO = 5.0

MAXDTOE = 7200.0                  # /* max time difference to GPS Toe (s) */
MAXDTOE_QZS = 7200.0              # /* max time difference to QZSS Toe (s) */
MAXDTOE_GAL = 14400.0             # /* max time difference to Galileo Toe (s) */
MAXDTOE_BDS = 21600.0             # /* max time difference to BeiDou Toe (s) */
MAXDTOE_GLO = 1800.0              # /* max time difference to GLONASS Toe (s) */
MAXDTOE_IRN = 7200.0              # /* max time difference to IRNSS Toe (s) */
MAXDTOE_SBS = 360.0               # /* max time difference to SBAS Toe (s) */
MAXDTOE_S   = 86400.0             # /* max time difference to ephem toe (s) for other */
MAXGDOP     = 300.0               # /* max GDOP */

eph_sel = np.array([#/* GPS,GLO,GAL,QZS,BDS,IRN,SBS */
                   0, 0, 1, 0, 0, 0, 0])

def var_uraeph(sys, ura):
    STD_GAL_NAPA = 500.0
    ura_value = np.array([2.4, 3.4, 4.85, 6.85, 9.65, 13.65, 24.0, 48.0, 96.0, 192.0, 384.0, 768.0, 1536.0, 3072.0, 6144.0])
    ura = ura
    if sys == uGNSS.GAL:
        if ura <= 49:
            var = (ura*0.01)**2
            return var
        if ura <= 74:
            var = (0.5+(ura-50)*0.02)**2
            return var
        if ura <= 99:
            var = (1.0+(ura-75)*0.04)**2
            return var
        if ura <= 125:
            var = (2.0+(ura-100)*0.16)**2
            return var
        var = STD_GAL_NAPA**2
    else:
        if ura < 0 or ura > 14:
            var = 6144**2
        else:
            var = ura_value[ura]**2
    return var

def setseleph(sys, sel):
    if sys == uGNSS.GPS:
        eph_sel[0] = sel
    elif sys == uGNSS.GLO:
        eph_sel[1] = sel
    elif sys == uGNSS.GAL:
        eph_sel[2] = sel
    elif sys == uGNSS.QZS:
        eph_sel[3] = sel
    elif sys == uGNSS.BDS:
        eph_sel[4] = sel
    elif sys == uGNSS.IRN:
        eph_sel[5] = sel
    elif sys == uGNSS.SBS:
        eph_sel[6] = sel

def getseleph(sys):
    if sys == uGNSS.GPS:
        return eph_sel[0]
    elif sys == uGNSS.GLO:
        return eph_sel[1]
    elif sys == uGNSS.GAL:
        return eph_sel[2]
    elif sys == uGNSS.QZS:
        return eph_sel[3]
    elif sys == uGNSS.BDS:
        return eph_sel[4]
    elif sys == uGNSS.IRN:
        return eph_sel[5]
    elif sys == uGNSS.SBS:
        return eph_sel[6]

def dtadjust(t1, t2, tw=604800):
    dt = timediff(t1, t2)
    if dt > tw:
        dt -= tw
    elif dt < -tw:
        dt += tw
    return dt

def sva2ura(sys, sva):
    ura_nominal = [[2.4, 3.4, 4.85, 6.85, 9.65, 13.65, 24.0, 48.0, 96.0, 192.0, 384.0, 768.0, 1536.0, 3072.0, 6144.0]]
    if sys == uGNSS.GAL:  #galileo sisa
       if sva <= 49:
           return (sva*0.01)**2
       if sva <= 74:
           return (0.5+(sva - 50)*0.02)**2
       if sva <= 99:
           return (1.0+(sva - 75)*0.04)**2
       if sva <= 125:
           return (2.0+(sva - 100)*0.16)**2
       return 500**2
    else: # gps ura
        if sva < 0 or sva > 14: return 6144**2
        return ura_nominal[int(sva)]

def eph2pos(t, eph):
    tk = timediff(t, eph.toe)
    sys, _ = sat2prn(eph.sat)
    if sys == uGNSS.GAL:
        mu = rCST.MU_GAL
        omge = rCST.OMGE_GAL
    elif sys == uGNSS.BDS:
        mu = rCST.MU_BDS
        omge = rCST.OMGE_BDS
    else:  # GPS,QZS,IRN
        mu = rCST.MU_GPS
        omge = rCST.OMGE

    M = eph.M0 + (np.sqrt(mu / eph.A**3) + eph.deln) * tk
    M = M +2*np.pi
    E, Ek = M, 0
    for _ in range(MAX_ITER_KEPLER):
        if abs(E - Ek) < RTOL_KEPLER:
            break
        Ek = E
        E -= (E - eph.e * np.sin(E) - M) / (1.0 - eph.e * np.cos(E))

    sinE, cosE = np.sin(E), np.cos(E)
    nus = np.sqrt(1.0 - eph.e**2) * sinE
    nuc = cosE - eph.e
    nue = 1.0 - eph.e * cosE
    u = np.arctan2(nus, nuc) + eph.omg
    r = eph.A * nue 
    i = eph.i0 + eph.idot * tk
    sin2u, cos2u = np.sin(2*u), np.cos(2*u)

    # k1 = eph.cus * sin2u + eph.cuc * cos2u
    # k2 = eph.crs * sin2u + eph.crc * cos2u
    # k3 = eph.cis * sin2u + eph.cic * cos2u
    u += eph.cus * sin2u + eph.cuc * cos2u
    r += eph.crs * sin2u + eph.crc * cos2u
    i += eph.cis * sin2u + eph.cic * cos2u
    x = r * np.cos(u)
    y = r * np.sin(u)
    cosi = np.cos(i)
    if sys == uGNSS.BDS and (sat2prn(eph.sat)[1] <= 5 or sat2prn(eph.sat)[1] >= 59):
        O = eph.OMG0 + eph.OMGd * tk - omge * eph.toes
        sinO, cosO = np.sin(O), np.cos(O)
        xg = x*cosO - y*np.cos(i)*sinO
        yg = x*sinO + y*np.cos(i)*cosO
        zg = y*np.sin(i)
        sino = np.sin(omge*tk)
        coso = np.cos(omge*tk)
        SIN_5 = -0.0871557427476582 # /* sin(-5.0 deg) */
        COS_5 = 0.9961946980917456 # /* cos(-5.0 deg) */
        rs = [xg*coso+yg*sino*COS_5+zg*sino*SIN_5, -xg*sino+yg*coso*COS_5+zg*coso*SIN_5, -yg*SIN_5+zg*COS_5]
    else:
        O = eph.OMG0 + (eph.OMGd - omge) * tk - omge * eph.toes
        sinO, cosO = np.sin(O), np.cos(O)
        rs = [x*cosO - y*cosi*sinO, x*sinO + y*cosi*cosO, y*np.sin(i)]

    tk = timediff(t, eph.toc)

    dts = np.zeros(2)
    dts[0] = eph.f0 + eph.f1 * tk + eph.f2 * tk**2
    # relativity correction
    dts[0] -= 2 *np.sqrt(mu * eph.A) * eph.e * sinE / rCST.CLIGHT**2

    var = var_uraeph(sys, int(eph.sva))

    return rs, var, dts

def deq(x, acc):
    xdot = np.zeros(6)

    r2 = np.dot(x[0:3], x[0:3])
    if r2 <= 0.0:
        return xdot
    r3 = r2 * np.sqrt(r2)
    omg2 = rCST.OMGE_GLO**2

    a = 1.5 * rCST.J2_GLO * rCST.MU_GLO * rCST.RE_GLO**2 / r2 / r3 
    b = 5.0 * x[2]**2 / r2 
    c = -rCST.MU_GLO / r3 - a * (1.0 - b)
    xdot[0:3] = x[3:6]
    xdot[3] = (c + omg2) * x[0] + 2.0 * rCST.OMGE_GLO * x[4] + acc[0]
    xdot[4] = (c + omg2) * x[1] - 2.0 * rCST.OMGE_GLO * x[3] + acc[1]
    xdot[5] = (c - 2.0 * a) * x[2] + acc[2]
    return xdot

def glorbit(t, x, acc):
    k1 = deq(x, acc)
    w = x + k1 * t / 2
    k2 = deq(w, acc)
    w = x + k2 * t / 2
    k3 = deq(w, acc)
    w = x + k3 * t
    k4 = deq(w, acc)
    x += (k1 + 2 * k2 + 2 * k3 + k4) * t / 6
    return x

def geph2pos(time, geph):
    t = timediff(time, geph.toe)
    dts = np.zeros(2)
    dts[0] = -geph.taun + geph.gamn * t
    x = np.append(geph.pos, geph.vel)

    tt = -TSTEP if t < 0 else TSTEP
    while abs(t) > 1E-5:  #1E-9
        if abs(t) < TSTEP:
            tt = t
        x = glorbit(tt, x, geph.acc)
        t -= tt

    var = ERREPH_GLO**2
    return x[0:3], var, dts

def seph2pos(time, seph):
    sys, _ = sat2prn(seph.sat)
    t = timediff(time, seph.t0)
    rs = []
    for i in range(3):
        rs.append(seph.pos[i]+seph.vel[i]*t+seph.acc[i]*t*t/2.0)
    dts = np.zeros(2)
    dts[0] = seph.af0 + seph.af1*t
    try:
        var = var_uraeph(sys, int(seph.sva))
    except Exception as e:
        print(e)

    return rs, var, dts

def ephpos(time, eph):
    tt = 1e-3  # delta t to calculate velocity
    rs = np.zeros(6)
    if sat2prn(eph.sat)[0] == uGNSS.GPS or sat2prn(eph.sat)[0] == uGNSS.GAL or sat2prn(eph.sat)[0] == uGNSS.QZS or sat2prn(eph.sat)[0] == uGNSS.BDS or sat2prn(eph.sat)[0] == uGNSS.IRN:
        rs[0:3], var, dts = eph2pos(time, eph)
        # use delta t to determine velocity
        t = timeadd(time, tt)
        rs[3:6], _, dtst = eph2pos(t, eph)
        svh = eph.svh
    elif sat2prn(eph.sat)[0] == uGNSS.GLO: # GLONASS
        rs[0:3], var, dts = geph2pos(time, eph)
        # use delta t to determine velocity
        t = timeadd(time, tt)
        rs[3:6], _, dtst = geph2pos(t, eph)
        svh = eph.svh
    elif sat2prn(eph.sat)[0] == uGNSS.SBS: # SBAS
        rs[0:3], var, dts = seph2pos(time, eph)
        # use delta t to determine velocity
        t = timeadd(time, tt)
        rs[3:6], _, dtst = seph2pos(t, eph)
        svh = eph.svh
    # /* satellite velocity and clock drift by differential approx */
    rs[3:6] = (rs[3:6] - rs[0:3]) / tt # 速度
    dts[1] = (dtst[0] - dts[0]) / tt # 钟漂
    return rs, var, dts

def satpos(t, eph):
    return ephpos(t, eph)

def eph2clk(time, eph):
    t = ts = timediff(time, eph.toc) # 先注释一下 看看效果
    for _ in range(2):
        t = ts - (eph.f0 + eph.f1 * t + eph.f2 * t**2)
    dts = eph.f0 + eph.f1*t + eph.f2 * t**2
    return dts

def geph2clk(time, geph):
    t = ts = timediff(time, geph.toe)
    for _ in range(2):
        t = ts - (-geph.taun + geph.gamn * t)
    return -geph.taun + geph.gamn*t

def seph2clk(time, seph):
    t = ts = timediff(time, seph.t0)
    for _ in range(2):
        t = ts - (seph.af0+seph.af1*t)
    return seph.af0+seph.af1*t

def ephclk(time, eph, sat):
    if sat2prn(sat)[0]==uGNSS.GPS or sat2prn(sat)[0]==uGNSS.GAL or sat2prn(sat)[0]==uGNSS.QZS or sat2prn(sat)[0]==uGNSS.BDS or sat2prn(sat)[0]==uGNSS.IRN:
        return eph2clk(time, eph)
    elif sat2prn(sat)[0] == uGNSS.SBS:
        return seph2clk(time, eph)
    elif sat2prn(sat)[0] == uGNSS.GLO:
        return geph2clk(time, eph)

def seleph(nav, t, sat): # 从导航数据中选择星历。当 iode>=0时，选择与输入期号相同的星历；否则，选择toe值与星历选择时间标准 time最近的那个星历。
    sys = sat2prn(sat)[0]
    if sys == uGNSS.GPS:
        dt_p = MAXDTOE + 1.0
        sel = eph_sel[0]
    elif sys == uGNSS.GLO:
        dt_p = MAXDTOE_GLO + 1.0
    elif sys == uGNSS.GAL:
        dt_p = MAXDTOE_GAL
        sel = eph_sel[2]
    elif sys == uGNSS.QZS:
        dt_p = MAXDTOE_QZS + 1.0
        sel = eph_sel[3]
    elif sys == uGNSS.SBS:
        dt_p = MAXDTOE_SBS + 1.0
    elif sys == uGNSS.BDS:
        dt_p = MAXDTOE_BDS + 1.0
        sel = eph_sel[4]
    elif sys == uGNSS.IRN:
        dt_p = MAXDTOE_IRN + 1.0
        sel = eph_sel[5]
    else:
        dt_p = MAXDTOE + 1.0

    dt_p_min = dt_p + 1.0
    stat = 1

    iode = -1 # 默认设置

    t_ob = t.time + t.sec

    i_p = 0
    if sys == uGNSS.GPS or sys == uGNSS.GAL or sys == uGNSS.QZS or sys == uGNSS.BDS or sys == uGNSS.IRN:
        # start with previous index for this sat
        t0 = np.abs(nav.eph_mat[:, 2] - t_ob)
        idx1 = np.where((nav.eph_mat[:, 0] == sat) & (t0 <= dt_p_min))
        if idx1[0].size == 0:
            stat = 0
            eph_ = None
            return eph_, stat
        t1 = t0[idx1]
        idx2 = np.argmin(t1)
        idx3 = idx1[0][idx2]
        i_p = idx3
        return nav.eph[i_p], stat
    elif sys == uGNSS.GLO: # GLONASS
        # start with previous index for this sat
        t0 = np.abs(nav.geph_mat[:, 2] - t_ob)
        idx1 = np.where((nav.geph_mat[:, 0] == sat) & (t0 <= dt_p_min))
        if idx1[0].size == 0:
            stat = 0
            geph_ = None
            return geph_, stat
        t1 = t0[idx1]
        idx2 = np.argmin(t1)
        idx3 = idx1[0][idx2]
        i_p = idx3
        return nav.geph[i_p], stat
    elif sys == uGNSS.SBS: # SBSS
        # start with previous index for this sat
        t0 = np.abs(nav.seph_mat[:, 1] - t_ob)
        idx1 = np.where((nav.seph_mat[:, 0] == sat) & (t0 <= dt_p_min))
        if idx1[0].size == 0:
            stat = 0
            seph_ = None
            return seph_, stat
        t1 = t0[idx1]
        idx2 = np.argmin(t1)
        idx3 = idx1[0][idx2]
        i_p = idx3
        return nav.seph[i_p], stat
    # nav.eph_index[sat] = max(nav.eph_index[sat] + i_p - 1, 0) # save index for next time
    # return nav.eph[i_p], stat

def satposs(obs, nav):
    n = obs.sat.shape[0]
    rs = np.zeros([n, 6])
    tgd = np.zeros([n, 6])
    dts = np.zeros((n, 2))
    var = np.zeros(n)
    svh = np.zeros(n, dtype=int)
    
    ep = time2epoch(obs.t)
    
    for i in np.argsort(obs.sat):
        sat = obs.sat[i]
        # search any pseudorange
        pr = obs.P[i, 0] if obs.P[i, 0] != 0 else obs.P[i, 1]
        # transmission time by satellite clock
        t = timeadd(obs.t, -pr/rCST.CLIGHT)

        eph, stat = seleph(nav, obs.t, sat)
        if eph is None:
            svh[i] = 1
            continue
        svh[i] = eph.svh
        # satellite clock bias by broadcast ephemeris
        dt = ephclk(t, eph, sat)
        t = timeadd(t, -dt)
        # satellite position and clock at transmission time

        rs[i], var[i], dts[i, :] = satpos(t, eph)

        # tgd
        sys, _ = sat2prn(sat)
        if sys == uGNSS.GLO:
            tgd[i][0] = eph.dtaun
        elif sys == uGNSS.SBS:
            pass
        else:
            tgd[i] = eph.tgd

    return rs, var, dts, svh, tgd


def satposs_qc(sat, t, nav):
    rs = np.zeros([1, 6])
    svh = 0
    ep = time2epoch(t)
    var = 0

    # search any pseudorange
    pr = 0
    # transmission time by satellite clock
    t = timeadd(t, -pr/rCST.CLIGHT)

    eph, stat = seleph(nav, t, sat)
    if eph is None:
        svh = 1
        return rs, var, svh

    # satellite clock bias by broadcast ephemeris
    dt = ephclk(t, eph, sat)
    t = timeadd(t, -dt)
    # satellite position and clock at transmission time

    rs, var, _ = satpos(t, eph)

    rs = rs.reshape([1, 6])

    return rs, var, svh