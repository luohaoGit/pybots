from http.server import HTTPServer, BaseHTTPRequestHandler
import pymysql
from urllib import parse
import traceback
import json
import datetime
from DBUtils.PooledDB import PooledDB
import time
import os
import re
from operator import itemgetter
from itertools import groupby

'''
http://kf.qq.com/faq/1701017fYr2q170101AfIr6J.html

QQ在线状态显示规则是什么？
1、当电脑端QQ、手机QQ、微信、超级QQ都设置为在线状态时，优先显示电脑QQ在线；

2、若电脑端QQ设置为隐身或者离线状态时，会优先显示手机QQ在线；

3、若电脑端QQ和手机QQ都设置退出或者隐身，会优先显示超级QQ在线；

4、若电脑端QQ和手机QQ都退出或隐身，并且超级QQ关闭在线状态，就会显示微信在线。
'''

host = ('localhost', 8888)
pool = PooledDB(pymysql, 1, host='127.0.0.1', user='root', passwd='root', db='lss', port=3306)
source_file_path = os.path.split(os.path.realpath(__file__))[0] + '/'
data_pat = re.compile(r'^/(?P<file_name>(?P<name>.*?)\.(?P<suffix>.*))$')
qq_sql_tpl = 'select id, status from qq_status where time > "%s" and time < "%s" order by id'
music163_sql = 'select * from music_163_total where time > "%s" and time < "%s" order by id'
music163_detail_sql = 'select * from music_163_detail where pid=%s order by song_index'

categories = ["手机在线 - WiFi", "手机在线 - 4G", "手机在线 - 3G", "手机在线 - 2G", "在线", "离开", "离线"]
colors = {
    "iPhone X在线 - WiFi": "#00CC00",
    "iPhone X在线 - 4G": "#99FF00",
    "iPhone X在线 - 3G": "#FFFF00",
    "iPhone X在线 - 2G": "#FF6600",
    "iPhone X在线": "#0099FF",
    "手机在线 - WiFi": "#42dc4a",
    "手机在线 - 4G": "#d82dd4",
    "手机在线 - 3G": "#6600FF",
    "手机在线 - 2G": "#000099",
    "在线": "#006633",
    "忙碌": "#0099FF",
    "离开": "#FF9933",
    "离线": "#4B4B4B"
}


class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        res = parse.urlparse(self.path)
        groups = data_pat.search(res.path)
        if '/favicon.ico' != self.path and groups:
            file_name = groups.group('file_name')
            name = groups.group('name')
            suffix = groups.group('suffix')
            if 'data' == suffix:
                try:
                    params = parse.parse_qs(res.query)
                    s = params['s'][0] if 's' in params else ''
                    e = params['e'][0] if 'e' in params else ''
                    if not s:
                        s = (datetime.datetime.now()).strftime('%Y-%m-%d')
                    if not e:
                        e = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

                    data = []
                    if name == 'qq-status':
                        results = fetch_all(qq_sql_tpl % (s, e))
                        length = len(results)
                        for i, row in enumerate(results):
                            timestamp, status = row
                            timestamp = timestamp * 1000
                            if i < length - 1:
                                next_timestamp = results[i + 1][0] * 1000
                            else:
                                next_timestamp = int(time.time()) * 1000
                            item = {
                                "name": status,
                                "value": [status, timestamp, next_timestamp],
                                "itemStyle": {
                                    "normal": {
                                        "color": colors[status]
                                    }
                                }
                            }
                            data.append(item)
                    elif name == 'music163':
                        results = fetch_all(music163_sql % (s, e))
                        pre_song_arr = []
                        pre_count = 0
                        temp_data = []
                        for i, (rid, count, song_time) in enumerate(results):
                            songs = fetch_all(music163_detail_sql % rid)
                            songs_arr = []
                            listen_songs = []
                            for _, _, s_index, s_id, s_name, s_singer, _ in songs:
                                songs_arr.append({
                                    's_index': s_index,
                                    's_id': s_id,
                                    's_name': s_name,
                                    's_singer': s_singer
                                })
                            if i > 0:
                                listen_songs = calc_listen_songs(pre_song_arr, songs_arr)
                                if count > pre_count and len(listen_songs) == 0:
                                    continue
                            pre_song_arr = songs_arr
                            pre_count = count
                            item = {
                                'id': rid,
                                'count': count,
                                'date': song_time.strftime('%Y-%m-%d'),
                                'time': song_time.strftime('%H:%M:%S'),
                                'listen_songs': listen_songs
                            }
                            temp_data.append(item)

                        if temp_data:
                            for date, items in groupby(temp_data, key=itemgetter('date')):
                                l_songs = [item for item in items]
                                data.append([date, len(l_songs), l_songs])

                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except Exception:
                    print(traceback.format_exc())
                    self.send_error(500, 'Exception: %s' % traceback.format_exc())
            else:
                try:
                    with open(source_file_path + file_name, 'rb') as f:
                        content = f.read()
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(content)
                except IOError:
                    print(traceback.format_exc())
                    self.send_error(404, 'File Not Found: %s' % self.path)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write('not found'.encode())


def fetch_all(sql):
    print(sql)
    conn = pool.connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def calc_listen_songs(pre_songs, songs):
    if not pre_songs:
        return songs
    res = []
    for song in songs:
        pre_song = find_song(song['s_id'], pre_songs)
        if not pre_song:
            res.append(song)
        if pre_song and pre_song[0]['s_index'] > song['s_index']:
            res.append(song)
    return res


def find_song(sid, songs):
    return [s for s in songs if sid == s['s_id']]


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
