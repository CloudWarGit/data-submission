# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging
import os, sys
import traceback

from data_submission.common import init_log_path, decode_values
from data_submission.push_task_data import push_task_data, push_zip_data
from data_submission.settings import settings
from data_submission.ztime import stamp_to_str


PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, ".."))



class Creater(object):
    buisy_dir = None
    relation_accounts = {}
    meta_funtion = None
    task_name = None


    def initial(self, log_time, begin_time, end_time):
        self.path_param = {
            'DATA_TYPE': settings.get('DATA_TYPE').get(self.buisy_dir),
            'BUISY_DIR': self.buisy_dir,
            'SERVER_IP': settings.get('SERVER_IP'),
            'log_time': log_time,
            'log_index': 0,
        }
        self.push_data={
            "task": self.task_name,
            "begin": str(begin_time),
            "end": str(end_time),
            "log_time": log_time
        }
        self._path = init_log_path(**self.path_param)
        self._name_format = settings.get('DATA_NAME')
        self.data_iter = None
        self.begin_time = stamp_to_str(begin_time)
        self.end_time = stamp_to_str(end_time)
        self.create_error = False
        self.zip_files = []


    def load_data(self):
        raise NotImplementedError

    def preload_data(self):
        return self

    def get_account(self, _data):
        pass

    def data_piece(self, data):
        raise NotImplementedError

    def write_file(self):
        offset = 0
        for index, _data in enumerate(self.data_iter):
            print(len(_data))
            self.path_param.update(log_index=index+offset)
            log_file_name = self._name_format.format(**self.path_param)
            while os.path.exists(self._path + log_file_name):
                offset += 1
                self.path_param.update(log_index=index+offset)
                log_file_name = self._name_format.format(**self.path_param)
            self.get_account(_data)
            if self.meta_funtion is not None:
                self.meta_funtion(_data)

            log_file = open(self._path + log_file_name, 'w')
            log_file.write('ICP\t2.2.1\t%s\r' % settings.get('DATA_TYPE').get(self.buisy_dir))
            self.zip_files.append(self._path + log_file_name)
    
            try:
                for data in _data:
                    try:
                        _dict = self.data_piece(data)
                        if _dict:
                            print(self.log_format.format(**_dict).encode('utf8'))
                            log_file.write(self.log_format.format(**_dict).encode('utf8'))
                        else:
                            continue
                    except Exception,e:
                        logging.error(e)
                        logging.error(traceback.format_exc())
                        self.create_error = True
                        break
            except Exception as e:
                print("error",e)
                self.create_error = True
            finally:
                log_file.close()
        else:
            print("***data_iter is none")
    
        return self

    def send_log(self):
        print(self.create_error)
        if self.create_error:
            for f in self.zip_files:
                os.remove(f)
            push_task_data(self.push_data)
        else:
            push_zip_data(self.zip_files)
    def create_log(self):
        #self.preload_data().load_data().write_file()
        self.preload_data().load_data().write_file().send_log()
