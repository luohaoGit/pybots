#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
from configparser import ConfigParser
import os

__all__ = [
    'send_email',
    ]

cfg = ConfigParser()
source_file_path = os.path.split(os.path.realpath(__file__))[0]
cfg.read(source_file_path + '/email.ini')
sender = cfg.get('account', 'from')
user = cfg.get('account', 'to')
passwd = cfg.get('account', 'pwd')


def send_email(subject, content):
    try:
        msg = MIMEText(content, 'plain', 'utf-8')
        msg['From'] = formataddr(['pybot', sender])
        msg['To'] = formataddr(['fleabag', user])
        msg['Subject'] = subject

        server = smtplib.SMTP_SSL('smtp.qq.com', 465)
        server.login(sender, passwd)
        server.sendmail(sender, [user, ], msg.as_string())
        server.quit()
        print('发送邮件成功')
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    send_email('test', 'hello')

