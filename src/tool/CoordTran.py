import numpy as np
import math

def get_datum(datum):
    if datum == 'WGS84':
        a = 6378137.0
        b = 6356752.3142
    elif datum == 'CGCS2000':
        a = 6378137.0
        b = 6356752.3141
    return a, b

# XYZ to BLH
def XYZ_BLH(datum, xyz):
    a, b = get_datum(datum)
    X = xyz[0]
    Y = xyz[1]
    Z = xyz[2]
    # a = 6378137.0
    # b = 6356752.3142
    e2 = (a**2 - b**2)/(a**2)
    e = math.sqrt(e2)
    # comput L
    if X == 0 and Y > 0:
        L = 90
    elif X == 0 and Y < 0:
        L = -90
    elif X < 0 and Y > 0:
        L = math.atan(Y/X)
        L = L * 180.0 / np.pi
        L = L + 180
    elif X < 0 and Y <= 0:
        L = math.atan(Y/X)
        L = L*180.0/np.pi
        L = L-180
    else:
        L = math.atan(Y/X)
        L = L*180.0/np.pi66
    b0 = math.atan(Z/math.sqrt(X**2 + Y**2))
    N_temp = a/math.sqrt((1 - e2*math.sin(b0)*math.sin(b0)))
    b1 = math.atan((Z + N_temp*e2*math.sin(b0))/math.sqrt(X**2 + Y**2))
    while abs(b0 - b1) > 1e-12:
        b0 = b1
        N_temp = a/math.sqrt(1 - e2*math.sin(b0)*math.sin(b0))
        b1 = math.atan((Z + N_temp*e2*math.sin(b0))/math.sqrt(X**2 + Y**2))
    B = b1
    N = a/math.sqrt(1 - e2*math.sin(B)**2)
    H = (math.sqrt(X**2 + Y**2)/math.cos(B)) - N
    B = math.degrees(B)
    #L = math.degrees(L)
    BLH = np.array([B, L, H])
    return BLH

def BLH_XYZ(datum, BLH):
    a, b = get_datum(datum)

    B = np.radians(BLH[0])
    L = np.radians(BLH[1])
    H = BLH[2]

    # a = 6378137.0    # WGS84
    # b = 6356752.3142 # WGS84

    alfa = (a - b)/a
    e = math.sqrt(2*alfa - alfa*alfa)
    W = math.sqrt(1.0 - e*e*math.sin(B)*math.sin(B))
    N = a/W

    X = (N + H)*math.cos(B)*math.cos(L)
    Y = (N + H)*math.cos(B)*math.sin(L)
    Z = (N*(1.0 - e*e) + H)*math.sin(B)
    XYZ = np.array([X, Y, Z])
    return XYZ

def XYZ_NEU(datum, REFXYZ, XYZ):
    """
     XYZ to NEH
     """
    BLH = XYZ_BLH(datum, REFXYZ)
    B = np.radians(BLH[0])
    L = np.radians(BLH[1])
    S = np.array([[-1*np.sin(B)*np.cos(L), -1*np.sin(B)*np.sin(L), np.cos(B)],
                  [-1*np.sin(L), np.cos(L), 0],
                  [np.cos(B)*np.cos(L), np.cos(B)*np.sin(L), np.sin(B)]])

    delta_XYZ = np.array([XYZ[0] - REFXYZ[0],
                          XYZ[1] - REFXYZ[1],
                          XYZ[2] - REFXYZ[2]])
    NEH = np.dot(S, delta_XYZ)
    N = NEH[0]
    E = NEH[1]
    U = NEH[2]
    NEU = np.array([N, E, U])
    return NEU

def NEU_XYZ(datum, REFXYZ, NEH):
    """
    NEU to XYZ
    """
    BLH = XYZ_BLH(datum, REFXYZ)
    B = np.radians(BLH[0])
    L = np.radians(BLH[1])

    S = np.array([[-1*np.sin(B)*np.cos(L), -1*np.sin(L), np.cos(B)*np.cos(L)],
                  [-1*np.sin(B)*np.sin(L), np.cos(L), np.cos(B)*np.sin(L)],
                  [np.cos(B), 0, np.sin(B)]])
    NEU_mat = np.array([NEH[0],
                        NEH[1],
                        NEH[2]])

    center = np.array([REFXYZ[0],
                       REFXYZ[1],
                       REFXYZ[2]])

    XYZ = np.add(center, np.dot(S, NEU_mat))
    X = XYZ[0]
    Y = XYZ[1]
    Z = XYZ[2]
    XYZ = np.array([X, Y, Z])
    return XYZ

def BLH_NEU(datum, REFXYZ, BLH):
    """
    BLH to NEU
    """
    return XYZ_NEU(datum,  REFXYZ, BLH_XYZ(datum, BLH))

def NEU_BLH(datum, REFXYZ, NEU):
    """
    NEU to BLH
    """
    return XYZ_BLH(datum, NEU_XYZ(datum, REFXYZ, NEU))


def degrees_dms(degree):
    degrees = int(degree)
    decimal_minutes = abs(degree-degrees)*60
    minutes = int(decimal_minutes)
    seconds = (decimal_minutes - minutes)*60
    output = f"{degrees}°{minutes}′{seconds:.6f}″"
    return output

def dms_degrees(dms):
    degree  = int(dms.split("°")[0])
    minutes = int(dms.split("°")[1].split("′")[0].strip())
    seconds = float(dms.split("°")[1].split("′")[1].split("″")[0].strip())
    angle_decimal = degree + minutes/60 + seconds/3600
    return angle_decimal