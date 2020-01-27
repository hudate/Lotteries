import json
import os
import time
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
    pass


def set_mail_receivers():
    pass


def set_cjw_account():
    pass