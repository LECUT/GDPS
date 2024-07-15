#-*- coding:utf-8 -*-

# ===========================================================
#     Initialization File (ini) Decoder
# ===========================================================
import configparser
from .str2typ import str2time

class GNSSconfig:
    def __init__(self, configfile=""):
        if configfile != "":
            cf = configparser.ConfigParser()
            cf.read(configfile, encoding='utf-8')

            if cf.has_section("inp"):
                self.inp_info = dict(cf.items("inp"))
            else:
                self.inp_info = dict()
            
            if cf.has_section("gen"):
                self.gen_info = dict(cf.items("gen"))
            else:
                self.gen_info = dict()

            if cf.has_section("qc"):
                self.qc_info = dict(cf.items("qc"))
            else:
                self.qc_info = dict()
# ===========================================================
#     Section gen info
# ===========================================================
    def time_beg(self):
        try:
            time_beg = str2time(self.gen_info["start_time"])
        except KeyError as e:
            print(str(e))
            print("- Can't get the ymd_beg from config file!! Check the config file!!!")
            exit(1)
        return time_beg

    def time_end(self):
        try:
            time_end = str2time(self.gen_info["end_time"])
        except KeyError as e:
            print(str(e))
            print("- Can't get the ymd_end from config file!! Check the config file!!!")
            exit(1)
        return time_end

    def interval(self):
        return float(self.gen_info["interval"])

    def satsys(self):
        return self.gen_info["satsys"]

    def gps_band(self):
        return self.gen_info["gps_band"]

    def glo_band(self):
        return self.gen_info["glo_band"]

    def gal_band(self):
        return self.gen_info["gal_band"]

    def qzs_band(self):
        return self.gen_info["qzs_band"]

    def bds_band(self):
        return self.gen_info["bds_band"]

    def irn_band(self):
        return self.gen_info["irn_band"]

    def sbs_band(self):
        return self.gen_info["sbs_band"]

# ===========================================================
#     Section QC model
# ===========================================================

    def elmin(self):
        return float(self.qc_info["elmin"])

    def cnrmin(self):
        return float(self.qc_info["cnrmin"])

    def ionoopt(self):
        return int(self.qc_info["ionoopt"])

    def tropopt(self):
        return int(self.qc_info["tropopt"])

    def pos_banpos(self):
        return list((map(int, self.qc_info["pos_banpos"].split())))

    def pos_option(self):
        return list((map(int, self.qc_info["pos_option"].split())))

    def pos_elcut(self):
        return float(self.qc_info["pos_elcut"])

    def pos_cnrcut(self):
        return float(self.qc_info["pos_cnrcut"])

    def pos_kin(self):
        return float(self.qc_info["pos_kin"])

    def mw_limit(self):
        return float(self.qc_info["mw_limit"])

    # def gf_limit(self):
    #     return float(self.qc_info["gf_limit"])
    #
    # def gap_limit(self):
    #     return int(self.qc_info["gap_limit"])

    def short_limit(self):
        return int(self.qc_info["int_pcs"])

# ===========================================================
#     Section input
# ===========================================================
    def obs_dir(self):
        return self.inp_info["rinexo"]

    def nav_dir(self):
        return self.inp_info["rinexn"]
