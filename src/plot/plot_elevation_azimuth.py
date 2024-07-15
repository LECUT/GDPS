import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings(action='ignore', message='Adding an axes using the same arguments as a previous axes currently reuses the earlier instance')

def azi_ele(data_a, data_e, legend):
    ax = plt.subplot(111)
    # ax = fig.add_subplot(111)
    sat_num = data_e.shape[1]
    # colors = distinctipy.get_colors(sat_num)
    for i in range(sat_num):
        df = data_a.iloc[:, i].apply(lambda x: x-180 if x > 180 else x+180)
        ax.scatter(df, data_e.iloc[:, i], s=20, marker='.', label=legend[i])
    ax.grid(linestyle='--')
    font = {'family': 'Times New Roman',
            'size': 16,
            'weight': 'bold',
            }
    ax.set_xlim([0, 360])
    ax.set_ylim([0, 90])
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.1), ncol=12, borderaxespad=0, labelspacing=0, handlelength=1, handleheight=1, handletextpad=0.01, columnspacing=0.01)
    ax.set_xlabel(u"Azimuth (°)", font)
    ax.set_ylabel(u"Elevation (°)", font)