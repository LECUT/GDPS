from .rtkcmn import timediff
import numpy as np

def timesapan(cfg, epoch_t):
    dt = cfg.interval()/timediff(epoch_t[1], epoch_t[0])
    conf_ts = cfg.time_beg()
    conf_te = cfg.time_end()
    obs_ts = epoch_t[0]
    obs_te = epoch_t[-1]
    if obs_ts.time != 0 and timediff(conf_ts, obs_ts) >= 0:
        ts = conf_ts
    else:
        ts = obs_ts
    if obs_te.time != 0 and timediff(conf_te, obs_te) <= 0:
        te = conf_te
    else:
        te = obs_te
    tspan = np.fix(timediff(te, ts)/dt) + 1
    ts_pos = np.nan
    te_pos = np.nan
    for i in range(len(epoch_t)):
        if timediff(epoch_t[i], ts) >= 0:
            ts_pos = i
            break
    for i in range(len(epoch_t)):
        if timediff(epoch_t[i], te) >= 0:
            te_pos = i
            break
    return tspan, ts, te, dt, ts_pos, te_pos