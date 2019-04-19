import re
import pytz
import datetime
import time
import re

if __name__ == '__main__':
    data_pat = re.compile(r'^/(?P<file_name>(?P<name>.*?)\.(?P<suffix>.*))$')
    groups = data_pat.search('/test.data')
    print(groups)
    print(groups.groupdict())
    print(groups.group('name'))
    print(groups.group('suffix'))
    print(groups.group('file_name'))
