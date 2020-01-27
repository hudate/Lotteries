import os
from proxy.settings import mongo_setting, redis_setting
from tools.logger import Logger
logger = Logger(__name__).logger


class SaveProxies(object):

    def __init__(self):
        self.coll = mongo_setting['proxies_coll']
        self.redis = redis_setting['PROXIES']['redis']
        self.r_key = redis_setting['proxies_key']


    def save_to_mongo(self, proxy):
        self.save_to_redis(proxy)
        data_dict = {'type': list(proxy.keys())[0], 'info': list(proxy.values())[0] }
        if not list(self.coll.find(data_dict, {'_id': 0})):
            self.coll.insert_one(data_dict)
            return 1
        else:
            return 0


    def save_to_file(self, proxy):
        if not os.path.exists(self.file):
            with open(self.file, 'a', encoding='utf-8') as f:
                f.write(','.join([proxy.keys(), '\n']))
        with open(self.file, 'a', encoding='utf-8') as f:
            f.write(','.join([proxy.values(), '\n']))


    def save_to_redis(self, proxy):
        if list(proxy.keys())[0] == 'https':
            self.redis.lpush(self.r_key, list(proxy.values())[0])


if __name__ == '__main__':
    list_proxy = ['https://121.40.90.189:8001', 'http://121.40.90.189:8001', 'https://123.123.12.23:8000']
    sp = SaveProxies()
    for proxy in list_proxy:
        sp.save_to_redis(proxy)

