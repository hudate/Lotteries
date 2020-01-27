
from settings import KILL_BALLS_COUNT, LOTTERY_BALLS_COUNT
import sys
from tools.logger import Logger
logger = Logger(__name__).logger


class ComposePredictData(object):

    def __init__(self, lottery):
        self.lottery = lottery

    def compose(self, predict, kill):
        predict_data_dict = {}
        kill = [k[0] for k in sorted(kill.items(), key= lambda x: x[1], reverse=True)]
        for k in KILL_BALLS_COUNT:
            predict_dict = {}
            for ball in predict:
                if ball not in kill[:k]:
                    try:
                        predict_dict[ball] = predict[ball]
                    except:
                        logger.critical('组合数据时发生了错误！')
            new_predict = sorted(predict_dict.items(), key= lambda x: x[1], reverse=True)
            new_predict_data = [item[0] for item in new_predict]
            # print(__name__, predict_data)
            predict_data_dict[k] = new_predict_data
        return predict_data_dict

    def compose_predict_data(self, predict_data):
        compose_data = []
        compose_list = []
        # print(__name__, LINE_ON.f_lineno, predict_data)
        for data in predict_data:
            compose_list.append(data)
            if len(compose_list) == 2:
                predict = compose_list[0]
                kill = compose_list[1]
                # print(predict, kill)
                compose_data.append(self.compose(predict, kill))
                compose_list = []
        return compose_data

    def cni(self, n, i):
        result = 1
        for j in range(1, i + 1):
            result = result * (n - i + j) // j
        return result

    def compute_price(self, predict_data):
        front_balls = LOTTERY_BALLS_COUNT[self.lottery[0]]
        back_balls = LOTTERY_BALLS_COUNT[self.lottery[1]]
        front_counts = self.cni(len(predict_data[0]), front_balls)
        back_counts = self.cni(len(predict_data[1]), back_balls)
        total_count = front_counts * back_counts
        total_money = 2 * total_count
        return total_count, total_money
