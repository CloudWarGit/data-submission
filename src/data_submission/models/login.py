# -*- coding: utf-8 -*-
__author__ = 'legenove'

from data_submission.models.common import CommonData
from data_submission.data_collect.db import guokr_auth_db


class LoginData(CommonData):
    '''
    -init: _data = LoginData(begin_time=begin, end_time=end)
    -item_get:
        item.account_id
        item.expires
    '''

    _req_param = "i.ukey as ukey,i.ip as ip,i.behavior as behavior,i.date_behavior as date_behavior,a.nickname as nickname"
    _table = "ip_behavior i, account a"
    is_dict = True

    _db = guokr_auth_db


    where_sql = "WHERE i.behavior='signin_success' AND i.ukey=a.ukey AND date_behavior>'{begin_time}' AND date_behavior<='{end_time}' "
    