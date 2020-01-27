import os
import time

import requests
from selenium.webdriver import ActionChains

from settings import lotteries_predict_data_db as lpdb
from settings import EXPERT_URL as EU
from selenium import webdriver
from tools.logger import Logger
logger = Logger(__name__).logger

# TODO 使用浏览器获取数据


class GetNowStagePredictData(object):

    def __init__(self, lottery, url, expert_id, data_type, data_file, cookies=None):
        self.password = None
        self.account = None
        self.expert = None
        self.stage = None
        self.lottery_id = None
        self.wb = None
        self.url = url
        self.expert_id = expert_id
        self.cookies = cookies
        self.predict_db = lpdb[lottery]
        self.kill_ball_db = lpdb[lottery + '_kill']
        self.data_type = data_type
        self.data_file = data_file

    def use_password(self, user, pwd):
        time.sleep(2)
        self.wb.find_element_by_xpath('//*[@id="comm_username"]').send_keys(user)
        self.wb.find_element_by_xpath('//*[@id="comm_pwd"]').send_keys(pwd)
        try:
            self.wb.find_element_by_xpath('//*[@id="comm_login"]').click()
            self.cookies = self.wb.get_cookies()
            return True
        except:
            return False

    def use_message_code(self, account):
        self.wb.find_element_by_xpath('//*[@id="login_1"]').click()
        self.wb.find_element_by_xpath('//*[@id="mobile"]').send_keys(account)
        time.sleep(0.5)
        self.wb.find_element_by_xpath('//*[@id="getcode"]').click()

        button = self.wb.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/form[1]/div/ul/li[3]/div/div/div[2]')

        x_js = '''
                    function getX(e){
                        var pos = e.getBoundingClientRect();
                        return pos.left
                    }
                    node = document.getElementsByClassName('handler handler_bg')[0]
                    return getX(node)'''

        y_js = '''
                        function getY(e){
                            var pos = e.getBoundingClientRect();
                            return pos.top
                        }
                        node = document.getElementsByClassName('handler handler_bg')[0]
                        return getY(node)'''
        x = self.wb.execute_script(x_js)
        y = self.wb.execute_script(y_js)
        print(x, y, type(x), type(y))

        url = 'https://www.cjcp.com.cn/member/ajax_sjbd.php?'

        requests.post(url, params={'action': 'login_yz', 'mobile': account})

        action = ActionChains(self.wb)  # 实例化一个action对象
        action.move_to_element(button)
        action.click_and_hold(button).perform()  # perform()用来执行ActionChains中存储的行为
        action.reset_actions()
        action.move_by_offset(360, 0).click()  # 移动滑块
        action.reset_actions()

        # a = 0
        # for i in range(360):
        #     a += 120
        #     # self.wb.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/form[1]/div/ul/li[3]/div/div/div[3]').click()
        #     # js = "document.getElementsByClassName(\"handler handler_bg\")[0].style.left='%spx';" % a
        #     # js2 = "document.getElementsByClassName(\"drag_bg\")[0].style.width='%spx';" % a
        #     # js3 = "document.getElementsByClassName(\"drag_text slidetounlock\")[0].style='color: rgb(255, 255, 255);';"
        #     # self.wb.execute_script(js)
        #     # self.wb.execute_script(js2)
        #     # self.wb.execute_script(js3)
        #     action = ActionChains(self.wb)  # 实例化一个action对象
        #     action.click_and_hold(button).perform()  # perform()用来执行ActionChains中存储的行为
        #     action.reset_actions()
        #     action.move_by_offset(x+360, 0).perform()  # 移动滑块
        #     time.sleep(0.1)
        # button.click()

        # self.wb.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/form[1]/div/ul/li[3]/div/div/div[3]').click()
        time.sleep(3)

        print('需要点一下')
        self.wb.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/form[1]/div/ul/li[3]/div/div/div[3]').click()

        self.wb.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/form[1]/div/ul/li[3]/div/div/div[2]').click()
        # self.wb.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/form[1]/div/ul/li[3]/div/div/div[3]')
        captch = input('请输入验证码：')
        self.wb.find_element_by_xpath('//*[@id="yzm"]').send_keys(captch)
        time.sleep(0.5)
        self.wb.find_element_by_xpath('//*[@id="sms_login"]').click()  # 登录按钮
        time.sleep(3)
        self.cookies = self.wb.get_cookies()
        print(self.cookies)

    def login(self):
        self.wb.find_element_by_xpath('/html/body/div[2]/div/div[1]/ul/li[1]/a').click()
        if not self.use_password(self.account, self.password):
            if self.use_message_code(self.account):
                return True
            else:
                pass
                # TODO 当登录不成功时，该怎么做？
        else:
            return True


    def parse_data(self, data):
        pass


    def set_browser(self):
        profile_dir = '/home/hdate/Softwares/Firefox'
        profile = webdriver.FirefoxProfile(profile_dir)
        self.wb = webdriver.Firefox()
        # self

    def get_data(self):
        self.set_browser()
        obj = self.wb.get(self.url)
        while self.cookies is None:
            self.login()

        time.sleep(10)

        self.wb.find_element_by_xpath('/html/body/div[14]/div[1]/div[1]/div/div[3]/div/div[3]/input').click()
        self.wb.find_element_by_xpath('//*[@id="wzcbar"]').click()
        # TODO 解决从firefox中拿出页面内容，并进行解析数据，存入数据库

        # 处理登录
        # 处理在新的tab中打开页面
        # TIDO 处理怎么去获取网页中的内容

    def run(self):
        self.get_data()
