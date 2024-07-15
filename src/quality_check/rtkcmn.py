from copy import copy, deepcopy
from enum import IntEnum
from math import floor, sin, cos, sqrt, asin, atan2, fabs
import numpy as np
from numpy.linalg import norm, inv
import sys

gpst0 = [1980, 1, 6, 0, 0, 0] # /* gps time reference */
gst0 = [1999, 8, 22, 0, 0, 0] # /* galileo system time reference */
bdt0 = [2006, 1, 1, 0, 0, 0]  # /* beidou time reference */
ion_default = np.array([ # 2004/1/1
    [0.1118E-07, -0.7451E-08, -0.5961E-07, 0.1192E-06],
    [0.1167E+06, -0.2294E+06, -0.1311E+06, 0.1049E+07]])

leaps = np.array([ # /* leap seconds (y,m,d,h,m,s,utc-gpst) */
    [2017, 1, 1, 0, 0, 0, -18],
    [2015, 7, 1, 0, 0, 0, -17],
    [2012, 7, 1, 0, 0, 0, -16],
    [2009, 1, 1, 0, 0, 0, -15],
    [2006, 1, 1, 0, 0, 0, -14],
    [1999, 1, 1, 0, 0, 0, -13],
    [1997, 7, 1, 0, 0, 0, -12],
    [1996, 1, 1, 0, 0, 0, -11],
    [1994, 7, 1, 0, 0, 0, -10],
    [1993, 7, 1, 0, 0, 0,  -9],
    [1992, 7, 1, 0, 0, 0,  -8],
    [1991, 1, 1, 0, 0, 0,  -7],
    [1990, 1, 1, 0, 0, 0,  -6],
    [1988, 1, 1, 0, 0, 0,  -5],
    [1985, 7, 1, 0, 0, 0,  -4],
    [1983, 7, 1, 0, 0, 0,  -3],
    [1982, 7, 1, 0, 0, 0,  -2],
    [1981, 7, 1, 0, 0, 0,  -1],
    [0]], dtype=object)

chisqr = np.array([ # /* chi-sqr(n) (alpha=0.001) */
    10.8, 13.8, 16.3, 18.5, 20.5, 22.5, 24.3, 26.1, 27.9, 29.6,
    31.3, 32.9, 34.5, 36.1, 37.7, 39.3, 40.8, 42.3, 43.8, 45.3,
    46.8, 48.3, 49.7, 51.2, 52.6, 54.1, 55.5, 56.9, 58.3, 59.7,
    61.1, 62.5, 63.9, 65.2, 66.6, 68.0, 69.3, 70.7, 72.1, 73.4,
    74.7, 76.0, 77.3, 78.6, 80.0, 81.3, 82.6, 84.0, 85.4, 86.7,
    88.0, 89.3, 90.6, 91.9, 93.3, 94.7, 96.0, 97.4, 98.7, 100 ,
    101 , 102 , 103 , 104 , 105 , 107 , 108 , 109 , 110 , 112 ,
    113 , 114 , 115 , 116 , 118 , 119 , 120 , 122 , 123 , 125 ,
    126 , 127 , 128 , 129 , 131 , 132 , 133 , 134 , 135 , 137 ,
    138 , 139 , 140 , 142 , 143 , 144 , 145 , 147 , 148 , 149], dtype=object)

nmf_coef = np.array([
    [1.2769934E-3, 1.2683230E-3, 1.2465397E-3, 1.2196049E-3, 1.2045996E-3],
    [2.9153695E-3, 2.9152299E-3, 2.9288445E-3, 2.9022565E-3, 2.9024912E-3],
    [62.610505E-3, 62.837393E-3, 63.721774E-3, 63.824265E-3, 64.258455E-3],
    [0.0000000E-0, 1.2709626E-5, 2.6523662E-5, 3.4000452E-5, 4.1202191E-5],
    [0.0000000E-0, 2.1414979E-5, 3.0160779E-5, 7.2562722E-5, 11.723375E-5],
    [0.0000000E-0, 9.0128400E-5, 4.3497037E-5, 84.795348E-5, 170.37206E-5],
    [5.8021897E-4, 5.6794847E-4, 5.8118019E-4, 5.9727542E-4, 6.1641693E-4],
    [1.4275268E-3, 1.5138625E-3, 1.4572752E-3, 1.5007428E-3, 1.7599082E-3],
    [4.3472961E-2, 4.6729510E-2, 4.3908931E-2, 4.4626982E-2, 5.4736038E-2]], dtype=object)
nmf_aht = [2.53E-5, 5.49E-3, 1.14E-3] # height correction

obscodes = [ #/* observation code strings */
    ""  , "1C", "1P", "1W", "1Y",  "1M", "1N", "1S", "1L", "1E", # /*  0- 9 */
    "1A", "1B", "1X", "1Z", "2C",  "2D", "2S", "2L", "2X", "2P", # /* 10-19 */
    "2W", "2Y", "2M", "2N", "5I",  "5Q", "5X", "7I", "7Q", "7X", # /* 20-29 */
    "6A", "6B", "6C", "6X", "6Z",  "6S", "6L", "8L", "8Q", "8X", # /* 30-39 */
    "2I", "2Q", "6I", "6Q", "3I",  "3Q", "3X", "1I", "1Q", "5A", # /* 40-49 */
    "5B", "5C", "9A", "9B", "9C",  "9X", "1D", "5D", "5P", "5Z", # /* 50-59 */
    "6E", "7D", "7P", "7Z", "8D",  "8P", "4A", "4B", "4X", "6D", # /* 60-69 */
    "6P", "1R", "2R"] # /* 70-71 */


codepris = ([  # /* code priority for each freq-index */
    # /* L1/E1/B1 L2/E5b/B2   L5/E5a/B2a E6/L6/B3 E5/B2(a+b) B1C      BDS3 B2b*/
    ["CPYWMNSLXR","CPYWMNDSLXR","IQX"     ,""       ,""       ,""       ,""       ],  # /* GPS */
    ["PC"        ,"PC"         ,"IQX"     ,"ABX"    ,"ABX"    ,""       ,""       ],  # /* GLO */
    ["IQX"       ,"IQX"        ,"DPX"     ,"IQXADPZ","DPX"    ,"DPXASLZ","ZDP"    ],  # /* BDS */
    ["CABXZ"     ,"IQX"        ,"IQX"     ,"ABCXZ"  ,"IQX"    ,""       ,""       ],  # /* GAL */
    ["CLSXZ"     ,"SLX"        ,"IQXDPZ"  ,"SLXEZ"  ,""       ,""       ,""       ],  # /* QZS */
    ["C"         ,"IQX"        ,""        ,""       ,""       ,""       ,""       ],  # /* SBS */
    ["ABCX"      ,"ABCX"       ,"DPX"     ,""       ,""       ,""       ,""       ]]) # /* IRN */

