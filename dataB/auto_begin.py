import time
from dataB.read_options import ro
from dataB.get_lotteries_data import GetBeforeLotteryData as GBLD
from multiprocessing import Pool

from tools.logger import Logger
logger = Logger(__name__).logger


class Begin(object):

    def __init__(self, lottery):
        self.stage_count = ''
        self.options = None
        self.lottery = lottery
        self.lottery_url = None
        if lottery == 'ssq' or self.lottery == '双色球':
            self.lottery_name = '双色球'
        if lottery == 'dlt' or self.lottery == '大乐透':
            self.lottery_name = '大乐透'

    def get_options(self, stage_count=0):
        self.options = ro()
        # 获取过去stage_count期的开奖数据
        self.stage_count = stage_count if stage_count != 0 else self.options['stage_count']
        self.lottery_url = self.options['options'][self.lottery]['url']

    def start_get_before_data(self):
        logger.info('获取"%s"往期开奖数据。' % self.lottery_name)
        params = {
            'expect': self.stage_count
        }

        gbld = GBLD()
        gbld.set(self.lottery, self.lottery_url, params)
        gbld.setDaemon(True)
        gbld.start()
        gbld.join()

    def begin(self):
        self.get_options()
        self.start_get_before_data()


if __name__ == '__main__':
    lottery = 'ssq'
    bg = Begin(lottery)
    bg.begin()
