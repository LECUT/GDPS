import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import warnings
warnings.filterwarnings(action='ignore', message='Adding an axes using the same arguments as a previous axes currently reuses the earlier instance')

def elev(time, data, band_pos_, legend):
    ax = plt.subplot(111)
    sat_num = data.shape[1]
    # colors = distinctipy.get_colors(sat_num)
    for i in range(sat_num):
        ax.scatter(time, data.iloc[:, i], s=14, marker='o', label=legend[i])
    ax.grid(linestyle='--')
    font = {'family': 'Times New Roman',
            'size': 16,
            'weight': 'bold',
            }
    legend_ax = ax.legend(bbox_to_anchor=((0.01, 0.01)), loc='lower left', ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
    for handle in legend_ax.legendHandles:
        handle.set_sizes([10])
        handle.set_alpha(0.4)
    ax.set_xlabel(u"GPST (HH:MM)", font)
    ax.set_ylabel(u"CN0 (dB-Hz)", font)
    xfmt = mdate.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)