freqpos = np.array([  # /* freq priority for each freq-index */
    # /* L1/E1/B1 L2/E5b/B2   L5/E5a/B2a  E6/LEX/B3  E5/B2(a+b)  B1C
    ['125']   ,   # /* GPS */
    ['12346'] ,   # /* GLO */
    ['275681'],  # /* BDS */
    ['17568'] ,   # /* GAL */
    ['1256']  ,   # /* QZS */
    ['15']    ,   # /* SBS */
    ['591']])      # /* IRN */

freqpris = np.array([  # /* freq priority for each freq-index */
    # /* L1/E1/B1 L2/E5b/B2   L5/E5a/B2a  E6/LEX/B3  E5/B2(a+b)  B1C         B2b
    [1.575420E9, 1.227600E9, 1.176450E9, 0         , 0         , 0         , 0        ], # /* GPS */
    [1.602000E9, 1.246000E9, 1.202025E9, 1.600995E9, 1.248060E9, 1.202025E9, 0        ], # /* GLO */
    [1.561098E9, 1.207140E9, 1.176450E9, 1.268520E9, 1.191795E9, 1.575420E9, 1.20714E9], # /* BDS */
    [1.575420E9, 1.207140E9, 1.176450E9, 1.278750E9, 1.191795E9, 0         , 0        ], # /* GAL */
    [1.575420E9, 1.227600E9, 1.176450E9, 1.278750E9, 0         , 0         , 0        ], # /* QZS */
    [1.575420E9, 1.176450E9, 0         , 0         , 0         , 0         , 0        ], # /* SBS */
    [1.176450E9, 2.492028E9, 1.575420E9, 0         , 0         , 0         , 0        ]]) # /* IRN */

codetype = "CLDS"    #/* observation type codes */

syscodes = "GRCEJSI" # /* satellite system codes */


# define TSYS_GPS    0                   /* time system: GPS time */
# define TSYS_UTC    1                   /* time system: UTC */
# define TSYS_GLO    2                   /* time system: GLONASS time */
# define TSYS_BDS    3                   /* time system: BeiDou time */
# define TSYS_GAL    4                   /* time system: Galileo time */
# define TSYS_QZS    5                   /* time system: QZSS time */
# define TSYS_IRN    6                   /* time system: IRNSS time */
htsys_GNSS = np.array([0, 1, 2, 3, 4, 5, 6, 7])


# global defines
DTTOL = 0.025
MAX_NFREQ = 7 # max freq number
SOLQ_NONE = 0
SOLQ_FIX = 1
SOLQ_FLOAT = 2
SOLQ_DGPS = 4
SOLQ_SINGLE = 5

MAX_VAR_EPH = 300**2 # max variance eph to reject satellite

MAXOBSTYPE = 64  # /* max number of obs type in RINEX */

MAXRNXLEN = 16*MAXOBSTYPE+4

CODE_NONE = 0     # /* obs code: none or unknown */

MAXCODE = 71      # /* max number of obs code */

FREQL1 = 1.57542E9           # /* L1/E1  frequency (Hz) */
FREQL2 = 1.22760E9           # /* L2     frequency (Hz) */
FREQE5b = 1.20714E9          # /* E5b    frequency (Hz) */
FREQL5 = 1.17645E9           # /* L5/E5a/B2a frequency (Hz) */
FREQL6 = 1.27875E9           # /* E6/L6 frequency (Hz) */
FREQE5ab = 1.191795E9        # /* E5a+b  frequency (Hz) */
FREQs = 2.492028E9           # /* S      frequency (Hz) */
FREQ1_GLO = 1.60200E9        # /* GLONASS G1 base frequency (Hz) */
DFRQ1_GLO = 0.56250E6        # /* GLONASS G1 bias frequency (Hz/n) */
FREQ2_GLO = 1.24600E9        # /* GLONASS G2 base frequency (Hz) */
DFRQ2_GLO = 0.43750E6        # /* GLONASS G2 bias frequency (Hz/n) */
FREQ3_GLO = 1.202025E9       # /* GLONASS G3 frequency (Hz) */
FREQ1a_GLO = 1.600995E9      # /* GLONASS G1a frequency (Hz) */
FREQ2a_GLO = 1.248060E9      # /* GLONASS G2a frequency (Hz) */
FREQ1_CMP = 1.561098E9       # /* BDS B1I     frequency (Hz) */
FREQ2_CMP = 1.20714E9        # /* BDS B2I/B2b frequency (Hz) */
FREQ3_CMP = 1.26852E9        # /* BDS B3      frequency (Hz) */


# /* type definition -----------------------------------------------------------*/
class sigind_t():                      # /* signal index type */
    def __init__(self):
        self.n = np.empty(uGNSS.GNSSMAX)                                # /* number of index */
        self.idx = np.empty((uGNSS.GNSSMAX, MAXOBSTYPE))           # /* signal freq-index */
        self.pos = np.empty((uGNSS.GNSSMAX, MAXOBSTYPE))           # /* signal index in obs data (-1:no) */
        self.pri = np.empty((uGNSS.GNSSMAX, MAXOBSTYPE))           # /* signal priority (15-0) */
        self.type = np.empty((uGNSS.GNSSMAX, MAXOBSTYPE))          # /* type (0:C,1:L,2:D,3:S) */
        self.code = np.empty((uGNSS.GNSSMAX, MAXOBSTYPE))          # /* obs-code (CODE_L??) */
        self.shift = np.empty((uGNSS.GNSSMAX, MAXOBSTYPE))         # /* phase shift (cycle) */

class Ts():
    SYS_NONE = '0x00'               # /* navigation system: none */
    SYS_GPS = '0x01'                # /* navigation system: GPS */
    SYS_SBS = '0x02'                # /* navigation system: SBAS */
    SYS_GLO = '0x04'                # /* navigation system: GLONASS */
    SYS_GAL = '0x08'                # /* navigation system: Galileo */
    SYS_QZS = '0x10'                # /* navigation system: QZSS */
    SYS_BDS = '0x20'                # /* navigation system: BeiDou */
    SYS_IRN = '0x40'                # /* navigation system: IRNS */
    SYS_LEO = '0x80'                # /* navigation system: LEO */
    SYS_ALL = '0xFF'                # /* navigation system: all */


