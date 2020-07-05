import gevent
from gevent import monkey, pool
from lxml import etree

monkey.patch_all()

import requests

from proxy.save_proxy import SaveProxies
from tools.logger import Logger
logger = Logger(__name__).logger


class CheckProxies(object):

    def __init__(self):
        self.http_url = 'http://www.net.cn/static/customercare/yourip.asp'
        self.https_url = 'https://ip.cn'
        # self.https_url = 'https://www.baidu.com/s?wd=%E6%88%91%E7%9A%84ip%E5%9C%B0%E5%9D%80'
        self.pool = pool.Pool(100)
        self.header = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        }

    def http_check(self, proxy):
        html, proxy_ip = self.get_info(self.http_url, proxy)
        if proxy_ip:
            ip = html.xpath('//h2/text()')[0]
            if ip == proxy_ip:
                self.save_proxy(proxy)

    def https_check(self, proxy):
        html, proxy_ip = self.get_info(self.https_url, proxy)
        if proxy_ip:
            ip = html.xpath('//code/text()')[0]
            if ip == proxy_ip:
                self.save_proxy(proxy)

    def get_info(self, url, proxy):
        proxy_ip = list(proxy.values())[0].split(':')[1][2:]
        req = requests.Response()
        try:
            req = requests.get(url=url, proxies=proxy, timeout=10, verify=False, headers=self.header)
        except:
            pass

        if req.status_code == 200:
            html = etree.HTML(req.text)
            return html, proxy_ip
        else:
            return None, None

    def save_proxy(self, proxy):
        sp = SaveProxies()
        sp.save_to_mongo(proxy)

    def start(self, proxies_list):
        for proxy in proxies_list:
            proxy_type = proxy.split(':')[0]
            new_proxy = {proxy_type: proxy}
            if proxy_type == 'https':
                self.pool.spawn(self.https_check, new_proxy)
            elif proxy_type == 'http':
                self.pool.spawn(self.http_check, new_proxy)
        self.pool.join()


# if __name__ == '__main__':
#     list_proxy =
#     cp = CheckProxies()
#     cp.start(list_proxy)
