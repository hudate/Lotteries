"""
获取专家列表：get_experts
获取每位专家的预测数据：get_per_expert_predict_data
拿出３５个球，进行投票，获取票数最高的前ｎ(dlt:8, ssq:9)和前m(dlt:4, ssq:3)个球
"""
import os

from gevent import monkey

from tools.common import get_the_next_stage

monkey.patch_all()

import time
from multiprocessing.dummy import Pool
from multiprocessing import Process
from dataP.auto_get_experts import GetExperts as GE
from dataP.auto_get_predict_data import GetPredictData as GPD
from dataP.auto_get_predict_data_urls import GetExpertsUrls as GEU
from settings import EXPERT_LIST_URLS, DATA_TYPE, miss_urls_db, EXPERT_COUNT
from settings import lotteries_predict_data_db as lpdb, MAX_EXPERTS_PAGE_COUNT
from tools.logger import Logger
logger = Logger(__name__).logger


class ExpertDataBegin(Process):

    def __init__(self, lottery, pause_delta_time=90, every_times_count=100):
        super(ExpertDataBegin, self).__init__()
        self.lottery = lottery
        self.expert_db = lpdb[lottery + '_experts']
        self.articles_miss_urls_db = miss_urls_db['predict_urls']
        self.articles_list_miss_urls_db = miss_urls_db['articles_list']
        self.miss_experts_db = miss_urls_db['experts']
        self.pause_delta_time = pause_delta_time
        self.every_times_count = every_times_count
        self.flag = 1

        if self.lottery == 'ssq' or self.lottery == '双色球':
            self.lottery_name = '双色球'
            self.lotteries_urls_list = EXPERT_LIST_URLS[4:]

        if self.lottery == 'dlt' or self.lottery == '大乐透':
            self.lottery_name = '大乐透'
            self.lotteries_urls_list = EXPERT_LIST_URLS[:4]

    def begin_get_experts(self):
        p = Pool(processes=os.cpu_count() * 5)
        logger.info('开始获取"%s"预测专家。' % self.lottery_name)
        stage = get_the_next_stage(self.lottery)
        for page in range(1, MAX_EXPERTS_PAGE_COUNT + 1):  # 获取专家的页数
            for dt_type in DATA_TYPE:
                url = self.lotteries_urls_list[dt_type]
                ge = GE(self.lottery_name, stage, url, dt_type, page)
                p.apply_async(ge.run)
        p.close()
        p.join()
        print('获取"%s"预测专家完毕。' % self.lottery_name)

    def begin_get_predict_urls(self, flag=0):
        # logger.info('开始获取"%s"专家预测数据的URLS。' % self.lottery_name)
        times = 0
        if flag:
            while 1:
                found_data = None
                find_data = {'lottery': self.lottery_name}
                filter_data = {'_id': 0}
                try:
                    found_data = list(self.articles_list_miss_urls_db.find(find_data, filter_data))
                except Exception as e:
                    logger.error(e)

                logger.info('times: %s, found_data_count: %s' % (times, len(list(found_data))))

                if len(found_data) > 0:
                    p = Pool(processes=os.cpu_count() * 5)
                    for expert_data in found_data:
                        expert_id = expert_data['expert_id']
                        data_type = expert_data['data_type']
                        params = expert_data['params']
                        geu = GEU(self.lottery_name, expert_id, data_type, flag)
                        geu.set_get_missed_articles_list_urls(params)
                        p.apply_async(geu.run)
                    p.close()
                    p.join()
                    times += 1

                if (not found_data) or times > 4:
                    break
        else:
            while 1:
                found_data = None
                find_data = {'lottery': self.lottery_name}
                filter_data = {'_id': 0}
                try:
                    found_data = list(self.expert_db.find(find_data, filter_data))
                except Exception as e:
                    logger.error(e)

                logger.info('times: %s, found_data_count: %s' %(times, len(list(found_data))))

                if len(found_data) > 0:
                    p = Pool(processes=os.cpu_count() * 5)
                    for expert_data in found_data:
                        expert_id = expert_data['expert_id']
                        data_type = expert_data['data_type']
                        print(__name__, 'Line: 91, ', expert_id, data_type)
                        geu = GEU(self.lottery_name, expert_id, data_type)
                        p.apply_async(geu.run)
                    p.close()
                    p.join()
                    time.sleep(5)
                else:
                    print('获取"%s"专家预测数据的URLS完毕。' % self.lottery_name)
                    break

                times += 1
                if (not found_data) or times > 4:
                    break

    def begin_get_predict_data(self):
        # logger.info('开始获取"%s"专家预测数据。' % self.lottery_name)
        times = 1
        while times < 5:
            urls_data = None
            find_data = {'lottery': self.lottery_name}
            filter_data = {'_id': 0}
            t3 = time.time()
            start_count = 0
            processes = os.cpu_count()

            try:
                start_count = self.articles_miss_urls_db.count_documents({})
                urls_data = list(self.articles_miss_urls_db.find(find_data, filter_data).limit(self.every_times_count))
            except Exception as e:
                logger.error(e)

            logger.info('db:%s find_data:%s, found_data:%s' % (self.articles_miss_urls_db, find_data, len(list(urls_data))))

            if urls_data:
                p = Pool(processes=processes)
                for url_data in urls_data:
                    expert_id = url_data['expert_id']
                    data_type = url_data['data_type']
                    url = url_data['url']
                    gpd = GPD()
                    gpd.set(self.lottery_name, expert_id, data_type, url)
                    p.apply_async(gpd.run)
                p.close()
                p.join()

            t4 = time.time()
            end_count = self.articles_miss_urls_db.count_documents({})
            record_str = 'start_time: %s, end_time: %s, cost_time: %04.2f, times: %s, pause_delta_time: %s, ' \
                         'every_times_count: %s start_count: %s, end_count: %s, real_get_count: %s urls_info_length: %s' \
                         ' processes: %s' % (
                             time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t3)),
                             time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t4)),
                             (t4 - t3),
                             times,
                             self.pause_delta_time,
                             self.every_times_count,
                             start_count,
                             end_count,
                             (start_count - end_count),
                             len(urls_data),
                             processes
                         )

            logger.info(record_str)
            time.sleep(self.pause_delta_time)
            times += 1

    def is_need_get_experts(self):
        if len(list(self.expert_db.find({}))) >= len(DATA_TYPE) * EXPERT_COUNT:
            return 0
        else:
            return 1

    def is_need_get_predict_urls(self):
        if len(list(self.articles_list_miss_urls_db.find({'lottery': self.lottery_name,
                                                          'stage': get_the_next_stage(self.lottery)}))) > 0:
            return 1
        else:
            return 0

    def is_need_get_predict_data(self):
        if len(list(self.articles_miss_urls_db.find({}))) > 0:
            return 1
        else:
            return 0

    def get_predict_urls(self, flag=0):
        if not flag:
            self.begin_get_predict_urls()

        if self.is_need_get_predict_urls():
            print('is_need_get_predict_urls')
            self.begin_get_predict_urls(1)

    def get_predict_data(self):
        self.begin_get_predict_data()

    def get_experts(self):
        if self.is_need_get_experts():
            self.begin_get_experts()

    def run(self):
        # 获取专家，期间可能会出错(但概率不大，毕竟只有3页)，将其存入数据库（包括url，彩票类型）
        if self.is_need_get_experts():
            self.begin_get_experts()

        # 获取专家，期间某些专家的数据会出错（240个专家，共有720（240*3）次请求），将其出错的请求数据存入数据库（包括url，彩票类型）
        # 也要将成功的数据存入数据库（注意参数从第二页算起，以减少请求）

        if self.is_need_get_predict_urls():
            print('is_need_get_predict_urls')
            self.begin_get_predict_urls(1)

        if self.is_need_get_predict_data():
            self.begin_get_predict_data()


if __name__ == '__main__':
    eb = ExpertDataBegin('dlt')
    # eb.begin_get_predict_urls(1)      # 获取丢失的文章列表
    eb.begin_get_predict_data()
    # eb.run()