class rCST():
    CLIGHT   = 299792458.0
    MU_GPS   = 3.9860050E14
    MU_GAL   = 3.986004418E14
    MU_GLO   = 3.9860044E14
    MU_BDS   = 3.986004418E14
    GME      = 3.986004415E+14
    GMS      = 1.327124E+20
    GMM      = 4.902801E+12
    OMGE     = 7.2921151467E-5
    OMGE_GAL = 7.2921151467E-5
    OMGE_GLO = 7.292115E-5
    OMGE_BDS = 7.292115E-5
    RE_WGS84 = 6378137.0
    RE_GLO   = 6378136.0
    FE_WGS84 = (1.0/298.257223563)
    J2_GLO   = 1.0826257E-3  # 2nd zonal harmonic of geopot
    AU       = 149597870691.0
    D2R      = 0.017453292519943295
    AS2R     = D2R/3600.0
    DAY_SEC  = 86400.0
    CENTURY_SEC = DAY_SEC*36525.0

class uGNSS(IntEnum):
    GPS = 0
    GLO = 1
    BDS = 2
    GAL = 3
    QZS = 4
    SBS = 5
    IRN = 6
    GNSSMAX = 7
    GPSMAX = 100
    GALMAX = 100
    QZSMAX = 100
    GLOMAX = 100
    BDSMAX = 100
    SBSMAX = 100
    IRNMAX = 100
    NONE = -1
    MAXSAT = GPSMAX+GLOMAX+GALMAX+BDSMAX+QZSMAX+SBSMAX+IRNMAX
    # MAXSAT = GNSSMAX*100

class uSIG(IntEnum):
    GPS_L1CA = 0
    GPS_L2W = 2
    GPS_L2CL = 3
    GPS_L2CM = 4
    GPS_L5Q = 6
    SBS_L1CA = 0
    GAL_E1C = 0
    GAL_E1B = 1
    GAL_E5BI = 5
    GAL_E5BQ = 6
    GLO_L1C = 0
    GLO_L2C = 1
    BDS_B1ID1 = 0
    BDS_B1ID2 = 1
    BDS_B2ID1 = 2
    BDS_B2ID2 = 3
    QZS_L1CA = 0
    QZS_L1S = 1
    QZS_L2CM = 4
    QZS_L2CL = 5
    GLO_L1OF = 0
    GLO_L2OF = 2
    NONE = -1
    SIGMAX = 8

class band(IntEnum):
    GPS_L1 = 0
    GPS_L2 = 1
    GPS_L5 = 4

    GLO_G1 = 0
    GLO_G2 = 1
    GLO_G3 = 2
    GLO_G1a = 3
    GLO_G2a = 5

    BDS_B1CA = 0
    BDS_B1 = 1
    BDS_B2a = 4
    BDS_B2b = 6
    BDS_B2ab = 8
    BSA_B3IA = 5

    GAL_E1 = 0
    GAL_E5a = 4
    GAL_E6 = 5
    GAL_E5b = 6
    GAL_E5ab = 7

    SBS_L1 = 0
    SBS_L5 = 4

    QZS_L1 = 0
    QZS_L2 = 1
    QZS_L5 = 4
    QZS_L6 = 5


class rSIG(IntEnum):

    NONE = 0                   # /* obs code: none or unknown */
    L1C =  1                   # /* obs code: L1C/A,G1C/A,E1C (GPS,GLO,GAL,QZS,SBS) */
    L1P =  2                   # /* obs code: L1P,G1P,B1P (GPS,GLO,BDS) */
    L1W =  3                   # /* obs code: L1 Z-track (GPS) */
    L1Y =  4                   # /* obs code: L1Y        (GPS) */
    L1M =  5                   # /* obs code: L1M        (GPS) */
    L1N =  6                   # /* obs code: L1codeless,B1codeless (GPS,BDS) */
    L1S =  7                   # /* obs code: L1C(D)     (GPS,QZS) */
    L1L =  8                   # /* obs code: L1C(P)     (GPS,QZS) */
    L1E =  9                   # /* (not used) */
    L1A = 10                   # /* obs code: E1A,B1A    (GAL,BDS) */
    L1B = 11                   # /* obs code: E1B        (GAL) */
    L1X = 12                  # /* obs code: E1B+C,L1C(D+P),B1D+P (GAL,QZS,BDS) */
    L1Z = 13                  # /* obs code: E1A+B+C,L1S (GAL,QZS) */
    L2C = 14                  # /* obs code: L2C/A,G1C/A (GPS,GLO) */
    L2D = 15                  # /* obs code: L2 L1C/A-(P2-P1) (GPS) */
    L2S = 16                  # /* obs code: L2C(M)     (GPS,QZS) */
    L2L = 17                  # /* obs code: L2C(L)     (GPS,QZS) */
    L2X = 18                  # /* obs code: L2C(M+L),B1_2I+Q (GPS,QZS,BDS) */
    L2P = 19                  # /* obs code: L2P,G2P    (GPS,GLO) */
    L2W = 20                  #/* obs code: L2 Z-track (GPS) */
    L2Y = 21                  #/* obs code: L2Y        (GPS) */
    L2M = 22                  #/* obs code: L2M        (GPS) */
    L2N = 23                  #/* obs code: L2codeless (GPS) */
    L5I = 24                  #/* obs code: L5I,E5aI   (GPS,GAL,QZS,SBS) */
    L5Q = 25                  #/* obs code: L5Q,E5aQ   (GPS,GAL,QZS,SBS) */
    L5X = 26                  #/* obs code: L5I+Q,E5aI+Q,L5B+C,B2aD+P (GPS,GAL,QZS,IRN,SBS,BDS) */
    L7I = 27                  #/* obs code: E5bI,B2bI  (GAL,BDS) */
    L7Q = 28                  #/* obs code: E5bQ,B2bQ  (GAL,BDS) */
    L7X = 29                  #/* obs code: E5bI+Q,B2bI+Q (GAL,BDS) */
    L6A = 30                  #/* obs code: E6A,B3A    (GAL,BDS) */
    L6B = 31                  #/* obs code: E6B        (GAL) */
    L6C = 32                  #/* obs code: E6C        (GAL) */
    L6X = 33                  #/* obs code: E6B+C,LEXS+L,B3I+Q (GAL,QZS,BDS) */
    L6Z = 34                  #/* obs code: E6A+B+C,L6D+E (GAL,QZS) */
    L6S = 35                  #/* obs code: L6S        (QZS) */
    L6L = 36                  #/* obs code: L6L        (QZS) */
    L8I = 37                  #/* obs code: E5abI      (GAL) */
    L8Q = 38                  #/* obs code: E5abQ      (GAL) */
    L8X = 39                  #/* obs code: E5abI+Q,B2abD+P (GAL,BDS) */
    L2I = 40                  #/* obs code: B1_2I      (BDS) */
    L2Q = 41                  #/* obs code: B1_2Q      (BDS) */
    L6I = 42                  #/* obs code: B3I        (BDS) */
    L6Q = 43                  #/* obs code: B3Q        (BDS) */
    L3I = 44                  #/* obs code: G3I        (GLO) */
    L3Q = 45                  #/* obs code: G3Q        (GLO) */
    L3X = 46                  #/* obs code: G3I+Q      (GLO) */
    L1I = 47                  #/* obs code: B1I        (BDS) (obsolute) */
    L1Q = 48                  #/* obs code: B1Q        (BDS) (obsolute) */
    L5A = 49                  #/* obs code: L5A SPS    (IRN) */
    L5B = 50                  #/* obs code: L5B RS(D)  (IRN) */
    L5C = 51                  #/* obs code: L5C RS(P)  (IRN) */
    L9A = 52                  #/* obs code: SA SPS     (IRN) */
    L9B = 53                  #/* obs code: SB RS(D)   (IRN) */
    L9C = 54                  #/* obs code: SC RS(P)   (IRN) */
    L9X = 55                  #/* obs code: SB+C       (IRN) */
    L1D = 56                  #/* obs code: B1D        (BDS) */
    L5D = 57                  #/* obs code: L5D(L5S),B2aD (QZS,BDS) */
    L5P = 58                  #/* obs code: L5P(L5S),B2aP (QZS,BDS) */
    L5Z = 59                  #/* obs code: L5D+P(L5S) (QZS) */
    L6E = 60                  #/* obs code: L6E        (QZS) */
    L7D = 61                  #/* obs code: B2bD       (BDS) */
    L7P = 62                  #/* obs code: B2bP       (BDS) */
    L7Z = 63                  #/* obs code: B2bD+P     (BDS) */
    L8D = 64                  #/* obs code: B2abD      (BDS) */
    L8P = 65                  #/* obs code: B2abP      (BDS) */
    L4A = 66                  #/* obs code: G1aL1OCd   (GLO) */
    L4B = 67                  #/* obs code: G1aL1OCd   (GLO) */
    L4X = 68                  #/* obs code: G1al1OCd+p (GLO) */
    SIGMAX = 68               #/* max number of obs code */


