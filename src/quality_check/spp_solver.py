from .pntpos_h import pntpos
import numpy as np
from .timespan import timesapan
from .adjnav import adjnav
from .rtkcmn import uGNSS, Sol
import datetime
from time import strftime, localtime
import copy

def solver(obs, nav, sta, cfg, epoch_t):
    eph_mat, geph_mat, seph_mat = adjnav(nav)
    nav.eph_mat = eph_mat
    nav.geph_mat = geph_mat
    nav.seph_mat = seph_mat

    tepoch_sol = []
    tepoch_sat_cod = []
    motion_model = cfg.pos_kin()
    sol = copy.deepcopy(Sol())

    if motion_model == 0:
        sol.sta_x = sta.pos

    for i in range(len(obs)):
        obs0 = obs[i]
        if len(obs0.sat) > 0:
            sol, stat_v, vsat, sac = pntpos(obs0, nav, sta, sol, cfg)
            if stat_v > 0 and motion_model == 0:
                sol.sta_x = sol.rr[0:3]
            tepoch_sat_cod.append(copy.deepcopy(sac))
            tepoch_sol.append(copy.deepcopy(sol))
            print('[{}] spp of epoch {}; Status: {}'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), i, stat_v))
        else:
            tepoch_sat_cod.append([])
            tepoch_sol.append([])
            print('[{}] spp of epoch {}: no data;  Status: {}'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), i, -1))
    return tepoch_sol, tepoch_sat_cod




