import os
import random
import time
import urllib3
from gevent import thread
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

    def __init__(self, total_times, pause_delta_time, every_times_count=100):
        self.parse_func = None
        self.total_times = total_times
        self.pause_delta_time = pause_delta_time
        self.every_times_count = every_times_count
        self.articles_miss_urls_db = miss_urls_db['predict_urls']
        self.save_predict_data_db = saved_db['saved_predict_urls']

    def get_urls(self):
        return self.articles_miss_urls_db.find(
            {},
            {'url': 1, '_id': 0, 'data_type': 1, 'expert_id': 1}
        ).limit(self.every_times_count)

    def get_predict_data(self, url, data_type, expert_id, times=0):
        print(url, times)

        found_data = []
        try:
            found_data = list(self.save_predict_data_db.find({'data_type': data_type, 'url': url}, {'_id': 0}))
        except Exception as e:
            logger.error(e)

        if found_data:
            print('found data, count:', len(found_data))
            self.remove_url(url, data_type)
        else:
            print('not found data')

            data = None
            header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn', 'Accept-Encoding': 'gzip'}
            if times < 3:
                times += 1
                if times < 2:
                    try:
                        req = requests.get(url, headers=header, timeout=(10, 15), allow_redirects=True)
                        if req.status_code == 403:
                            self.get_predict_data(url, data_type, expert_id, times)
                        data = req.text
                    except Exception as e:
                        logger.error(e)
                        logger.error(url + ' ' + str(times))
                        self.get_predict_data(url, data_type, times)
                else:
                    sp = SP()
                    proxy = sp.set_proxies()
                    logger.warning(proxy)
                    try:
                        req = requests.get(url, headers=header, proxies=proxy, timeout=(20, 15),
                                           verify=False)
                        if req.status_code == 403:
                            self.get_predict_data(url, data_type, expert_id, times)
                        data = req.text
                    except Exception as e:
                        logger.error(e)
                        logger.error(url + ' ' + str(times))
                        self.get_predict_data(url, data_type, times)
            if data:
                self.parse_data(data, url, data_type, expert_id, times)
            elif times < 3:
                self.get_predict_data(url, data_type, expert_id, times)
            else:
                print('本次gg, url: ', url)

    def parse_data(self, data, url, data_type, expert_id, times):
        # h_url = url.replace('/', '_').replace(':', '+')
        ba_data = bs(data, 'lxml')
        title = None
        try:
            title = ba_data.find_all('title')[0].text
            print(url, title)
        except Exception:
            self.get_predict_data(url, data_type, expert_id, times)

        if '色球' in title:
            title.split('色球')
            self.ssq_parse(ba_data, url, title.split('色球'), data_type, expert_id)

        if '乐透' in title:
            title.split('乐透')
            self.dlt_parse(ba_data, url, title.split('乐透'), data_type, expert_id)

        # try:
        #     title = ba_data.find_all('title')[0].text
        #     logger('%s, %s' % (title, url))
        #     if '色球' in title:
        #         title.split('色球')
        #         self.ssq_parse(ba_data, url, title.split('色球'), data_type, expert_id)
        #     elif '乐透' in title:
        #         title.split('乐透')
        #         self.dlt_parse(ba_data, url, title.split('乐透'), data_type, expert_id)
        #     else:
        #         self.get_predict_data(url, data_type, expert_id, times)
        # except Exception as e:
        #     if '<title>' in data:
        #         print(url, title)
        #         # h_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'html_show_err_data', h_url)
        #         # with open(h_file, 'w', encoding='gbk') as f:
        #         #     f.write(data)
        #         logger.error(e)
        #         logger.error('title in html')
        #         # logger.error(ba_data.find_all('title')[0].text)
        #         # if '色球' in title:
        #         #     self.ssq_parse(ba_data, url, title.split('色球'), data_type, expert_id)
        #         # elif '乐透' in title:
        #         #     self.dlt_parse(ba_data, url, title.split('乐透'), data_type, expert_id)
        #     else:
        #         h_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'html_has_err_data', h_url)
        #         with open(h_file, 'w', encoding='utf-8') as f:
        #             f.write(data)
        #         logger.error(e)
        #         logger.error('title not in html')
        # # else:
        # #     logger.error(url + ' ' + str(times))
        # #     self.get_predict_data(url, data_type, expert_id, times)

    def ssq_parse(self, data, url, title, data_type, expert_id):
        print('ssq解析')
        lottery_name = '双色球'
        balls = []
        print(title)

        try:
            expert_name = lpdb['all_experts'].find_one(
                {'expert_id': expert_id},
                {'_id': 0, 'expert_name': 1}
            ).get('expert_name')
        except Exception:
            try:
                expert_name = lpdb['ssq_experts'].find_one(
                    {'expert_id': expert_id},
                    {'_id': 0, 'expert_name': 1}
                ).get('expert_name')
            except Exception:
                expert_name = title[0].split('福彩双')[0]

        stage = title[1].split('期')[0]
        print(title, lottery_name, expert_name, stage, url)
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

        print(lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url)

        if balls:
            self.save_balls(lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url=url)

    def dlt_parse(self, data, url, title, data_type, expert_id):
        print('大乐透解析')
        lottery_name = '大乐透'
        balls = []
        # expert_name = lpdb['all_experts'].find_one({'expert_id': expert_id}, {'_id': 0, 'expert_name': 1})['expert_name']

        try:
            expert_name = lpdb['all_experts'].find_one(
                {'expert_id': expert_id},
                {'_id': 0, 'expert_name': 1}
            ).get('expert_name')
        except Exception:
            try:
                expert_name = lpdb['dlt_experts'].find_one(
                    {'expert_id': expert_id},
                    {'_id': 0, 'expert_name': 1}
                ).get('expert_name')
            except Exception:
                expert_name = title[0].split('体彩大')[0]

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
                return True
            except Exception as e:
                logger.error(e)
        return False

    def remove_url(self, url, data_type):
        find_data = {'url': url, 'data_type': data_type}
        try:
            found_data = list(self.articles_miss_urls_db.find(find_data, {'_id': 1}))
            print()
            for data in found_data:
                # print(find_data)
                # new_data = self.articles_miss_urls_db.find_one(data, {'_id': 0, 'url': 1, 'data_type': 1, 'expert_id': 1, 'expert_name': 1})
                # print(self.articles_miss_urls_db.find_one(data, {'_id': 0, 'url': 1, 'data_type': 1, 'expert_id': 1, 'expert_name': 1}))
                self.articles_miss_urls_db.delete_one(data)
        except Exception as e:
            logger.error(e)

    def save_balls(self, lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url):
        print(lottery_name, expert_name, expert_id, stage, show_time, balls, data_type, url)
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
            thread.sleep(0.2)
            if self.save_url(sld, url, data_type):
                thread.sleep(0.2)
                self.remove_url(url, data_type)

    def run(self):
        pause_time = 0
        for i in range(self.total_times):
            t3 = time.time()
            start_count = self.articles_miss_urls_db.count_documents({})
            logger.info('time: %s, totla_times: %s, times: %s, url count: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'),
                                                                                 self.total_times, (i + 1),
                                                                start_count))
            urls_info = list(self.get_urls())
            processes = 8
            p = Pool(processes=processes)
            if urls_info:
                for url_info in urls_info:
                    # self.get_predict_data(url_info['url'], url_info['data_type'], url_info['expert_id'])
                    p.apply_async(
                        func=self.get_predict_data,
                        args=(url_info['url'], url_info['data_type'], url_info['expert_id'])
                    )
                p.close()
                p.join()
            t4 = time.time()
            end_count = self.articles_miss_urls_db.count_documents({})
            logger.info('time: %s, times: %s, cost time: %s' % (time.strftime('%Y-%m-%d %H:%M:%S'), (i + 1), (t4 - t3)))
            record_str = 'start_time: %s, end_time: %s, cost_time: %04.2f, pause_delta_time: %s, pause_time: %s, ' \
                         'every_times_count: %s start_count: %s, end_count: %s, real_get_count: %s urls_info_length: %s' \
                         ' processes: %s' % (
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t3)),
                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t4)),
                (t4 - t3),
                self.pause_delta_time,
                pause_time,
                self.every_times_count,
                start_count,
                end_count,
                (start_count - end_count),
                len(urls_info),
                processes
            )
            logger.info(record_str)
            with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'record_file.txt'), 'a', encoding='utf-8') as f:
                f.write(record_str + '\n')
            pause_time = (random.randint(self.pause_delta_time - 100, self.pause_delta_time))
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