class gtime_t():
    def __init__(self, time=0, sec=0.0):
        self.time = time
        self.sec = sec


class Obs():
    def __init__(self):
        self.t = gtime_t()
        self.P = []
        self.L = []
        self.S = []
        self.D = []
        self.lli = []
        self.Lstd = []
        self.Pstd = []
        self.sat = []
        self.sys = []


class Eph():
    sat = 0
    iode = 0
    iodc = 0
    f0 = 0.0
    f1 = 0.0
    f2 = 0.0
    toc = 0
    toe = 0
    tot = 0
    week = 0
    crs = 0.0
    crc = 0.0
    cus = 0.0
    cuc = 0.0
    cis = 0.0
    cic = 0.0
    e = 0.0
    i0 = 0.0
    A = 0.0
    deln = 0.0
    M0 = 0.0
    OMG0 = 0.0
    OMGd = 0.0
    omg = 0.0
    idot = 0.0
    tgd = np.zeros(6)
    isc = np.zeros(6)
    sva = 0
    svh = 0
    fit = 0
    toes = 0
    code = 0
    flag = 0

    def __init__(self, sat=0):
        self.sat = sat

class Geph():
    sat = 0
    iode = 0
    frq = 0
    svh = 0
    sva = 0
    age = 0
    toe = 0
    tof = 0
    pos = np.zeros(3)
    vel = np.zeros(3)
    acc = np.zeros(3)
    taun = 0.0
    gamn = 0.0
    dtaun = 0.0

    def __init__(self, sat=0):
        self.sat = sat

class Seph():
    sat = 0
    svh = 0
    sva = 0
    t0 = 0
    tof = 0
    pos = np.zeros(3)
    vel = np.zeros(3)
    acc = np.zeros(3)
    af0 = 0.0
    af1 = 0.0

    def __init__(self, sat=0):
        self.sat = sat

class Headinfo():
    def __init__(self):
        self.ver = np.nan
        self.type = np.nan
        self.sys = np.nan
        self.tsys = np.nan

class Nav():
    def __init__(self):
        self.ver = np.nan
        self.type = np.nan
        self.eph = []
        self.geph = []
        self.seph = []
        self.eph_GPS = []
        self.eph_GLO = []
        self.eph_GAL = []
        self.eph_BDS = []
        self.eph_QZS = []
        self.eph_IRN = []
        self.eph_SBS = []

        self.ion = ion_default
        self.rb = [0, 0, 0]  # base station position in ECEF [m]
        self.rr = [0, 0, 0]
        self.stat = SOLQ_NONE
        self.leaps = 0

        # satellite header
        self.utc_gps = np.zeros(8) # /* GPS delta-UTC parameters {A0,A1,Tot,WNt,dt_LS,WN_LSF,DN,dt_LSF} */
        self.utc_glo = np.zeros(8) # /* GLONASS UTC time parameters {tau_C,tau_GPS} */
        self.utc_gal = np.zeros(8) # /* Galileo UTC parameters */
        self.utc_qzs = np.zeros(8) # /* QZS UTC parameters */
        self.utc_bds = np.zeros(8) # /* BeiDou UTC parameters */
        self.utc_irn = np.zeros(9) # /* IRNSS UTC parameters {A0,A1,Tot,...,dt_LSF,A2} */
        self.utc_sbs = np.zeros(4) # /* SBAS UTC parameters */
        self.ion_gps = np.zeros(8) # /* GPS iono model parameters {a0,a1,a2,a3,b0,b1,b2,b3} */
        self.ion_gal = np.zeros(4) # /* Galileo iono model parameters {ai0,ai1,ai2,0} */
        self.ion_qzs = np.zeros(8) # /* QZSS iono model parameters {a0,a1,a2,a3,b0,b1,b2,b3} */
        self.ion_bds = np.zeros([1000, 8]) # /* BeiDou iono model parameters {a0,a1,a2,a3,b0,b1,b2,b3} */
        self.ion_irn = np.zeros(8) # /* IRNSS iono model parameters {a0,a1,a2,a3,b0,b1,b2,b3} */
        self.glo_fcn = np.zeros(32, dtype=int) # /* GLONASS FCN + 8 */

        # 匹配广播星历的数据
        self.eph_mat = np.nan
        self.geph_mat = np.nan
        self.seph_mat = np.nan

        self.excsats = []

        self.err = [0, 0.003, 0.003, 0.0, 0, 0, 5e-12]  # error sigmas [-, base, el, bl, snr, rcvstd, satclk] 设置方差的拟合参数


