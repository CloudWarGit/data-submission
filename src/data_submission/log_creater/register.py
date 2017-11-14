# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
import os, sys

from data_submission.cache.accounts import cache_accounts
from data_submission.common import values_cut, decode_values
from data_submission.log_creater import Creater
from data_submission.models.account import AccountData, AccountMobile
from data_submission.settings import settings
from data_submission.ztime import stamp_to_str, str_stamp,str_time

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..",".."))






class RegisterLogInfo(object):
    log_format = '{ICP_CODE}\t{DATA_TYPE}\t{USER_ID}\t{USER_NAME}\t{PASSWORD}\t{NICK_NAME}\t' \
                 '{STATUS}\t{REAL_NAME}\t{SEX}\t{BIRTHDAY}\t{CONTACT_TEL}\t{CERTIFICATE_TYPE}\t{CERTIFICATE_CODE}\t' \
                 '{BIND_TEL}\t{BIND_QQ}\t{BIND_MSN}\t{EMAIL}\t{REGISTER_TIME}\t{LAST_LOGIN_TIME}\t' \
                 '{LAST_CHANGE_PASSWORD}\t{LAST_MODIFY_TIME}\t{REGISTER_IP}\t{REGISTER_PORT}\t{REGISTER_MAC}\t' \
                 '{REGISTER_BIOS_ID}\t{PROVINCE}\t{CITY}\t{ADDRESS}\t{IMAGE_NAME}\t{CORP_ACCOUNT_TYPE}\t' \
                 '{CORP_ACCOUNT}\t{BIND_PAY_ACCOUNT_TYPE}\t{BIND_PAY_ACCOUNT}\t{IMEI}\t{LONGITUDE}\t{LATITUDE}\t' \
                 '{CITY_CODE}\t{ACOUNT_TYPE}\t{IMSI_CODE}\t{REAL_NAME_AUTHENTICATION}\t{USER_BRIEF_INTRODUCTION}\t{PERSONAL_HOMEPAGE}\t{PERSON_TAG}\r'

    default_dict = {
        'ICP_CODE': settings.get('ICP_CODE'),
        'DATA_TYPE': "PASSPORT",
        'USER_ID': '',                     # account.ukey
        'USER_NAME': '',                   # account.nickname
        'NICK_NAME': '',                   # account.nickname
        'STATUS': '',                      # 答主：3 普通：2
        'REAL_NAME': '',                   # account.realname
        'CONTACT_TEL': '',                 # account.mobile 联表
        'BIND_TEL': '',                    # account.mobile 联表
        'REGISTER_TIME': '',               # account.date_created
        'LAST_MODIFY_TIME': '',            # account.date_updated
        'IMAGE_NAME': '', 
        'PERSON_TAG':'',                 # 下载头像文件
        # -----------
        'PASSWORD': '',                    # 微信登录，无密码
        'SEX': '',                         # 性别
        'BIRTHDAY': '',                    # 生日
        'CERTIFICATE_TYPE': '',            # 证件类型
        'CERTIFICATE_CODE': '',            # 证件号码
        'BIND_QQ': '',                     # 绑定qq
        'BIND_MSN': '',                    # 绑定msn
        'EMAIL': '',                       # 邮箱
        'LAST_LOGIN_TIME': '',             # 上次登录时间
        'LAST_CHANGE_PASSWORD': '',        # 上次密码
        'REGISTER_IP': '',                 # 注册ip
        'REGISTER_PORT': '',               # 注册端口
        'REGISTER_MAC': '',                # 注册MAC地址
        'REGISTER_BIOS_ID': '',            # 注册设备IMEI或者其他硬件特征码
        'PROVINCE': '',                    # 省份
        'CITY': '',                        # 城市
        'ADDRESS': '',                     # 地址
        'CORP_ACCOUNT_TYPE':'',
        'CORP_ACCOUNT':'',
        'BIND_PAY_ACCOUNT_TYPE':'',
        'BIND_PAY_ACCOUNT':'',
        'IMEI':'',
        'LONGITUDE':'',
        'LATITUDE':'',
        'CITY_CODE':'',
        'ACOUNT_TYPE':'',
        'IMSI_CODE':'',
        'REAL_NAME_AUTHENTICATION':'手机号',
        'USER_BRIEF_INTRODUCTION':'',
        'PERSONAL_HOMEPAGE':'None',      
    }


