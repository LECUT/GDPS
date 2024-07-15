# function nav=adjnav(nav,opt)
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# %eph and geph struct to eph and geph matrix
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import numpy as np
# 快速匹配星历
def adjnav(nav):
    # %adjust eph
    eph0 = np.nan
    geph0 = np.nan
    seph0 = np.nan
    if len(nav.eph) > 0:
        eph0 = np.zeros([len(nav.eph), 4])
        for i in range(len(nav.eph)):
            from .rtkcmn import sat2prn
            # sys, prn =sat2prn(168)
            # i = 7641
            eph = nav.eph[i]
            # eph0[i, :] = [eph.sat, eph.iode, eph.iodc, eph.sva, eph.svh, eph.week, eph.code, eph.toc.time, eph.toc.sec,
            #               eph.toe.time, eph.toe.sec, eph.A, eph.e, eph.i0, eph.OMG0, eph.omg, eph.M0,
            #               eph.deln, eph.OMGd, eph.idot, eph.crc, eph.crs, eph.cuc, eph.cus, eph.cic, eph.cis, eph.toes,
            #               eph.fit, eph.f0, eph.f1, eph.f2]
            eph0[i, :] = [eph.sat, eph.iode, eph.toe.time + eph.toe.sec, eph.code]
        # nav.eph = eph0

    # %adjust geph
    if len(nav.geph) > 0:
        geph0 = np.zeros([len(nav.geph), 3])
        for i in range(len(nav.geph)):
            geph = nav.geph[i]
            # geph0[i, :] = [geph.sat, geph.iode, geph.frq, geph.svh, geph.sva, geph.age, geph.toe.time, geph.toe.sec, geph.tof.time, geph.tof.sec,
            #                geph.pos.T, geph.vel.T, geph.acc.T, geph.taun,
            #                geph.gamn, geph.dtaun]
            geph0[i, :] = [geph.sat, geph.iode, geph.toe.time + geph.toe.sec]
        # nav.geph = geph0

    # %adjust seph
    if len(nav.seph) > 0:
        seph0 = np.zeros([len(nav.seph), 2])
        for i in range(len(nav.seph)):
            seph = nav.seph[i]
            # seph0[i, :] = [seph.sat, seph.iode, seph.frq, seph.svh, seph.sva, seph.age, seph.toe.time, seph.toe.sec, seph.tof.time, seph.tof.sec,
            #                seph.pos.T, seph.vel.T, seph.acc.T, seph.taun,
            #                seph.gamn, seph.dtaun]
            seph0[i, :] = [seph.sat, seph.t0.time + seph.t0.sec]
        # nav.seph = seph0

    eph_mat = eph0
    geph_mat = geph0
    seph_mat = seph0
    return eph_mat, geph_mat, seph_mat