class Obs_set():
    def __init__(self):
        self.GNSS = []
        self.GPS = []
        self.GLO = []
        self.GAL = []
        self.BDS = []
        self.QZS = []
        self.IRN = []
        self.SBS = []

class Sta():
    ver = 0.0           # /* version */
    name = None         # /* marker name */
    marker = None       # /* marker number */
    antdes = None       # /* antenna descriptor */
    antsno = None       # /* antenna serial number */
    rectype = None      # /* receiver type descriptor */
    recver = None       # /* receiver firmware version */
    recsno = None       # /* receiver serial number */
    antsetup = None     # /* antenna setup id */
    itrf = None         # /* ITRF realization year */
    deltype = None      # /* antenna delta type (0:enu,1:xyz) */
    pos = np.zeros(3)   # /* station position (ecef) (m) */
    dela = np.zeros(3)  # /* antenna position delta (e/n/u or x/y/z) (m) */
    hgt = 0.0           # /* antenna height (m) */
    glo_cp_align = None # /* GLONASS code-phase alignment (0:no,1:yes) */
    glo_cp_bias = np.zeros(4)   # /* GLONASS code-phase biases {1C,1P,2C,2P} (m) */
    interval = None     # /* interval */
    first_time = None

class Sol():
      def __init__(self):
          self.dtr = np.zeros(5) # 钟差和系统时间偏移
          self.dtrd = 0
          self.rr = np.zeros(6) # 位置和速度
          self.qr = np.zeros(6) # 方差+协方差
          self.qv = np.zeros((3, 3))
          self.stat = SOLQ_NONE # 判断数据是否可用
          self.ns = 0
          self.age = 0
          self.ratio = 0
          self.t = gtime_t()
          self.bias = np.zeros(3)
          self.b1 = 0
          self.dop = np.zeros(4)
          # ele and azi
          self.az = np.nan
          self.el = np.nan
          self.az_sat = np.nan
          self.el_sat = np.nan

          self.sta_x = np.zeros(3)

class Sac():
    def __init__(self):
        self.rs = np.nan
        self.Vars = np.nan
        self.svh = np.nan

class Sat_():
    def __init__(self):
        self.vsat = np.nan
        self.az = np.nan
        self.el = np.nan
        self.resp = np.nan

        # gross test
        self.v = np.nan
        self.ns = np.nan
        self.satpos = np.nan
        # w test
        self.Q = np.nan
        self.H = np.nan


def epoch2time(ep):
    doy = [1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335]
    time = gtime_t()
    year = int(ep[0])
    mon = int(ep[1])
    day = int(ep[2])

    if year < 1970 or year > 2099 or mon < 1 or mon > 12:
        return time
    days = (year-1970)*365+(year-1969)//4+doy[mon-1]+day-2
    if year % 4 == 0 and mon >= 3:
        days += 1
    sec = int(ep[5])
    time.time = days*86400+int(ep[3])*3600+int(ep[4])*60+sec
    time.sec = ep[5]-sec
    return time

def time2epoch(t):
    mday = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31, 31, 28, 31, 30, 31,
            30, 31, 31, 30, 31, 30, 31, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31,
            30, 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    days = int(t.time/86400)
    sec = int(t.time-days*86400)
    day = days % 1461
    for mon in range(48):
        if day >= mday[mon]:
            day -= mday[mon]
        else:
            break
    ep = [0, 0, 0, 0, 0, 0]
    ep[0] = 1970+days//1461*4+mon//12
    ep[1] = mon % 12+1
    ep[2] = day+1
    ep[3] = sec//3600
    ep[4] = sec % 3600//60
    ep[5] = sec % 60+t.sec
    return ep

def gpst2utc(tgps, leaps_=0):
    for i in range(leaps.shape[0]):
        if leaps[i][0] > 0:
            tutc = timeadd(tgps, leaps[i][6])
            if timediff(tutc, epoch2time(leaps[i])) >= 0.0:
                return tutc
    return tgps

def utc2gpst(tutc, leaps_=0):
    for i in range(leaps.shape[0]):
        if leaps[i][0] > 0:
            if timediff(tutc, epoch2time(leaps[i])) >= 0.0:
                tgps = timeadd(tutc, -leaps[i][6])
                return tgps
    return tutc

def timeadd(t: gtime_t, sec: float):
    tr = copy(t)
    tr.sec += sec
    tt = floor(tr.sec)
    tr.time += int(tt)
    tr.sec -= tt
    return tr

def timediff(t1: gtime_t, t2: gtime_t):
    dt = t1.time - t2.time
    dt += (t1.sec - t2.sec)
    return dt

def gpst2time(week, tow):
    t = epoch2time(gpst0)
    if tow < -1e9 or tow > 1e9:
        tow = 0.0
    t.time += 86400*7*week+int(tow)
    t.sec = tow-int(tow)
    return t

def time2gpst(t: gtime_t):
    t0 = epoch2time(gpst0)
    sec = t.time-t0.time
    week = int(sec/(86400*7))
    tow = sec-week*86400*7+t.sec
    return week, tow

def bdt2time(week, tow):
    t = epoch2time(bdt0)
    if tow < -1e9 or tow > 1e9:
        tow = 0.0
    t.time += 86400*7*week+int(tow)
    t.sec = tow-int(tow)
    return t

def time2bdt(t: gtime_t):
    t0 = epoch2time(bdt0)
    sec = t.time-t0.time
    week = int(sec/(86400*7))
    tow = sec-week*86400*7+t.sec
    return week, tow

def gst2time(week, tow):
    t = epoch2time(gst0)
    if tow < -1e9 or tow > 1e9:
        tow = 0.0
    t.time += 86400*7*week+int(tow)
    t.sec = tow-int(tow)
    return t

def time2gst(t: gtime_t):
    t0 = epoch2time(gst0)
    sec = t.time-t0.time
    week = int(sec/(86400*7))
    tow = sec-week*86400*7+t.sec
    return week, tow

def bdt2gpst(t: gtime_t):
    return timeadd(t, 14.0)

def gpst2bdt(t: gtime_t):
    return timeadd(t, -14.0)

def time2doy(t):
    ep = time2epoch(t)
    ep[1] = ep[2] = 1.0
    ep[3] = ep[4] = ep[5] = 0.0
    return timediff(t, epoch2time(ep))/86400+1

