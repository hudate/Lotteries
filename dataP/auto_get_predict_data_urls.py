import json
import time
import requests
from settings import lotteries_predict_data_db as lpdb, STAGE_COUNT, avoid_experts_db, PER_EXPERT_ARTICLES_LIST_MAX_PAGE
from settings import EXPERT_URL
from tools.common import get_the_next_stage
from tools.save_data import SaveLotteriesData as SLD
from tools.ua import ua
from settings import saved_db
from settings import LOTTERY_DICT, miss_urls_db
from tools.set_proxies import SetProxies as SP
from tools.logger import Logger
logger = Logger(__name__).logger


class GetExpertsUrls(object):

    def __init__(self, lottery_name, expert_id, data_type, has_missed_list_urls=0):
        # super(GetExpertsUrls, self).__init__()
        self.lottery_name = lottery_name
        self.expert_id = expert_id
        self.data_type = data_type
        self.max_page = PER_EXPERT_ARTICLES_LIST_MAX_PAGE       # 获取文章列表时，page取范围
        self.url = EXPERT_URL

        self.page = None
        self.params = None
        self.lottery_id = None

        self.urls_db = lpdb[LOTTERY_DICT[self.lottery_name] + '_articles_list']     #
        self.articles_list_miss_urls_db = miss_urls_db['articles_list']         # 保存丢失的
        self.save_urls_db = miss_urls_db['predict_urls']        # 保存获取到专家每期预测的urls
        self.save_articles_list_urls_db = saved_db['saved_articles_list_urls']      # 保存已经成功获取过文章列表的params
        self.has_missed_list_urls = has_missed_list_urls        # 判断本次是不是第一次爬取专家的列表，
        self.expert_db = lpdb[LOTTERY_DICT[self.lottery_name] + '_experts']
        self.all_expert_db = lpdb['all_experts']
        self.avoid_experts_db = avoid_experts_db
        self.the_next_stage_saved_articles_list_url = saved_db['the_next_stage_saved_predict_urls']

    def set_lottery_id(self):
        if self.lottery_name == '双色球':
            self.lottery_id = 1

        if self.lottery_name == '大乐透':
            self.lottery_id = 4

    def __set_cookies(self):
        cookies = {}
        cookies['XcQszWaqeglybiaos'] = "999"
        cookies['XcQszWaqeglyurl'] = str(int(time.time()))
        cookies['XcQszWaqegurllaiyuan'] = str(int(time.time()))
        cookies['Hm_lvt_78803024be030ae6c48f7d9d0f3b6f03'] = "https://www.cjcp.com.cn/minsort_ssq_mf.php?id=%s" \
                                                             % self.expert_id
        cookies['Hm_lpvt_78803024be030ae6c48f7d9d0f3b6f03'] = "https://www.cjcp.com.cn"
        return cookies

    def get_urls_data(self, times=0):
        data = None
        header = {'User-Agent': ua(), 'Host': 'www.cjcp.com.cn'}
        cookies = self.__set_cookies()
        found_data = None
        find_data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                     'url': self.url, 'params': self.params, 'expert_id': self.expert_id}
        logger.info(find_data)
        try:
            found_data = self.save_articles_list_urls_db.find_one(find_data, {'_id': 0})
        except Exception as e:
            logger.error(e)

        if not found_data:
            try:
                found_data = list(self.the_next_stage_saved_articles_list_url.find(find_data, {'_id': 0}))
            except Exception as e:
                logger.error(e)

        logger.info(found_data)

        if not found_data:
            if times < 4:
                times += 1
                if times == 1:
                    req = requests.get(self.url, headers=header, params=self.params, timeout=(30, 30), cookies=cookies)
                    data = req.text
                    self.parse_data(data, times)
                else:
                    sp = SP()
                    proxy = sp.set_proxies()
                    try:
                        req = requests.get(self.url, headers=header, params=self.params, proxies=proxy, timeout=(30, 30),
                                           verify=False)
                        data = req.text
                        self.parse_data(data, times)
                    except:
                        self.get_urls_data(times)
            else:
                insert_data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                               'url': self.url, 'params': self.params, 'expert_id': self.expert_id}

                # 此处保存的是某位专家的第几页文章列表数据没有爬取
                save_someone_somepage_flag = 1

                if self.the_next_stage_saved_articles_list_url.find_one(insert_data):
                    save_someone_somepage_flag = 0

                if self.save_articles_list_urls_db.find_one(insert_data):
                    save_someone_somepage_flag = 0

                if save_someone_somepage_flag:
                    w_db = SLD()
                    w_db.save_data(self.articles_list_miss_urls_db, insert_data)
        else:
            found_data = found_data[0]
            self.articles_list_miss_urls_db.delete_many(found_data)
            self.articles_list_miss_urls_db.delete_many(found_data)

    def handle_stages(self, stages):
        new_stages = []
        change_year_index = len(stages) + 1
        if "001" in stages:
            change_year_index = stages.index('001')

        for index in range(len(stages)):
            year = time.strftime('%Y')
            if index > change_year_index:
                year = str(int(year) - 1)
            new_stages.append(year + stages[index])
        new_stages.sort()
        return new_stages

    def parse_data(self, data, times):
        # TODO 这里会出错，需要看一下怎么回事。
        total_articles_count = 1000000
        try:
            data = json.loads(data[1:-1])
            if '条文章' in data['content']:
                total_articles_count = int(data['content'].split('条文章')[0][-10:].split('共')[1])
            else:
                total_articles_count = 0
        except:
            self.get_urls_data(times)

        # 当专家的总的文章数量少于排名的期数时，把该专家从专家表中删除，并且写入文件中，下次获取时，不在获取该专家的数据
        logger.debug(total_articles_count, STAGE_COUNT)

        # 取消在此处对于专家预测文章数量的检查，而将此检查移至分析数据时从数据库获取专家，依据此判断取出专家
        # if total_articles_count < STAGE_COUNT:
        #     find_dict = {'expert_id': self.expert_id, 'stage': get_the_next_stage(LOTTERY_DICT[self.lottery_name]),
        #                  'data_type': self.data_type, 'lottery': self.lottery_name}
        #     found_data = self.expert_db.find_one(find_dict, {'_id': 0})
        #     self.articles_list_miss_urls_db.delete_many({'expert_id': self.expert_id})
        #
        #     if found_data:
        #         self.avoid_experts_db.insert_one(found_data)
        #         found_data.pop('_id')
        #         self.expert_db.delete_one(found_data)
        #         self.all_expert_db.delete_one(found_data)
        # else:

        if total_articles_count:
            href_data = list()
            stage_data = list()
            try:
                href_data = data['content'].split(r'<a href="')[1:-2]
                stage_data = data['content'].split('ul>')[1].split(r'期彩币推荐')[:-1]
            except:
                self.get_urls_data(times)

            if href_data:
                urls = [data.split(r'" target="_blank"')[0] for data in href_data]
                stages_list = [data[-3:] for data in stage_data]
                stages = self.handle_stages(stages_list)

                if not urls:
                    self.get_urls_data(times)

                for stage in stages_list:
                    if stage not in stages:
                        stages.append(stage)

                if self.page == 1:
                    urls = urls[1:]

                sld = SLD()

                all_experts_db = lpdb["all_experts"]
                all_experts_db.update_one({'lottery': self.lottery_name, 'data_type': self.data_type,
                                       'expert_id': self.expert_id, 'stage': get_the_next_stage(LOTTERY_DICT[self.lottery_name])},
                                      {'$set': {'articles_count': total_articles_count}})

                for index in range(len(urls)):
                    url = urls[index]
                    stage = stages[index]
                    url = url if url.startswith('https://www.cjcp.com.cn/') else 'https://www.cjcp.com.cn/' + url
                    data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                            'expert_id': self.expert_id, 'url': url}

                    # 先查看爬取保存的数据中有没有，如果保存的数据中有，那就不用保存了
                    found_data = None
                    try:
                        found_data = list(saved_db['saved_predict_urls'].find(data))
                    except Exception as e:
                        logger.error(e)

                    if (not found_data) and stage != get_the_next_stage(LOTTERY_DICT[self.lottery_name]):
                        # 把解析到的文章的urls保存到还没有爬取的数据库中
                        sld.save_data(self.save_urls_db, data)

                data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                        'url': self.url, 'params': self.params, 'expert_id': self.expert_id}
                sld.save_data(self.the_next_stage_saved_articles_list_url, data)

                # 把爬取过的articles_list_url的参数保存到saved_articles_list数据库中
                if self.params['page'] > 1:
                    data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                            'url': self.url, 'params': self.params, 'expert_id': self.expert_id}
                    sld.save_data(self.save_articles_list_urls_db, data)

                # 删除missed_articles_list_urls中的对应数据
                data = {'lottery': self.lottery_name, 'data_type': self.data_type,
                        'url': self.url, 'params': self.params, 'expert_id': self.expert_id}

                self.articles_list_miss_urls_db.delete_one(data)

        else:
            self.get_urls_data(times)

    def get_predict_articles_list(self):    # 获取本期的预测专家列表
        self.set_lottery_id()
        for page in range(1, self.max_page + 1):
            self.page = page
            params = {
                'action': 'expertartlist',
                'page': page,
                'lotteryid': self.lottery_id,
                'articletype': 1,
                'id': self.expert_id
            }
            self.params = params
            self.get_urls_data()

    def set_get_missed_articles_list_urls(self, params):
        self.params = params

    def run(self):
        if self.has_missed_list_urls:
            self.get_urls_data()
        else:
            self.get_predict_articles_list()
