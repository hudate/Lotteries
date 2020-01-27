# -*- coding: utf-8 -*-
import threading

import requests
from lxml import etree
from bs4 import BeautifulSoup as bs
from tools.save_data import SaveLotteriesData as SLD
from settings import lotteries_data_db as ldb
from settings import LOTTERY_DICT


class GetBeforeLotteryData(threading.Thread):

    def __init__(self):
        super(GetBeforeLotteryData, self).__init__()
        self.lottery_name = None
        self.url = None
        self.data_table = None
        self.params = None
        self.db = None

    def set(self, lottery_name, url, params):
        self.lottery_name = lottery_name
        self.url = url
        self.params = params
        self.db = ldb[LOTTERY_DICT[lottery_name]] if lottery_name in LOTTERY_DICT else ldb[lottery_name]

    def get_lottery_data(self):
        req = requests.get(self.url, params=self.params)
        data = req.text
        return data

    def ssq_parse_data(self, data):
        trs = data.find_all('table')[1].find_all('tr', attrs={'class': ''})[1:-13]

        for tr in trs:
            stage = ''
            rad_ball = []
            blue_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                        if td['class'][0] == 'chartBall02':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            blue_ball.append(ball)
                    except:
                        pass

            data = {
                'stage': stage,
                'redBall': rad_ball,
                'blueBall': blue_ball
            }

            self.data_table.save_data(self.db, data)

    def qlc_parse_data(self, data):
        trs = data.find_all('table')[1].find_all('tr', attrs={'class': ''})[2:-10]

        for tr in trs:
            stage = ''
            rad_ball = []
            special_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                        if td['class'][0] == 'specialball':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            special_ball.append(ball)
                    except:
                        pass

            data = {
                'stage': stage,
                'redBall': rad_ball,
                'specialBall': special_ball
            }

            self.data_table.save_data(self.db, data)

    def fc3d_parse_data(self, data):
        trs = data.find_all('table')[1].find_all('tr', attrs={'class': ''})[2:-14]

        for tr in trs:
            stage = ''
            rad_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                        if len(rad_ball) == 3:
                            break
                    except:
                        pass

            data = {
                'stage': stage,
                'ball': rad_ball,
            }

            self.data_table.save_data(self.db, data)

    def dlt_parse_data(self, data):
        trs = data.find_all('table')[2].find_all('tr')[2:-14]
        for tr in trs:
            stage = ''
            rad_ball = []
            blue_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                        if td['class'][0] == 'chartBall02':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            blue_ball.append(ball)
                    except:
                        pass

            data = {
                'stage': stage,
                'redBall': rad_ball,
                'blueBall': blue_ball,
            }

            self.data_table.save_data(self.db, data)

    def qxc_parse_data(self, data):
        trs = data.find_all('table')[1].find_all('tr', attrs={'class': ''})[2:-11]

        for tr in trs:
            stage = ''
            rad_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                    except:
                        pass

            data = {
                'stage': stage,
                'ball': rad_ball,
            }

            self.data_table.save_data(self.db, data)

    def pls_parse_data(self, data):
        trs = data.find_all('table')[1].find_all('tr', attrs={'class': ''})[2:-13]

        for tr in trs:
            stage = ''
            rad_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                        if len(rad_ball) == 3:
                            break
                    except:
                        pass

            data = {
                'stage': stage,
                'ball': rad_ball,
            }

            self.data_table.save_data(self.db, data)

    def plw_parse_data(self, data):
        trs = data.find_all('table')[1].find_all('tr', attrs={'class': ''})[2:-11]

        for tr in trs:
            stage = ''
            rad_ball = []
            try:
                if tr['class'][0] == 'tdbck':
                    continue
            except:
                pass

            for td in tr.find_all('td'):
                try:
                    if td['align'] == 'center':
                        stage = td.text.strip()
                except Exception as e:
                    try:
                        if td['class'][0] == 'chartBall01' or td['class'][0] == 'chartBall03':
                            ball = td.text.strip()
                            ball = '0' + ball if int(ball) < 10 else ball
                            rad_ball.append(ball)
                    except:
                        pass

            data = {
                'stage': stage,
                'ball': rad_ball,
            }

            self.data_table.save_data(self.db, data)

    def parse_data(self, data):
        data = bs(data, 'lxml')
        self.data_table = SLD()

        if self.lottery_name == '双色球' or self.lottery_name == 'ssq':
            self.ssq_parse_data(data)

        if self.lottery_name == '七乐彩' or self.lottery_name == 'qlc':
            self.qlc_parse_data(data)

        if self.lottery_name == '福彩3D' or self.lottery_name == 'fc3d':
            self.fc3d_parse_data(data)

        if self.lottery_name == '大乐透' or self.lottery_name == 'dlt':
            self.dlt_parse_data(data)

        if self.lottery_name == '七星彩' or self.lottery_name == 'qxc':
            self.qxc_parse_data(data)

        if self.lottery_name == '排列3' or self.lottery_name == 'pls':
            self.pls_parse_data(data)

        if self.lottery_name == '排列5' or self.lottery_name == 'plw':
            self.plw_parse_data(data)

    def run(self):
        data = self.get_lottery_data()
        self.parse_data(data)
