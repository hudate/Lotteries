import random
from settings import proxies_tb


class SetProxies(object):

    def __init__(self):
        self.db = proxies_tb

    def set_proxies(self):
        find_data = {}
        filter_data = {'_id': 0}
        found_data = list(self.db.find(find_data, filter_data))
        data = random.choice(found_data)
        return {'https': data['info']}