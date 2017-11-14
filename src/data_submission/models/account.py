# -*- coding: utf-8 -*-
__author__ = 'legenove'

from data_submission.data_collect.db import guokr_auth_db
from data_submission.models.common import CommonData


class AccountData(CommonData):
    '''
    -init: follow_data = FollowData(begin_time=begin, end_time=end)
    -item_get:
        item.id
        item.nickname
        item.realname
        item.introduction
        item.price
        item.image_url
        item.date_created
        item.date_updated
    '''
    _req_param = "a.ukey as ukey, a.nickname as nickname, a.status as status, a.date_last_signed_in as date_last_signed_in," \
               " p.phone as mobile, p.date_created as mobile_date_created, e.oauth2_uid as oauth2_uid, e.oauth2_type as oauth2_type, e.date_created as auth_date_created"
    _table = "account a, phone p, external_oauth2 e"
    is_dict = True
    
    _db = guokr_auth_db

    where_sql = "WHERE a.ukey=p.ukey AND a.ukey=e.ukey AND p.date_created>'{begin_time}' AND p.date_created<='{end_time}' "


class AccountCacheData(CommonData):
    '''
    -init: follow_data = FollowData(begin_time=begin, end_time=end)
    -item_get:
        item.id
        item.nickname
        item.realname
        item.title
        item.price
        item.date_created
        item.date_updated
    '''
    _req_param = "a.ukey as ukey, a.nickname as nickname, a.status as status, a.date_last_signed_in as date_last_signed_in," \
               " p.phone as mobile, p.date_created as mobile_date_created, e.oauth2_uid as oauth2_uid, e.oauth2_type as oauth2_type, e.date_created as auth_date_created"
    _table = "account a, phone p,external_oauth2 e"
    is_dict = True
    
    _db = guokr_auth_db

    where_sql = "WHERE a.ukey=p.ukey AND a.ukey=e.ukey AND   a.ukey in '{ids_str}' "


class AccountMobile(CommonData):
    '''
    -init: follow_data = FollowData(begin_time=begin, end_time=end)
    -item_get:
        item.account_id
        item.mobile
    '''
    _req_param = "ukey,phone as mobile, date_created"
    _table = "phone"
    is_dict = True

    _db = guokr_auth_db

    where_sql = "WHERE ukey = '{ukeys_str}' "


