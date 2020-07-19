from bs4 import BeautifulSoup as bs
import time
import urllib3
from gevent import thread
urllib3.disable_warnings()
import requests
from settings import lotteries_predict_data_db as lpdb, saved_db
from settings import miss_urls_db, LOTTERY_DICT
from tools.save_data import SaveLotteriesData as SLD
from tools.ua import ua
from tools.set_proxies import SetProxies as SP
from tools.logger import Logger
logger = Logger(__name__).logger


class GetPredictData(object):

    def __init__(self):
        # super(GetPredictData, self).__init__()

        self.url = None
        self.parse_func = None
        self.lottery_name = None
        self.expert_id = None
        self.predict_ball_db = None
        self.kill_ball_db = None
        self.db = None
        self.data_type = None
        self.save_predict_data_db = saved_db['saved_predict_urls']
        self.articles_miss_urls_db = miss_urls_db['predict_urls']

    def save_url(self, save_class):
        # TODO 重点查看
        find_data = {'url': self.url, 'data_type': self.data_type}
        found_data = self.articles_miss_urls_db.find_one(find_data, {'_id': 0})
        if found_data:
            try:
                save_class.save_data(self.save_predict_data_db, found_data)
                return True
            except Exception as e:
                logger.error(e)
        return False

    def remove_url(self):
        find_data = {'url': self.url, 'data_type': self.data_type}
        found_data = list(self.articles_miss_urls_db.find(find_data, {'_id': 1, 'url': 1, 'data_type': 1, 'expert_id': 1, 'expert_name': 1}))
        try:
            for data in found_data:
                print(find_data)
                print(data)
                self.articles_miss_urls_db.delete_one(data)
        except Exception as e:
            logger.error(e)

    def save_balls(self, expert_name, stage, show_time, balls):
        print(self.lottery_name, expert_name, self.expert_id, stage, show_time, balls, self.data_type, self.url)
        data = {
            'lottery': self.lottery_name,
            'expert_id': self.expert_id,
            'expert_name': expert_name,
            'stage': stage,
            'data_type': self.data_type,
            'balls': balls,
            'show_time': show_time,
            'show_time_stamp': int(time.mktime(time.strptime(show_time, "%Y-%m-%d %H:%M:%S")))
        }

        sld = SLD()
        if sld.save_data(self.db, data):
            thread.sleep(0.2)
            if self.save_url(sld):
                thread.sleep(0.2)
                self.remove_url()

    def ssq_parse(self, data, title):
        print('ssq解析')
        balls = []
        try:
            expert_name = lpdb['all_experts'].find_one(
                {'expert_id': self.expert_id},
                {'_id': 0, 'expert_name': 1}
            ).get('expert_name')
        except Exception:
            try:
                expert_name = lpdb['ssq_experts'].find_one(
                    {'expert_id': self.expert_id},
                    {'_id': 0, 'expert_name': 1}
                ).get('expert_name')
            except Exception:
                expert_name = title[0].split('福彩双')[0]

        stage = title[1].split('期')[0]
        trs = data.find_all('table', attrs={'class': 'zb_wz_table'})[0].find_all('tr')
        show_time = data.find_all('div', attrs={'class': 'zx_all'})[0].text.split('：')[1].strip()[:-3].strip()
        for tr in trs:
            tds = tr.find_all('td')
            if self.data_type == 0:
                if '25码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if self.data_type == 1:
                if '定五码' in tds[0].text or '定5码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if self.data_type == 2:
                if '杀六码' in tds[0].text or '杀6码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if self.data_type == 3:
                if '杀五码' in tds[0].text or '杀5码' in tds[0].text and self.lottery_name == '双色球':
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break

        print(self.lottery_name, expert_name, self.expert_id, stage, show_time, balls, self.data_type, self.url)
        if balls:
            self.save_balls(expert_name, stage, show_time, balls)

    def dlt_parse(self, data, title):
        print('大乐透解析')
        balls = []
        try:
            expert_name = lpdb['all_experts'].find_one(
                {'expert_id': self.expert_id},
                {'_id': 0, 'expert_name': 1}
            ).get('expert_name')
        except Exception:
            try:
                expert_name = lpdb['dlt_experts'].find_one(
                    {'expert_id': self.expert_id},
                    {'_id': 0, 'expert_name': 1}
                ).get('expert_name')
            except Exception:
                expert_name = title[0].split('体彩大')[0]

        stage = title[1].split('期')[0]
        print(stage)
        trs = data.find_all('table', attrs={'class': 'zb_wz_table'})[0].find_all('tr')
        show_time = data.find_all('div', attrs={'class': 'zx_all'})[0].text.split('：')[1].strip()[:-3].strip()
        for tr in trs:
            tds = tr.find_all('td')
            if self.data_type == 0:
                if '25码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if self.data_type == 1:
                if '定六码' in tds[0].text or '定6码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if self.data_type == 2:
                if '杀六码' in tds[0].text or '杀6码' in tds[0].text:
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break
            if self.data_type == 3:
                if '后区杀三码' in tds[0].text or '后区杀3码' in tds[0].text and self.lottery_name == '双色球':
                    src = tds[1].find_all('script')[0]['src']
                    balls = src.split('zbnum=')[1].split(',')
                    break

        print(self.lottery_name, expert_name, self.expert_id, stage, show_time, balls, self.data_type, self.url)

        if balls:
            self.save_balls(expert_name, stage, show_time, balls)

    def set(self, lottery_name, expert_id, data_type, url):
        self.expert_id = expert_id
        self.data_type = data_type
        self.url = url
        self.lottery_name = lottery_name
        self.predict_ball_db = lpdb[LOTTERY_DICT[lottery_name]]
        self.kill_ball_db = lpdb[LOTTERY_DICT[lottery_name] + '_kill']

        if data_type == 0 or data_type == 1:
            self.db = self.predict_ball_db
        else:
            self.db = self.kill_ball_db

        if lottery_name == '双色球':
            self.parse_func = self.ssq_parse

        if lottery_name == '大乐透':
            self.parse_func = self.dlt_parse

    def get_predict_data(self, times=0):
        print(self.url, times)
        found_data = []
        try:
            found_data = list(self.save_predict_data_db.find({'data_type': self.data_type, 'url': self.url}, {'_id': 0}))
        except Exception as e:
            logger.error(e)

        if found_data:
            print('found data')
            self.remove_url()
        else:
            print('not found data')
            data = None
            header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn', 'Accept-Encoding': 'gzip'}
            if times < 3:
                times += 1
                if times <= 1:
                    try:
                        req = requests.get(self.url, headers=header, timeout=(10, 15), allow_redirects=True)
                        if req.status_code == 403:
                            # logger.warning(str(req.history) + self.url + str(req.status_code))
                            self.get_predict_data(times)
                        data = req.text
                    except Exception as e:
                        logger.error(e)
                        logger.error(self.url + ' ' + str(times))
                        self.get_predict_data(times)
                else:
                    sp = SP()
                    proxy = sp.set_proxies()
                    logger.warning(proxy)
                    try:
                        req = requests.get(self.url, headers=header, proxies=proxy, timeout=(20, 15),
                                           verify=False)
                        if req.status_code == 403:
                            # logger.warning(str(req.history) + self.url + str(req.status_code))
                            self.get_predict_data(times)
                        data = req.text
                    except Exception as e:
                        logger.error(e)
                        logger.error(self.url + ' ' + str(times))
                        self.get_predict_data(times)
            # else:
            #     insert_data = {'lottery': self.lottery_name, 'data_type': self.data_type,
            #                    'expert_id': self.expert_id, 'url': self.url}
            #
            #     w_db = SLD()  # 此处保存的是某位专家的哪篇文章数据没有爬取
            #     w_db.save_data(self.articles_miss_urls_db, insert_data)

            if data:
                self.parse_data(data, times)
            elif times < 3:
                self.get_predict_data(times)
            else:
                print('本次gg, url: ', self.url)

    def parse_data(self, data, times):
        ba_data = bs(data, 'lxml')
        title = ''
        try:
            title = ba_data.find_all('title')[0].text
            print(self.url, title)
        except Exception:
            self.get_predict_data(times)

        if '色球' in title:
            self.ssq_parse(ba_data, title.split('色球'))

        if '乐透' in title:
            self.dlt_parse(ba_data, title.split('乐透'))

    def run(self):
        self.get_predict_data()
