import math
from .rtkcmn import uGNSS, rCST, timediff, sat2prn, MAX_NFREQ
import numpy as np

def MPms(P1, P2, L1, L2, f1, f2):
    a = (f1/f2)**2
    wavl1 = rCST.CLIGHT/f1
    wavl2 = rCST.CLIGHT/f2
    MP1 = P1 - L1*(2/(a-1)+1)*wavl1 + L2*(2/(a-1))*wavl2
    MP2 = P2 - L1*((2*a)/(a-1))*wavl1 + L2*((2*a)/(a-1)-1)*wavl2
    return MP1, MP2

def IOms(L1, L2, f1, f2):
    wavl1 = rCST.CLIGHT/f1
    wavl2 = rCST.CLIGHT/f2
    ION1 = (f2**2)/(f1**2-f2**2)*(L2*wavl2 - L1*wavl1)
    ION2 = (f1**2)/(f1**2-f2**2)*(L2*wavl2 - L1*wavl1)
    return ION1, ION2

def GFIms(L1, L2, L3, f1, f2, f3):
    a0 = (f1**2)/(f1**2 - f2**2)
    a1 = (f1**2)/(f1**2 - f3**2)
    a2 = (f2**2)/(f1**2 - f2**2)
    a3 = (f3**2)/(f1**2 - f3**2)
    wavl1 = rCST.CLIGHT/f1
    wavl2 = rCST.CLIGHT/f2
    wavl3 = rCST.CLIGHT/f3
    gfif_ = (a0-a1)*L1*wavl1 - a2*L2*wavl2 + a3*L3*wavl3
    return gfif_

def GFms(L1, L2, f1, f2):
    gfl = (L1/f1 - L2/f2)*rCST.CLIGHT
    return gfl

def MWms(P1, P2, L1, L2, f1, f2):
    lamwl = rCST.CLIGHT/(f1 - f2)
    lwl = (L1 - L2)*rCST.CLIGHT/(f1 - f2)
    pnl = (f1*P1 + f2*P2)/(f1 + f2)
    mw = (lwl - pnl)/lamwl
    return mw

def mwmeas(satL_mat, satP_mat, freq_mat, sat):
    sys, _ = sat2prn(sat)
    f1 = freq_mat[0]
    f2 = freq_mat[1]
    f3 = freq_mat[2]
    f4 = freq_mat[3]
    f5 = freq_mat[4]
    f6 = freq_mat[5]
    f7 = freq_mat[6]
    MW = np.full([satP_mat.shape[0], satP_mat.shape[1]], np.nan)
    if sys == uGNSS.GPS:
        MW[:, 0] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 1] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 2] = MWms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)
    elif sys == uGNSS.GLO:
        MW[:, 0] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 1] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 2] = MWms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)
    elif sys == uGNSS.GAL:
        MW[:, 0] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 1] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 2] = MWms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)
        MW[:, 3] = MWms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)
        MW[:, 4] = MWms(satP_mat[:, 0], satP_mat[:, 4], satL_mat[:, 0], satL_mat[:, 4], f1, f5)
    elif sys == uGNSS.QZS:
        MW[:, 0] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 1] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 2] = MWms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)
        MW[:, 3] = MWms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)
    elif sys == uGNSS.SBS:
        MW[:, 0] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 1] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
    elif sys == uGNSS.BDS:
        MW[:, 0] = MWms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)
        MW[:, 1] = MWms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        MW[:, 2] = MWms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)
        MW[:, 3] = MWms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)
        MW[:, 4] = MWms(satP_mat[:, 0], satP_mat[:, 4], satL_mat[:, 0], satL_mat[:, 4], f1, f5)
        MW[:, 5] = MWms(satP_mat[:, 5], satP_mat[:, 3], satL_mat[:, 5], satL_mat[:, 3], f6, f4)
        MW[:, 6] = MWms(satP_mat[:, 0], satP_mat[:, 6], satL_mat[:, 0], satL_mat[:, 6], f1, f7)
    elif sys == uGNSS.IRN:
        MW[:, 0] = MWms(satP_mat[:, 1], satP_mat[:, 0], satL_mat[:, 1], satL_mat[:, 0], f2, f1)
        MW[:, 1] = MWms(satP_mat[:, 1], satP_mat[:, 0], satL_mat[:, 1], satL_mat[:, 0], f2, f1)
        MW[:, 3] = MWms(satP_mat[:, 2], satP_mat[:, 0], satL_mat[:, 2], satL_mat[:, 0], f3, f1)
    return MW

