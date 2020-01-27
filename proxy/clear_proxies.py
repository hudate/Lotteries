from settings import proxies_tb
from tools.logger import Logger
logger = Logger(__name__).logger


def clear_proxies_db():
    try:
        proxies_tb.drop()
        logger.info('成功清除代理数据库。')
    except Exception as e:
        logger.error(e)
