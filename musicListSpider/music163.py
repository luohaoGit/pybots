from urllib import request
from html.parser import HTMLParser
from html.entities import name2codepoint


class MusicHTMLParser(HTMLParser):
    def __init__(self):
        super(MusicHTMLParser, self).__init__()
        self.count = 0
        self.musicList = list()
        self.__parseName = ''

    def handle_starttag(self, tag, attrs):
        if ('class', 'm-top') in attrs:
            self.__parseName = 'count'

    def handle_endtag(self, tag):
        self.__parseName = ''

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_data(self, data):
        if self.__parseName == 'count':
            print(data)

    def handle_comment(self, data):
        pass

    def handle_entityref(self, name):
        pass

    def handle_charref(self, name):
        pass

    def error(self, message):
        pass


url = 'https://music.163.com/user/songs/rank?id=544588069'
req = request.Request(url)
req.add_header('Host', 'music.163.com')
req.add_header('Referer', 'https://music.163.com/')
req.add_header('Upgrade-Insecure-Requests', 1)
with request.urlopen(req) as f:
    data = f.read()
    print('Status:', f.status, f.reason)
    html = data.decode('utf-8')
    parser = MusicHTMLParser()
    print(html)
    #parser.feed(html)
