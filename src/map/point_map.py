import math
import numpy as np

# XYZ to BLH
def XYZ_BLH(xyz):
    X = xyz[0]
    Y = xyz[1]
    Z = xyz[2]
    a = 6378137.0
    b = 6356752.3142
    e2 = (a ** 2 - b ** 2) / (a ** 2)
    e = math.sqrt(e2)
    # comput L
    if X == 0 and Y > 0:
        L = 90
    elif X == 0 and Y < 0:
        L = -90
    elif X < 0 and Y > 0:
        L = math.atan(Y / X)
        L = L * 180.0 / np.pi
        L = L + 180
    elif X < 0 and Y <= 0:
        L = math.atan(Y / X)
        L = L * 180.0 / np.pi
        L = L - 180
    else:
        L = math.atan(Y / X)
        L = L * 180.0 / np.pi
    b0 = math.atan(Z / math.sqrt(X ** 2 + Y ** 2))
    N_temp = a / math.sqrt((1 - e2 * math.sin(b0) * math.sin(b0)))
    b1 = math.atan((Z + N_temp * e2 * math.sin(b0)) / math.sqrt(X ** 2 + Y ** 2))
    while abs(b0 - b1) > 1e-12:
        b0 = b1
        N_temp = a / math.sqrt(1 - e2 * math.sin(b0) * math.sin(b0))
        b1 = math.atan((Z + N_temp * e2 * math.sin(b0)) / math.sqrt(X ** 2 + Y ** 2))
    B = b1
    N = a / math.sqrt(1 - e2 * math.sin(B) ** 2)
    H = (math.sqrt(X ** 2 + Y ** 2) / math.cos(B)) - N
    B = math.degrees(B)
    #L = math.degrees(L)
    cacilated_BLH = np.array([B, L, H])
    return cacilated_BLH

def data_convert(spp_data, data_dir):
    import pandas as pd
    # spp_data = pd.read_csv('E:/working/data_process/data/result/cpt0870.pos', sep='\s+')
    spp_data_ = np.array(spp_data[['X(m)', 'Y(m)', 'Z(m)']])
    spp_blh = np.full([spp_data_.shape[0], spp_data_.shape[1]], np.nan)
    for i in range(spp_data_.shape[0]):
        spp_blh[i] = XYZ_BLH(spp_data_[i])
    BL = spp_blh[:, 0:2].tolist()
    f = open(data_dir+'/lib/map/js/point_data.js', 'w+', encoding='UTF-8')
    f.truncate()
    f.write('data='+str(BL))
    f.close()
    return spp_blh

def point_map(spp_data, data_dir):
    spp_blh = data_convert(spp_data, data_dir)

