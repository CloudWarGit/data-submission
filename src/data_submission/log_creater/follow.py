# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from copy import deepcopy
import os, sys

from data_submission.cache.accounts import get_accounts
from data_submission.common import init_log_path, decode_values
from data_submission.log_creater import Creater
from data_submission.models.follow import FollowData, CountFollowData, CountFollowerData
from data_submission.models.account import AccountMobile
from data_submission.settings import settings
from data_submission.ztime import stamp_to_str, str_stamp


__author__ = 'legenove'


PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", ".."))





class FollowLogInfo(object):
    log_format = '{ICP_CODE}\t{DATA_TYPE}\t{USER_ID}\t{USER_NAME}\t{NICK_NAME}\t' \
                 '{CONNECT_USER_ID}\t{CONNECT_USER_NAME}\t{CONNECT_NICK_NAME}\t{FRIENDLIST}\t' \
                 '{GROUP_NAME}\t{MODIFY_TIME}\t{ACTION}\t{FRIENDTYPE}\t{FRIEND_REMARK}\t{FRIENDS_MOBILE}\t{NUM_OF_FOCUS}\t{NUM_OF_FANS}\r' \

    default_dict = {
        'ICP_CODE': '11010513810001',
        'DATA_TYPE': "PASSPORT",
        'USER_ID': "",                           # account.id
        'USER_NAME': "",                         # account.nickname
        'NICK_NAME': "", 
        'CONNECT_USER_ID':"",                        # account.nickname
        'CONNECT_USER_NAME':"",
        'CONNECT_NICK_NAME':"",
        'FRIENDLIST':"",
        'GROUP_NAME':"",
        'MODIFY_TIME':"",
        'ACTION':"关注",
        'FRIENDTYPE':"",
        'FRIEND_REMARK':"",
        'FRIENDS_MOBILE':"",
        'NUM_OF_FOCUS':"",
        'NUM_OF_FANS':""
    }


class FollowCreater(Creater, FollowLogInfo):
    buisy_dir = 'connect'
    task_name = 'connect'

    def __init__(self, log_time, begin_time, end_time):
        self.initial(log_time, begin_time, end_time)

    def load_data(self):
        self.data_iter = FollowData(begin_time=self.begin_time, end_time=self.end_time)
        return self

    def preload_data(self):
        self.follower_num = dict(CountFollowData.get_data(pk='ukey'))
        self.followed_num = dict(CountFollowerData.get_data(pk='ukey'))
        return self

    def get_account(self, _data):
        account_ukey = set()
        for data in _data:
            account_ukey.add(data.ukey)
            account_ukey.add(data.ukey_following)
        print("~~~~~~~~~")
        print(len(account_ukey))
        self.relation_accounts = get_accounts(*account_ukey)
        

    def data_piece(self, data):
        try:
            #print("好友：", data.ukey_following)
            _dict = deepcopy(self.default_dict)
#             print("~~~~~~~~~")
#             print(self.relation_accounts)
#             print("~~~~~~~~~")
#             print (self.relation_accounts.get(data.ukey))
            #nickname = decode_values(self.relation_accounts.get(data.ukey).get('nickname'))
            #friend_nickname = decode_values(self.relation_accounts.get(data.ukey_following).get('nickname'))
            friend_mobile = AccountMobile(ukeys_str=str(data.ukey_following)).get_data()
            if friend_mobile:
                friend_mobile = friend_mobile[0].mobile
            else:
                friend_mobile = ""
            
            log_dict = {
                'DATA_TYPE': settings.get('DATA_TYPE').get(self.buisy_dir),
                'USER_ID': data.ukey,
                'USER_NAME': "",
                'NICK_NAME': "",
                'CONNECT_USER_ID':data.ukey_following,
                'NUM_OF_FOCUS': self.follower_num.get(data.ukey, 0),
                'NUM_OF_FANS': self.followed_num.get(data.ukey, 0),
                'FRIENDS_MOBILE': friend_mobile,
                'MODIFY_TIME': str_stamp(data.date_created),
            }
            _dict.update(log_dict)
        except Exception as e:
            print("err",e)
            return {}
        return _dict


_Creater = FollowCreater


def task_create_log(**kwargs):
    _creater = _Creater(**kwargs)
    _creater.create_log()


if __name__ == "__main__":
    task_create_log(log_time=1465721117,
                    begin_time=1477761163,
                    end_time=1477872163)
