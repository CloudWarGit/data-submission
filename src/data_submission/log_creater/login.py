# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
from datetime import timedelta
import os, sys

from data_submission.cache.accounts import get_accounts
from data_submission.common import decode_values
from data_submission.log_creater import Creater
from data_submission.models.login import LoginData
from data_submission.settings import settings
from data_submission.ztime import stamp_to_str, str_stamp

try:
    from data_submission.util.ip_convert import ip_convert
except:
    print "fuck"

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", ".."))





day = settings.get('expires')

class LoginLogInfo(object):
    log_format = '{ICP_CODE}\t{DATA_TYPE}\t{SRC_IP}\t{SRC_PORT}\t{CORP_SITE}\t' \
                 '{CORP_LOGIN_ACCOUNT}\t{USER_ID}\t{USER_NAME}\t{NICK_NAME}\t{PASSWORD}\t' \
                 '{MAC_ADDRESS}\t{INNER_IP}\t{ACTION_TIME}\t{ACTION}\t{LONGITUDE}\t' \
                 '{LATITUDE}\t{TERMINAL_TYPE}\t{OS_TYPE}\t{STATION_ID}\t{COMMUNITY_CODE}\t' \
                 '{IMEI_CODE}\t{IMSI_CODE}\t{LOGIN_CITY_CODE}\t{LOGIN_DEV_SOFTWARE}\t{LOGIN_DEV_TYPE}\t{LOGIN_IDEN_STRING}\r'

    default_dict = {
        'ICP_CODE': settings.get('ICP_CODE'),
        'DATA_TYPE': "PASSPORT",
        'USER_ID': "",                           # account.id
        'USER_NAME': "",                         # account.nickname
        'NICK_NAME': "",                         # account.nickname
        'ACTION_TIME': "",                       # 登录时间
        'ACTION': "上线",                        # 上线/登录 下线/离线/退出等
        # -----------
        'SRC_IP': "",                            # 源ip
        'SRC_PORT': "",                          # 源端口
        'CORP_SITE': "",                         # 合作网站
        'CORP_LOGIN_ACCOUNT': "",                # 合作网站账号
        'PASSWORD': "",                          # 微信登录
        'MAC_ADDRESS': "",                       # 源Mac
        'INNER_IP': "",                          # 内网IP
        'LONGITUDE': "",                         # 经度
        'LATITUDE': "",                          # 纬度
        'TERMINAL_TYPE': "",                     # 终端类型  01:PC   02:手机  03:PAD
        'OS_TYPE': "",                           # 操作系统 09:WINDOWS  10:UNIX  11:LINUX  12:MAC  13:IOS  14:ANDROID
        'STATION_ID': "",                        # 手机基站号
        'COMMUNITY_CODE': "",                    # 手机小区号
        'IMEI_CODE': "",                         # 移动终端设备
        'IMSI_CODE': "", 
        'LOGIN_CITY_CODE':'',                        # 移动用户的 IMSI
        'LOGIN_DEV_SOFTWARE': "",                     # 预留1
        'LOGIN_DEV_TYPE': "",                     # 预留2
        'LOGIN_IDEN_STRING': ""                      # 预留3
    }


class LoginCreater(Creater, LoginLogInfo):
    buisy_dir = 'login'
    expires = 3600*24*day
    task_name = 'login'
    def __init__(self, log_time, begin_time, end_time):
       # begin_time += self.expires
       # end_time += self.expires
        self.initial(log_time, begin_time, end_time)

    def load_data(self):
        self.data_iter = LoginData(begin_time=self.begin_time, end_time=self.end_time)
        return self

    def get_account(self, _data):
        account_id = set()
        for data in _data:
            account_id.add(data.ukey)
        self.relation_accounts = get_accounts(*account_id)

    def data_piece(self, data):
        try:
            _dict = deepcopy(self.default_dict)
            #nickname = decode_values(self.relation_accounts.get(data.account_id).get('nickname'))
            ip = ip_convert(data.ip)
            log_dict = {
                'DATA_TYPE': settings.get('DATA_TYPE').get(self.buisy_dir),
                'USER_ID': data.ukey,                           # account.id
                'USER_NAME': data.nickname,                         # account.nickname
                'NICK_NAME': data.nickname,
#                 'ACTION':data.behavior,                         # account.nickname
                'ACTION_TIME': str_stamp(data.date_behavior), 
                'SRC_IP': ip                      # 登录时间
            }
            _dict.update(log_dict)
        except Exception as e:
            print(e)
            return {}
        return _dict


_Creater = LoginCreater


def task_create_log(**kwargs):
    _creater = _Creater(**kwargs)
    _creater.create_log()


if __name__ == "__main__":
    task_create_log(log_time=1478464511,
                    begin_time=1478464450,
                    end_time=1478564451)
