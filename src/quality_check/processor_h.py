from .rinex_h import rnx_decode
from .spp_solver import solver
from .cal_qc1 import ele_azi, data_inte, data_full
from .cal_qc2 import data_tirm, data_visibility, pseudorange_gross, cs_mian, clk_jmp2, cal_csr, cal_multipath, cal_gfif, cal_iondelay, cal_pseudons, cal_carns, cal_time
from .save_data import save_path, save_file
from time import strftime, localtime
import numpy as np
from .gnss_config import GNSSconfig
import time
import functools
import warnings
warnings.filterwarnings(action='ignore', message='Error in atexit._run_exitfuncs')

def read_file(cfg):
    if cfg.nav_dir() != '':
        nav = rnx_decode.decode_navh(cfg.nav_dir())
        nav = rnx_decode.decode_navb(nav, cfg.nav_dir())
        print('[{}] success load broadcast ephemeris file!!!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    else:
        nav = None
        print('[{}] Have no broadcast ephemeris file!!!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))

    if cfg.obs_dir() != '':
        sta, ind, obs, epoch_t = rnx_decode.decode_obs(cfg.obs_dir(), cfg)
        print('[{}] success load observation file!!!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    else:
        sta, ind, obs, epoch_t = None, None, None, None
        print('[{}] Have no observation file!!!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))

    return nav, sta, ind, obs, epoch_t

def get_interval(sta, epoch_t):
    # set interval
    if sta.interval == None:
        epoch_s = np.array([t.time + t.sec for t in epoch_t])
        sta.interval = np.ceil(np.min(np.abs(np.diff(epoch_s - epoch_s[0]))))
        print('[{}] The data inerval is modified!!!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    return sta

def gnss_spp(id, obs, nav, sta, cfg, epoch_t):
    if len(obs) > 0:
        tepoch_sol_, tepoch_sat_cod_ = solver(obs, nav, sta, cfg, epoch_t)
    else:
        tepoch_sol_ = None
        tepoch_sat_cod_ = None
        print('[{}] No data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    return id, tepoch_sol_, tepoch_sat_cod_


def expos(configfile, executor):
    # configfile = './config_check.ini'

    print('[{}] Strat Execute!!!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))

    cfg = GNSSconfig(configfile)  # Configure File [ini]

    nav, sta, ind, obs, epoch_t = read_file(cfg)

    sta = get_interval(sta, epoch_t)

    # single point positioning (No discard data)
    spp_stime = time.time()
    # if len(obs.GPS) > 0:
    #     tepoch_sol_G, _ = solver(obs.GPS, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_G = None
    #     print('[{}] No GPS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.GLO) > 0:
    #     tepoch_sol_R, _ = solver(obs.GLO, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_R = None
    #     print('[{}] No GLONASS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.BDS) > 0:
    #     tepoch_sol_C, _ = solver(obs.BDS, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_C = None
    #     print('[{}] No BDS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.GAL) > 0:
    #     tepoch_sol_E, _ = solver(obs.GAL, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_E = None
    #     print('[{}] No Gailieo data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.QZS) > 0:
    #     tepoch_sol_J, _ = solver(obs.QZS, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_J = None
    #     print('[{}] No QZSS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.SBS) > 0:
    #     tepoch_sol_S, _ = solver(obs.SBS, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_S = None
    #     print('[{}] No SABS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.IRN) > 0:
    #     tepoch_sol_I, _ = solver(obs.IRN, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_I = None
    #     print('[{}] No IRNSS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # if len(obs.GNSS) > 0:
    #     tepoch_sol_M, tepoch_sat_cod_M = solver(obs.GNSS, nav, sta, cfg, epoch_t)
    # else:
    #     tepoch_sol_M = None
    #     print('[{}] No GNSS data!'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
    # tepoch_sol = dict(zip(['GPS', 'GLO', 'GAL', 'QZS', 'SBS', 'BDS', 'IRN', 'MIX'], [tepoch_sol_G, tepoch_sol_R, tepoch_sol_E, tepoch_sol_J, tepoch_sol_S, tepoch_sol_C, tepoch_sol_I, tepoch_sol_M]))
    # # tepoch_sol = dict(zip(['MIX'], [tepoch_sol_M]))
    # tepoch_sat_cod = dict(zip(['MIX'], [tepoch_sat_cod_M]))
    # single point positioning (No discard data)
    # tepoch_sol, az_el_sat = cs_spp(obs, nav, sta, cfg, epoch_t)

    tepoch_sol = {}
    tepoch_sat_cod = {}
    # with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor
    with executor:
        # Submit tasks to the process pool for execution
        numbers = [obs.GPS, obs.GLO, obs.BDS, obs.GAL, obs.QZS, obs.IRN, obs.SBS, obs.GNSS]
        partial_task = functools.partial(gnss_spp, nav=nav, sta=sta, cfg=cfg, epoch_t=epoch_t)
        # results = executor.map(partial_task, numbers)
        sys_id = ['GPS', 'GLO', 'BDS', 'GAL', 'QZS', 'IRN', 'SBS', 'MIX']
        futures = [executor.apply_async(partial_task, args=(sys_id[id], obs_)) for id, obs_ in enumerate(numbers)]

        # Get the results of the execution of the tasks (in the order of submission)
        for future in futures:
            result = future.get()
            tepoch_sat_cod[result[0]] = result[2]
            tepoch_sol[result[0]] = result[1]

    # concurrent.futures.wait(futures)
    print('[{}] SPP processing completed.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))

    spp_etime = time.time()
    print('[{}] SPP processing time:{}s'.format(strftime('%Y-%m-%d %H:%M:%S', localtime()), spp_etime-spp_stime))

    # date quality inspection
    if len(tepoch_sol['MIX']) > 0 or tepoch_sol['MIX'] != None:
        # data trim
        P_mat, L_mat, frq_mat, sat_idx, epoch, qc_cnr = data_tirm(obs.GNSS)
        print('[{}] Data structure adjustment completed.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # ele and azi
        ele, azi, inte_Tcount, inte_Acount, full_Pcount, full_Lcount = ele_azi(obs.GNSS, tepoch_sol['MIX'], tepoch_sat_cod['MIX'], nav, sta, sat_idx, P_mat, L_mat, cfg)
        print('[{}] Complete the calculation of satellite elevation and azimuth.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # date integrity rate
        qc_inte = data_inte(inte_Tcount, inte_Acount)
        print('[{}] Complete the calculation of data integrity rate.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # date saturation rate
        qc_full = data_full(full_Pcount, full_Lcount)
        print('[{}] Complete the calculation of date saturation rate.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # data visibility
        data_visible = data_visibility(P_mat, L_mat)
        print('[{}] Complete the calculation of satellite visibility.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # gross detect
        gro_slip, P_mat = pseudorange_gross(P_mat, sat_idx)
        print('[{}] Complete pseudorange gross errors detection and deletion.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # clk jump detect
        clk_slip, L_mat = clk_jmp2(P_mat, L_mat, frq_mat, obs.GNSS, sta, epoch, cfg)
        print('[{}] Complete clock jump detection and repair.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # cycle sklip detect
        cycle_slip, L_mat = cs_mian(P_mat, L_mat, frq_mat, sat_idx, sta, ele, epoch, cfg)
        print('[{}] Complete cycle slips detection.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # CSR
        qc_csr = cal_csr(cycle_slip.copy(), inte_Acount.copy())
        print('[{}] Complete the calculation of cycle ratio.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # code MP
        qc_mp = cal_multipath(P_mat, L_mat, frq_mat, sat_idx, sta, epoch, cycle_slip, cfg)
        print('[{}] Complete the calculation of pseudorange multipath.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # carrier MP
        qc_gfif = cal_gfif(L_mat, frq_mat, sat_idx, sta, epoch, cycle_slip, cfg)
        print('[{}] Complete the calculation of carrier phase multipath.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # iod
        qc_iod = cal_iondelay(L_mat, frq_mat, sat_idx, sta, epoch, cycle_slip, cfg)
        print('[{}] Complete the calculation of ionospheric delay rate.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # phase noise
        qc_pnoise = cal_pseudons(P_mat, sat_idx, sta, epoch, cycle_slip, cfg)
        print('[{}] Complete the calculation of pseudorange observation noise.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
        # carrier noise
        qc_lnoise = cal_carns(L_mat, sat_idx, frq_mat, sta, epoch, cycle_slip, cfg)
        print('[{}] Complete the calculation of carrier phase observation noise.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))

        # time utc array
        qc_time = cal_time(epoch_t)

        # save sol data
        # save path
        dirStr = save_path(cfg.obs_dir())
        # save result of txt format
        save_file(dirStr, clk_slip, cycle_slip, qc_time, tepoch_sol, ele, azi, qc_inte, qc_full, qc_cnr, qc_csr, qc_mp, qc_gfif, qc_iod, qc_pnoise, qc_lnoise, data_visible, sat_idx)
        print('[{}] Complete quality checking result file output.'.format(strftime('%Y-%m-%d %H:%M:%S', localtime())))
