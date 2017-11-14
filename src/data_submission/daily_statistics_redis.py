import redis
from data_submission.settings import settings

sta_redis_backend=settings.get('STA_REDIS_BACKEND')

class sta_redis_list(object):
    def __init__(self):
        host=sta_redis_backend['servers']
        port=sta_redis_backend['port']
        db=sta_redis_backend['db']
        self.redis_client=redis.StrictRedis(host=host, port=port, db=db)
    
    def put_zip_data(self,zip_data):
        self.redis_client.lpush('daily_zip_list',zip_data)
        
    def get_zip_data(self):
        zip_datas=[]
        while True:
            zip_data=self.redis_client.lpop('daily_zip_list')
            if zip_data:
                zip_datas.append(zip_data)
            else:
                break
        return zip_datas


if __name__ == '__main__':
    sta_redis=sta_redis_list()
    sta_redis.put_zip_data('test')
