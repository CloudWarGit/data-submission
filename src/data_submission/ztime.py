# -*- coding: utf-8 -*-
# 时间处理相关方法

from datetime import datetime, timedelta, date, time
from time import localtime, strftime, mktime

import pytz


bjtz = pytz.timezone('Asia/Shanghai')

def now(tz='beijing'):
    """返回带有时间戳的当前时间，默认为utc时间"""
    if tz == 'beijing':
        return datetime.now(bjtz)
    return datetime.now(pytz.utc)

# http://stackoverflow.com/questions/24856643/unexpected-results-converting-timezones-in-python
def str_time(dt, fmt='%Y-%m-%d %H:%M:%S', with_timezone=False):
    """将数据库取出来的时间转化为北京时间字符串"""
    if not dt or not isinstance(dt, (datetime, date, time)):
        # 取出来的值为空或者不是日期类型，直接返回
        return dt
    if not dt.tzinfo:
        # 没有时间戳信息，加上utc
        dt = pytz.utc.localize(dt)
    bjdt = dt.astimezone(bjtz)

    if with_timezone:
        fmt = "%Y-%m-%d %H:%M:%S %Z%z"
    str_time = bjdt.strftime(fmt)
    return str_time

def stamp_to_str(timestamp):
    x = localtime(timestamp)
    return strftime('%Y-%m-%d %H:%M:%S', x)

def str_stamp(dt):
    otherStyleTime = dt.strftime("%Y%m%d%H%M%S")
    return str(otherStyleTime)

def now_stamp():
    return str(int(mktime(now().timetuple())))

if __name__ == "__main__":
    print now_stamp()