# 是用来调整t与t0的周数在同一周
def adjweek(t, t0):
    tt = timediff(t, t0)
    if tt < -302400.0:
        return timeadd(t, 604800.0)
    if tt > 302400.0:
        return timeadd(t, -604800.0)
    return t

# 是用来调整t与t0的周数在同一天 GLONASS
def adjday(t, t0):
    tt = timediff(t, t0)
    if tt < -43200.0:
        return timeadd(t, 86400.0)
    if tt > 43200.0:
        return timeadd(t, -86400.0)
    return t

def prn2sat(sys, prn):
    if sys == uGNSS.GPS:
        sat = prn
    elif sys == uGNSS.GLO:
        sat = prn + 100
    elif sys == uGNSS.BDS:
        sat = prn + 200
    elif sys == uGNSS.GAL:
        sat = prn + 300
    elif sys == uGNSS.QZS:
        sat = prn + 400
    elif sys == uGNSS.SBS:
        sat = prn + 500
    elif sys == uGNSS.IRN:
        sat = prn + 600
    else:
        sat = 0
    return sat

def sat2prn(sat):
    if sat > 600:
        prn = sat - 600
        sys = uGNSS.IRN
    elif sat > 500:
        prn = sat - 500
        sys = uGNSS.SBS
    elif sat > 400:
        prn = sat - 400
        sys = uGNSS.QZS
    elif sat > 300:
        prn = sat - 300
        sys = uGNSS.GAL
    elif sat > 200:
        prn = sat - 200
        sys = uGNSS.BDS
    elif sat > 100:
        prn = sat - 100
        sys = uGNSS.GLO
    else:
        prn = sat
        sys = uGNSS.GPS
    return (sys, prn)

def sat2id(sat):
    sys, prn = sat2prn(sat)
    gnss_tbl = {uGNSS.GPS: 'G', uGNSS.GAL: 'E', uGNSS.BDS: 'C', uGNSS.GLO: 'R',
                uGNSS.QZS: 'J', uGNSS.IRN: 'I', uGNSS.SBS: 'S'}
    return '%s%02d' % (gnss_tbl[sys], prn)

def id2sat(id_):
    gnss_tbl = {'G': uGNSS.GPS, 'E': uGNSS.GAL, 'C': uGNSS.BDS, 'R': uGNSS.GLO,
                'J': uGNSS.QZS, 'I': uGNSS.IRN, 'S': uGNSS.SBS}
    if id_[0] not in gnss_tbl:
        return -1
    sys = gnss_tbl[id_[0]]
    prn = int(id_[1:3])
    sat = prn2sat(sys, prn)
    return sat

def vnorm(r):
    return r / norm(r)

def satexclude(sat, var, svh, nav):
    sys, _ = sat2prn(sat)
    if sat in nav.excsats:
        return 1
    if sys == uGNSS.QZS:
        svh = svh & 254
    if svh:
       return 1
    if var > MAX_VAR_EPH:
        return 1
    return 0

def geodist(rs, rr):
    e = rs - rr
    r = norm(e)
    e /= r
    r += rCST.OMGE * (rs[0] * rr[1] - rs[1] * rr[0]) / rCST.CLIGHT
    return r, e

def geodist_h(rs, rr):
    e = rs - rr
    r = np.linalg.norm(x=e, axis=1, keepdims=False)
    r = r[:, np.newaxis]
    e /= r
    ra = rCST.OMGE*(rs[:, 0]*rr[1]-rs[:, 1]*rr[0])/rCST.CLIGHT
    r = r.T + ra
    return r, e

def dops_h(H):
    Qinv = inv(np.dot(H.T, H))
    dop = np.diag(Qinv)
    hdop = dop[0]+dop[1]  # TBD
    vdop = dop[2]  # TBD
    pdop = hdop+vdop
    gdop = pdop+dop[3]
    dop = np.sqrt(np.array([gdop, pdop, hdop, vdop]))
    return dop

def dops_mh(H, rr):
    llh = ecef2pos(rr)
    B = llh[0]
    L = llh[1]
    S = np.array([[-sin(B)*cos(L), -sin(B)*sin(L), cos(B)],
                  [-sin(L), cos(B), 0],
                  [cos(B)*cos(L), cos(B)*sin(L), sin(B)]])

    Qinv = inv(np.dot(H.T, H))
    H_ = H[:, 0:3] @ S
    Qinv_ = S @ Qinv[0:3, 0:3] @ S.T
    dop_xyzt = np.diag(Qinv)
    dop_neu = np.diag(Qinv_)
    hdop = dop_neu[0] + dop_neu[1]  # TBD
    vdop = dop_neu[2]  # TBD
    pdop = dop_xyzt[0] + dop_xyzt[1] + dop_xyzt[2]
    gdop = pdop+dop_xyzt[3]
    dop = np.sqrt(np.array([gdop, pdop, hdop, vdop]))
    return dop

def dops(az, el, elmin):
    nm = az.shape[0]
    H = np.zeros((nm, 4))
    n = 0
    for i in range(nm):
        if el[i] < elmin:
            continue
        cel = cos(el[i])
        sel = sin(el[i])
        H[n, 0] = cel*sin(az[i])
        H[n, 1] = cel*cos(az[i])
        H[n, 2] = sel
        H[n, 3] = 1
        n += 1
    if n < 4:
        return None
    Qinv = inv(H.T @ H)
    dop = np.diag(Qinv)
    hdop = dop[0]+dop[1]
    vdop = dop[2]
    pdop = hdop+vdop
    gdop = pdop+dop[3]
    dop = np.sqrt(np.array([gdop, pdop, hdop, vdop]))
    return dop


def xyz2enu(pos):
    sp = sin(pos[0])
    cp = cos(pos[0])
    sl = sin(pos[1])
    cl = cos(pos[1])
    E = np.array([[-sl, cl, 0],
                  [-sp*cl, -sp*sl, cp],
                  [cp*cl, cp*sl, sp]])
    return E


def ecef2pos(r):
    pos = np.zeros(3)
    e2 = rCST.FE_WGS84*(2-rCST.FE_WGS84)
    r2 = r[0]**2+r[1]**2
    v = rCST.RE_WGS84
    z = r[2]
    zk = 0
    while abs(z - zk) >= 1e-4:
        zk = z
        sinp = z / np.sqrt(r2+z**2)
        v = rCST.RE_WGS84 / np.sqrt(1 - e2 * sinp**2)
        z = r[2] + v * e2 * sinp
    pos[0] = np.arctan(z / np.sqrt(r2)) if r2 > 1e-12 else np.pi / 2 * np.sign(r[2])
    pos[1] = np.arctan2(r[1], r[0]) if r2 > 1e-12 else 0
    pos[2] = np.sqrt(r2 + z**2) - v
    return pos

