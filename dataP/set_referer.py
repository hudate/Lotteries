import random

referer = [
    'https://www.lagou.com/jobs/list_python?&px=default&city=%E6%9D%AD%E5%B7%9E',
    'https://www.lagou.com/jobs/list_%E5%8C%BA%E5%9D%97%E9%93%BE/p-city_215?&cl=false&fromSearch=true&labelWords'
    '=&suginput=',
    'https://www.lagou.com/jobs/list_python/p-city_215?&cl=false&fromSearch=true&labelWords=&suginput=',

]

position_referer = [
    'https://www.lagou.com/jobs/list_python/p-city_252?px=default&district=%E6%AD%A6%E4%BE%AF%E5%8C%BA',
    'https://www.lagou.com/jobs/list_python?&px=default&city=%E6%9D%AD%E5%B7%9E',


]

def ref():
    return random.choice(referer)