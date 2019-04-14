import re
import pytz
from datetime import datetime

if __name__ == '__main__':
    line = '''183.206.18.237 - - [13/Apr/2019:12:49:16 -0400] "GET /tm.jpg HTTP/1.1" 304 0 "https://mail.qq.com/" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36" "-"'''
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