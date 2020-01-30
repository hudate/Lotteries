import json
import os
import time
import re

from settings import lotteries_predict_data_db as lpdb, MAX_EXPERTS_PAGE_COUNT, lotteries_data_db as ldb


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


def now_time():
    return time.strftime('%Y-%m-%d %H:%M:%S')


def get_the_next_stage(lottery):       # 获取当前未开奖的期数
    db = ldb[lottery]
    stages_dict = list(db.find({}, {'_id': 0, 'stage': 1}))
    last_stage = sorted([list(stage.values())[0] for stage in stages_dict], reverse=True)[0]
    if time.strftime('%m') == '01':
        if last_stage.startswith(time.strftime('%y' + '00')):
            stage = '20' + str(int(last_stage) + 1)
        else:
            stage = str(int(time.strftime('%Y'))) + '001'
    else:
        stage = '20' + str(int(last_stage) + 1)
    return stage


def set_mail_data(data_file):
    url = 'https://www.cjcp.com.cn/expert/expertinfo.php?id='
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for key in data:
        if key.endswith('experts_list'):
            # print(key)
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
    if sender.strip() == '' or password.strip() == '':
        print('error:\t发件人或者密码不能为空！')
        set_mail_sender()

    if '@' not in sender:
        print('error:\t发件人格式有误，"@"不在发件人中！！！')
        set_mail_sender()

    if sender.startswith('@') or sender.endswith('@'):
        print('error:\t发件人格式有误，发件人以"@"开头或者结尾！！！')
        set_mail_sender()

    return sender, password


def set_mail_receivers():
    receivers = []
    _receivers = input('请输入收件人列（多个收件人之间请使用","分割，注意不要空格）)：')
    if ' ' in _receivers:
        print('error:\t收件人列表不能包含空格！！！')
        set_mail_receivers()
    else:
        receivers = _receivers.strip('[').strip(']').strip(',').split(',')
        receivers = [receiver.strip('"') for receiver in receivers]

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