#!/usr/bin/python
# -*- coding: UTF-8 -*-

import json
import os
import sys
import time
import traceback
import platform
from datetime import datetime
from threading import Timer
from urllib.parse import parse_qs
from ..utils.EmailUtil import send_email

import pytz
from bs4 import BeautifulSoup
# http://npm.taobao.org/mirrors/chromedriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

uid = sys.argv[1]
source_file_path = os.path.split(os.path.realpath(__file__))[0]
driver_path = source_file_path + '/chromedriver'
if platform.system() == 'Windows':
    driver_path += '.exe'
source_url = 'https://music.163.com/user/songs/rank?id=' + uid
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
drive = webdriver.Chrome(driver_path, options=chrome_options)
tz = pytz.timezone('Asia/Shanghai')
timestamp_file_name = 'timestamp_of_' + uid
dump_file_name_tpl = '{timestamp}.' + uid + '.dump'
email_subject = 'music 163'


def get_song(inc, pre_count, pre_song_list):
    now_str = get_now_str()
    print(now_str)
    count = 0
    song_list = []
    error = ''
    try:
        soup = get_soup(source_url)
        count = int(soup.select("#m-record")[0]['data-songs'])
        print(count)
        for node in soup.select(".j-flag li"):
            divs = node.select('div')
            index = divs[0].select_one('.num').get_text()[:-1]
            sid = parse_qs(divs[1].select_one('a')['href'])['/song?id'][0]
            name = divs[1].select_one('b')['title']
            singer = divs[1].select_one('span span').select_one('span')['title']
            song = Song(index, sid, name, singer)
            song_list.append(song)
    except Exception as ex:
        error = traceback.format_exc()
        print(error)

    up_songs = []
    new_songs = []
    has_never_heard = pre_count < count
    for s in song_list:
        if s not in pre_song_list:
            new_songs.append(s)
        else:
            pre_index = pre_song_list.index(s)
            s_index = song_list.index(s) + 1
            if s_index < pre_index:
                up_songs.append(s)

    if has_never_heard or len(new_songs) > 0 or len(up_songs) > 0:
        dump_file(Dump(now_str, count, song_list), dump_file_name_tpl.format(timestamp=now_str))
        with open(timestamp_file_name, 'w') as file:
            file.write(now_str)
        content = '''time: {time}\ntotal: {total}\ndelta: {delta} \nnew:{new}\nup:{up}'''\
            .format(time=now_str, total=count,
                    delta=count - pre_count,
                    new="\n".join(list(map(Song.__repr__, new_songs))),
                    up="\n".join(list(map(Song.__repr__, up_songs))),)
        send_email(email_subject, content)

    if error:
        send_email(email_subject, error)

    if not len(song_list):
        song_list = pre_song_list

    if count == 0:
        count = pre_count

    t = Timer(inc, get_song, (inc, count, song_list))
    t.start()


def get_soup(url):
    drive.get(url)
    time.sleep(2)
    iframe = drive.find_elements_by_id('g_iframe')[0]
    drive.switch_to.frame(iframe)
    return BeautifulSoup(drive.page_source, "lxml")


def get_now_str():
    return datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d_%H_%M_%S')


class Song(object):
    def __init__(self, index, sid, name, singer):
        self.index = index
        self.sid = sid
        self.name = name
        self.singer = singer

    def __str__(self):
        return '{self.index}.{self.sid}.{self.name}-{self.singer}'.format(self=self)

    __repr__ = __str__

    def __eq__(self, other):
        return self.sid == other.sid


class Dump(object):
    def __init__(self, time_str, total, songs):
        self.time_str = time_str
        self.total = total
        self.songs = []
        for s in songs:
            if type(s) == dict:
                self.songs.append(Song(s['index'], s['sid'], s['name'], s['singer']))
            else:
                self.songs.append(s)


def dump_file(dump, file_name):
    json.dump(dump, open(file_name, 'w+'), default=lambda obj: obj.__dict__)


if __name__ == '__main__':
    try:
        pre_timestamp = ''
        if not os.path.exists(timestamp_file_name):
            with open(timestamp_file_name, 'w+') as f:
                pre_timestamp = get_now_str()
                f.write(pre_timestamp)
        else:
            with open(timestamp_file_name, 'r') as f:
                pre_timestamp = f.read()

        if not pre_timestamp:
            raise RuntimeError('no pre_timestamp error')

        dump_file_name = dump_file_name_tpl.format(timestamp=pre_timestamp)
        if not os.path.exists(dump_file_name):
            empty_dump = Dump(pre_timestamp, 0, [])
            dump_file(empty_dump, dump_file_name)

        res = json.load(open(dump_file_name, 'r'))
        pre_dump = Dump(res['time_str'], res['total'], res['songs'])

        get_song(60 * 1, pre_dump.total, pre_dump.songs)
    except Exception as e:
        print(traceback.format_exc())

