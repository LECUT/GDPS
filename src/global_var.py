# -*- coding: utf-8 -*-

def _init():
    global _global_dict
    _global_dict = {}

def set_value(key, value):
    # global variable
    _global_dict[key] = value

def get_value(key):
    # Get a global variable, if it doesn't exist, it will ask you if the corresponding variable failed to play
    try:
        return _global_dict[key]
    except:
        print('read'+key+'failure\r\n')