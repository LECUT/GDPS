from ftplib import FTP_TLS as FTP
import paramiko
from urllib.request import urlopen
import urllib.request
from bs4 import BeautifulSoup
import time

'''
-----------------------------------------------------------------------------------------------------------------------
Function:site-name obtain  
input:url
output:site-name
author:huweijian
time:2022-07-19
-----------------------------------------------------------------------------------------------------------------------
'''
s_time = time.time()
# 1. chaim url
# url = 'ftp://igs.gnsswhu.cn/pub/gps/data/daily/2023/001/23d/'
# url = 'https://igs.bkg.bund.de/root_ftp/IGS/obs_v3/2020/001/'
url = 'ftps://gdc.cddis.eosdis.nasa.gov/pub/gps/data/daily/2023/001/23d/'
# url = 'sftp://sftp.data.gnss.ga.gov.au/rinex/daily/2023/001/ABMF00GLP_R_20230010000_01D_30S_MO.crx.gz'
# url = 'ftp://ftp.geodetic.gov.hk/rinex2/2023/001'


def get_url_type(url):
    if url.startswith("http://"):
        return "HTTP"
    elif url.startswith("https://"):
        return "HTTPS"
    elif url.startswith("ftp://"):
        return "FTP"
    elif url.startswith("ftps://"):
        return "FTPS"
    elif url.startswith("sftp://"):
        return "SFTP"
    else:
        return "Unknown"


# 2. if url type
if get_url_type(url)=="HTTP" or get_url_type(url)=="HTTPS":
    response = urllib.request.urlopen(url)
    print(response.status)
    # analytic html
    soup = BeautifulSoup(response.read(), 'lxml')
    print(soup)
    # obtain value
    html_site_name = soup.select('a[href]')
    # site-name list
    site_name = []
    for i in range(len(html_site_name)):
        site_name.append(html_site_name[i].get('href'))
    # to repeat
    site_name = list(set(site_name))
    # site-name sort
    site_name = sorted(site_name)
    # delete useless info
    site_name = [name for name in site_name if name.find('.') >= 0]

    # save data
    fid = open('station_name.txt', 'w+')
    for i in site_name:
        fid.write(i + '\n')
    fid.close()

elif get_url_type(url)=="FTP":
    response = urllib.request.urlopen(url)
    # decode html
    ftp_html = response.read().decode('utf-8')
    # char to list
    ftp_html_list = ftp_html.split()
    print(ftp_html_list)
    # site-name list
    site_name = []
    for i in range(8, len(ftp_html_list), 9):
        site_name.append(ftp_html_list[i])
    # delete useless info
    site_name = [name for name in site_name if name.find('.') >= 0]

    fid = open('station_name.txt', 'w+')
    for i in site_name:
        fid.write(i + '\n')
    fid.close()

    print(site_name)

elif get_url_type(url)=="FTPS":
    ftps = FTP()
    ftps.encoding = 'gbk'
    try:
        ftps.set_pasv(True)
        ftps.connect("gdc.cddis.eosdis.nasa.gov", 21)
        ftps.login("anonymous", "l_teamer@163.com")
        ftps.prot_p()
    except Exception as e:
        print(e)

    # target content
    directory = '/pub/gps/data/daily/2023/001/23d/'

    # go target content
    ftps.cwd(directory)

    # get filename
    site_name = []
    ftps.retrlines('NLST', site_name.append)

    # close
    ftps.quit()

    # save data
    fid = open('station_name.txt', 'w+')
    for i in site_name:
        fid.write(i + '\n')
    fid.close()

elif get_url_type(url)=="SFTP":
    try:
        client = paramiko.Transport(('sftp.data.gnss.ga.gov.au', 22))
    except Exception as error:
        print('Sftp connection failed')
    else:
        try:
            client.connect(username='anonymous', password='l_teamer@163.com')
        except Exception as error:
            print('Login failed')
        else:
            sftp = paramiko.SFTPClient.from_transport(client)

    # target content
    directory = '/rinex/daily/2023/001/'

    # get filename
    site_name = sftp.listdir(directory)

    # close
    sftp.close()
    client.close()

    # save data
    fid = open('station_name.txt', 'w+')
    for i in site_name:
        fid.write(i + '\n')
    fid.close()

e_time = time.time()
print('耗时：{}'.format(e_time-s_time))

