# -*- coding: UTF-8 -*-
import json
import os
import sys
import time
import traceback
from datetime import datetime
from threading import Timer

import pytz
from appium import webdriver

from ..utils.EmailUtil import send_email

qq = sys.argv[1]
desired_caps = {
    'platformName': 'Android',
    'platformVersion': '5.1.1',
    'deviceName': '127.0.0.1:5555',
    'appPackage': 'com.tencent.mobileqq',
    'appActivity': 'com.tencent.mobileqq.activity.SplashActivity',
    'unicodeKeyboard': True,
    'noReset': True,
    'newCommandTimeout': 60 * 5
}
driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
driver.implicitly_wait(20)
driver.find_element_by_id('com.tencent.mobileqq:id/et_search_keyword').send_keys(qq)
tz = pytz.timezone('Asia/Shanghai')
log_path = './network_status_' + qq + '_' + datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d_%H_%M_%S') + '.log'
pre_status_file = './pre_status_' + qq
email_subject = 'tencent qq'
exception_times = 0


def parse_network_status(inc, pre_status):
    global exception_times
    ns = pre_status
    try:
        driver.find_element_by_id('com.tencent.mobileqq:id/result_layout').find_element_by_xpath('//*[@text="(' + qq + ')"]').click()
        time.sleep(1)
        ns_eles = driver.find_elements_by_id('com.tencent.mobileqq:id/title_sub')
        if ns_eles:
            ns = ns_eles[0].text
        else:
            ns = 'offline'
        driver.find_element_by_id('com.tencent.mobileqq:id/rlCommenTitle').find_elements_by_class_name('android.widget.LinearLayout')[0].click()
        now = datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d %H:%M:%S')
        content = qq + "\t" + now + "\t" + pre_status + " =======> " + ns
        print(content)
        dump_log(Status(now, qq, ns))
        if pre_status != 'init' and pre_status != ns:
            send_email(email_subject, content)
    except Exception as ex:
        exception_times += 1
        print(traceback.format_exc())
        if exception_times == 3:
            raise ex

    t = Timer(inc, parse_network_status, (inc, ns))
    t.start()


def dump_log(status):
    with open(log_path, "a") as log_file:
        json.dump(status, log_file, default=lambda obj: obj.__dict__)
        log_file.write("\n")
    with open(pre_status_file, 'w') as status_file:
        status_file.write(status.status)


class Status(object):
    def __init__(self, time_str, qq, status):
        self.time_str = time_str
        self.qq = qq
        self.status = status


if __name__ == '__main__':
    try:
        init_status = 'init'
        if not os.path.exists(pre_status_file):
            with open(pre_status_file, 'w+') as f:
                f.write(init_status)
        else:
            with open(pre_status_file, 'r') as f:
                init_status = f.read()
        parse_network_status(60 * 1, init_status)
    except Exception as e:
        print(traceback.format_exc())
