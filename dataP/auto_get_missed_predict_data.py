import os

import time
import urllib3
urllib3.disable_warnings()
import requests
from multiprocessing.dummy import Pool
from settings import lotteries_predict_data_db as lpdb, saved_db
from settings import miss_urls_db, LOTTERY_DICT
from tools.set_proxies import SetProxies as SP
from tools.save_data import SaveLotteriesData as SLD
from bs4 import BeautifulSoup as bs
from tools.ua import ua
from tools.logger import Logger
logger = Logger(__name__).logger


class GetMissedPredictData(object):

    def __init__(self):
        # Process.__init__(self)
        self.parse_func = None
        self.articles_miss_urls_db = miss_urls_db['predict_urls']

    def get_urls(self):
        return self.articles_miss_urls_db.find({}, {'url': 1, '_id': 0, 'data_type': 1, 'expert_id': 1}).limit(8000)

    def get_data(self, url, data_type, expert_id, times=0):
        data = None
        header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn'}
        if times < 4:
            times += 1
            if times < 3:
                try:
                    req = requests.get(url, headers=header, timeout=(5, 5))
                    # print(url, req.status_code)
                    if req.status_code == 403:
                        logger.warn(str(req.history) + url + req.status_code)
                    data = req.text
                except:
                    logger.info(url + ' ' + str(times))
                    self.get_data(url, data_type, times)
            else:
                sp = SP()
                proxy = sp.set_proxies()
                try:
                    req = requests.get(url, headers=header, proxies=proxy, timeout=(20, 15),
                                       verify=False)
                    if req.status_code == 403:
                        logger.warn(str(req.history) + url + req.status_code)
                    data = req.text
                except:
                    logger.info(url + ' ' + str(times))
                    self.get_data(url, data_type, times)
        if data:
            self.parse_data(data, url, data_type, expert_id, times)

    def parse_data(self, data, url, data_type, expert_id, times):
        data = bs(data, 'lxml')
        try:
            title = data.find_all('title')[0].text
            if '双色球' in title:
                self.ssq_parse(data, url, title.split('福彩双色球'), data_type, expert_id)
            elif '大乐透' in title:
                self.dlt_parse(data, url, title.split('体彩大乐透'), data_type, expert_id)
            else:
                self.get_data(url, data_type, expert_id, times)
        except:
            self.get_data(url, data_type, expert_id, times)

    def ssq_parse(self, data, url, title, data_type, expert_id):
        lottery_name = '双色球'
        balls = []
        # print(lottery_name, title)
        expert_name = title[0]
        stage = title[1].split('期')[0]
        trs = data.find_all('table', attrs={'class': 'zb_wz_table'})[0].find_all('tr')
        show_time = data.find_all('div', attrs={'class': 'zx_all'})[0].text.split('：')[1].strip()[:-3].strip()
        for tr in trs:
            tds = tr.find_all('td')
            if data_type == 0:
                if '25码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if data_type == 1:
                if '定五码' in tds[0].text or '定5码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if data_type == 2:
                if '杀六码' in tds[0].text or '杀6码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if data_type == 3:
                if '杀五码' in tds[0].text or '杀5码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break

        if balls:
            self.save_balls(lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url=url)

    def dlt_parse(self, data, url, title, data_type, expert_id):
        lottery_name = '大乐透'
        balls = []
        # print(lottery_name, title)
        expert_name = title[0]
        stage = title[1].split('期')[0]
        trs = data.find_all('table', attrs={'class': 'zb_wz_table'})[0].find_all('tr')
        show_time = data.find_all('div', attrs={'class': 'zx_all'})[0].text.split('：')[1].strip()[:-3].strip()
        for tr in trs:
            tds = tr.find_all('td')
            if data_type == 0:
                if '25码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if data_type == 1:
                if '定六码' in tds[0].text or '定6码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if data_type == 2:
                if '杀六码' in tds[0].text or '杀6码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if data_type == 3:
                if '后区杀三码' in tds[0].text or '后区杀3码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
        if balls:
            self.save_balls(lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url=url)

    def save_url(self, save_instance, url, data_type):
        # TODO 重点查看
        # 保存url到数据库中
        db = saved_db['saved_predict_urls']
        find_data = {'url': url, 'data_type': data_type}
        found_data = self.articles_miss_urls_db.find_one(find_data, {'_id': 0})
        if found_data:
            try:
                save_instance.save_data(db, found_data)
                self.articles_miss_urls_db.delete_one(found_data)
            except Exception as e:
                logger.error(e)

    def save_balls(self, lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url):
        data = {
            'lottery': lottery_name,
            'expert_id': expert_id,
            'expert_name': expert_name,
            'stage': stage,
            'data_type': data_type,
            'balls': balls,
            'show_time': show_time,
            'show_time_stamp': int(time.mktime(time.strptime(show_time, "%Y-%m-%d %H:%M:%S")))
        }

        predict_ball_db = lpdb[LOTTERY_DICT[lottery_name]]
        kill_ball_db = lpdb[LOTTERY_DICT[lottery_name] + '_kill']
        if data_type == 0 or data_type == 1:
            db = predict_ball_db
        else:
            db = kill_ball_db

        sld = SLD()
        if sld.save_data(db, data):
            self.save_url(sld, url, data_type)

    def run(self):
        for i in range(50):
            t3 = time.time()
            urls_info = self.get_urls()
            p = Pool(processes=10 * os.cpu_count())
            # p = threadpool.ThreadPool(maxsize=200)
            if urls_info:
                print(urls_info)
                for url_info in urls_info:
                    print(url_info)
                    p.apply_async(self.get_data, url_info['url'], url_info['data_type'], url_info['expert_id'])
                p.close()
                p.join()
            del p
            t4 = time.time()
            print('cost time:', t4 - t3)
            time.sleep(1700)


if __name__ == '__main__':
    t1 = time.time()
    gmpd = GetMissedPredictData()
    gmpd.run()
    t2 = time.time()
    print('cost time:', t2 - t1)
