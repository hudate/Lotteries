from threading import Thread
from settings import lotteries_data_db as ldb
from settings import lotteries_predict_data_db as lpdb
from tools.save_data import SaveLotteriesData as SLD
from tools.logger import Logger
logger = Logger(__name__).logger


class AnalysePredictData(Thread):

    def __init__(self):
        super(AnalysePredictData, self).__init__()
        self.lottery_name = None
        self.lottery_db = None
        self.predict_db = None
        self.stage = None
        self.analyse_func = None
        self.ball_dict = {}
        self.choice_expert = None
        self.right_ratio_db = None
        self.right_location_db = None

    def set(self, lottery_name, stage):
        self.stage = stage
        self.lottery_name = lottery_name
        if self.lottery_name == '双色球':
            self.lottery_db = ldb['ssq']
            self.predict_db = lpdb['ssq']
            self.right_ratio_db = lpdb['ssq_right_ratio']
            self.right_location_db = lpdb['ssq_right_location']
            self.analyse_func = self.analyse_ssq

        if self.lottery_name == '大乐透':
            self.lottery_db = ldb['dlt']
            self.predict_db = lpdb['dlt']
            self.right_ratio_db = lpdb['dlt_right_ratio']
            self.right_location_db = lpdb['dlt_right_location']
            self.analyse_func = self.analyse_dlt

    def analyse_ssq(self):
        rad_keys = [str(i) if i > 9 else '0' + str(i) for i in range(1, 34)]
        rad_values = [0 for i in range(1, 34)]
        blue_keys = [str(i) if i > 9 else '0' + str(i) for i in range(1, 37)]
        blue_values = [0 for i in range(1, 17)]
        rad_dict = dict(zip(rad_keys, rad_values))
        blue_dict = dict(zip(blue_keys, blue_values))
        find_data = {'stage': self.stage[2:]}
        filter_data = {'_id': 0}
        lottery_data = self.lottery_db.find_one(find_data, filter_data)  # 开奖数据
        lottery_rad_balls = lottery_data['redBall']
        lottery_blue_balls = lottery_data['blueBall']
        find_data = {'stage': self.stage}
        experts_predict_data = self.predict_db.find(find_data, filter_data)  # 本期的预测数据

        for predict_data in experts_predict_data:
            predict_rad_balls = predict_data['redBall']
            predict_blue_balls = predict_data['blueBall']
            for ball in predict_rad_balls:
                rad_dict[ball] = rad_dict[ball] + 1

            for ball in predict_blue_balls:
                # TODO -> 胡少博 修正从网站拿到的的预测数据，因为有些专家的预测数据少一行，导致拿到的“后区定六码”数据有问题
                try:
                    blue_dict[ball] = blue_dict[ball] + 1
                except Exception as e:
                    logger.error(e)
                    logger.error(predict_blue_balls)
                    break

        sorted_rad_balls = sorted(rad_dict.items(), key=lambda x: x[1], reverse=True)
        sorted_blue_balls = sorted(blue_dict.items(), key=lambda x: x[1], reverse=True)
        now_stage_predict_data = [sorted_rad_balls, sorted_blue_balls]
        now_stage_lottery_data = [lottery_rad_balls, lottery_blue_balls]

        # TODO -> 胡少博 实现前N个球的正确率，在right_ratio.py中


    def analyse_dlt(self):
        rad_keys = [str(i) if i > 9 else '0' + str(i) for i in range(1, 36)]
        rad_values = [0 for i in range(1, 36)]
        blue_keys = [str(i) if i > 9 else '0' + str(i) for i in range(1, 13)]
        blue_values = [0 for i in range(1, 13)]
        rad_dict = dict(zip(rad_keys, rad_values))
        blue_dict = dict(zip(blue_keys, blue_values))
        # print(self.stage, type(self.stage), int(self.stage[2:]))

        find_data = {'stage': self.stage[2:]}
        filter_data = {'_id': 0}
        lottery_data = self.lottery_db.find_one(find_data, filter_data)     # 开奖数据
        lottery_rad_balls = lottery_data['redBall']
        lottery_blue_balls = lottery_data['blueBall']
        find_data = {'stage': self.stage}
        experts_predict_data = self.predict_db.find(find_data, filter_data)     # 本期的预测数据

        for predict_data in experts_predict_data:
            predict_rad_balls = predict_data['redBall']
            predict_blue_balls = predict_data['blueBall']
            for ball in predict_rad_balls:
                rad_dict[ball] = rad_dict[ball] + 1

            for ball in predict_blue_balls:
                try:
                    blue_dict[ball] = blue_dict[ball] + 1
                except Exception as e:
                    print(predict_blue_balls)
                    print(self.stage, predict_data)
                    break

        sorted_rad_balls = sorted(rad_dict.items(), key=lambda x: x[1], reverse=True)
        sorted_blue_balls = sorted(blue_dict.items(), key=lambda x: x[1], reverse=True)
        now_stage_predict_data = [sorted_rad_balls, sorted_blue_balls]
        now_stage_lottery_data = [lottery_rad_balls, lottery_blue_balls]

        # TODO -> 胡少博 实现前N个球的正确率，在right_ratio.py中
        rr = RR()
        rr.set(self.lottery_name, 9)
        rr.show_right_ratio(now_stage_predict_data, now_stage_lottery_data)

    def analyse_data(self, data):
        if self.lottery_name == '双色球':
            self.lottery_db = ldb['ssq']
            self.analyse_func = self.analyse_ssq

        if self.lottery_name == '大乐透':
            self.lottery_db = ldb['dlt']
            self.analyse_func = self.analyse_dlt

    def get_data_from_mongo(self):
        find_data = {'stage': self.stage, 'lottery': self.lottery_name}
        filter_data = {'_id': 0}
        found_data = self.predict_db.find(find_data, filter_data)
        for data in found_data:
            print(data)
            self.analyse_func()
        #     # TODO @HuShaobo 统计分析每期的专家数据

    def compute_right_ratio(self, precit_data, lottery_data):
        right_balls = []
        right_location = []
        for ball in precit_data:
            if ball in lottery_data:
                right_balls.append(ball)
                right_location.append(1)
            else:
                right_location.append(0)
        return (len(right_balls) / len(lottery_data)) * 10000, right_balls, right_location

    def ssq_dlt_compute(self):
        find_data = {'stage': self.stage[2:]}
        filter_data = {'_id': 0}
        lottery_data = self.lottery_db.find_one(find_data, filter_data)  # 开奖数据
        lottery_red = lottery_data['redBall']
        lottery_blue = lottery_data['blueBall']
        l_data = [lottery_red, lottery_blue]

        find_data = {'stage': self.stage}
        experts_predict_data = self.predict_db.find(find_data, filter_data)  # 本期的预测数据
        predict_red = experts_predict_data['redBall']
        predict_blue = experts_predict_data['blueBall']
        predict_data = [predict_red, predict_blue]

        expert_id = experts_predict_data['expert_id']
        expert_name = experts_predict_data['expert']

        for p_data in predict_data:
            right_ratio_data = {
                'stage': self.stage,
                'expert_id': expert_id,
                'expert_name': expert_name,
                'red_right_ratio': [],
                'blue_right_ratio': []
            }

            right_location_data = {
                'stage': self.stage,
                'expert_id': expert_id,
                'expert_name': expert_name,
                'red_right_location': [],
                'blue_right_location': [],
                'red_right_balls': [],
                'blue_right_balls': []
            }

            for i in range(len(p_data)):
                right_ratio, right_balls, right_location = self.compute_right_ratio(p_data[i], l_data[i])
                if i == 0:
                    right_ratio_data['red_right_ratio'] = right_ratio
                    right_location_data['red_right_location'] = right_location
                    right_location_data['red_right_balls'] = right_balls
                else:
                    right_ratio_data['blue_right_ratio'] = right_ratio
                    right_location_data['blue_right_location'] = right_location
                    right_location_data['blue_right_balls'] = right_balls

            sld = SLD()
            sld.save_data(self.right_ratio_db, right_ratio_data)
            sld.save_data(self.right_location_db, right_location_data)

    def run(self):
        self.analyse_func()


if __name__ == '__main__':
    apd = AnalysePredictData()
    apd.set('大乐透', 19120)
    apd.run()
