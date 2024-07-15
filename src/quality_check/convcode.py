from .rtkcmn import uGNSS
# rinex 2.* to rinex 3.*的观测值编码转换
def convcode(ver, str, sys):
    type = ''
    if str == 'P1':
        if sys == uGNSS.GPS:
            type = 'C1W'
        if sys == uGNSS.GLO:
            type = 'C1P'
    elif str == 'P2':
        if sys == uGNSS.GPS:
            type = 'C2W'
        if sys == uGNSS.GLO:
            type = 'C2P'
    elif str == 'C1':
        if ver >= 2.12:
            pass
        elif sys == uGNSS.GPS:
            type = 'C1C'
        elif sys == uGNSS.GLO:
            type = 'C1C'
        elif sys == uGNSS.GAL:
            type = 'C1X'
        elif sys == uGNSS.QZS:
            type = 'C1C'
        elif sys == uGNSS.SBS:
            type = 'C1C'

    elif str == 'C2':
        if sys == uGNSS.GPS:
            if ver >= 2.12:
                type = 'C2W'
            else:
                type = 'C2X'
        elif sys == uGNSS.GLO:
            type = 'C2C'
        elif sys == uGNSS.BDS:
            type = 'C2X'
        elif sys == uGNSS.QZS:
            type = 'C2X'

    elif ver >= 2.12 and str[1] == 'A':
        if sys == uGNSS.GPS:
            type = str[0] + '1C'
        elif sys == uGNSS.GLO:
            type = str[0] + '1C'
        elif sys == uGNSS.QZS:
            type = str[0] + '1C'

    elif ver >= 2.12 and str[1] == 'B':
        if sys == uGNSS.GPS:
            type = str[0] + '1X'
        elif sys == uGNSS.QZS:
            type = str[0] + '1X'

    elif ver >= 2.12 and str[1] == 'C':
        if sys == uGNSS.GPS:
            type = str[0] + '2X'
        elif sys == uGNSS.QZS:
            type = str[0] + '2X'

    elif ver >= 2.12 and str[1] == 'D':
        if sys == uGNSS.GLO:
            type = str[0] + '2C'

    elif ver >= 2.12 and str[1] == '1':
        if sys == uGNSS.GPS:
            type = str[0] + '1W'
        elif sys == uGNSS.GLO:
            type = str[0] + '1P'
        elif sys == uGNSS.GAL:
            type = str[0] + '1X'
        elif sys == uGNSS.BDS:
            type = str[0] + '1X'
    elif ver < 2.12 and str[1] == '1':
        if sys == uGNSS.GPS:
            type = str[0] + '1C'
        elif sys == uGNSS.GLO:
            type = str[0] + '1C'
        elif sys == uGNSS.GAL:
            type = str[0] + '1X'
        elif sys == uGNSS.QZS:
            type = str[0] + '1C'
        elif sys == uGNSS.SBS:
            type = str[0] + '1C'

    elif str[1] == '2':
        if sys == uGNSS.GPS:
            type = str[0] + '2W'
        elif sys == uGNSS.GLO:
            type = str[0] + '2P'
        elif sys == uGNSS.BDS:
            type = str[0] + '2X'
        elif sys == uGNSS.QZS:
            type = str[0] + '2X'

    elif str[1] == '5':
        if sys == uGNSS.GPS:
            type = str[0] + '5X'
        elif sys == uGNSS.GAL:
            type = str[0] + '5X'
        elif sys == uGNSS.QZS:
            type = str[0] + '5X'
        elif sys == uGNSS.SBS:
            type = str[0] + '5X'

    elif str[1] == '6':
        if sys == uGNSS.GAL:
            type = str[0] + '6X'
        elif sys == uGNSS.BDS:
            type = str[0] + '6X'
        elif sys == uGNSS.QZS:
            type = str[0] + '6X'

    elif str[1] == '7':
        if sys == uGNSS.GAL:
            type = str[0] + '7X'
        elif sys == uGNSS.BDS:
            type = str[0] + '7X'

    elif str[1] == '8':
        if sys == uGNSS.GAL:
            type = str[0] + '8X'

    return type



