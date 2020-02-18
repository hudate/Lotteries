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

    def __init__(self, lottery):
        self.lottery = lottery
        self.lottery_dict = dlt_dict if lottery == 'dlt' else ssq_dict
        self.level_dict = dlt_level_dict if lottery == 'dlt' else ssq_level_dict
        self.detail = {}
        self.fore_count = 0
        self.back_count = 0
        self.fore_right_count = 0
        self.back_right_count = 0
        self.add_expenditure = 0
        self.price = 0
        self.money = 0
        self.count = 0
        self.income = {'固定收入': 0, '浮动收入': 0}
        self.profit = {'固定收益': 0, '浮动收益': 0}
        self.profit_rate = {'固定收益率': 0, '浮动收入': 0}

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
            logger.info('等级：%s \t\t单价：%s \t\t注数：%s \t\t奖金：%s' % (self.level_dict[k], k, v, v * k if v != 0 else 0))
            if isinstance(k, int):
                self.income['固定收入'] += k * v
            elif v == 0:
                self.income['浮动收入'] += 0
            else:
                try:
                    self.income['浮动收入'] += '+' + '%s%s' % (v, k)
                except:
                    self.income['浮动收入'] = '%s%s' % (v, k)
        logger.info('共计奖金：%s' % self.income)
        return

    # 计算组合数
    def __cni(self, i, n):
        result = 1
        for j in range(1, n + 1):
            result = result * (i - n + j) // j
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

    # 计算收益率
    def calculate_profit_rate(self):
        logger.warning('本次只计算固定收益率')
        self.profit_rate = '%.2f' % ((self.income['固定收入'] - self.money) / self.money * 100) + '%'
        logger.info('投入：%s 固定收益：%s 固定收益率：%s 浮动收益：%s' % (self.money, self.income['固定收入'] - self.money,
                                                            self.profit_rate,  self.income['浮动收入']))
        return

    def set_balls_count(self, freq, breq, fhit, bhit):
        self.fore_count = freq
        self.back_count = breq
        self.fore_right_count = fhit
        self.back_right_count = bhit
        return

    # 计算前区或后区命中指定个数的方案注数
    def solve_hits(self, num, req, opt, req_hit, opt_hit):
        opt_left = num - req
        opt_miss = opt - opt_hit
        most = req_hit + opt_hit
        hits = [0 for i in range(num + 1)]
        for i in range(num + 1):
            if (i < req_hit) or (i > most):
                hits[i] = 0
            else:
                opt_need = i - req_hit
                hits[i] = self.__cni(opt_hit, opt_need) * self.__cni(opt_miss, opt_left - opt_need)
        return hits

    # 计算各奖项命中的方案注数
    def calculate_detail(self):
        # fHits: 前区命中个数， bHits: 后区命中个数
        fReq = 0
        fReqHit = 0
        bReq = 0
        bReqHit = 0
        fHits = self.solve_hits(LOTTERY_BALLS_COUNT[self.lottery][0], fReq, self.fore_count, fReqHit, self.fore_right_count)
        bHits = self.solve_hits(LOTTERY_BALLS_COUNT[self.lottery][1], bReq, self.back_count, bReqHit, self.back_right_count)
        for k, v in self.lottery_dict.items():
            self.detail[k] = 0
            for i in range(len(fHits)):
                for j in range(len(bHits)):
                    if [i, j] == self.lottery_dict[k] or [i, j] in self.lottery_dict[k]:
                        self.detail[k] += fHits[i] * bHits[j]
        return

    def calculate(self):
        self.calculate_count()
        self.calculate_price()
        self.calculate_add_expenditure()
        self.calculate_money()
        self.calculate_detail()
        self.calculate_income()
        self.calculate_right_ratio()
        self.calculate_profit_rate()


if __name__ == '__main__':
    calc = Calculate('dlt')
    calc.set_balls_count(freq=7, breq=4, fhit=3, bhit=2)
    # calc.set_fore_req(fore_req, fore_opt, fore_req_hit, fore_opt_hit)
    # calc.set_back_req(back_req, back_opt, back_req_hit, back_opt_hit)
    calc.calculate()
