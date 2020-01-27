import threading
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from bs4 import BeautifulSoup as bs
from settings import lotteries_predict_data_db as lpdb, miss_urls_db, LOTTERY_DICT, saved_db
from tools.save_data import SaveLotteriesData as SLD
from tools.ua import ua
from tools.set_proxies import SetProxies as SP
from tools.logger import Logger
logger = Logger(__name__).logger


class GetPredictData(threading.Thread):

    def __init__(self):
        super(GetPredictData, self).__init__()

        self.url = None
        self.parse_func = None
        self.lottery_name = None
        self.expert_id = None
        self.predict_ball_db = None
        self.kill_ball_db = None
        self.db = None
        self.data_type = None
        self.save_predict_data_db = None
        self.articles_miss_urls_db = miss_urls_db['predict_urls']

    def save_url(self, save_class):
        # TODO 重点查看
        # 保存url到数据库中
        db = saved_db['saved_predict_urls']
        find_data = {'url': self.url, 'data_type': self.data_type}
        found_data = self.articles_miss_urls_db.find_one(find_data, {'_id': 0})
        if found_data:
            try:
                save_class.save_data(db, found_data)
                self.articles_miss_urls_db.delete_one(found_data)
            except Exception as e:
                logger.error(e)

    def save_balls(self, expert_name, stage, show_time, balls):
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
        sld.save_data(self.db, data)
        self.save_url(sld)

    def ssq_parse(self, data, times):
        balls = []
        title = []
        try:
            title = data.find_all('title')[0].text.split('福彩双色球')
        except:
            self.get_data(times)

        if title:
            expert_name = title[0]
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

            if balls:
                self.save_balls(expert_name, stage, show_time, balls)

    def dlt_parse(self, data, times):
        balls = []
        title = []
        try:
            title = data.find_all('title')[0].text
        except Exception as e:
            self.get_data(times)

        if '体彩大乐透' in title:
            title = title.split('体彩大乐透')
            expert_name = title[0]
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

            if balls:
                self.save_balls(expert_name, stage, show_time, balls)
        else:
            self.get_data(times)

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

    def get_data(self, times=0):
        found_data = None
        find_data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                     'url': self.url, 'expert_id': self.expert_id}
        try:
            found_data = list(self.save_predict_data_db.find(find_data))
        except:
            pass

        data = None

        header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn'}
        if times < 4:
            times += 1
            if times == 1:
                req = requests.get(self.url, headers=header, timeout=(5, 5))
                data = req.text
            else:

                sp = SP()
                proxy = sp.set_proxies()
                try:
                    req = requests.get(self.url, headers=header, proxies=proxy, timeout=(30, 30),
                                       verify=False)
                    data = req.text
                except:
                    self.get_data(times)
        else:
            insert_data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                           'expert_id': self.expert_id, 'url': self.url}

            w_db = SLD()  # 此处保存的是某位专家的哪篇文章数据没有爬取
            w_db.save_data(self.articles_miss_urls_db, insert_data)

        if data:
            self.parse_data(data, times)

    def parse_data(self, data, times):
        data = bs(data, 'lxml')
        self.parse_func(data, times)

    def run(self):
        self.get_data()
