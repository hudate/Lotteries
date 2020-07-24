import os
import sys
from threading import Thread

import requests
from settings import LOTTERY_DICT, REAL
from settings import lotteries_predict_data_db as lpdb
from settings import EXPERT_URL as EU
from dataP.get_now_stage_expert_predict_data_with_browser import GetNowStagePredictData as GNSPD_WB
from dataP.get_now_stage_expert_predict_data_without_browser import GetNowStagePredictData as GNSPD_WOB

# TODO 不使用浏览器去获取预测数据
from tools.ua import ua
from tools.logger import Logger
logger = Logger(__name__).logger


class GetNowStagePredictUrl(object):

    def __init__(self, lottery, expert_list, stage, data_type, data_file):
        self.expert_list = expert_list
        self.lottery = lottery
        self.predict_db = lpdb[lottery]
        self.data_type = data_type
        self.kill_db = lpdb[lottery + '_kill']
        self.url = None
        self.now_stage = stage
        self.data_file = data_file
        if lottery == 'ssq':
            self.lottery_id = 1

        if lottery == 'dlt':
            self.lottery_id = 4

    def get_data_from_db(self, expert_id):
        if self.data_type < 2:
            db = self.kill_db
        else:
            db = self.predict_db

        find_data = {'data_type': self.data_type, 'expert_id': expert_id, 'stage': self.now_stage}
        filter_data = {'_id': 0, 'balls': 1}
        found_data = []

        try:
            found_data = db.find_one(find_data, filter_data)
        except Exception as e:
            logger.error(e)
        return found_data

    def save_balls(self, balls, expert_id):
        data = {
            'expert_id': expert_id,
            'balls': balls,
        }

        with open(self.data_file, 'a', encoding='utf-8') as f:
            f.write(str(data) + '\n')

    def parse_url(self, data, expert_id):
        # href_data = []
        # stage_data = []
        stage_index = ''
        urls = []
        url = ''

        href_data = data.split(r'<a href=\"')[1:-2]
        stage_data = data.split('ul>')[1].split(r'期彩币推荐</a>')[:-1]

        if href_data:
            urls = [href.split(r'\" target=\"_blank\"')[0] for href in href_data]
            stages = [stage[-3:] for stage in stage_data]
            print(self.now_stage)
            # TODO 此处会报错，原因是每次的预测验证期数不一定在专家的预测list网页中
            stage_index = stages.index(self.now_stage[-3:])

        if urls:
            url = urls[stage_index] if urls[stage_index].startswith('https://www.cjcp.com.cn/') else 'https://www.cjcp.com.cn/' + urls[stage_index]

        if url:
            if REAL:
                # todo 获取cookies
                gpd = GNSPD_WB(self.lottery, url, expert_id, self.data_type, self.data_file)
                gpd.run()
            else:
                gpd = GNSPD_WOB(self.lottery, url, expert_id, self.data_type, self.data_file)
                gpd.run()

    def get_money_url(self, expert_id):
        header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn'}
        params = {
            'action': 'expertartlist',
            'page': 1,
            'lotteryid': self.lottery_id,
            'articletype': 1,
            'id': expert_id
        }

        req = requests.get(url=EU, params=params, headers=header, timeout=(10, 10))
        self.parse_url(req.text, expert_id)

    def run(self):
        for expert_id in self.expert_list:
            balls = self.get_data_from_db(expert_id)
            if not balls:
                self.get_money_url(expert_id)
            else:
                self.save_balls(balls, expert_id)


if __name__ == '__main__':
    expert_list = ['273281']
    gnspu = GetNowStagePredictUrl('ssq', expert_list, '2020007', 0, './123.txt')
    gnspu.run()