def gfmeas(satL_mat, freq_mat, sat):
    satL_mat = satL_mat.reshape(1, len(satL_mat))
    sys, _ = sat2prn(sat)
    f1 = freq_mat[0]
    f2 = freq_mat[1]
    f3 = freq_mat[2]
    f4 = freq_mat[3]
    f5 = freq_mat[4]
    f6 = freq_mat[5]
    f7 = freq_mat[6]
    GF = np.full([satL_mat.shape[0], satL_mat.shape[1]], np.nan)
    if sys == uGNSS.GPS:
        GF[:, 0] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 1] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 2] = GFms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)
    elif sys == uGNSS.GLO:
        GF[:, 0] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 1] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 2] = GFms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)
    elif sys == uGNSS.GAL:
        GF[:, 0] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 1] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 2] = GFms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)
        GF[:, 3] = GFms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)
        GF[:, 4] = GFms(satL_mat[:, 0], satL_mat[:, 4], f1, f5)
    elif sys == uGNSS.QZS:
        GF[:, 0] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 1] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 2] = GFms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)
        GF[:, 3] = GFms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)
    elif sys == uGNSS.SBS:
        GF[:, 0] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 1] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
    elif sys == uGNSS.BDS:
        GF[:, 0] = GFms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)
        GF[:, 1] = GFms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)
        GF[:, 2] = GFms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)
        GF[:, 3] = GFms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)
        GF[:, 4] = GFms(satL_mat[:, 0], satL_mat[:, 4], f1, f5)
        GF[:, 5] = GFms(satL_mat[:, 5], satL_mat[:, 3], f6, f4)
        GF[:, 6] = GFms(satL_mat[:, 0], satL_mat[:, 6], f1, f7)
    elif sys == uGNSS.IRN:
        GF[:, 0] = GFms(satL_mat[:, 1], satL_mat[:, 0], f2, f1)
        GF[:, 1] = GFms(satL_mat[:, 1], satL_mat[:, 0], f2, f1)
        GF[:, 2] = GFms(satL_mat[:, 2], satL_mat[:, 0], f3, f1)
    return GF

# /* geometry-free phase measurement -------------------------------------------*/
def gfmeas_h(satL_mat, freq_mat, freq_pos1, freq_pos2):
    f1 = freq_mat[freq_pos1]
    f2 = freq_mat[freq_pos2]
    gfl = (satL_mat[:, freq_pos1]/f1 - satL_mat[:, freq_pos2]/f2)*rCST.CLIGHT
    return gfl

# /* Melbourne-Wubbena linear combination --------------------------------------*/
def mwmeas_h(satL_mat, satP_mat, freq_mat, freq_pos1, freq_pos2):
    f1 = freq_mat[freq_pos1]
    f2 = freq_mat[freq_pos2]
    lamwl = rCST.CLIGHT/(f1-f2)
    lwl = (satL_mat[:, freq_pos1] - satL_mat[:, freq_pos2])*rCST.CLIGHT/(f1 - f2)
    pnl = (f1*satP_mat[:, freq_pos1] + f2*satP_mat[:, freq_pos2])/(f1 + f2)
    mw = (lwl-pnl)/lamwl
    return mw

