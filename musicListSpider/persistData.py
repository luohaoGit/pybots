#!/usr/bin/python
# -*- coding: UTF-8 -*-

import glob
import json
import time
import traceback
from datetime import datetime

import pymysql

data_path = 'D:\music163\d4'
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', database='lss', charset='utf8')
main_sql = 'INSERT INTO music_163_total (id, total, time) VALUES (%s, %s, %s);'
detail_sql = 'INSERT INTO music_163_detail (pid, song_index, song_id, song_name, song_singer, time) VALUES (%s, %s, %s, %s, %s, %s);'


if __name__ == '__main__':
    file_names = [name for name in glob.glob(data_path + '/*.dump')]
    for file_name in file_names:
        with open(file_name, 'r') as f:
            dump_dict = json.load(f)
            total = int(dump_dict['total'])
            if total != 0:
                try:
                    songs = dump_dict['songs']
                    if songs:
                        cursor = conn.cursor()
                        time_str = dump_dict['time_str']
                        datetime = datetime.strptime(time_str, "%Y-%m-%d_%H_%M_%S")
                        data_id = int(time.mktime(datetime.timetuple()))

                        song_data = []
                        for song in songs:
                            song_data.append((data_id, song['index'], song['sid'], song['name'], song['singer'], datetime))
                        cursor.execute(main_sql, [data_id, total, datetime])
                        cursor.executemany(detail_sql, song_data)
                        conn.commit()
                        cursor.close()
                except Exception as e:
                    print(traceback.format_exc())
                    conn.rollback()
