import pandas as pd
import os

def read_list(mfile_path):
    path = os.path.dirname(mfile_path)
    file_str = open(mfile_path, 'r+')
    file_dict = eval(file_str.read())
    file_str.close()
    return file_dict, path

def read_data(file_dict, path):
    out_data = {'sol': [], 'ele': [], 'azi': [], 'inte': [], 'satu': [], 'CN0': [], 'MP': [], 'GFIF': [], 'iod': [], 'Pnoise': [], 'Cnoise': [], 'sat': [], 'cycle': [], 'clkjump': []}
    out_data['sol']      = pd.read_csv(os.path.join(path, file_dict['sol'][0]), sep='\s+', index_col=0)
    out_data['ele']      = pd.read_csv(os.path.join(path,  file_dict['ele'][0]), sep='\s+')
    out_data['azi']      = pd.read_csv(os.path.join(path,  file_dict['azi'][0]), sep='\s+')
    out_data['inte']     = pd.read_csv(os.path.join(path,  file_dict['inte'][0]), sep='\s+', index_col=0)
    out_data['satu']     = pd.read_csv(os.path.join(path,  file_dict['satu'][0]), sep='\s+', index_col=0)
    out_data['CN0']      = pd.read_csv(os.path.join(path,  file_dict['CN0'][0]), sep='\s+', index_col=0)
    out_data['MP']       = pd.read_csv(os.path.join(path,  file_dict['MP'][0]), sep='\s+', index_col=0)
    out_data['iod']      = pd.read_csv(os.path.join(path,  file_dict['iod'][0]), sep='\s+', index_col=0)
    out_data['GFIF']     = pd.read_csv(os.path.join(path,  file_dict['GFIF'][0]), sep='\s+')
    out_data['Pnoise']   = pd.read_csv(os.path.join(path,  file_dict['Pnoise'][0]), sep='\s+', index_col=0)
    out_data['Cnoise']   = pd.read_csv(os.path.join(path,  file_dict['Cnoise'][0]), sep='\s+', index_col=0)
    out_data['sat']      = pd.read_csv(os.path.join(path,  file_dict['sat'][0]), sep='\s+')
    out_data['cycle']    = pd.read_csv(os.path.join(path,  file_dict['cycle'][0]), sep='\s+', index_col=0)
    out_data['clkjump']  = pd.read_csv(os.path.join(path,  file_dict['clkjump'][0]), sep='\s+')

    #-----------------------\ # combinat date and time
    out_data['sol']['Epoch']     = pd.to_datetime(out_data['sol']['Date'] + ' ' + out_data['sol']['Time'])
    out_data['ele']['Epoch']     = pd.to_datetime(out_data['ele']['Date'] + ' ' + out_data['ele']['Time'])
    out_data['azi']['Epoch']     = pd.to_datetime(out_data['azi']['Date'] + ' ' + out_data['azi']['Time'])
    out_data['CN0']['Epoch']     = pd.to_datetime(out_data['CN0']['Date'] + ' ' + out_data['CN0']['Time'])
    out_data['MP']['Epoch']      = pd.to_datetime(out_data['MP']['Date'] + ' ' + out_data['MP']['Time'])
    out_data['iod']['Epoch']     = pd.to_datetime(out_data['iod']['Date'] + ' ' + out_data['iod']['Time'])
    out_data['GFIF']['Epoch']    = pd.to_datetime(out_data['GFIF']['Date'] + ' ' + out_data['GFIF']['Time'])
    out_data['Pnoise']['Epoch']  = pd.to_datetime(out_data['Pnoise']['Date'] + ' ' + out_data['Pnoise']['Time'])
    out_data['Cnoise']['Epoch']  = pd.to_datetime(out_data['Cnoise']['Date'] + ' ' + out_data['Cnoise']['Time'])
    out_data['cycle']['Epoch']   = pd.to_datetime(out_data['cycle']['Date'] + ' ' + out_data['cycle']['Time'])
    out_data['clkjump']['Epoch'] = pd.to_datetime(out_data['clkjump']['Date'] + ' ' + out_data['clkjump']['Time'])
    #-----------------------\
    # aa = out_data['sol']['POSGPS':'POSGPS'] # get row data
    return out_data