def ecef2pos_h(r):
    pos = np.zeros(3)
    e2 = rCST.FE_WGS84*(2-rCST.FE_WGS84)
    r2 = r[0]**2+r[1]**2
    v = rCST.RE_WGS84
    z = r[2]
    zk = 0
    while abs(z - zk) >= 1e-4:
        zk = z
        sinp = z / np.sqrt(r2+z**2)
        v = rCST.RE_WGS84 / np.sqrt(1 - e2 * sinp**2)
        z = r[2] + v * e2 * sinp
    pos[0] = np.arctan(z / np.sqrt(r2)) if r2 > 1e-12 else np.pi / 2 * np.sign(r[2])
    pos[1] = np.arctan2(r[1], r[0]) if r2 > 1e-12 else 0
    pos[2] = np.sqrt(r2 + z**2) - v
    return pos


def pos2ecef(pos, isdeg: bool = False):
    if isdeg:
        pos[0] *= np.pi/180.0
        pos[1] *= np.pi/180.0
    s_p = sin(pos[0])
    c_p = cos(pos[0])
    s_l = sin(pos[1])
    c_l = cos(pos[1])
    e2 = rCST.FE_WGS84 * (2.0 - rCST.FE_WGS84)
    v = rCST.RE_WGS84 / sqrt(1.0 - e2 * s_p**2)
    r = np.array([(v + pos[2]) * c_p*c_l,
                  (v + pos[2]) * c_p*s_l,
                  (v * (1.0 - e2) + pos[2]) * s_p])
    return r


def ecef2enu(pos, r):
    E = xyz2enu(pos)
    e = E @ r
    return e

def ecef2enu_h(pos, r):
    E = xyz2enu(pos)
    e = E @ r
    return e

def covenu(llh, P):
    E = xyz2enu(llh)
    return E @ P @ E.T

def covecef(llh, Q):
    E = xyz2enu(llh)
    return E.T @ Q @ E

def deg2dms(deg):
    if deg < 0.0:
        sign = -1
    else:
        sign = 1
    a = fabs(deg)
    dms = np.zeros(3)
    dms[0] = floor(a)
    a = (a-dms[0])*60.0
    dms[1] = floor(a)
    a = (a-dms[1])*60.0
    dms[2] = a
    dms[0] *= sign
    return dms

def satazel(pos, e):
    if pos[2] > -rCST.RE_WGS84 + 1:
        enu = ecef2enu(pos, e)
        az = atan2(enu[0], enu[1]) if np.dot(enu, enu) > 1e-12 else 0
        az = az if az > 0 else az + 2 * np.pi
        el = asin(enu[2])
        return az, el
    else:
        return 0, np.pi/2

def satazel_h(pos, e):
    if pos[2] > -rCST.RE_WGS84 + 1:
        enu = ecef2enu(pos, e.T)
        enu = enu.T
        az = np.arctan2(enu[:, 0], enu[:, 1])
        az[np.linalg.norm(x=enu, axis=1, keepdims=False) <= 1e-6] = 0
        az[az <= 0] += 2*np.pi
        el = np.arcsin(enu[:, 2])
        return az, el
    else:
        one = np.ones(e.shape[0])
        return one*0, one*np.pi/2

def ionmodel(t, pos, az, el, ion=None):
    ion_default = np.array([ # /* 2004/1/1 */
        0.1118E-07, -0.7451E-08, -0.5961E-07, 0.1192E-06,
        0.1167E+06, -0.2294E+06, -0.1311E+06, 0.1049E+07])

    if pos[2] < -1E3 or el <= 0:
        return 0.0
    if norm(ion, 8) <= 0.0:
        ion = ion_default

    psi = 0.0137 / (el / np.pi + 0.11) - 0.022
    phi = pos[0] / np.pi + psi * cos(az)
    phi = np.max((-0.416, np.min((0.416, phi))))
    lam = pos[1]/np.pi + psi * sin(az) / cos(phi * np.pi)
    phi += 0.064 * cos((lam - 1.617) * np.pi)
    _, tow = time2gpst(t)
    tt = 43200.0 * lam + tow  # local time
    tt -= np.floor(tt / 86400) * 86400
    f = 1.0 + 16.0 * np.power(0.53 - el/np.pi, 3.0)  # slant factor

    h = [1, phi, phi**2, phi**3]
    amp = np.dot(h, ion[0:4])
    per = np.dot(h, ion[4:8])
    amp = max(amp, 0)
    per = max(per, 72000.0)
    x = 2.0 * np.pi * (tt - 50400.0) / per
    if np.abs(x) < 1.57:
        v = 5e-9 + amp * (1.0 + x * x * (-0.5 + x * x / 24.0))
    else:
        v = 5e-9
    diono = rCST.CLIGHT * f * v
    return diono

def tropmodel(t, pos, el, humi):
    temp0  = 15 # temparature at sea level
    if pos[2] < -100 or pos[2] > 1e4 or el <= 0:
        return 0, 0, 0
    hgt = max(pos[2], 0)
    # standard atmosphere
    pres = 1013.25 * np.power(1 - 2.2557e-5 * hgt, 5.2568)
    temp = temp0 - 6.5e-3 * hgt + 273.16
    e = 6.108 * humi * np.exp((17.15 * temp - 4684.0) / (temp - 38.45))
    # saastamoinen model
    z = np.pi / 2.0 - el
    trop_hs = 0.0022768 * pres / (1.0 - 0.00266 * np.cos(2 * pos[0]) - 
              0.00028e-3 * hgt) / np.cos(z)
    trop_wet = 0.002277 * (1255.0 / temp+0.05) * e / np.cos(z)
    M = 1.001/sqrt(0.002001+(sin(el))**2) # 映射函数
    return trop_hs, trop_wet, z

# 分隔字符串
def flt1(u):
    u = u.replace('D', 'E')
    u = u.replace('0-', '0 -')
    u = u.replace('1-', '1 -')
    u = u.replace('2-', '2 -')
    u = u.replace('3-', '3 -')
    u = u.replace('4-', '4 -')
    u = u.replace('5-', '5 -')
    u = u.replace('6-', '6 -')
    u = u.replace('7-', '7 -')
    u = u.replace('8-', '8 -')
    u = u.replace('9-', '9 -')
    data = u.split()
    return data

def obs2code(obs):
    try:
        return obscodes.index(obs)
    except:
        return 0

def code2obs(code):
    if (code <= CODE_NONE or MAXCODE<code):
        return ""
    return obscodes[code]

