from http.server import HTTPServer, BaseHTTPRequestHandler
import pymysql
from urllib import parse
import traceback
import json
import datetime
from DBUtils.PooledDB import PooledDB
import time
import os

host = ('localhost', 8888)
pool = PooledDB(pymysql, 1, host='127.0.0.1', user='root', passwd='', db='lss', port=3306)
sql_tpl = 'select id, status from qq_status where time > "%s" and time < "%s" order by id'
source_file_path = os.path.split(os.path.realpath(__file__))[0] + '/'

categories = ["手机在线 - WiFi", "手机在线 - 4G", "手机在线 - 3G", "手机在线 - 2G", "在线", "离开", "离线"]
colors = {
    "手机在线 - WiFi": "#42dc4a",
    "手机在线 - 4G": "#d82dd4",
    "手机在线 - 3G": "#6600FF",
    "手机在线 - 2G": "#365880",
    "在线": "#990000",
    "离开": "#9999FF",
    "离线": "#e0474d"
}


class Resquest(BaseHTTPRequestHandler):
    def do_GET(self):
        res = parse.urlparse(self.path)
        _, *path = res.path
        file_name = ''.join(path)
        if 'qq-status.data' in file_name:
            try:
                params = parse.parse_qs(res.query)
                s = params['s'][0] if 's' in params else ''
                e = params['e'][0] if 'e' in params else ''
                if not s:
                    s = (datetime.datetime.now()).strftime('%Y-%m-%d')
                if not e:
                    e = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
                sql = sql_tpl % (s, e)
                print(sql)
                conn = pool.connection()
                cursor = conn.cursor()
                cursor.execute(sql)
                results = cursor.fetchall()
                data = []
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
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception:
                print(traceback.format_exc())
                self.send_error(500, 'Exception: %s' % traceback.format_exc())
        elif 'qq-status.html' in file_name:
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


if __name__ == '__main__':
    server = HTTPServer(host, Resquest)
    print("Starting server, listen at: %s:%s" % host)
    server.serve_forever()
