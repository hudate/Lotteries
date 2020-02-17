from settings import LOTTERY_BALLS_COUNT
from tools.logger import Logger

'''
需要计算的内容：
1. 总注数
2. 总价格
3. 总正确率
4. 正确详情（一等奖，二等奖，三等奖，四等奖，五等奖，六等奖，七等奖，八等奖，九等奖等各多少注）
5. 总收益
6. 收益率
'''

ADD_EXPENDITURE = [15, 16, 17, 18, 13, 14, 12, 10]

logger = Logger('calculate.py').logger

dlt_dict = {
    'A': [5, 2], 'B': [5, 1], 10000: [5, 0], 3000: [4, 2], 300: [4, 1], 200: [3, 2],
    100: [4, 0], 15: [[3, 1], [2, 2]], 5: [[3, 0], [1, 2], [2, 1], [0, 2]]
}

dlt_level_dict = {
    5: '九等奖', 15: '八等奖', 100: '七等奖', 200: '六等奖', 300: '五等奖',
    3000: '四等奖', 10000: '三等奖', 'B': '二等奖', 'A': '一等奖'
}

ssq_dict = {
    'A': [6, 1], 'B': [6, 0], 3000: [5, 1], 200: [[5, 0], [4, 1]],
    10: [[4, 0], [3, 1]], 5: [[2, 1], [1, 1], [0, 1]]
}

ssq_level_dict = {
    5: '六等奖', 10: '五等奖', 200: '四等奖', 3000: '三等奖', 'B': '二等奖', 'A': '一等奖'
}


class Calculate(object):

    def __init__(self, lottery, fore_count, back_count, fore_right_count, back_right_count):
        self.lottery = lottery
        self.fore_count = fore_count
        self.back_count = back_count
        self.fore_right_count = fore_right_count
        self.back_right_count = back_right_count
        self.lottery_dict = dlt_dict if lottery == 'dlt' else ssq_dict
        self.level_dict = dlt_level_dict if lottery == 'dlt' else ssq_level_dict
        self.detail = {}
        self.add_expenditure = 0
        self.price = 0
        self.money = 0
        self.count = 0
        self.income = 0
        self.profit = 0
        self.profit_rate = 0

    # 计算额外话费
    def calculate_add_expenditure(self):
        # 主要是专家数据支出, 把每个专家的数据钱数相加即可
        self.add_expenditure = sum(ADD_EXPENDITURE)
        pass

    # 计算总钱数
    def calculate_money(self):
        self.money = self.price + self.add_expenditure
        return

    # 计算总正确率
    def calculate_right_ratio(self):
        pass

    def calculate_income(self):
        for k, v in self.detail.items():
            logger.info('等级：%s 单价：%s 注数%s 奖金：%s' % (self.level_dict[k], k, v, k * v))

            if isinstance(k, int):
                self.income += k * v
            else:
                try:
                    self.income += self.income + '%s * %s' % (v, k)
                except:
                    self.income += str(self.income) + '%s * %s' % (v, k)
        logger.info('共计奖金：%s' % self.income)
        return

    # 计算组合数
    def __cni(self, n, i):
        result = 1
        for j in range(1, i + 1):
            result = result * (n - i + j) // j
        return result

    # 计算总注数
    def calculate_count(self):
        fore_count = self.__cni(self.fore_count, LOTTERY_BALLS_COUNT[self.lottery][0])
        back_count = self.__cni(self.back_count, LOTTERY_BALLS_COUNT[self.lottery][1])
        self.count = fore_count * back_count
        return

    # 计算价格
    def calculate_price(self):
        if self.count:
            self.price = self.count * 2
            logger.info('Price is %s' % self.price)
        else:
            logger.error('Please use compute_count() first!!!')
        return

    # 计算详情
    def calculate_detail(self):
        for i in range(self.fore_right_count + 1):
            for j in range(self.back_right_count + 1):
                for k, v in self.lottery_dict.items():
                    if [i, j] == v or [i, j] in v:
                        # print('中奖：', [i, j])
                        # print(LOTTERY_BALLS_COUNT[self.lottery][0], i)
                        # print(self.__cni(LOTTERY_BALLS_COUNT[self.lottery][0], i))
                        # print(LOTTERY_BALLS_COUNT[self.lottery][1], j)
                        # print(self.__cni(LOTTERY_BALLS_COUNT[self.lottery][1], j))
                        self.detail[k] = (self.__cni(LOTTERY_BALLS_COUNT[self.lottery][0], i) *
                                          self.__cni(LOTTERY_BALLS_COUNT[self.lottery][1], j)) \
                            if k not in self.detail else (self.detail[k] +
                                                          self.__cni(LOTTERY_BALLS_COUNT[self.lottery][0], i) *
                                                          self.__cni(LOTTERY_BALLS_COUNT[self.lottery][1], j))
        # print(self.detail)
        return

    # 计算收益率
    def calculate_profit_rate(self):
        self.profit_rate = (self.income - self.money) / self.money
        return

    def calculate(self):
        self.calculate_count()
        self.calculate_price()
        self.calculate_add_expenditure()
        self.calculate_money()
        self.calculate_detail()
        self.calculate_income()
        self.calculate_right_ratio()


if __name__ == '__main__':
    calc = Calculate('dlt', fore_count=7, back_count=4, fore_right_count=3, back_right_count=2)
    calc.calculate()
    # print(calc.count, calc.price, calc.add_expenditure, calc.money)