# /* MP */ #
def muphmeas(satL_mat, satP_mat, freq_mat, sat, cycslip):
    sys, _ = sat2prn(sat)
    f1 = freq_mat[0]
    f2 = freq_mat[1]
    f3 = freq_mat[2]
    f4 = freq_mat[3]
    f5 = freq_mat[4]
    f6 = freq_mat[5]
    f7 = freq_mat[6]
    MP = np.full([satP_mat.shape[0], satP_mat.shape[1]], np.nan)
    cs_ = cycslip.copy()
    cs = cycslip.copy()
    if sys == uGNSS.GPS:
        MP[:, 0] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        MP[:, 1] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        MP[:, 2] = MPms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
    elif sys == uGNSS.GLO:
        MP[:, 0] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        MP[:, 1] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        MP[:, 2] = MPms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
    elif sys == uGNSS.GAL:
        MP[:, 0] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        MP[:, 1] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        MP[:, 2] = MPms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        MP[:, 3] = MPms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)[1]
        MP[:, 4] = MPms(satP_mat[:, 0], satP_mat[:, 4], satL_mat[:, 0], satL_mat[:, 4], f1, f5)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
        cs[:, 3] = cs_[:, 0] + cs_[:, 3]
        cs[:, 4] = cs_[:, 0] + cs_[:, 4]
    elif sys == uGNSS.QZS:
        MP[:, 0] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        MP[:, 1] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        MP[:, 2] = MPms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        MP[:, 3] = MPms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
        cs[:, 3] = cs_[:, 0] + cs_[:, 3]
    elif sys == uGNSS.SBS:
        MP[:, 0] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        MP[:, 1] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
    elif sys == uGNSS.BDS:
        MP[:, 0] = MPms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)[0]
        MP[:, 1] = MPms(satP_mat[:, 0], satP_mat[:, 1], satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        MP[:, 2] = MPms(satP_mat[:, 0], satP_mat[:, 2], satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        MP[:, 3] = MPms(satP_mat[:, 0], satP_mat[:, 3], satL_mat[:, 0], satL_mat[:, 3], f1, f4)[1]
        MP[:, 4] = MPms(satP_mat[:, 0], satP_mat[:, 4], satL_mat[:, 0], satL_mat[:, 4], f1, f5)[1]
        MP[:, 5] = MPms(satP_mat[:, 5], satP_mat[:, 3], satL_mat[:, 5], satL_mat[:, 3], f6, f4)[0]
        MP[:, 6] = MPms(satP_mat[:, 0], satP_mat[:, 6], satL_mat[:, 0], satL_mat[:, 6], f1, f7)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 3]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
        cs[:, 3] = cs_[:, 0] + cs_[:, 3]
        cs[:, 4] = cs_[:, 0] + cs_[:, 4]
        cs[:, 5] = cs_[:, 5] + cs_[:, 3]
        cs[:, 6] = cs_[:, 0] + cs_[:, 6]
    elif sys == uGNSS.IRN:
        MP[:, 0] = MPms(satP_mat[:, 1], satP_mat[:, 0], satL_mat[:, 1], satL_mat[:, 0], f2, f1)[1]
        MP[:, 1] = MPms(satP_mat[:, 1], satP_mat[:, 0], satL_mat[:, 1], satL_mat[:, 0], f2, f1)[0]
        MP[:, 3] = MPms(satP_mat[:, 2], satP_mat[:, 0], satL_mat[:, 2], satL_mat[:, 0], f3, f1)[0]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
    return MP, cs

# /* ionospheric delay */ #
def ionpmeas(satL_mat, freq_mat, sat, cycslip):
    sys, _ = sat2prn(sat)
    f1 = freq_mat[0]
    f2 = freq_mat[1]
    f3 = freq_mat[2]
    f4 = freq_mat[3]
    f5 = freq_mat[4]
    f6 = freq_mat[5]
    f7 = freq_mat[6]
    ION = np.full([satL_mat.shape[0], satL_mat.shape[1]], np.nan)
    cs_ = cycslip.copy()
    cs = cycslip.copy()
    if sys == uGNSS.GPS:
        ION[:, 0] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        ION[:, 1] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        ION[:, 2] = IOms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
    elif sys == uGNSS.GLO:
        ION[:, 0] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        ION[:, 1] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        ION[:, 2] = IOms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
    elif sys == uGNSS.GAL:
        ION[:, 0] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        ION[:, 1] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        ION[:, 2] = IOms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        ION[:, 3] = IOms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)[1]
        ION[:, 4] = IOms(satL_mat[:, 0], satL_mat[:, 4], f1, f5)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
        cs[:, 3] = cs_[:, 0] + cs_[:, 3]
        cs[:, 4] = cs_[:, 0] + cs_[:, 4]
    elif sys == uGNSS.QZS:
        ION[:, 0] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        ION[:, 1] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        ION[:, 2] = IOms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        ION[:, 3] = IOms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
        cs[:, 3] = cs_[:, 0] + cs_[:, 3]
    elif sys == uGNSS.SBS:
        ION[:, 0] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[0]
        ION[:, 1] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
    elif sys == uGNSS.BDS:
        ION[:, 0] = IOms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)[0]
        ION[:, 1] = IOms(satL_mat[:, 0], satL_mat[:, 1], f1, f2)[1]
        ION[:, 2] = IOms(satL_mat[:, 0], satL_mat[:, 2], f1, f3)[1]
        ION[:, 3] = IOms(satL_mat[:, 0], satL_mat[:, 3], f1, f4)[1]
        ION[:, 4] = IOms(satL_mat[:, 0], satL_mat[:, 4], f1, f5)[1]
        ION[:, 5] = IOms(satL_mat[:, 5], satL_mat[:, 3], f6, f4)[0]
        ION[:, 6] = IOms(satL_mat[:, 0], satL_mat[:, 6], f1, f7)[1]
        cs[:, 0] = cs_[:, 0] + cs_[:, 3]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
        cs[:, 3] = cs_[:, 0] + cs_[:, 3]
        cs[:, 4] = cs_[:, 0] + cs_[:, 4]
        cs[:, 5] = cs_[:, 5] + cs_[:, 3]
        cs[:, 6] = cs_[:, 0] + cs_[:, 6]
    elif sys == uGNSS.IRN:
        ION[:, 0] = IOms(satL_mat[:, 1], satL_mat[:, 0], f2, f1)[1]
        ION[:, 1] = IOms(satL_mat[:, 1], satL_mat[:, 0], f2, f1)[0]
        ION[:, 2] = IOms(satL_mat[:, 2], satL_mat[:, 0], f3, f1)[0]
        cs[:, 0] = cs_[:, 0] + cs_[:, 1]
        cs[:, 1] = cs_[:, 0] + cs_[:, 1]
        cs[:, 2] = cs_[:, 0] + cs_[:, 2]
    return ION, cs

