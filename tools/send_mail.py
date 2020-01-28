import json
import os
import smtplib  # smtp服务器
import time
from email.mime.text import MIMEText  # 邮件文本
from settings import REAL, SETUP_FILE
from tools.common import set_mail_data
from tools.logger import Logger
logger = Logger(__name__).logger


class SendMail(object):

    def __init__(self, data_file):
        self.sender = None
        self.password = None
        self.receivers = None
        self.message = None
        self.data_file = data_file
        self.setup_file = SETUP_FILE
        self.data = None
        self.right_ratio = None
        self.get_setup()

    def get_setup(self):
        with open(self.setup_file, 'r', encoding='utf-8') as f:
            contents = json.load(f)['mail_options']
        self.sender = contents['sender']
        self.receivers = contents['receivers']
        self.password = contents['password']

    def get_data(self):
        self.data = set_mail_data(self.data_file)

        if not REAL:
            self.data['front_right_ratio_color'] = '0a0' if self.data['front_right_ratio'] > '60.00%' else 'f00'
            self.data['back_right_ratio_color'] = '0a0' if self.data['back_right_ratio'] > '50.00%' else '00f'

    def set_message(self):
        subject_real = "预测邮件：彩票预测"  # 邮件主题
        subject_test = "测试邮件：彩票预测"
        content_real = '''
        <h3 style="color:#07f"><pre>  第<font color="#f70" face="sans-serif"><u>%s</u></font>期 <font color="#80e" face="sans-serif"><u>%s</u></font>:</pre></h3>
        <h4 style="color:#red;font:{"Arial",12}"><pre>     前区：<font color="#f00" face="sans-serif">%s</font></pre></h4>
        <h4 style="color:#blue;font:{"Arial",12}"><pre>     后区：<font color="#00f" face="sans-serif">%s</font></pre></h4>
        <h3 style="color:#07f"><pre>  共：<font color="#f70" face="sans-serif"><u>%s</u></font>注    计：<font color="#f70" face="sans-serif"><u> %s </u></font>元</h3>
        
        <h3 style="color:#07f"><pre>前区预测专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>
        <h3 style="color:#07f"><pre>前区杀球专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>
        <h3 style="color:#07f"><pre>后区预测专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>
        <h3 style="color:#07f"><pre>后区杀球专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>''' \
                  % (self.data['stage'], self.data['lottery'], ', '.join(self.data['front_predict_balls']),
                     ', '.join(self.data['back_predict_balls']), self.data['lottery_counts'], self.data['lottery_money'],
                     ', '.join(self.data['front_predict_balls']),
                     ', '.join(self.data['back_predict_balls']),
                     ', '.join(self.data['front_predict_experts_list']),
                     ', '.join(self.data['front_kill_experts_list']))

        content_test = '''
                <h3 style="color:#07f"><pre>  第<font color="#f70" face="sans-serif"><u>%s</u></font>期 <font color="#80e" face="sans-serif"><u>%s</u></font>:</pre></h3>
                
                </hr>
                <h3 style="color:#07f"><pre> 本期预测结果：</h3>
                <h4 style="color:#red;font:{"Arial",12}"><pre>     前区： <font color="#f00" face="sans-serif">%s</font></pre></h4>
                <h4 style="color:#blue;font:{"Arial",12}"><pre>     后区： <font color="#00f" face="sans-serif">%s</font></pre></h4>
                <h3 style="color:#07f"><pre>  共： <font color="#f70" face="sans-serif"><u>%s</u></font>注&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;计： <font color="#f70" face="sans-serif"><u> %s </u></font>元</h3>
                
                </hr>
                <h3 style="color:#07f"><pre> 本期开奖情况：</h3>
                <h4 style="color:#red;font:{"Arial",12}"><pre>     前区： <font color="#f00" face="sans-serif">%s</font></pre></h4>
                <h4 style="color:#blue;font:{"Arial",12}"><pre>     后区： <font color="#00f" face="sans-serif">%s</font></pre></h4>
                
                </hr>
                <h3 style="color:#07f"><pre> 本期预测正确率：</h3>
                <h4 style="color:#red;font:{"Arial",12}"><pre>     前区： <font color="#%s" face="sans-serif">%s</font></pre></h4>
                <h4 style="color:#blue;font:{"Arial",12}"><pre>     后区： <font color="#%s" face="sans-serif">%s</font></pre></h4>
                
                <h3 style="color:#07f"><pre>前区预测专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>
                <h3 style="color:#07f"><pre>前区杀球专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>
                <h3 style="color:#07f"><pre>后区预测专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>
                <h3 style="color:#07f"><pre>后区杀球专家：<font color="#f70" face="sans-serif"><u>%s</u></font></h3>''' \
                       % (self.data['stage'], self.data['lottery'], ', '.join(self.data['front_predict_balls']),
                          ', '.join(self.data['back_predict_balls']), self.data['lottery_counts'],
                          self.data['lottery_money'],
                          ', '.join(self.data['lottery_front_balls']),
                          ', '.join(self.data['lottery_back_balls']),
                          self.data['front_right_ratio_color'], self.data['front_right_ratio'],
                          self.data['back_right_ratio_color'], self.data['back_right_ratio'],
                          ', '.join(self.data['front_predict_experts_list']),
                          ', '.join(self.data['front_kill_experts_list']),
                          ', '.join(self.data['back_predict_experts_list']),
                          ', '.join(self.data['back_kill_experts_list']))

        self.message = MIMEText(content_real if REAL else content_test, "html", "utf-8")
        self.message['Subject'] = subject_real if REAL else subject_test    # 邮件主题
        self.message['From'] = self.sender  # 发件人

    def send_mail(self):
        self.get_data()
        self.set_message()
        self.message['To'] = ','.join(self.receivers)  # 收件人
        if self.data:
            try:
                smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
                smtp.login(self.sender, self.password)  # 发件人登录
                smtp.sendmail(self.sender, self.receivers, self.message.as_string())  # as_string 对 message 的消息进行了封装
                smtp.close()
            except Exception as e:
                logger.error('发送邮件失败！ 失败原因：%s' % e)
        else:
            logger.error('未获取到预测文件！')

    def send_test_mail(self):
        self.get_data()
        self.set_message()
        self.message['To'] = '1258670852@qq.com'
        if self.data:
            try:
                smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
                smtp.login(self.sender, self.password)  # 发件人登录
                smtp.sendmail(self.sender, 'hbombdate@163.com', self.message.as_string())
                smtp.close()
            except Exception as e:
                logger.error('发送邮件失败！ 失败原因：%s' % e)
                self.send_flush('发送邮件失败！ 失败原因：%s' % e)
        else:
            flush_str = "%s 主机：%s 发送邮件失败原因：%s" % (time.strftime('%Y-%m-%d %H:%M:%S'), os.popen('hostname').read()[:-1], '未获取到预测文件！')
            logger.error('未获取到预测文件！')
            self.send_flush(flush_str)

    def send_flush(self, flush):
        message = MIMEText(flush, "html", "utf-8")
        message['Subject'] = 'action消息'  # 邮件主题
        message['To'] = 'hdatebomb@163.com'  # 收件人
        message['From'] = self.sender  # 发件人
        try:
            smtp = smtplib.SMTP_SSL("smtp.163.com", 994)  # 实例化smtp服务器
            smtp.login(self.sender, self.password)  # 发件人登录
            smtp.sendmail(self.sender, 'hdatebomb@163.com', message.as_string())  # as_string 对 message 的消息进行了封装
            smtp.close()
        except Exception as e:
            logger.error('发送邮件失败！ 失败原因：%s' % e)


if __name__ == '__main__':
    sm = SendMail('test_data_1.json')
    sm.send_test_mail()




