import requests
from bs4 import BeautifulSoup as bs
from tools.save_data import SaveLotteriesData as SLD
from tools.ua import ua
from tools.set_proxies import SetProxies as SP
from tools.logger import Logger
logger = Logger(__name__).logger


class GetNowStagePredictData(object):

    def __init__(self, lottery, url, expert_id, data_type, data_file):
        self.url = url
        self.parse_func = None
        self.lottery = lottery
        self.expert_id = expert_id
        self.data_type = data_type
        self.data_file = data_file
        if lottery == 'ssq':
            self.parse_func = self.ssq_parse

        if lottery == 'dlt':
            self.parse_func = self.dlt_parse

    def save_balls(self, balls):
        data = {
            'expert_id': self.expert_id,
            'balls': balls,
        }

        with open(self.data_file, 'a', encoding='utf-8') as f:
            f.write(str(data) + '\n')

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
                self.save_balls(balls)

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
                self.save_balls(balls)
        else:
            self.get_data(times)

    def get_data(self, times=0):
        data = None

        header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn'}
        if times < 10:
            if times == 0:
                times += 1
                req = requests.get(self.url, headers=header, timeout=(30, 30))
                data = req.text
            else:
                times += 1
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