# /* carrier multipath */ #
def gfifmeas(satL_mat, freq_mat, sat):
    sys, prn = sat2prn(sat)
    f1 = freq_mat[0]
    f2 = freq_mat[1]
    f3 = freq_mat[2]
    f4 = freq_mat[3]
    f5 = freq_mat[4]
    f6 = freq_mat[5]
    f7 = freq_mat[6]
    GFIF = None
    band_select = []
    if sys == uGNSS.GPS:
        GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 1], satL_mat[:, 2], f1, f2, f3)
        band_select = [0, 1, 2]
    elif sys == uGNSS.GLO:
        GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 1], satL_mat[:, 2], f1, f2, f3)
        band_select = [0, 1, 2]
    elif sys == uGNSS.GAL:
        GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 1], satL_mat[:, 2], f1, f2, f3)
        band_select = [0, 1, 2]
    elif sys == uGNSS.QZS:
        GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 1], satL_mat[:, 2], f1, f2, f3)
        band_select = [0, 1, 2]
    elif sys == uGNSS.SBS:
        GFIF = np.full([satL_mat.shape[0], 1], np.nan)
        band_select = []
    elif sys == uGNSS.BDS:
        if prn<=18:
            GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 1], satL_mat[:, 3], f1, f2, f4)
            band_select = [0, 1, 3]
        else:
            GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 6], satL_mat[:, 3], f1, f7, f4)
            band_select = [0, 6, 3]
    elif sys == uGNSS.IRN:
        GFIF = GFIms(satL_mat[:, 0], satL_mat[:, 1], satL_mat[:, 2], f1, f2, f3)
        band_select = [0, 1, 2]
    return GFIF, band_select

