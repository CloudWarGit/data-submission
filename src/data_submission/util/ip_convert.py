# -*- coding: utf-8 -*-
from IPy import IP

def ip_convert(ip):
    try:
        ip=IP(ip)
        return ip.int()
    except Exception as e:
        print(e)
        return ""
