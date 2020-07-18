# -*- coding:utf-8 -*-

import os
import pymongo

pym_client = pymongo.MongoClient(host='localhost', port=27017, waitQueueTimeoutMS=100)
db = pym_client['Lotteries']

# 往期开奖数据的存储
lotteries_data_db = {
    'ssq': db['lottery_ssq'],
    'qlc': db['lottery_qlc'],
    'fcd': db['lottery_fcd'],
    'dlt': db['lottery_dlt'],
    'qxc': db['lottery_qxc'],
    'pls': db['lottery_pls'],
    'plw': db['lottery_plw'],
}

# 往期别人预测数据的存储
lotteries_predict_data_db = {
    'ssq': db['predict_ssq'],
    'dlt': db['predict_dlt'],
    'ssq_kill': db['kill_ssq'],
    'dlt_kill': db['kill_dlt'],
    'ssq_experts': db['experts_ssq'],
    'dlt_experts': db['experts_dlt'],
    'all_experts': db['experts_all'],
    'ssq_right_ratio': db['right_ratio_ssq'],
    'dlt_right_ratio': db['right_ratio_dlt'],
    'ssq_right_location': db['right_location_ssq'],
    'dlt_right_location': db['right_location_dlt'],
    'ssq_articles_list': db['articles_list_ssq'],
    'dlt_articles_list': db['articles_list_dlt'],
}


saved_db = {
    'saved_articles_list_urls': db['saved_articles_list'],    # 数据内容包括：expert_id，url，
    'saved_predict_urls': db['saved_predict_urls'],
    'the_next_stage_saved_predict_urls': db['the_next_stage_saved_predict_urls']    # 主要保存待开奖期的保存过的文章列表数据
}


miss_urls_db = {
    'experts': db['missed_experts'],
    'articles_list': db['missed_articles_list'],
    'predict_urls': db['missed_predict_urls']
}

avoid_experts_db = db['avoid_experts']      # 计入某些不符合要求的专家

AVOID_EXPERTS = []

LOTTERY_DICT = {
    '双色球': 'ssq', '大乐透': 'dlt', '七星彩': 'qxc', '七乐彩': 'qlc', '排列三': 'pls', '排列五': 'plw', '福彩3D': 'fcd',
    '刮刮乐': 'ggl'
}

LOTTERY_DICT_2 = {v: k for k, v in LOTTERY_DICT.items()}
# 获取之前的预测数据的期数
LOT_PRE_STA_COUNT = 100

# 专家列表页，每页的专家个数，这个数在原来的页面上是固定的：30, 但是在这里为了便于控制专家的数量，改了这个值
PER_PAGE_EXPERTS_COUNT = 30

# 最多获取几页专家, 这两项确定了获取专家的个数 专家个数=每页专家个数×最多几页
MAX_EXPERTS_PAGE_COUNT = 5

# 每期获取专家的数量
EXPERT_COUNT = PER_PAGE_EXPERTS_COUNT * MAX_EXPERTS_PAGE_COUNT

# 每个专家文章列表页数
PER_EXPERT_ARTICLES_LIST_MAX_PAGE = 2

# 预测期数
STAGE_COUNT_LIST = [30, 20, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5]
STAGE_COUNT = 30

# 每期预测的专家数量
EXPERT_COUNT_LIST = [30, 20, 15, 13, 10, 7, 5]

# 这里注意，第一个是预测时，最少的预测球数：此时，预测球个数=开奖球数+该数， 比如大乐透，开奖球数是5，那么预测球个数为7~8
PREDICT_BALLS_COUNT = [2, 5]
KILL_BALLS_COUNT = [0, 1, 2, 3]

#  0：代表全面测试阶段，主要测试本期预测的结果与本期开奖的差异和准确率，需要考虑模块之间的调用和各种异常处理
#  1：代表上线使用阶段，全面应用，需要考虑支付，以爬取档期的预测数据，当期查看专家数据花费的金额（预测本期的收益率）
REAL = 0

# 获取专家文章列表的网址，参数在请求时给出
EXPERT_URL = 'https://www.cjcp.com.cn/ajax.php?'

# 获取专家列表的网址
EXPERT_LIST_URLS = [
    'https://www.cjcp.com.cn/showsortinfo.php?id=104040307',      # 大乐透前区25码
    'https://www.cjcp.com.cn/showsortinfo.php?id=1304040307',     # 大乐透后区定6码
    'https://www.cjcp.com.cn/showsortinfo.php?id=8040403011',     # 大乐透前区杀6码
    'https://www.cjcp.com.cn/showsortinfo.php?id=12040403015',    # 大乐透后区杀3码
    'https://www.cjcp.com.cn/showsortinfo.php?id=401040307',      # 双色球前区25码
    'https://www.cjcp.com.cn/showsortinfo.php?id=9010403011',     # 双色球后区定5码
    'https://www.cjcp.com.cn/showsortinfo.php?id=3010403011',     # 双色球前区杀6码
    'https://www.cjcp.com.cn/showsortinfo.php?id=5010403031',     # 双色球后区杀5码
]

DATA_TYPE = [
    0,      # 前区预测
    1,      # 后区预测
    2,      # 前区杀球
    3,      # 后区杀球
]

RIGHT_RATIO_CSV_FILE = '%s_right_ratio.csv'

cookies_db = db['cookies_coll']

# 代理池数据库
proxies_tb = pym_client['Proxies']['proxies']

DAYS_DICT = {'0': '日', '1': '一', '2': '二', '3': '三', '4': '四', '5': '五', '6': '六'}

LOTTERY_BALLS_COUNT = {'ssq': [6, 1], 'dlt': [5, 2]}

BASE_DIR = os.path.dirname(__file__)

SETUP_FILE = os.sep.join([BASE_DIR, 'setup.json'])
SETUP_TEMPLATE = os.sep.join([BASE_DIR, 'setup_template.json'])

# 日期-彩票-期数
DATA_FILE = os.sep.join([BASE_DIR, 'record', '%s_%s_%s.json'])        # 用于保存各种中间数据

# 设置cookies的计算基数
COOKIES_BASE_COUNT = 500
