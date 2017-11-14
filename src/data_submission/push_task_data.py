# -*- coding: utf-8 -*-

import os
import sys
from data_submission import ztime

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))

sys.path.insert(0, os.path.join(PROJECT_ROOT, "..", "site-packages"))

from redis_model.queue import Client

queue_client = Client()

def push_task_data(data):
    queue_client.dispatch("WXB_Schedule.log", data)

def push_zip_data(data):
    queue_client.dispatch("WXB_Schedule.zip", data)