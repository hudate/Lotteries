# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs
from settings import lotteries_predict_data_db as lpdb, EXPERT_COUNT, avoid_experts_db, AVOID_EXPERTS
from tools.save_data import SaveLotteriesData as SLD
from settings import LOTTERY_DICT, miss_urls_db
from tools.ua import ua
from tools.set_proxies import SetProxies as SP
from tools.logger import Logger
logger = Logger(__name__).logger


class GetExperts(object):

    def __init__(self, lottery_name, stage,  url, data_type, expert_page=1, has_missed_urls = 0):
        super(GetExperts, self).__init__()
        self.lottery_name = lottery_name
        self.url = url
        self.data_table = None
        self.params = {
            'page': expert_page
        }
        self.data_type = data_type
        self.miss_url_db = miss_urls_db['experts']
        self.articles_list_miss_urls_db = miss_urls_db['articles_list']
        self.has_missed_urls = has_missed_urls
        self.stage = stage
        self.all_experts_db = lpdb['all_experts']
        avoid_experts = list(avoid_experts_db.find({}, {'_id': 0, 'expert_id': 1}))
        if avoid_experts:
            self.avoid_experts = [expert['expert_id'] for expert in avoid_experts]
        else:
            self.avoid_experts = []

    def get_expert_data(self, times=0):
        data = None
        header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn'}

        if times < 5:
            if times == 0:
                times += 1
                req = requests.get(self.url, headers=header, params=self.params, timeout=(5, 5))
                data = req.text
            else:
                times += 1
                sp = SP()
                proxy = sp.set_proxies()
                try:
                    req = requests.get(self.url, headers=header, params=self.params, proxies=proxy, timeout=(5, 5),
                                       verify=False)
                    data = req.text
                except:
                    self.get_expert_data(times)
        else:
            insert_data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                           'url': self.url, 'params': self.params}
            db = lpdb['predict_urls']
            found_data = None
            try:
                found_data = db.find_one(insert_data)
            except Exception as e:
                raise e

            if found_data is None:
                w_db = SLD()
                w_db.save_data(self.miss_url_db, insert_data)

        if data:
            self.parse_data(data, times)

    def parse_data(self, data, re_times):
        # print('Line 55:', re_times, self.params)
        soup = bs(data, 'lxml')
        table = None
        try:
            table = soup.find_all('table', attrs={'class': 'rank_table'})[0]
        except Exception as e:
            self.get_expert_data(re_times)

        if table:
            trs = table.find_all('tr')[1:]
            for tr in trs:
                try:
                    td_a = tr.find_all('td')[1].find('a')
                    name = td_a.text
                    href = td_a['href']
                    expert_id = href.split('?')[1].split('=')[1]
                    if (expert_id not in self.avoid_experts) and (expert_id not in AVOID_EXPERTS):
                        data = {
                            'lottery': self.lottery_name,
                            'data_type': self.data_type,
                            'expert_name': name,
                            'expert_id': expert_id,
                            'stage': self.stage
                        }

                        db = lpdb[LOTTERY_DICT[self.lottery_name] + '_experts']

                        find_dict = {'data_type': self.data_type, 'lottery': self.lottery_name}
                        if len(list(db.find(find_dict))) < EXPERT_COUNT:
                            w_db = SLD()
                            # 保存专家信息
                            w_db.save_data(db, data)

                            if '_id' in data:
                                data.pop('_id')
                            # 保存专家至总的专家列表中
                            w_db.save_data(self.all_experts_db, data)

                except Exception as e:
                    print(e)

    def run(self):
        self.get_expert_data()
