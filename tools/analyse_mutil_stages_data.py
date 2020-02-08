import json
import os
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import time

from dataP.get_now_stage_experts_predict_data import GetNowStagePredictUrl
from settings import lotteries_data_db as ldb, DATA_TYPE, REAL, \
    lotteries_predict_data_db as lpdb, LOTTERY_DICT_2, SETUP_FILE
from tools.auto_get_kjxx import GetKJXX

from tools.save_data import SaveLotteriesData as SLD
import numpy as np
from tools.auto_compose_data import ComposePredictData as CSPD  # Compose nowStage Predict Data
from tools.logger import Logger
logger = Logger(__name__).logger


class MutilStagesAnalyseData(object):

    def __init__(self, lottery, now_stage, data_file):
        self.lottery = lottery
        self.stage_list = []
        self.experts_list = []
        self.now_stage = now_stage
        self.stage_count = None
        self.lottery_data_db = ldb[lottery]
        self.predict_data_db = lpdb[lottery]
        self.kill_data_db = lpdb[lottery + '_kill']
        self.right_ratio_db = lpdb[lottery + '_right_ratio']
        self.right_location_db = lpdb[lottery + '_right_location']
        self.expert_db = lpdb['all_experts']
        self.stage_count_list = None
        self.front_predict_expert_count_list = None
        self.front_kill_expert_count_list = None
        self.back_predict_expert_count_list = None
        self.back_kill_expert_count_list = None
        self.front_predict_balls_count_list = None
        self.front_kill_balls_count_list = None
        self.back_predict_balls_count_list = None
        self.back_kill_balls_count_list = None
        self.lottery_name = LOTTERY_DICT_2[lottery]
        self.data_file = data_file
        self.setup_file = SETUP_FILE

    # 获取专家和球数（前预、前杀、后预、后杀）
    def get_experts_balls_count(self):
        with open(self.setup_file) as f:
            content = json.load(f)
        self.stage_count_list = content[self.lottery + '_group']['analyse_stages_count']
        self.front_predict_expert_count_list = content[self.lottery + '_group']['front_predict_expert_count']
        self.front_kill_expert_count_list = content[self.lottery + '_group']['front_kill_expert_count']
        self.back_predict_expert_count_list = content[self.lottery + '_group']['back_predict_expert_count']
        self.back_kill_expert_count_list = content[self.lottery + '_group']['back_kill_expert_count']
        self.front_predict_balls_count_list = content[self.lottery + '_group']['front_predict_balls_count']
        self.front_kill_balls_count_list = content[self.lottery + '_group']['front_kill_balls_count']
        self.back_predict_balls_count_list = content[self.lottery + '_group']['back_predict_balls_count']
        self.back_kill_balls_count_list = content[self.lottery + '_group']['back_kill_balls_count']

    def get_stage_list(self):
        year = int(time.strftime("%Y"))
        last_year = year - 1
        year_list = [str(year)[-2:], str(last_year)[-2:]]
        all_stage = [stage_dict['stage'] for stage_dict in self.lottery_data_db.find({}, {'_id': 0, 'stage': 1})]
        stage_list = [stage for stage in all_stage if stage[:2] in year_list]
        stage_list.sort(reverse=True)
        if self.now_stage[2:] in stage_list:
            start_index = stage_list.index(self.now_stage[2:])
            self.stage_list = stage_list[start_index: start_index + self.stage_count]
        else:
            self.stage_list = stage_list[:self.stage_count]
        logger.info('self.stage_list is: %s' % self.stage_list)

    def compute_right_ratio(self, predict_data, lottery_data, kill=False):
        right_balls = []
        right_location = []
        for ball in predict_data:
            if kill:
                if ball not in lottery_data:
                    right_location.append(0)
                else:
                    right_balls.append(ball)
                    right_location.append(1)
            else:
                if ball in lottery_data:
                    right_balls.append(ball)
                    right_location.append(1)
                else:
                    right_location.append(0)
        return (len(right_balls) / len(lottery_data)), right_balls, right_location

    def analyse_some_stage_data(self, predict_data, lottery_data):
        expert_id = predict_data.pop('expert_id')
        expert_name = predict_data.pop('expert_name')
        stage = predict_data.pop('stage')
        data_type = predict_data.pop('data_type')

        if 'stage' in lottery_data:
            lottery_data.pop('stage')

        predict_data = predict_data['balls']

        if len(predict_data) == 25:
            lottery_data = lottery_data['redBall']
        else:
            lottery_data = lottery_data['blueBall']

        right_ratio, right_balls, right_location = self.compute_right_ratio(predict_data, lottery_data)
        right_ratio_data = {
            'stage': stage,
            'expert_id': expert_id,
            'expert_name': expert_name,
            'data_type': data_type,
            'right_ratio': right_ratio,
        }

        right_location_data = {
            'stage': stage,
            'expert_id': expert_id,
            'expert_name': expert_name,
            'data_type': data_type,
            'right_location': right_location,
            'right_balls': right_balls
        }

        sld = SLD()
        sld.save_data(self.right_ratio_db, right_ratio_data)
        sld.save_data(self.right_location_db, right_location_data)

    def analyse_right_info(self):
        for dt_type in DATA_TYPE:
            for stage in self.stage_list:   # 逐期分析正确率
                find_dict = {'stage': stage}
                filter_dict = {'_id': 0}
                predict_find_dict = {'stage': '20'+stage, 'data_type': dt_type}
                lottery_data = self.lottery_data_db.find_one(find_dict, filter_dict)
                if dt_type < 2:
                    predict_data = list(self.predict_data_db.find(predict_find_dict, filter_dict))
                else:
                    predict_data = list(self.kill_data_db.find(predict_find_dict, filter_dict))
                for data in predict_data:
                    self.analyse_some_stage_data(data, lottery_data)

    def get_experts(self, data_type):
        find_dict = {'data_type': data_type, 'stage': self.now_stage, 'lottery': self.lottery_name}
                     # 'articles_count': {"$gt": self.stage_count}}
        filter_dict = {'_id': 0, 'expert_name': 0, 'lottery': 0, }
        experts_dict_list = list(self.expert_db.find(find_dict, filter_dict))
        self.experts_list = [expert_dict['expert_id'] for expert_dict in experts_dict_list]
        logger.info(self.experts_list)

    def compute_mean_and_std(self, expert_id, data_type):
        find_dict = {'expert_id': expert_id, 'data_type': data_type}
        filter_dict = {'_id': 0, 'expert_name': 0}
        found_data = list(self.right_ratio_db.find(find_dict, filter_dict))
        expert_ratio_list = [data['right_ratio'] for data in found_data]

        try:
            expert_mean = sum(expert_ratio_list) / len(expert_ratio_list)
            expert_std = np.std(expert_ratio_list, ddof=1)
            return expert_mean, expert_std
        except Exception as e:
            logger.error(find_dict)

    def expert_sort(self, mean_list, std_list):
        result = []
        mean_l = sorted(list(set(mean_list)), reverse=True)
        for mean in mean_l:
            res = []
            index_list = []
            for i in range(len(mean_list)):
                if mean_list[i] == mean:
                    res.append(std_list[i])
                    index_list.append(i)
            if len(res) > 1:
                x = np.array(res)
                y = x.argsort()
                new_list = [index_list[i] for i in y]
                index_list = new_list
            result.extend(index_list)

        return[self.experts_list[i] for i in result]

    def get_lottery_data(self, stage=None):
        if stage is None:
            stage = self.now_stage
        find_dict = {'stage': stage}
        filter_dict = {'_id': 0, 'stage': 0}
        try:
            found_data = self.lottery_data_db.find_one(find_dict, filter_dict)
            return found_data
        except Exception as e:
            logger.error(e)

    def expert_rank(self, data_type):
        mean_list = []
        std_list = []
        self.get_experts(data_type)
        if len(self.experts_list):
            for expert in self.experts_list:
                # 计算均值， 方差， 按照均值第一，方差第二的原则进行排序
                expert_mean, expert_std = self.compute_mean_and_std(expert_id=expert, data_type=data_type)
                mean_list.append(expert_mean)
                std_list.append(expert_std)
            return self.expert_sort(mean_list, std_list)
        else:
            logger.error('self.experts_list为空，不能计算均值和方差！！！')

    def get_predict_data_from_file(self, file, expert_count):
        predict_dict = {}
        with open(file, 'r', encoding='utf-8') as f:
            contents = f.readlines()

        if len(contents) != expert_count:
            logger.error('预测数据条数据条数列表长度与专家数量不符！ 预测数据条数据条数：%s 专家数量：%s' % (len(contents), expert_count))

        for content in contents:
            data = eval(content)['balls']
            for ball in data:
                if ball in predict_dict:
                    predict_dict[ball] = predict_dict[ball] + 1
                else:
                    predict_dict[ball] = 1
        os.remove(file)
        return predict_dict

    def predict_kill_experts_list(self):
        # 前区
        for front_predict_expert_count in self.front_predict_expert_count_list:
            print('front_predict_expert_count:', front_predict_expert_count)
            try:
                front_pre_experts_list = self.expert_rank(data_type=0)[:front_predict_expert_count]
                logger.info('stage: %s\t red predict balls expert count: %s expert list: %s'
                            % (self.now_stage, len(front_pre_experts_list), front_pre_experts_list))
            except Exception as e:
                logger.error(e)

        for front_kill_expert_count in self.front_kill_expert_count_list:
            print(front_kill_expert_count)
            try:
                front_kill_experts_list = self.expert_rank(data_type=2)[:front_kill_expert_count]
                logger.info('stage: %s\t red kill balls experts count:%s expert list:%s'
                            % (self.now_stage, len(front_kill_experts_list), front_kill_experts_list))
            except Exception as e:
                logger.error(e)

        # 后区
        for back_predict_expert_count in self.back_predict_expert_count_list:
            print(back_predict_expert_count)
            try:
                back_pre_experts_list = self.expert_rank(data_type=1)[:back_predict_expert_count]
                logger.info('stage: %s\t blue balls experts count:%s expert list:%s'
                            % (self.now_stage, len(back_pre_experts_list), back_pre_experts_list))
            except Exception as e:
                logger.error(e)

        for back_kill_expert_count in self.back_kill_expert_count_list:
            print(back_kill_expert_count)
            try:
                back_kill_experts_list = self.expert_rank(data_type=3)[:back_kill_expert_count]
                logger.info('stage: %s\t blue kill balls experts count:%s expert list:%s'
                            % (self.now_stage, len(back_kill_experts_list), back_kill_experts_list))
            except Exception as e:
                logger.error(e)

    def get_the_next_experts_predict_kill_data(self):
        predict_data = []
        with open(self.data_file, 'r') as f:
            content = json.load(f)

        for data_type in DATA_TYPE:
            experts_list = []
            if data_type == 0:
                experts_list = content['front_predict_experts_list']
            if data_type == 1:
                experts_list = content['front_kill_experts_list']
            if data_type == 2:
                experts_list = content['back_predict_experts_list']
            if data_type == 3:
                experts_list = content['back_kill_experts_list']

            data_file = '%s_%s' % (self.lottery, data_type)

            gnspu = GetNowStagePredictUrl(self.lottery, experts_list, self.now_stage, data_type, data_file)
            gnspu.run()
            predict_data.append(self.get_predict_data_from_file(data_file, front_predict_expert_count))

        # # predict_data里边有四个列表（如果是七乐彩，就只有前两个），分别是前区预测，前区杀球预测，后区预测，后区杀球预测
        # assert (len(predict_data) == 2 * 2), '彩票名称：%s\t期望列表长度：%s\t实际列表长度：%s' % (
        #     self.lottery, 2 * 2, len(predict_data))

        # 进行每种配置正确率的判断
        cspd = CSPD(self.lottery)
        predict_data = cspd.compose_predict_data(predict_data,
                                                 front_predict_balls_count,
                                                 front_kill_balls_count,
                                                 back_predict_balls_count,
                                                 back_kill_balls_count)

        counts = cspd.compute_price(predict_data)
        money = 2 * counts

        all_data = {
            "lottery": self.lottery_name,
            "stage": self.now_stage[2:],
            "front_predict_balls": sorted(predict_data[0]),
            "back_predict_balls": sorted(predict_data[1]),
            "lottery_counts": counts,
            "lottery_money": money,
            "front_predict_experts_list": content['front_predict_experts_list'],
            "front_kill_experts_list": content['front_kill_experts_list'],
            "back_predict_experts_list": content['back_predict_experts_list'],
            "back_kill_experts_list": content['back_kill_experts_list']
        }

        if not REAL:
            # 测饿期间使用
            kjxx = GetKJXX(self.lottery)
            lottery_data = kjxx.get_kjxx()
            all_data['lottery_front_balls'] = lottery_data[0]
            all_data['lottery_back_balls'] = lottery_data[1]
            front_right_ratio = self.compute_right_ratio(predict_data[0], lottery_data[0])[0]
            all_data['front_right_ratio'] = str(front_right_ratio * 100)[:5] + '%'
            back_right_ratio = self.compute_right_ratio(predict_data[1], lottery_data[1], kill=True)[0]
            all_data['back_right_ratio'] = str(back_right_ratio * 100)[:5] + '%'

        with open(self.data_file, 'w') as f:
            json.dump(all_data, f)

        self.right_ratio_db.drop()
        self.right_location_db.drop()

    def start_analyse(self):
        p = ThreadPoolExecutor()
        self.get_experts_balls_count()
        for stage_count in self.stage_count_list:
            print('stage_count', stage_count)
            self.stage_count = stage_count
            self.get_stage_list()
            p.submit(self.analyse_right_info)  # 分析正确率和正确位置
            self.predict_kill_experts_list()
        p.shutdown()


if __name__ == '__main__':
    now_stage = '2020008'
    ad = MutilStagesAnalyseData('ssq', now_stage, 'test_data_1.json')
    ad.start_analyse()
    ad.get_the_next_experts_predict_kill_data()
