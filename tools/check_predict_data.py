# 检查对了几个
from tools.logger import Logger
logger = Logger(__name__).logger


class CheckPredictData(object):

    def __init__(self):
        self.short_name = None
        self.rbBall = None
        self.db = None
        self.experts_list = None
        self.area = None
        self.stage = None

    def set(self, lottery, stage, db, expert_list, data_type):
        self.short_name = lottery
        self.db = db
        self.experts_list = expert_list
        self.data_type = data_type
        self.stage = stage

    def get_predict_dict(self, data, predict_dict):
        predict_data = data['balls']
        if predict_data:
            if isinstance(predict_data[0], list):
                predict_data = predict_data[0]
            for ball in predict_data:
                if ball in predict_dict:
                    predict_dict[ball] = predict_dict[ball] + 1
                else:
                    predict_dict[ball] = 1
        # print(predict_dict)
        return predict_dict

    def start_check(self):
        predict_dict = {}
        for expert_id in self.experts_list:
            find_dict = {
                'stage': '20' + self.stage,
                'expert_id': expert_id,
                'data_type': self.data_type
            }

            try:
                found_data = self.db.find_one(find_dict, {'_id': 0})
            except Exception as e:
                raise e

            if found_data:
                predict_dict = self.get_predict_dict(found_data, predict_dict)
            else:
                # TODO 记录下experid_id和stage,需要去网页获取该数据, 并且把获取的数据返回，但如果该专家没有本期数据，那该如何处理？
                logger.error('没有专家%s的%s期数据！' % (expert_id, self.stage))

        if predict_dict:
            return predict_dict

    def run(self):
        pass
