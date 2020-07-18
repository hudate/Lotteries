from gevent import monkey, pool
monkey.patch_all()

import os
import random
import time
import requests
import urllib3
from lxml import etree
from proxy.check_proxy import CheckProxies
from tools.ua import ua
from proxy.config import *

urllib3.disable_warnings()
from tools.logger import Logger
logger = Logger(__name__).logger


class GetProxies(object):
    def __init__(self):
        self.proxies_websites = {
            '西拉免费代理HTTPS': 'http://www.xiladaili.com/https/',
            '西拉免费代理HTTP': 'http://www.xiladaili.com/http/',
            '西刺代理HTTPS': 'https://www.xicidaili.com/wn/',
            '西刺代理HTTP': 'https://www.xicidaili.com/wt/'
        }
        self.u_a = {}
        self.header = {}
        self.pool = pool.Pool(30)
        self.proxy = None
        self.proxy_coll = mongo_setting['proxies_coll']

    def set_ua(self):
        self.u_a = ua()

    def set_header(self):
        self.header = {
            'User-Agent': self.u_a,
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }

    def start_request(self, url, name, error_count=0):
        self.set_ua()
        self.set_header()
        req = None
        try:        # 请求成功
            req = requests.get(url=url, headers=self.header, proxies=self.proxy, verify=False, timeout=30)
        except Exception as e:  # 请求失败
            error_count += 1
            failed_info = {
                'name': name,
                'err_times': str(error_count),
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'page': url.split('/')[-1],
                'UA': self.u_a
            }
            if not os.path.exists('failed_record.txt'):
                with open('failed_record.csv', 'a', encoding='utf-8') as f:
                    f.write(','.join(list(failed_info.keys()))+'\n')
            with open('failed_record.csv', 'a', encoding='utf-8') as f:
                f.write(','.join(list(failed_info.values())) + '\n')

            # print('line 75:', url, self.stop_request(error_count))

            if not self.stop_request(error_count):
                self.set_proxy(url)    # 设置代理
                self.start_request(url, name, error_count)
            else:
                return

        if req is not None and req.status_code != 200:
            error_count += 1
            if not self.stop_request(error_count):
                self.set_proxy(url)  # 设置代理
                self.start_request(url, name, error_count)
            else:
                return
        else:
            proxies = self.parse_req(req, name)

    def parse_req(self, req, name):
        html = etree.HTML(req.text)
        trs = html.xpath('//table//tr')[1:]
        proxies_list = []
        for tr in trs:
            tds_text_list = tr.xpath('td//text()')
            if name.startswith('西刺'):
                proxies = self.parse_xici(tds_text_list)

            if name.startswith('西拉'):
                proxies = self.parse_xila(tds_text_list)

            if isinstance(proxies, list):
                proxies_list.extend(proxies)
            else:
                proxies_list.append(proxies)
        ck = CheckProxies()
        ck.start(proxies_list)
        return proxies_list

    def parse_xici(self, text_list):
        proxy_type = text_list[6] if '\n' not in text_list[6] else text_list[4]
        proxy_ip = text_list[0]
        proxy_port = text_list[1]
        return '://'.join([proxy_type.lower(), ':'.join([proxy_ip, proxy_port])])

    def parse_xila(self, text_list):
        proxy_types = text_list[1][:-2].split(',')
        proxy_info = text_list[0]
        if len(proxy_types) == 2:
            proxies = ['://'.join([proxy_type.lower(), proxy_info]) for proxy_type in proxy_types]
        else:
            proxies = '://'.join([proxy_types[0].lower(), proxy_info])
        return proxies

    def stop_request(self, error_count):    # 判断错误次数
        if error_count == 5:
            return 1
        else:
            return 0

    def set_proxy(self, url):
        print(url, type(url), url.split(':')[0])
        proxy = random.choice(list(self.proxy_coll.find({'type': url.split(':')[0]}, {'_id': 0})))
        self.proxy = {proxy['type']: proxy['info']}

    def start(self):
        for k, v in self.proxies_websites.items():
            for i in range(1, proxies_setting['stop_pages'] + 1):
                print('正在爬取 网站:%s，第%s页' % (k, i))
                url = v + str(i)
                self.pool.spawn(self.start_request, url, k)
                time.sleep(0.5)
        self.pool.join()


if __name__ == '__main__':
    gp = GetProxies()
    gp.start()
    # pool.close()
    # pool.join()



