import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import warnings
warnings.filterwarnings(action='ignore', message='Adding an axes using the same arguments as a previous axes currently reuses the earlier instance')

def azim(time, data, legend):
    ax = plt.subplot(111)
    # ax = fig.add_subplot(111)
    sat_num = data.shape[1]
    # colors = distinctipy.get_colors(sat_num)
    for i in range(sat_num):
        df = data.iloc[:, i].apply(lambda x: x - 180 if x > 180 else x + 180)
        ax.scatter(time, df, s=25, marker='o', label=legend[i])
    ax.grid(linestyle='--')
    font = {'family': 'Times New Roman',
            'size': 16,
            'weight': 'bold',
            }
    legend_ax = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
    for handle in legend_ax.legendHandles:
        handle.set_sizes([10])
        handle.set_alpha(0.4)
    ax.set_ylim([0, 360])
    ax.set_xlabel(u"GPST (HH:MM)", font)
    ax.set_ylabel(u"Azimuth (°)", font)
    xfmt = mdate.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)