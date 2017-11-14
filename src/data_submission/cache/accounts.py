# -*- coding: utf-8 -*-
__author__ = 'legenove'

from .common import memcached_muti_ids_function
from data_submission.ztime import str_stamp
from data_submission.models.account import AccountCacheData


def account_cache_dict(account):
    #print("account*****",dir(account))
    return dict(
        ukey=account.ukey,
        nickname=account.nickname,
        realname=account.nickname,
        mobile=account.mobile,
        mobile_date_created=str_stamp(account.mobile_date_created),
        auth_date_created=str_stamp(account.auth_date_created),
        date_last_signed_in=account.date_last_signed_in,
        oauth2_uid=account.oauth2_uid,
        oauth2_type=account.oauth2_type,
        status=account.status    
    )

def get_accounts(*account_ids):
    result = {}
    if len(account_ids) == 1:
        account_ids = '(%s)' % account_ids[0]
    elif len(account_ids) == 0:
        return result
    account_cache_datas = AccountCacheData(ids_str=str(account_ids))
    for accounts in account_cache_datas:
        for account in accounts:
            result[account.ukey] = account_cache_dict(account)
    return result

@memcached_muti_ids_function('account_ukey', prefix="account_mata", cache_reflesh='YES')
def cache_accounts(*account_ids, **kwargs):
    '''
    :param account_ids:
    :param kwargs:
        accounts
        cache_reflesh:'YES'
    :return:
    '''
    result = {}

    for account in kwargs.get('accounts', []):
        #print(account.values)
        result[account.ukey] = account_cache_dict(account)
    #print(result)
    return result

