
from settings import LOTTERY_BALLS_COUNT
from tools.logger import Logger
logger = Logger(__name__).logger


class ComposePredictData(object):

    def __init__(self, lottery):
        self.lottery = lottery

    def compose_area_data(self, predict_data, kill_data, predict_count, kill_count):
        kill_data = [k[0] for k in sorted(kill_data.items(), key=lambda x: x[1], reverse=True)]
        predict_dict = {}
        for ball in predict_data:
            if ball not in kill_data[:kill_count]:
                predict_dict[ball] = predict_data[ball]
        new_predict = sorted(predict_dict.items(), key=lambda x: x[1], reverse=True)
        new_predict_data = [item[0] for item in new_predict]
        composed_data = new_predict_data[:predict_count]
        return composed_data

    def cni(self, n, i):
        result = 1
        for j in range(1, i + 1):
            result = result * (n - i + j) // j
        return result

    def compose_predict_data(self, predict_data, front_predict_count,
                             front_kill_count, back_predict_count, back_kill_count):
        compose_data = list()
        compose_data.append(self.compose_area_data(predict_data[0], predict_data[2],
                                                   front_predict_count, front_kill_count))
        compose_data.append(self.compose_area_data(predict_data[1], predict_data[3],
                                                   back_predict_count, back_kill_count))
        return compose_data

    def compute_price(self, predict_data):
        front_balls = LOTTERY_BALLS_COUNT[self.lottery][0]
        back_balls = LOTTERY_BALLS_COUNT[self.lottery][1]
        front_counts = self.cni(len(predict_data[0]), front_balls)
        back_counts = self.cni(len(predict_data[1]), back_balls)
        total_count = front_counts * back_counts
        return total_count