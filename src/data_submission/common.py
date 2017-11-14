# -*- coding: utf-8 -*-

import os
import re
import sys
import sys

from data_submission.settings import settings
from ztime import now_stamp


reload(sys)
sys.setdefaultencoding('utf-8')



def init_log_path(**kwargs):
    '''
    :param kwargs:
        BUISY_DIR:
        LOG_TIME:
        DATA_TYPE:
    :return:
    '''
    log_path = settings.get('PATH_DIR')
    data_path = settings.get('DATA_PATH')

    _path = log_path + data_path.format(**kwargs)

    if not os.path.exists(_path):
        os.makedirs(_path)

    return _path


def decode_values(v):
    if isinstance(v, (bool, int, long, float, str)):
        return str(v).decode()
    elif isinstance(v, unicode):
        return v




def make_xlat(*args, **kwds):
    adict = dict(*args, **kwds)
    rx = re.compile('|'.join(map(re.escape, adict)))

    def one_xlat(match):
        return adict[match.group(0)]

    def xlat(text):
        return rx.sub(one_xlat, text)

    return xlat


xlat = make_xlat(**{
    '\t': ' ',
    '\n': ' ',
    '\r': ' ',
})

def values_cut(text, length):
    return decode_values(xlat(text))[:length]