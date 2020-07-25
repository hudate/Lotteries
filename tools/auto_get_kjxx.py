import time

import requests
import json

from settings import DATA_FILE
from tools.logger import Logger
logger = Logger(__name__).logger


class GetKJXX(object):

    def __init__(self, lottery):
        url = {
            'ssq': 'http://www.cwl.gov.cn/cwl_admin/kjxx/findDrawNotice?name=ssq&issueCount=1',
            'dlt': 'https://www.lottery.gov.cn/tz_kj.json'
        }
        headers = {
            'ssq': {
                'Host': 'www.cwl.gov.cn',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
                'Referer': 'http://www.cwl.gov.cn/kjxx/'
            },
            'dlt': {}
        }

        parse_func = {'ssq': self.ssq_parse,
                      'dlt': self.dlt_parse}
        self.url = url[lottery]
        self.header = headers[lottery]
        self.parse_func = parse_func[lottery]

    def ssq_parse(self, data):
        red_balls = data['result'][0]['red'].split(',')
        blue_balls = data['result'][0]['blue'].split(',')
        return red_balls, blue_balls

    def dlt_parse(self, data):
        balls = data[0]['dlt']['numberCode']
        red_balls = balls[:5]
        blue_balls = balls[5:]
        return red_balls, blue_balls

    def get_kjxx(self):
        data = ''
        lottery_data = []
        try:
            req = requests.get(url=self.url, headers=self.header, timeout=(30, 30))
            data = json.loads(req.text)
        except Exception as e:
            logger.error(e)

        if data:
            lottery_data = self.parse_func(data)

        if len(lottery_data):
            return lottery_data


if __name__ == '__main__':
    kjxx = GetKJXX('dlt')
    lottery_data = kjxx.get_kjxx()
