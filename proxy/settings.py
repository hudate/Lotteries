#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# from gevent import monkey
# monkey.patch_all()

import pymongo
import pymysql
import redis
import ftplib

redis_db = [1, 3, 5, 7, 9]     # ['拉勾', 'Boss', '猎聘', '51job', '智联']
MR = redis.Redis(host='localhost', port=6379, password='123456')
redis_setting = {

    'PROXIES': {
        'redis': redis.Redis(host='localhost', port=6379, password='123456', db=0),
    },
    'proxies_key': 'proxies',
}


MC = pymongo.MongoClient(host='localhost', port=27017)        # MongoDB客户端设置
mongo_setting = {
    'proxies_coll': MC['Proxies']['proxies']
}

proxies_setting = {
    'delta_time': 10,       # 设置爬虫爬取代理信息的时间间隔，单位：分钟
    'gevent_count': 3,			# 设置获取代理的协程数量
    'stop_pages': 100,      # 获取代理的停止页数
    'proxies_gevent_count': 40,       # gevent协程数
    'proxies_file': 'proxies.csv'
}
