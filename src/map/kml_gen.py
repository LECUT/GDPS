import math
import numpy as np

kmlstr_header = '''<?xml version = "1.0" encoding = "UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"
     xmlns:gx = "http://www.google.com/kml/ext/2.2" > 
<Document>
      <Style id="track">
         <IconStyle>
            <color>%s</color>
            <colorMode>normal</colorMode>
            <scale> 0.50</scale>
            <Icon>
               <href>http://maps.google.com/mapfiles/kml/shapes/track.png</href>
            </Icon>
         </IconStyle>
         <LabelStyle>
            <color>%s</color>
            <scale>7.000000e-01</scale>
         </LabelStyle>
      </Style>'''
kmlstr_body = '''
   <Placemark>
      <styleUrl>#track</styleUrl>
      <Style> <IconStyle>  <heading>%f</heading> </IconStyle>  </Style>
      <Point>
         <coordinates>%.9f,%.9f,%f</coordinates>
      </Point>
      <ExtendedData>
         <Data name="Index">
         <value>%d</value>
         </Data>
      </ExtendedData>
   </Placemark>'''
kmlstr_end = '''
</Document>
</kml>
'''

# XYZ to BLH
def XYZ_BLH(xyz):
    X = xyz[0]
    Y = xyz[1]
    Z = xyz[2]
    a = 6378137.0
    b = 6356752.3142
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
        L = L*180.0/np.pi
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

def XYZ_NEH(XYZ, REFXYZ):
    """
     XYZ to NEH
     """
    from quality_check import rtkcmn as com
    BLH = XYZ_BLH(REFXYZ)
    B = np.radians(BLH[0])
    L = np.radians(BLH[1])
    S = np.array([[-np.sin(B)*np.cos(L), -np.sin(B)*np.sin(L), np.cos(B)],
                  [-np.sin(L), np.cos(L), 0],
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


def data_convert(spp_data):
    # spp_data = pd.read_csv('E:/working/data_process/data/result/cpt0870.pos', sep='\s+')
    spp_data_ = np.array(spp_data[['X(m)', 'Y(m)', 'Z(m)']])
    spp_blh = np.full([spp_data_.shape[0], spp_data_.shape[1]], np.nan)
    for i in range(spp_data_.shape[0]):
        spp_blh[i] = XYZ_BLH(spp_data_[i])
    return spp_blh

def kml_gen(data_dir, spp_blh):
    heading = None
    name = 'pathgen'
    color = 'ffff0000'
    max_points = None
    pos = spp_blh.copy()

    # gen kml according to data and template
    kml_file = data_dir + '.kml'
    f = open(kml_file, 'w+')
    f.truncate()
    # write header
    lines = (kmlstr_header)% (color, color)
    f.write(lines)
    # write data
    ndim = pos.ndim
    if ndim == 1:
        if heading is None:
            lines = (kmlstr_body)% (0, pos[1], pos[0], pos[2], 0)
        else:
            lines = (kmlstr_body)% (heading, pos[1], pos[0], pos[2], 0)
        f.write(lines)
    else:
        if max_points is None:
            max_points = 8000.0
        step = int(math.ceil(pos.shape[0]/max_points))
        for i in range(0, pos.shape[0], step):
            if pos[i][2] < 0:
                pos[i][2] = 0
            if heading is None:
                lines = (kmlstr_body)% (0, pos[i][1], pos[i][0], pos[i][2], i)
            else:
                lines = (kmlstr_body)% (heading[i], pos[i][1], pos[i][0], pos[i][2], i)
            f.write(lines)
    # write end
    f.write(kmlstr_end)
    f.close()
    return kml_file

def kml_expos(spp_data, data_dir):
    spp_blh = data_convert(spp_data)
    kml_file = kml_gen(data_dir, spp_blh)
    return kml_file