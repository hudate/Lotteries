# -*- coding:utf-8 -*-

import logging
import os
from logging.handlers import RotatingFileHandler
from settings import BASE_DIR

LOG_DIR = BASE_DIR + os.sep + 'log'

LOG_FILE = LOG_DIR + os.sep + 'lotteries.log'


class Logger(object):
    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, logger=None, level='info'):
        if not os.path.exists(LOG_DIR):
            os.mkdir(LOG_DIR)

        # 先获取记录器：
        self.logger = logging.getLogger(logger)

        # 设置日志等级
        self.logger.setLevel(self.levels[level])

        # 设置日志输出格式
        formatter = logging.Formatter('[%(asctime)s] [%(pathname)s:%(lineno)d] - %(levelname)s: %(message)s')

        # 设置日志文件及回滚
        frHandler = RotatingFileHandler(LOG_FILE, maxBytes=20 * 1024 * 1024, backupCount=30, encoding='utf-8')
        frHandler.setLevel(self.levels[level])
        frHandler.setFormatter(formatter)

        # 设置console输出
        console = logging.StreamHandler()
        console.setLevel(self.levels[level])
        console.setFormatter(formatter)

        # 添加以上两个handler
        self.logger.addHandler(frHandler)
        self.logger.addHandler(console)

        frHandler.close()
        console.close()

    # def write_log(self, msg, level='info'):
    #     if level == 'info':
    #         self.logger.info(msg)
    #     elif level == 'debug':
    #         self.logger.debug(msg)
    #     else:
    #         self.logger.error(msg)

    def getlog(self):
        return self.logger