# comput CMC
def ccmeas(P, L, frq):
    CC = P - L*rCST.CLIGHT/frq
    return CC

#  existing observations
def obs_exist(obs, j):
    freq_num = MAX_NFREQ
    data_ext = np.zeros(freq_num)
    nnan_id = np.where((obs.P[j] != 0) & (obs.L[j] != 0), 1, data_ext)
    return nnan_id

#  existing observations
def obs_exist_h(P, L):
    P[np.isnan(P)] = 0
    L[np.isnan(L)] = 0
    freq_num = MAX_NFREQ
    data_ext = np.zeros(freq_num)
    nnan_id = np.where((P != 0) & (L != 0), 1, data_ext)
    return nnan_id

# satiation observations
def obs_full(obs, j):
    freq_num = MAX_NFREQ
    pha_obs = np.zeros(freq_num) # pseudo range
    car_obs = np.zeros(freq_num)  # carrier phase
    pnnan_id = np.where((obs.P[j] != 0), 1, pha_obs)
    cnnan_id = np.where((obs.L[j] != 0), 1, car_obs)
    return pnnan_id, cnnan_id

# satiation observations
def obs_full_h(P, L):
    P[np.isnan(P)] = 0
    L[np.isnan(L)] = 0
    freq_num = MAX_NFREQ
    pha_obs = np.zeros(freq_num) # pseudo range
    car_obs = np.zeros(freq_num)  # carrier phase
    pnnan_id = np.where((P != 0), 1, pha_obs)
    cnnan_id = np.where((L != 0), 1, car_obs)
    return pnnan_id, cnnan_id

# expected observations
def obs_ideal(sys, prn):
    if sys == uGNSS.GPS:
        if prn in [1, 24, 27, 30, 6, 9, 3, 26, 8, 10, 32, 4, 11, 14, 18, 23]:
            return np.array([1, 1, 1, 0, 0, 0, 0])
        else:
            return np.array([1, 1, 0, 0, 0, 0, 0])
    elif sys == uGNSS.GLO:
        if prn in [4, 5, 9, 12, 21, 24, 26]:
            return np.array([1, 1, 1, 1, 1, 0, 0])
        else:
            return np.array([1, 1, 0, 1, 1, 0, 0])
    elif sys == uGNSS.GAL:
        return np.array([1, 1, 1, 1, 1, 0, 0])
    elif sys == uGNSS.QZS:
        return np.array([1, 1, 1, 1, 0, 0, 0])
    elif sys == uGNSS.SBS:
        return np.array([1, 1, 0, 0, 0, 0, 0])
    elif sys == uGNSS.BDS:
        if prn <= 16:
            return np.array([1, 1, 0, 1, 0, 0, 0])
        elif prn in [56, 57, 58, 59, 60, 61, 62]:
            return np.array([1, 0, 0, 1, 0, 0, 1])
        else:
            return np.array([1, 0, 1, 1, 1, 1, 1])
    elif sys == uGNSS.IRN:
        return np.array([1, 1, 1, 0, 0, 0, 0])


def rmse(records):
    return math.sqrt(sum([x**2 for x in records])/len(records))
