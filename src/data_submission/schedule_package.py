# -*- coding: utf-8 -*-

import os
import sys
import json
import paramiko

from ftplib import FTP
from scp import SCPClient

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, "..",))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", "site-packages"))

from redis_model.queue import RedisQueue

from data_submission.settings import settings
from data_submission.ztime import now_stamp
from data_submission.push_task_data import push_zip_data
from data_submission.daily_statistics_redis import sta_redis_list

ftp_server='192.168.10.100'
timeout=30
port=21
ftp_user='guoke'
ftp_passwd = 'n5t6y8u9'

def data_upload(filename):
    dirname=os.path.dirname(filename)
    filename=os.path.basename(filename)
    ftp=FTP()
    ftp.connect(ftp_server, port, timeout)
    ftp.login(ftp_user, ftp_passwd)
    os.chdir(dirname)
    with open(filename,'rb') as fp:
        ftp.storbinary("STOR {}".format(filename), fp)

def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

_path = "/tmp/"

def get_zip_schedule(zip_path):
    mq = RedisQueue("WXB_Schedule.zip")
    zip_files = []
    while True:
        list = mq.pop()
        if list:
            zip_files.extend(json.loads(list))
        else:
            break
    zip_name = zip_path + "data_" + now_stamp() + '.zip'
    error = False
    kw = {
        'password': settings.get('zip_password'),
     'zip_filename': zip_name,
     'filename': ''
    }
    zip_exc = 'zip -P {password} {zip_filename} {filename}'
    try:
        for zip_file in zip_files:
            size = os.path.getsize(zip_file)
            if size<20:
                continue
            kw.update(filename=zip_file)
            print(kw)
            zipresult=os.system(zip_exc.format(**kw))
            print(zipresult)
    except:
        error = True
    try:    
        size = os.path.getsize(zip_name)
        print(size)
    except:
        size = -1
    if size > 2000:
        try:
            #ssh = createSSHClient( '192.168.10.100', 22, 'guoke', 'n5t6y8u9')
            #scp = SCPClient(ssh.get_transport())
            #scp.put(zip_name,'/home/guoke')
            data_upload(zip_name)
            sta_redis=sta_redis_list()
            sta_redis.put_zip_data(zip_name)
            import time
            print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()),"%s has been submitted successfully" % zip_name)
        except Exception,e:
            print(e)
            error = True
    else:
        error = True
    if error and size > 0:
        push_zip_data(zip_files)
        os.remove(zip_name)
    elif size < 0:
        print("no zip_files")
    return zip_files

if __name__ == "__main__":
    zip_path = _path + 'zip_files/'
    if not os.path.exists(zip_path):
        os.makedirs(zip_path)
    get_zip_schedule(zip_path)
