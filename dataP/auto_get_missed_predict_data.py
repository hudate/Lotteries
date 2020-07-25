import sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../..')
import os
import time
from multiprocessing.dummy import Pool
from dataP.auto_get_predict_data import GetPredictData as GPD
from settings import miss_urls_db, saved_db
from tools.logger import Logger

logger = Logger(__name__).logger


class GetMissedPredictData(object):

    def __init__(self, total_times, pause_delta_time, every_times_count=100):
        self.total_times = total_times
        self.pause_delta_time = pause_delta_time
        self.every_times_count = every_times_count
        self.articles_miss_urls_db = miss_urls_db['predict_urls']
        self.save_predict_data_db = saved_db['saved_predict_urls']

    def get_urls(self):
        return self.articles_miss_urls_db.find(
            {},
            {'url': 1, '_id': 0, 'data_type': 1, 'expert_id': 1, 'lottery': 1}
        ).limit(self.every_times_count)

    def run(self):
        for i in range(self.total_times):
            start_time = time.time()
            start_count = self.articles_miss_urls_db.count_documents({})
            urls_info = list(self.get_urls())
            processes = 6 if os.cpu_count() < 6 else os.cpu_count()
            p = Pool(processes=processes)
            if urls_info:
                for url_info in urls_info:
                    gpd = GPD()
                    gpd.set(url_info['lottery'], url_info['expert_id'], url_info['data_type'], url_info['url'])
                    p.apply_async(gpd.run)
                p.close()
                p.join()
            end_time = time.time()
            end_count = self.articles_miss_urls_db.count_documents({})
            record_str = 'totla_times: %s, now_times: %s, start_time: %s, end_time: %s, cost_time: %04.2f, ' \
                         'pause_delta_time: %s, every_times_count: %s, start_count: %s, end_count: %s, ' \
                         'real_get_count: %s, urls_info_length: %s, processes: %s' % \
                         (self.total_times, (i + 1), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time)),
                          time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)), (end_time - start_time),
                          self.pause_delta_time, self.every_times_count, start_count, end_count,
                          (start_count - end_count), len(urls_info), processes)
            logger.info(record_str)

            if end_count == 0:
                logger.info('所有的数据已经爬取完成，退出爬取任务！')
                break
            time.sleep(self.pause_delta_time)


if __name__ == '__main__':
    every_times_count = 100
    pause_delta_time = 90
    t1 = time.time()
    today_start_time = time.mktime(time.strptime(time.strftime('%Y-%m-%d'), '%Y-%m-%d'))
    today_surplus_time = 24 * 3600 - (time.time() - today_start_time)
    total_times = int(today_surplus_time /(1.5 * pause_delta_time))
    gmpd = GetMissedPredictData(total_times, pause_delta_time)
    gmpd.run()
    t2 = time.time()
    print('cost time:', t2 - t1)
