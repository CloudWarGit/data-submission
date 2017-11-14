# -*- coding: utf-8 -*-

import functools
import hashlib
import inspect
import logging
import socket
import traceback

from pymemcache.client.hash import HashClient

from data_submission.settings import settings


try:
    import simplejson as json
except ImportError:
    import json


def format_memcached_servers(memcached_urls):
    servers = []
    urls = memcached_urls
    for url in urls:
        server = url.split(':')
        if not server or len(server) != 2:
            break
        host, port = server
        servers.append((host, int(port)))
    return servers

class Memcache(object):

    def __init__(self):
        self._memc_client = None

    def local_memc(self):
        servers = format_memcached_servers(settings.get('MEMC_SERVERS'))
        memc = HashClient(servers, timeout=1)
        return memc

    # def init_app(self, app, strict=False):
    #     if app.config.get('TESTING', None):
    #         self._memc_client = MockMemcache()
    #     else:
    #         self._memc_client = self.local_memc(app)
    #
    #     if not hasattr(app, 'extensions'):
    #         app.extensions = {}
    #     app.extensions['memc'] = self

    def __getattr__(self, name):
        return getattr(self._memc_client, name)

mc = Memcache()
memc = mc.local_memc()

class ExpireTime(object):
    u"""缓存超时时间, 单位秒"""
    HALF_MIN = 30
    MIN = 60
    FIVE_MINS = 60 * 5
    TEN_MINS = 60 * 10
    TWENTY_MINS = 60 * 20
    HALF_HOUR = 60 * 30
    HOUR = 60 * 60
    HALF_DAY = 60 * 60 * 12
    DAY = 60 * 60 * 24
    TWO_DAY = 60 * 60 * 48
    MONTH_DAY = 60 * 60 * 24 * 30

# default expire time
expire_time = ExpireTime.MONTH_DAY


def incr(key, _mc=memc):
    result = _mc.incr(key)
    return result


def decr(key, _mc=memc):
    result = _mc.decr(key)
    return result


def add(key, value, time=expire_time, _mc=memc):
    result = _mc.add(key, value, time)
    return result


def delete(key, _mc=memc):
    result = _mc.delete(key)
    return result


def set(key, value, time=expire_time, _mc=memc):
    result = _mc.set(key, value, time)
    return result


def set_multi(mapping, time=expire_time, _mc=memc):
    result = _mc.set_multi(mapping, time)
    return result


def get(key, _mc=memc):
    result = _mc.get(key)
    return result


def get_multi(keys, _mc=memc):
    result = _mc.get_multi(keys)
    return result


def _encode_cache_key(k):
    if isinstance(k, (bool, int, long, float, str)):
        return str(k)
    elif isinstance(k, unicode):
        return k.encode('utf-8')
    elif isinstance(k, dict):
        import urllib

        for x in k.keys():
            k[x] = _encode_cache_key(k[x])
        return urllib.urlencode(sorted(k.items()), True)
    else:
        return repr(k)

def memcached_muti_ids_function(cache_key, prefix=None, suffix=None, expire_time=expire_time,
                                cache_reflesh='', extkws={}):
    u"""
       cache_keys: 参数名称，参数对应值为id列表
       prefix                   : 前缀
       suffix                   : 后缀
       expire_time              : 缓存时间，defaut time 30天
       cache_reflesh="YES" or '': 是否马上更新缓存,否则到expire_time才更新缓存
       extkws={}                : 追加缓存参数,同名覆盖缓存参数

    """

    def _get_ckey(ckey):
        ckey_list = []
        if prefix is not None:
            ckey_list.append(prefix)
        if ckey:
            if isinstance(ckey, (bool, int, long, float, str)):
                ckey_list.append(str(ckey))
            elif isinstance(ckey, unicode):
                ckey_list.append(ckey.encode('utf-8'))
        if suffix is not None:
            ckey_list.append(suffix)
        return ':'.join(ckey_list)

    def _get_ckeys(cache_list=None):
        format_key = _get_ckey('%s')
        ckeys = [format_key % ckey for ckey in cache_list]
        return ckeys

    def _set_muti(result):
        format_key = _get_ckey('%s')
        _map = {format_key % k: json.dumps(v) for k, v in result.items()}
        set_multi(_map, expire_time)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            arg_names, varargs, varkw, defaults = inspect.getargspec(func)
            # defaults
            _defargs = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
            _args1 = dict(zip(arg_names, args))
            _kwds = dict(_defargs, **_args1)
            _kwds.update(kwargs)
            _kwds.update(extkws)
            if varargs:
                tmp = _args1.values()
                otheragrs = [v for v in args if v not in tmp]
                if otheragrs:
                    _kwds[varargs] = otheragrs
            cache_list = _kwds.get(cache_key, [])
            result = {}
            ckeys = _get_ckeys(cache_list)
            if ckeys:
                try:
                    # TODO: cache_reflesh 刷新功能
                    if _kwds.get('cache_reflesh', '').upper() == 'YES':
                        dirty = cache_list
                    else:
                        result_dict = get_multi(ckeys)
                        if result_dict is None:
                            raise socket.error
                        dirty = []
                        for _id in cache_list:
                            r = result_dict.get(_get_ckey(_id), None)
                            if r:
                                result[_id] = json.loads(r)
                            else:
                                dirty.append(_id)
                    dirty = filter(lambda id: id and str(id).isdigit(), dirty)
                    if dirty:
                        if 'self' in _kwds:
                            dirty.insert(0, _kwds.get('self'))
                        dirty_result = func(*dirty, **kwargs)
                        if dirty_result:
                            _set_muti(dirty_result)
                        result.update(dirty_result)
                    return result
                except Exception, e:
                    logging.error(traceback.format_exc())
                    if isinstance(e, socket.error):
                        raise e
                    logging.error(e)
                    return func(*args, **kwargs)
            return func(*args, **kwargs)
        wrapper.original_function = func
        wrapper.func_name = func.func_name
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator

