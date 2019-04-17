#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import time
import traceback
from datetime import datetime

import pymysql

file_name = 'E:/python_workspace/network_status_3166756541_2019-04-16_09_06_34.log'
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='lss', charset='utf8')
sql = 'INSERT INTO qq_status (id, status, time) VALUES (%s, %s, %s);'


if __name__ == '__main__':
    with open(file_name, 'r') as f:
        persis_data = []
        pre_status = 'init'
        for line in f:
            status_dict = json.loads(line)
            time_str = status_dict['time_str']
            datetime = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            data_id = int(time.mktime(datetime.timetuple()))
            status = status_dict['status']
            if status != pre_status:
                persis_data.append((data_id, status, datetime))
                pre_status = status
        if persis_data:
            try:
                cursor = conn.cursor()
                cursor.executemany(sql, persis_data)
                conn.commit()
                cursor.close()
            except Exception as e:
                print(traceback.format_exc())
                conn.rollback()
            finally:
                conn.close()
