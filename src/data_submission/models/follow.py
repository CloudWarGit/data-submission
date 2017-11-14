# -*- coding: utf-8 -*-
__author__ = 'legenove'

from data_submission.models.common import CommonData, CountCommonData


class FollowData(CommonData):
    '''
    -init: follow_data = FollowData(begin_time=begin, end_time=end)
    -item_get:
        item.follower_id
        item.followed_id
        item.date_created
    '''

    _req_param = "ukey,ukey_following,date_created"
    _table = "user_following"
    is_dict = True

    where_sql = "WHERE date_created>'{begin_time}' AND date_created<='{end_time}' "

class CountFollowData(CountCommonData):
    '''
    -init: follow_data = FollowData(key='ukey', value=account_id)
    -item_get:
        item.count
    '''

    _table = "user_following"
    begin_sql = "SELECT {pk},count(*) FROM {_table} "
    where_sql = " group by {pk} "
    
class CountFollowerData(CountCommonData):
    '''
    -init: follow_data = FollowData(key='ukey', value=account_id)
    -item_get:
        item.count
    '''

    _table = "user_follower"
    begin_sql = "SELECT {pk},count(*) FROM {_table} "
    where_sql = " group by {pk} "