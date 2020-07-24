# -*- coding:utf-8 -*-
import gevent
from gevent import monkey; monkey.patch_all()
import shutil
import os
from settings import DAYS_DICT, avoid_experts_db, LOTTERY_DICT_2, DATA_FILE, miss_urls_db, SETUP_FILE, BASE_DIR, \
    saved_db, REAL, SETUP_TEMPLATE, TIMES_TRANSLATE

os.chdir(BASE_DIR)
from dataP.auto_get_missed_predict_data import GetMissedPredictData

import signal
from multiprocessing import Process
from dataB import auto_begin as abg
from proxy.clear_proxies import clear_proxies_db
from proxy.get_proxy import GetProxies
from tools.send_mail import SendMail
from tools.analyse_one_stage_data import AnalyseData
from tools.common import *
from tools.auto_check_articles_list import CheckArticlesList as CAL
from dataP.auto_begin import ExpertDataBegin as EB
from tools.logger import Logger
logger = Logger(logger=__name__).getlog()

process_flag = 0
normal_main_process_time_delta = 900
abnormal_main_process_time_delta = 300
hostname = os.popen('hostname').read()[:-1]


def get_work_times():
    content = get_json_content(SETUP_FILE)
    common_times = content['common_actions_time']
    real_times = content['real_actions_time']
    test_times = content['test_actions_time']
    se_times = content['start_end_times']
    actions_times = real_times if REAL == 1 else test_times
    actions_times.update(se_times)
    actions_times.update(common_times)
    actions_times['pause_delta_time'] = content['pause_delta_time']
    actions_times['every_times_count'] = content['every_times_count']
    return actions_times


def start_ctrl(lottery, now_stage, work_times):
    logger.info('上班了，上班了！')
    data_file = DATA_FILE % (time.strftime('%Y-%m-%d'), lottery, now_stage)
    sm = SendMail(data_file)
    logger.info('主机：%s 彩票：%s 期数：%s 数据文件：%s' % (hostname, lottery, now_stage, data_file))
    sm.send_flush(now_time() + ' 主机：%s, 彩票：%s, 期数：%s 数据文件：%s' % (hostname, lottery, now_stage, data_file))
    ad = AnalyseData(lottery, now_stage, data_file)
    global process_flag
    process_flag = 1
    while 1:
        bg = EB(
            lottery,
            pause_delta_time=work_times['pause_delta_time'],
            every_times_count=work_times['every_times_count']
        )

        for key in work_times:
            if time.strftime('%H:%M') == work_times[key]:
                if key == "end_time":  # 今天结束了
                    logger.info('下班，明天是个好日子！!')
                    process_flag = 0
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' 下班，明天是个好日子！！')
                    os.kill(os.getpid(), signal.SIGKILL)

                # 开始获取往期的开奖数据
                if key == 'get_lotteries_data':
                    logger.info('开始获取往期的开奖数据。')
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' 开始获取往期的开奖数据。')
                    bag = abg.Begin(lottery)  # 获取往期的开奖数据
                    bag.begin()

                # 初次获取代理
                if key.startswith('get_proxies'):
                    times_zh = TIMES_TRANSLATE[key.rsplit('_', 1)[1]]
                    times_str = '%s获取代理。' % times_zh
                    logger.info(times_str)
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' ' + times_str)
                    clear_proxies_db()
                    gp = GetProxies()
                    gp.start()

                if key == 'check_the_next_stage_experts_articles_list':
                    logger.info('检查所有专家的文章列表是否有漏爬!')
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' 检查所有专家的文章列表是否有漏爬！')
                    cal = CAL(LOTTERY_DICT_2[lottery], now_stage)
                    cal.start_check()
                    bg.get_predict_urls(1)

                # 获取当前待开奖的预测数据
                if key.startswith('get_the_next_stage_experts_all_predict_data'):
                    times_zh = TIMES_TRANSLATE[key.rsplit('_', 1)[1]]
                    times_str = '%s获取每个专家的所有预测数据。' % times_zh
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' ' + times_str)
                    bg.get_predict_data()

                # 获取本期的所有专家的预测数据url列表
                if key.startswith('get_the_next_stage_experts_articles_list'):
                    times_zh = TIMES_TRANSLATE[key.rsplit('_', 1)[1]]
                    times_str = '%s获取下期每个专家的预测文章的URL列表。' % times_zh
                    logger.info(times_str)
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' ' + times_str)
                    bg.get_predict_urls()

                # 开始分析“预测专家列表”，并记入DATA_FILE
                if key == 'get_the_next_stage_experts_list':
                    logger.info('开始分析“预测专家列表”！')
                    sm.send_flush('%s %s %s' % (now_time(), hostname, data_file) + ' 开始分析“预测专家列表”！')
                    ad.start_analyse()

                # 开始获取本期的专家
                if key.startswith('get_the_next_stage_all_experts'):
                    times_zh = TIMES_TRANSLATE[key.rsplit('_', 1)[1]]
                    times_str = '%s获取下期所有专家。' % times_zh
                    logger.info(times_str)
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' ' + times_str)
                    bg.get_experts()

                # 依据“预测专家列表”获取“专家预测数据”
                if key == 'get_all_stage_experts_predict_data':
                    logger.info('依据“预测专家列表”获取“专家预测数据”！')
                    sm.send_flush('%s %s %s' % (now_time(), hostname, data_file) + ' 依据“预测专家列表”获取“专家预测数据”！')
                    ad.get_the_next_experts_predict_kill_data()

                # 开始发送邮件
                if key.startswith('send_mail'):
                    times_zh = TIMES_TRANSLATE[key.rsplit('_', 1)[1]]
                    times_str = '%s发送邮件。' % times_zh
                    logger.info(times_str)
                    sm.send_flush('%s %s' % (now_time(), hostname) + ' ' + times_str)
                    sm.send_mail()

                # 使用像周五一样的手段去爬取数据
                if key == 'get_all_stage_experts_all_predict_data':
                    pause_delta_time = work_times['pause_delta_time'] + 50
                    every_times_count = work_times['every_times_count']
                    today_start_time = time.mktime(time.strptime(now_time('%Y-%m-%d'), '%Y-%m-%d'))
                    today_surplus_time = 21.5 * 3600 - (time.time() - today_start_time)
                    total_times = int(today_surplus_time / pause_delta_time)
                    if total_times > 0:
                        gmpd = GetMissedPredictData(total_times, pause_delta_time, every_times_count)
                        gmpd.run()

                if key == 'clear_database':
                    logger.info('开始清除数据库：%s！' %
                                ([lpdb[lottery + '_experts'], avoid_experts_db, miss_urls_db['articles_list']]))
                    try:
                        lpdb[lottery + '_experts'].drop()
                        lpdb[lottery + '_right_location'].drop()
                        saved_db['the_next_stage_saved_predict_urls'].drop()
                        avoid_experts_db.drop()
                        miss_urls_db['articles_list'].drop()
                        remove_browser_tmp('/tmp')
                        logger.info('成功清除数据库：%s！' %
                                    ([lpdb[lottery + '_experts'], avoid_experts_db, miss_urls_db['articles_list']]))
                        sm.send_flush('%s %s' % (now_time(), hostname) + ' 开始清除数据库完成！！')
                    except Exception as e:
                        logger.error(e)

                time.sleep(15)      # 为了防止某些操作一分钟内执行了两次
        logger.info('休息中...')
        time.sleep(58)


