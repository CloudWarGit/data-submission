import time

from data_submission.data_collect.db import guokr_community_db


#from data_submission.ztime import now
class Items(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.iteritems():
            self.__setattr__(k, v)

class CommonData(object):
    _sql = None
    _db = guokr_community_db
    _req_param = None
    _table = None
    is_dict = True
    begin_sql = "SELECT {req_param} FROM {_table} "
    where_sql = ""
    end_sql = "OFFSET {offset} LIMIT {limit};"

    def __init__(self, limit=5000, start_page=0, **kwargs):
        self.limit = limit
        self.offset = start_page * limit
        self.param = kwargs
        self.param.update({
            "req_param": self._req_param,
            "_table": self._table,
        })
        self._req_list = []
        req_param_list = self._req_param.split(",")
        for req in req_param_list:
            if ' as ' in req:
                self._req_list.append(req.split(' as ')[1].strip())
            elif 'account' not in req and 'count' in req:
                self._req_list.append('count')
            else:
                self._req_list.append(req.strip())
        if self._sql is None:
            self._sql = self.begin_sql + self.where_sql + self.end_sql

    def _get_sql(self, offset=None):
        param = self.param
        param.update({
            'limit': self.limit
        })
        if offset is None:
            param.update({
                'offset': 0,
            })
            sql = self._sql.format(**param)
        else:
            param.update({
                'offset': offset,
            })
            sql = self._sql.format(**param)
        return sql

    def get_data(self, offset=None):
        sql = self._get_sql(offset=offset)
        ret, datas = self._db.query(sql)
        if self.is_dict:
            datas = self._format_dict(datas)
        return datas

    def _format_dict(self, _datas):
        datas = []
        for _d in _datas:
            _p = dict(zip(self._req_list, _d))
            _p.update({'values':_d})
            datas.append(Items(**_p))
        return datas

    def __iter__(self):
        return self

    def next(self):

        self.datas = self.get_data(self.offset)
        if self.datas:
            self.offset += self.limit
            return self.datas
        raise StopIteration()

class CountCommonData(object):
    _sql = None
    _db = guokr_community_db
    _table = None
    is_dict = True
    begin_sql = ""
    where_sql = ""
    end_sql = " ;"

    @classmethod
    def get_data(cls, **kwargs):
        param = {
            "_table": cls._table,
        }
        param.update(kwargs)
        if cls._sql is None:
            cls._sql = cls.begin_sql + cls.where_sql + cls.end_sql
        sql = cls._sql.format(**param)
        #print sql
        ret, datas = cls._db.query(sql)
        return datas
