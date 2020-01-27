from settings import miss_urls_db, saved_db, lotteries_predict_data_db as lpdb, PER_EXPERT_ARTICLES_LIST_MAX_PAGE, \
    EXPERT_URL, DATA_TYPE
from tools.logger import Logger
logger = Logger(__name__).logger


class CheckArticlesList(object):

    def __init__(self, lottery_name, now_stage):
        self.lottery_name = lottery_name
        self.now_stage = now_stage
        self.articles_list_miss_urls_db = miss_urls_db['articles_list']
        self.the_next_stage_saved_predict_urls = saved_db['the_next_stage_saved_predict_urls']
        self.saved_predict_urls = saved_db['saved_articles_list_urls']
        self.expert_db = lpdb['all_experts']
        self.experts_list = None
        self.lottery_id_dict = {'双色球': 1, '大乐透': 4}
        self.url = EXPERT_URL

    def get_all_experts(self, data_type):
        experts_dicts = self.expert_db.find({'stage': self.now_stage, 'data_type': data_type},
                                                {'_id': 0, 'expert_name': 0, 'lottery': 0})
        self.experts_list = [data['expert_id'] for data in experts_dicts]

    def check_articles_list(self, data_type):
        for page in range(1, PER_EXPERT_ARTICLES_LIST_MAX_PAGE + 1):
            for expert_id in self.experts_list:
                found_data_1 = None
                found_data_2 = None
                params = {
                    'action': 'expertartlist',
                    'page': page,
                    'lotteryid': self.lottery_id_dict[self.lottery_name],
                    'articletype': 1,
                    'id': expert_id
                }

                data = {'lottery': self.lottery_name, 'data_type': data_type,
                        'url': self.url, 'params': params, 'expert_id': expert_id}

                try:
                    found_data_1 = self.the_next_stage_saved_predict_urls.find_one(data)
                except Exception as e:
                    logger.error(e)

                try:
                    found_data_2 = self.the_next_stage_saved_predict_urls.find_one(data)
                except Exception as e:
                    logger.error(e)

                if not (found_data_1 or found_data_2):
                    self.articles_list_miss_urls_db.insert_one(data)

    def start_check(self):
        for data_type in DATA_TYPE:
            self.get_all_experts(data_type)
            self.check_articles_list(data_type)