# 索引转换为观测类型 0:C 1:L 2:D 3:S
def id2type(i):
    return codetype[i]

# /* GPS obs code to frequency -------------------------------------------------*/
def code2freq_GPS(code):
    obs = code2obs(code)

    if obs[0] == '1': # /* L1 */
        freq = FREQL1
        return 0, freq
    elif obs[0] == '2': # /* L2 */
        freq = FREQL2
        return 1, freq
    elif obs[0] == '5':
        freq = FREQL5
        return 2, freq

# /* GLONASS obs code to frequency ---------------------------------------------*/
def code2freq_GLO(code):
    fcn = 0
    obs = code2obs(code)
    if obs[0] == '1':
        freq = FREQ1_GLO+DFRQ1_GLO*fcn
        return 0, freq #/*G1*/
    elif obs[0] == '2':
        freq = FREQ2_GLO+DFRQ2_GLO*fcn
        return 1, freq #/*G2*/
    elif obs[0] == '3':
        freq = FREQ3_GLO
        return 2, freq #/*G3*/
    elif obs[0] == '4':
        freq = FREQ1a_GLO
        return 3, freq #/*G1a*/
    elif obs[0] == '6':
        freq = FREQ2a_GLO
        return 4, freq #/*G2a*/

# /* BDS obs code to frequency -------------------------------------------------*/
def code2freq_BDS(code):
    obs = code2obs(code)
    if obs[0] == '1':
        freq = FREQL1
        return 5, freq  # /* B1C */
    elif obs[0] == '2':
        freq = FREQ1_CMP
        return 0, freq  # /* B1I */
    elif obs[0] == '7':
        freq = FREQ2_CMP
        if obs[1] == 'D' or obs[1] == 'P' or obs[1] == 'Z':
            return 6, freq  # /* B2b */
        return 1, freq  # /* B2I*/
    elif obs[0] == '5':
        freq = FREQL5
        return 2, freq  # /* B2a */
    elif obs[0] == '6':
        freq = FREQ3_CMP
        return 3, freq  # /* B3 */
    elif obs[0] == '8':
        freq = FREQE5ab
        return 4, freq  # /* B2ab */

# /* Galileo obs code to frequency ---------------------------------------------*/
def code2freq_GAL(code):
    obs = code2obs(code)
    if obs[0] == '1':
        freq = FREQL1
        return 0, freq  # /* E1 */
    elif obs[0] == '7':
        freq = FREQE5b
        return 1, freq  # /* E5b */
    elif obs[0] == '5':
        freq = FREQL5
        return 2, freq  # /* E5a */
    elif obs[0] == '6':
        freq = FREQL6
        return 3, freq  # /* E6 */
    elif obs[0] == '8':
        freq = FREQE5ab
        return 4, freq  # /* E5ab */

# /* QZSS obs code to frequency ------------------------------------------------*/
def code2freq_QZS(code):
    obs = code2obs(code)
    if obs[0] == '1':
        freq = FREQL1
        return 0, freq  # /* L1 */
    elif obs[0] == '2':
        freq = FREQL2
        return 1, freq  # /* L2 */
    elif obs[0] == '5':
        freq = FREQL5
        return 2, freq  # /* L5 */
    elif obs[0] == '6':
        freq = FREQL6
        return 3, freq  # /* L6 */

# /* SBAS obs code to frequency ------------------------------------------------*/
def code2freq_SBS(code):
    obs = code2obs(code)
    if obs[0] == '1':
        freq = FREQL1
        return 0, freq  # /* L1 */
    elif obs[0] == '5':
        freq = FREQL5
        return 1, freq  # /* L5 */


# /* NavIC obs code to frequency -----------------------------------------------*/
def code2freq_IRN(code):
    obs = code2obs(code)
    if obs[0] == '5':
        freq = FREQL1
        return 0, freq  # /* L5 */
    elif obs[0] == '9':
        freq = FREQs
        return 1, freq  # /* S */
    elif obs[0] == '1':
        freq = FREQs
        return 2, freq  # /* S */

def code2idx(sys, code):

    if sys == 0:
        return code2freq_GPS(code)
    elif sys == 1:
        return code2freq_GLO(code)
    elif sys == 2:
        return code2freq_BDS(code)
    elif sys == 3:
        return code2freq_GAL(code)
    elif sys == 4:
        return code2freq_QZS(code)
    elif sys == 5:
        return code2freq_SBS(code)
    elif sys == 6:
        return code2freq_IRN(code)

def getcodepri(sys, code):
    i = 0
    if sys == 0:
        i = 0
    elif sys == 1:
        i = 1
    elif sys == 2:
        i = 2
    elif sys == 3:
        i = 3
    elif sys == 4:
        i = 4
    elif sys == 5:
        i = 5
    elif sys == 6:
        i = 6

    if (code2idx(sys, code)[0]) < 0:
        return 0
    obs = code2obs(code)

    j = code2idx(sys, code)[0]
    # /* search code priority */
    if codepris[i][j].find(obs[1])+1:
        return 14 - codepris[i][j].find(obs[1])
    else:
        return 0

def code2freq(sys, code):
    if sys == uGNSS.GPS:
        freq = code2freq_GPS(code)[1]
    elif sys == uGNSS.GLO:
        freq = code2freq_GLO(code)[1]
    elif sys == uGNSS.BDS:
        freq = code2freq_BDS(code)[1]
    elif sys == uGNSS.GAL:
        freq = code2freq_GAL(code)[1]
    elif sys == uGNSS.QZS:
        freq = code2freq_QZS(code)[1]
    elif sys == uGNSS.SBS:
        freq = code2freq_SBS(code)[1]
    elif sys == uGNSS.IRN:
        freq = code2freq_IRN(code)[1]
    return freq

def sat2freq(freq, code):
    return freq[code]

# if char to float
def isFloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

# if char to int
def isint(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def rms(data):
    squared_data = np.square(data)
    mean_squared = np.nanmean(squared_data, axis=0)
    rms = np.sqrt(mean_squared)
    return rms

def rcvstds(nav, obs):
    # skip if weighting factor is zero
    if nav.err[3] == 0:
        return
    for i in np.argsort(obs.sat):
        for f in range(nav.nf):
            s = obs.sat[i] - 1
            # Lstd: 0.004 cycles -> m
            nav.rcvstd[s, f] = obs.Lstd[i, f] * 0.004 * 0.2
            # Pstd: 0.01*2^(n+5)
            nav.rcvstd[s, f+nav.nf] = 0.01 * (1 << (obs.Pstd[i, f] + 5))
