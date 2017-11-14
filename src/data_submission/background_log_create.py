# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-

import os
import sys
import logging
import importlib

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", "site-packages"))


from redis_model.queue import Worker

from data_submission.settings import settings

schedules = settings.get('schedule_name')

def log_create(data):
    logging.error(data)
    task_name = data.get("task")
    print(task_name)

    param = {
        "begin_time": int(data.get("begin")),
        "end_time": int(data.get("end")),
        "log_time": data.get("log_time"),
    }
    mod = None
    try:
        mod = importlib.import_module(schedules.get(task_name))
        print mod
    except Exception, e:
        print "test"
        print e
    if mod:
        if hasattr(mod, 'task_create_log'):
            getattr(mod, 'task_create_log')(**param)


if __name__ == "__main__":
    worker = Worker("WXB_Schedule.log")
    try:
        worker.register(log_create)
        worker.start()
    except KeyboardInterrupt:
        worker.stop()
        print "exited cleanly"
        sys.exit(1)
    except Exception, e:
        print e
