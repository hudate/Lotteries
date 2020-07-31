import json
import os
import time
import re
import requests
from settings import lotteries_predict_data_db as lpdb, lotteries_data_db as ldb, GET_NEXT_STAGE_URLS, LOTTERY_DICT_2, \
    LOTTERY_DICT, next_stage_db
from tools.logger import Logger
logger = Logger(__name__).logger


def get_stage(url):
    try:
        res = requests.get(url=url % str(time.time()).split('.')[0])
        stage = res.text.split("推荐")[1][: -1]
        return stage
    except Exception as e:
        logger.error('error url: %s' % url)
        logger.error('error info: %s' % e)


def clear_db(db):
    db.drop()


def is_need_to_clear_db(day1, day2):
    if day1 == day2:
        return False
    else:
        return True


def avoid_whole_point():
    minute = time.strftime("%M")
    if minute == '00' or minute == '30':
        time.sleep(90)


def now_time(format_str='%Y-%m-%d %H:%M:%S'):
    return time.strftime(format_str)


def get_the_next_stage(lottery):       # 获取当前未开奖的期数
    next_stage = ''
    lottery = lottery if lottery in LOTTERY_DICT_2 else LOTTERY_DICT[lottery]
    try:
        next_stage = next_stage_db.find_one({}, {'_id': 0, 'stage': 1})['stage']
    except Exception as e:
        logger.error(e)

    if not next_stage:
        url = GET_NEXT_STAGE_URLS[lottery]
        last_stage = get_stage(url)
        if len(last_stage) == 3:
            next_stage = now_time('%Y') + last_stage
        elif len(last_stage) == 5:
            next_stage = now_time('%Y')[:2] + last_stage
        elif len(last_stage) == 7:
            next_stage = last_stage
        else:
            logger.error('获取到错误的期数：', last_stage)

        if next_stage:
            try:
                next_stage_db.insert_one({'stage': next_stage})
            except Exception as e:
                logger.error(e)

    return next_stage


def set_mail_data(data_file):
    url = 'https://www.cjcp.com.cn/expert/expertinfo.php?id='
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for key in data:
        if key.endswith('experts_list'):
            experts_name_list = []
            find_dict = {'lottery': data['lottery'], 'stage': '20' + data['stage']}
            filter_dict = {'_id': 0, 'expert_name': 1, 'expert_id': 1}
            experts_list = list(lpdb['all_experts'].find(find_dict, filter_dict))

            for expert_id in data[key]:
                for expert in experts_list:
                    if expert_id == expert['expert_id']:
                        experts_name_list.append(expert['expert_name'])
                        break

            data[key] = ['<a href="%s%s" >%s</a>' % (url, data[key][index], experts_name_list[index])
                                               for index in range(len(experts_name_list))]
    return data


def get_json_content(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def remove_browser_tmp(tmp_dir):
    for file_dir in os.listdir(tmp_dir):
        if os.path.isdir(file_dir) and file_dir.startswith('tmp') or file_dir.startswith('rust_'):
            os.chmod(tmp_dir + os.sep + file_dir, 777)
            os.removedirs(tmp_dir + os.sep + file_dir)


def set_mail_sender():
    sender = input('请输入发件人：')
    password = input('请输入对应密码：')
    find_str = re.compile(r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9\u4e00-\u9fa5_-]+(\.[a-zA-Z0-9_-]+)+$')
    if not re.findall(find_str, sender):
        set_mail_receivers()

    return sender, password


def set_mail_receivers():
    _receivers = input('请输入收件人（多个收件人之间请使用","分割，注意不要空格）)：')
    receivers = _receivers.strip('[').strip(']').strip(',').strip().split(',')
    receivers = [receiver.strip('"').strip() for receiver in receivers]
    if not (receivers or ''.join(receivers)):
        set_mail_receivers()

    for receiver in receivers:
        find_str = re.compile(r'^[A-Za-z0-9\u4e00-\u9fa5]+@[a-zA-Z0-9\u4e00-\u9fa5_-]+(\.[a-zA-Z0-9_-]+)+$')
        if not re.findall(find_str, receiver):
            set_mail_receivers()

    return list(set(receivers))


def set_cjw_account():
    account = input('请输入彩经网登录用户：')
    password = input('请输入对应密码：')
    if account.strip() == '' or password.strip() == '':
        print('error:\t发件人或者密码不能为空！')
        set_cjw_account()
    return account, password
