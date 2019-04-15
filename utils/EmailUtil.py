#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from configparser import ConfigParser
from email.mime.text import MIMEText
from email.utils import formataddr

__all__ = [
    'send_email',
    ]

cfg = ConfigParser()
cfg.read('email.ini')
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

