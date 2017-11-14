#!/usr/local/bin/python

import os,zipfile,time,sys

PROJECT_ROOT = os.path.realpath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "..",))

from data_submission.schedule_package import data_upload
from data_submission.daily_statistics_redis import sta_redis_list

class STA_Item(object):
    sta_file_format='{ZIP_NAME}\t{BCP_NAME}\t{BUSINESS}\t{PROTOCOL}\t{DATA_COUNT}\t{DATA_SIZE}\r'
    sta_dict={
        'ZIP_NAME':'',
        'BCP_NAME':'',
        'BUSINESS':'',
        'PROTOCOL':'',
        'DATA_COUNT':'',
        'DATA_SIZE':''
    }

class BCPFile(object):
    def __init__(self,bcp_name):
        self.bcp_name=bcp_name
        self.business=self.get_info(2)
        self.protocol=self.get_info(4)
        self.data_count=self.get_data_count()

    def get_info(self,index):
        return self.bcp_name.split('/')[index]

    def get_data_count(self):
        bcpfile="/"+self.bcp_name
        lines=open(bcpfile).readlines()
        data_items=lines[0].split('\r')
        self.data_count=len(data_items)-2
        return self.data_count

    def set_data_size(self,data_size):
        self.data_size=data_size


class ZipFile(object):
    def __init__(self,zip_name):
        self.zip_name=zip_name.split('/')[-1]
        self.zip_file=zipfile.ZipFile(zip_name)
        self._bcp_files=[]
        self.get_bcp_files()

    def get_bcp_files(self):
        bcp_files=self.zip_file.namelist()
        for bcp_name in bcp_files:
            bcp_file=BCPFile(bcp_name)
            bcp_file.set_data_size(self.zip_file.getinfo(bcp_name).file_size)
            self._bcp_files.append(bcp_file)
        return self._bcp_files

def get_zip_datas():
    daily_zip_list=sta_redis_list()
    zip_datas=daily_zip_list.get_zip_data()
    return zip_datas

def main():
    date=time.strftime("%Y%m%d",time.localtime())
    sta_file="count_"+date+".sta"
    zip_datas=get_zip_datas()
    print(zip_datas)
    sta_file_path='/tmp/count_files/{}'.format(sta_file)
    with open(sta_file_path, "a") as f:
        for i in zip_datas:
            zip_file=ZipFile(i)
            bcpfiles=zip_file.get_bcp_files()
            for bcp in bcpfiles:
                sta_item=STA_Item()
                sta_item.sta_dict['ZIP_NAME']=zip_file.zip_name
                sta_item.sta_dict['BCP_NAME']=bcp.bcp_name.split('/')[-1]
                sta_item.sta_dict['BUSINESS']=bcp.business
                sta_item.sta_dict['PROTOCOL']=bcp.protocol
                sta_item.sta_dict['DATA_COUNT']=bcp.data_count
                sta_item.sta_dict['DATA_SIZE']=bcp.data_size
                
                f.write(sta_item.sta_file_format.format(**sta_item.sta_dict))
    data_upload(sta_file_path)

if __name__ == "__main__":
    main()
