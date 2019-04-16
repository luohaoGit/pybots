import re
import pytz
from datetime import datetime

if __name__ == '__main__':
    line = '''49.74.84.35 - - [16/Apr/2019:11:27:26 +0800] "GET /px1.gif?t=1555385217781 HTTP/1.1" 200 826 "-" "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36" "-"'''
    if line:
        print(line.find('px1.gif'))
    pattern = '''(?P<remote_addr>[\d\.]{7,}) - - (?:\[(?P<datetime>[^\[\]]+)\]) "(?P<request>[^"]+)" (?P<status>\d+) (?P<size>\d+) "(?P<http_referer>[^"]+)" "(?P<user_agent>[^"]+)" "(?:[^"]+)"'''
    regex = re.compile(pattern)
    matcher = regex.match(line)

    tz = pytz.timezone('Asia/Shanghai')
    ops = {
        'datetime': lambda timestr: datetime.strptime(timestr, "%d/%b/%Y:%H:%M:%S %z").astimezone(tz),
        'status': int,
        'size': int
    }

    if matcher:
        res = {k: ops.get(k, lambda x: x)(v) for k, v in matcher.groupdict().items()}

        for k, v in res.items():
            print(k, v)
    else:
        raise Exception('No match')