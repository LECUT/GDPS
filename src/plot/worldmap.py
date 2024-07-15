from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np
from adjustText import adjust_text

plt.figure(figsize=(12,9))
plt.rc('font', family='Times New Roman')
plt.rc('font', size=20)
plt.rc('lines', linewidth=2)
# BSHM CIBG PTGG GAMG KIT3 KRGG JOZE METG MIZU NNOR
sites=['BSHM','CIBG','PTGG','GAMG','KIT3','KRGG','JOZE','METG','MIZU','NNOR']
lons=[35.023,106.849,121.041,127.920,66.885,70.256,21.032,24.384,141.133,116.193]
lats=[32.779,-6.490,14.535,35.590,39.135,-49.352,52.097,60.242,39.135,-31.049]

mymap = Basemap(projection='robin', lat_0=0, lon_0=0,resolution='i',
                area_thresh=5000.0)
mymap.fillcontinents(color='white', lake_color='lightskyblue')
mymap.drawmapboundary(fill_color='skyblue')
mymap.drawmeridians(np.arange(0, 360, 60), labels=[1,0,0,1])
mymap.drawparallels(np.arange(-90, 90.001, 30), labels=[1,0,0,1])
x, y = mymap(lons, lats)

for name,lon,lat in zip(sites,x,y):
    print (name, lon, lat)
    plt.plot(lon, lat, marker='o', color='red', markersize=9)
    # plt.text(lon, lat, name, transform=ccrs.Geodetic())
    if name=='GAMG':
        plt.text(lon + 300000, lat - 650000, name, horizontalalignment='left')
    else:
        plt.text(lon+300000, lat-280000, name,horizontalalignment='left')

# plt.show()
savename = 'result.png'


plt.savefig(savename, dpi=600, bbox_inches='tight')
plt.close()