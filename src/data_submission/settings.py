# -*- coding: utf-8 -*-

import importlib
from os import getenv


modules = ('data_submission')


def load_settings(*modules):
    settings = {}
    init_settings(settings)
    kwargs = {}
    mods = []

    for module in modules:
        try:
            print(module)
            mods.append(importlib.import_module('%s.my_settings' % module))
        except:
            pass

    for mod in mods:
        if hasattr(mod, 'load_settings'):
            getattr(mod, 'load_settings')(settings, **kwargs)
    print("mods****: ",mods)
    return settings


def init_settings(settings):
    settings.update({
        'SERVER_IP': '172.31.0.174',
        'ICP_CODE': '11010513810000',  # TODO: ICP编码
        'DATA_TYPE': {
            'register':'PASSPOST',
            'login': 'PASSPOST',
            'connect': 'SNS'
            },  # TODO: 协议类型标识
        'expires': 7,
        'BUISY_DIRS': [  # TODO: 我们需要上报的类型
                         'register',
                         'connect',
                         'login',
        ],
        'schedule_name': {
            'register': 'data_submission.log_creater.register',
            'connect': 'data_submission.log_creater.follow',
            'login': 'data_submission.log_creater.login',
        },
        'PATH_DIR': '/data/',
        'DATA_PATH': '{SERVER_IP}/{BUISY_DIR}/{log_time}/{DATA_TYPE}/',
        'DATA_NAME': '{BUISY_DIR}_{DATA_TYPE}_{log_time}_{log_index}.bcp',
        'DB_GUOKR_AUTH': {
            'host': '172.31.0.174',
            #'host': '172.31.0.174', #线上数据库
            'port': 5432,
            'user': 'auth',
            'password': 'aaaa',
            'database': 'auth',
        },
        'DB_GUOKR_COMMUNITY': {
            'host': '172.31.0.174',
            'port': 5432,
            'user': 'community',
            'password': 'cccc',
            'database': 'community',
        },
        'MEMC_SERVERS': (
            '10.10.0.219:11211',
        ),
        "STA_REDIS_BACKEND": {"servers": 'redis-live.xeejgj.0001.cnn1.cache.amazonaws.com.cn', "port": 6379, "db": 13, 'password': ''},
        'zip_password': 'run1234!@#'
    })


settings = load_settings(modules)
#print(settings)
