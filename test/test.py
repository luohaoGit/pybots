import re
import pytz
import datetime
import time

if __name__ == '__main__':
    a = slice(5, 10, 2)
    s = 'HelloWorld'
    for i in range(*a.indices(len(s))):
        print(s[i])
