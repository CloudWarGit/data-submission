# -*- coding: utf-8 -*-

from Queue import Queue
from multiprocessing import Process
import os
import signal
import sys

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", "site-packages"))

from data_submission.push_task_data import push_task_data
from data_submission.settings import settings
from data_submission import ztime


schedules = settings.get('schedule_name')
_path = "/tmp/"

def push_log_schedule(log_stamp, begin, end):
    for schedule_name in schedules.iterkeys():
        data = {
            "task": schedule_name,
            "begin": str(begin),
            "end": str(end),
            "log_time": log_stamp
        }
        push_task_data(data)

if __name__ == '__main__':
    print(ztime.now_stamp())
    now_stamp = int(ztime.now_stamp())
    try:
        file_name = sys.argv[1]
    except:
        file_name = "log_time.log"
    file_path = _path + 'time_log/'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    begin = int(now_stamp - 5 * 60 * 60)
    end = int(now_stamp - 60)
    lines = [str(begin)+' '+str(end)+'\r\n']
    if file_name:
        if os.path.exists(file_path+str(file_name)):
            with open(file_path+str(file_name), 'r') as f:
                lines = f.readlines()
                last_line = lines[-1]
                lines = lines[-1000:]
                begin = int(last_line.strip('\r\n').split()[1])
                end = int(now_stamp-60)
                lines.append(str(begin)+' '+str(end)+'\r\n')
    with open(file_path+str(file_name), 'w') as f:
        f.writelines(lines)

    # diff = 3600
    # now_stamp, begin, end = 1476749251, 1476600165, 1476700165

    push_log_schedule(now_stamp, begin, end)