class RegisterCreater(Creater, RegisterLogInfo):
    buisy_dir = 'register'
    image_head_url = True
    task_name = 'register'

    def __init__(self, log_time, begin_time, end_time):
        self.initial(log_time, begin_time, end_time)

    def load_data(self):
        self.data_iter = AccountData(begin_time=self.begin_time, end_time=self.end_time)
        #print(self.data_iter)
        return self

    def get_account(self, _data):
        
        account_ukey = set()
        for data in _data:
            account_ukey.add(data.ukey)
        
        self.relation_accounts = cache_accounts(cache_reflesh='YES', accounts=_data, *account_ukey)
        
        
    #以下代码没用
    def get_account_mobile(self, *account_ukeys):
        #print(self.begin_time)
        account_mobile_datas = AccountMobile(ukeys_str=str(account_ukeys))
        #print("mobile",account_mobile_datas)
        for accounts in account_mobile_datas:
            for account in accounts:
                #print("account***",account.values)
                if account.ukey in self.relation_accounts:

                    self.relation_accounts[account.ukey]['mobile'] = account.mobile
                    #print(self.relation_accounts[account.ukey])
            
    def data_piece(self, data):
        try:
            #self.image_path = '{log_time}_{log_index}/'.format(**self.path_param)
            #self.ima_path=None
            
            _dict = deepcopy(self.default_dict)
            #print(self.relation_accounts)
            #print(self.relation_accounts.get(data.ukey))
            nickname = decode_values(self.relation_accounts.get(data.ukey).get('nickname',""))
            realname = decode_values(self.relation_accounts.get(data.ukey).get('realname',""))
            #print("relation_accounts",self.relation_accounts.get(data.ukey))
            mobile = decode_values(self.relation_accounts.get(data.ukey).get('mobile', ''))
            date_created = decode_values(self.relation_accounts.get(data.ukey).get('mobile_date_created', ''))
            #print(type(date_created))

#             image_url=None
#             image_name = ''
#             if self.image_head_url:
#                 image_name = image_url
#             else:
#                 if image_url:
#                     r = requests.get(image_url, timeout=(30, 30))
#                     if r.status_code >= 400:
#                         image_name = ''
#                     else:
#                         if not os.path.exists(self._path + self.image_path):
#                             os.makedirs(self._path + self.image_path)
#                         image_head = open(self._path + self.image_path + str(data.ukey) + '.jpg', "wb")
#                         try:
#                             image_head.write(r.content)
#                             image_name = self.image_path + str(data.ukey) + '.jpg'
#                         except:
#                             image_name = ''
#                         finally:
#                             image_head.close()
            log_dict = {
                'DATA_TYPE': settings.get('DATA_TYPE').get(self.buisy_dir),
                'USER_ID': data.ukey,                # account.ukey
                'USER_NAME': nickname,             # account.nickname
                'NICK_NAME': nickname,             # account.nickname
               # 'BRIF_Intro': introduction,   # account.introduction
                'STATUS': "启用" if data.status == "active" else "停用",                      # 答主：3 普通：2
                'REAL_NAME': realname if realname else '',             # account.realname
                'CONTACT_TEL': data.mobile,                 # account.mobile 联表
                'BIND_TEL': mobile,                    # account.mobile 联表
                'REGISTER_TIME': date_created,               # account.date_created
                'LAST_MODIFY_TIME': date_created,
                'CORP_ACCOUNT_TYPE':data.oauth2_type,
                'CORP_ACCOUNT':data.oauth2_uid if data.oauth2_uid else ''           # account.date_updated
                #'IMAGE_NAME': image_name,                  # 下载头像文件
            }
            _dict.update(log_dict)
        except Exception as e:
            print(e)
            return {}
        return _dict


_Creater = RegisterCreater


def task_create_log(**kwargs):
    _creater = _Creater(**kwargs)
    _creater.create_log()


if __name__ == "__main__":
    task_create_log(log_time=1465721117,
                    begin_time=1477661163,
                    end_time=1477872163)


# if __name__ == "__main__":
#     begin = stamp_to_str(1465721116)
#     end = stamp_to_str(1465727870)
#     account_datas = AccountData(begin_time=begin, end_time=end)
#     for index, account_data in enumerate(account_datas):
#         account_ukey = set()
#         for data in account_data:
#             account_ukey.add(data.ukey)
#             print data.ukey
#             print data.nickname
#             print data.realname
#             print data.introduction
#             print data.price
#             print data.image_url
#             print data.date_created
#             print data.date_updated
#             print str_time(data.date_created)
#             print data.values
#             break
#         print list(account_ukey)