def start():
    if not os.path.exists(os.path.dirname(DATA_FILE)):
        os.mkdir(os.path.dirname(DATA_FILE))

    while 1:
        work_times = get_work_times()
        logger.info(work_times)
        start_time = work_times['start_time']
        end_time = work_times['end_time']
        friday_start_time = work_times['friday_start']
        friday_end_time = work_times['friday_end']
        avoid_whole_point()
        today = int(time.strftime("%w"))

        if today in [1, 3, 6]:
            lottery = 'dlt'
        elif today in [0, 2, 4]:
            lottery = 'ssq'
        else:
            lottery = 'ggl'

        logger.info('今天星期%s，开奖：%s！！！' % (DAYS_DICT[time.strftime('%w')], LOTTERY_DICT_2[lottery]))

        if lottery == 'ggl':
            if (friday_start_time[:2] <= time.strftime('%H') and time.strftime('%H:%M') < friday_end_time):
                pause_delta_time = work_times['pause_delta_time']
                every_times_count = work_times['every_times_count']
                today_start_time = time.mktime(time.strptime(now_time('%Y-%m-%d'), '%Y-%m-%d'))
                today_surplus_time = 23.5 * 3600 - (time.time() - today_start_time)
                total_times = int(today_surplus_time / pause_delta_time)
                gmpd = GetMissedPredictData(total_times, pause_delta_time, every_times_count)
                gmpd.run()
        else:
            if not process_flag and (start_time[:2] <= time.strftime('%H') and time.strftime('%H:%M') <= end_time):
                now_stage = get_the_next_stage(lottery)
                p1 = Process(target=start_ctrl, args=(lottery, now_stage, work_times))
                p1.daemon = True
                p1.start()
                p1.join()

            if not process_flag:
                logger.info('工人已经下班了！')

        if process_flag:
            time.sleep(normal_main_process_time_delta)
        else:
            time.sleep(abnormal_main_process_time_delta)

        # TODO 删除tmp目录中selenium产生的文件夹


def first_run(data):
    # TODO
    # 1. 各种条件判断，包括安装所需库，软件环境判断,以及当前work_dir
    # 2. 复制setup_template.json -> setup.json
    # 3. 提示修改邮箱密码，收/发件人

    for lottery in ['ssq', 'dlt']:
        bag = abg.Begin(lottery)  # 获取往期的开奖数据
        bag.begin()

    mail_sender, mail_password = set_mail_sender()
    cjw_account, cjw_password = set_cjw_account()
    data['mail_options']['sender'] = mail_sender
    data['mail_options']['password'] = mail_password
    data['mail_options']['receivers'] = set_mail_receivers()
    data['cjw_options']['account'] = cjw_account
    data['cjw_options']['password'] = cjw_password
    data['run_times'] = 1
    with open(SETUP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)


def other_test():
    while 1:
        bg = EB('ssq')
        bg.get_experts()
        bg.get_predict_urls(1)
        bg.get_predict_data()
        time.sleep(2400)


if __name__ == '__main__':
    if not os.path.exists(SETUP_FILE):
        shutil.copyfile(SETUP_TEMPLATE, SETUP_FILE)

    with open(SETUP_FILE, 'r', encoding='utf-8') as f:
        content = json.load(f)
        is_first_run = content['run_times']     # 若setup.json文件中的run_times为0,则认为需要进行第一次爬取

    if not is_first_run:
        first_run(content)

    start()
