# -*- coding: UTF-8 -*-
import os
import re
import pytz
import json
from datetime import datetime
from pyinotify import WatchManager, Notifier, ProcessEvent, IN_MODIFY


pattern = '''(?P<remote_addr>[\d\.]{7,}) - - (?:\[(?P<datetime>[^\[\]]+)\]) "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>\d+) "(?P<http_referer>[^"]+)" "(?P<user_agent>[^"]+)" "(?:[^"]+)"'''
log_path = '/var/log/nginx/access.log'
file = None
tz = pytz.timezone('Asia/Shanghai')
pic_name = 'px1.gif'
access_log = 'access.log'


'''
183.206.18.237 - - [13/Apr/2019:12:49:16 -0400] "GET /tm.jpg HTTP/1.1" 304 0 "https://mail.qq.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36" "-"
'''

ops = {
    'datetime': lambda timestr: datetime.strptime(timestr, "%d/%b/%Y:%H:%M:%S %z").astimezone(tz),
    'status': int,
    'size': int
}


def extract(line):
    regex = re.compile(pattern)
    matcher = regex.match(line)
    if matcher:
        return {k: ops.get(k, lambda x: x)(v) for k, v in matcher.groupdict().items()}
    else:
        raise Exception('No match')


class ProcessTransientFile(ProcessEvent):
    def process_IN_MODIFY(self, event):
        print("Modify file: %s " % os.path.join(event.path, event.name))
        global file
        line = file.readline()
        if line:
            print(line)
            info = extract(line)
            json_str = json.dumps(info)
            with open(access_log, 'a') as f:
                f.write(json_str + '\n')


def monitor(file_name='.'):
    global file
    file = open(file_name, 'r')
    st_results = os.stat(file_name)
    st_size = st_results[6]
    file.seek(st_size)
    wm = WatchManager()
    notifier = Notifier(wm)
    wm.watch_transient_file(file_name, IN_MODIFY, ProcessTransientFile)
    print('now starting monitor %s' % file_name)
    notifier.loop()


if __name__ == "__main__":
    monitor(log_path)