def memcached_function(cache_keys, prefix=None, suffix=None, expire_time=expire_time,
                       cache_reflesh='', extkws={}, is_json=False, is_md5=False, nil=None):
    u"""
       cache_keys: 缓存取那些参数当key,key之间用豆号(,)分割，参数的属性当key，使用冒号(:)分割
                  例：“key1,key2:p” 获取key1和key2.p为key
       prefix                   : 前缀
       suffix                   : 后缀
       expire_time              : 缓存时间，defaut time 30天
       from_g                   : 是否从g中获取数据
       cache_reflesh="YES" or '': 是否马上更新缓存,否则到expire_time才更新缓存
       extkws={}                : 追加缓存参数,同名覆盖缓存参数
       is_json                  : bool 是否返回json
       is_md5                   : bool 是否为key进行md5加密
       nil:当出错时，返回的空数据格式

       生成ckey的长度len不超过200
    """

    def _get_ckey(ckey):
        ckey_list = []
        if prefix is not None:
            ckey_list.append(prefix)
        if ckey:
            if isinstance(ckey, (bool, int, long, float, str)):
                ckey_list.append(str(ckey))
            elif isinstance(ckey, unicode):
                ckey_list.append(ckey.encode('utf-8'))
        if suffix is not None:
            ckey_list.append(suffix)
        return ':'.join(ckey_list)

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_keys_list = []
            if cache_keys:
                cache_keys_list = cache_keys.split(',')
                # 去除cache key里面的空格
                cache_keys_list = [ele.strip() for ele in cache_keys_list]
            arg_names, varargs, varkw, defaults = inspect.getargspec(func)
            # defaults
            _defargs = dict(zip(arg_names[-len(defaults):], defaults)) if defaults else {}
            _args1 = dict(zip(arg_names, args))
            _kwds = dict(_defargs, **_args1)
            _kwds.update(kwargs)
            _kwds.update(extkws)
            if varargs:
                tmp = _args1.values()
                otheragrs = [v for v in args if v not in tmp]
                if otheragrs:
                    for i in xrange(0, len(otheragrs)):
                        _k = "_arg{}".format(i)
                        _kwds[_k] = otheragrs[i]
            ckey = None
            if cache_keys_list:
                ckey = []
                for cache_key in cache_keys_list:
                    cache_key = cache_key.split(":")
                    if cache_key[0] in _kwds:
                        if len(cache_key) > 2:
                            continue
                        cache_value = getattr(_kwds.get(cache_key[0], None), cache_key[1], None) \
                            if len(cache_key) == 2 else _kwds.get(cache_key[0], None)
                        if cache_value is not None:
                            ckey.append(_encode_cache_key(cache_value))
                ckey = ':'.join(ckey) if ckey else None
            if is_md5 and ckey is not None:
                ckey = hashlib.md5(ckey).hexdigest()
            ckey = _get_ckey(ckey)
            if len(ckey) > 200:
                ckey = ckey[:200]
            if ckey:
                try:
                    # TODO : cache_reflesh 刷新功能
                    result = None if _kwds.get('cache_reflesh', '').upper() == 'YES' else get(ckey)
                    if result is None:
                        result = func(*args, **kwargs)
                        if result:
                            # TODO : json dump 可能会出现问题
                            if is_json:
                                result = json.dumps(result)
                            set(ckey, result, expire_time)
                        elif kwargs.get('cache_reflesh', '').upper() == 'YES':
                            # 新数据为空的时候，不会更新key，所以要删除key
                            delete(ckey)
                    if is_json and result is not None and result:
                        try:
                            result = json.loads(result)
                        except:
                            result = nil
                    return result
                except Exception, e:
                    if isinstance(e, socket.error):
                        raise e
                    logging.error(e)
                    logging.error(traceback.format_exc())
                    return func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        wrapper.original_function = func
        wrapper.func_name = func.func_name
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


if __name__ == '__main__':
    set('aaaaa123', '123')
    print get('aaaaa123')
