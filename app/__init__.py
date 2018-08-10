try:
    from config import Config
except:
    from .config import Config

import datetime
import sys
import feedparser
from hashids import Hashids
from random import shuffle
from time import sleep
from matterhook import Webhook

def id_from_string(string):
    val = []
    for char in string:
        tempstr = char.encode("utf-8")
        val.append(tempstr.hex())
    tmp = ''.join(val)
    hashids = Hashids(salt=config.SECRET_KEY)
    return(hashids.encode_hex(tmp))

class article(object):
    def __init__(self, title="none",stamp='',text='Lorem Ipsum',link='',source=''):
        self.title=title
        self.stamp=stamp
        self.text=text
        self.link=link
        self.source=source
        self.seen=False
        if(stamp==''):
            self.stamp=datetime.datetime.now()
        else:
            self.stamp = stamp
        tmptitle = self.title.replace(source,'')
        if(len(tmptitle)<16): tmptitle += self.stamp
        self.id = id_from_string(tmptitle[-16]+source[1:9])
    def totext(self):
        dumpstr = '[' + self.source + '] "' + self.title + '" @' + str(self.stamp) + '\n' + '\t' + self.link + '\n'
        return(dumpstr)


class RSSfeed(object):
    def __init__(self, url,maxi=10):
        self.articles = []
        d = feedparser.parse(url)
        self.source = url
        self.title = d['feed']['title']
        self.max = maxi
    def text(self):
        a = '## ' + str(self.title) + ' ##' + '\n'
        count = 1
        for arti in self.articles:
            if(arti.seen == False):
                a += '* ' + str(count) + ': ' + str(arti.title) + ' ' + arti.link +'\n'
                arti.seen = True
                count += 1
        return(a)
    def refresh(self):
        #self.articles = []
        count = 1
        d = feedparser.parse(self.source)
        for entry in d['entries']:
            if(count > self.max): break
            try:
                stamp = entry['published']
            except KeyError:
                stamp = ''
            art = article(title=str(entry['title']), link=str(entry['link']),source=str(self.source),stamp=stamp)
            self.articles.append(art)
            count += 1
        self.last_updated = datetime.datetime.now()
    def unseen(self):
        count = 0
        for arti in self.articles:
          if(arti.seen == False):
              count += 1
        return(count)

config = Config()

if(config.broadcast == True):
    mwh = Webhook(config.baseURL, config.hook)

minute = 60
hour = 60 * minute

refresh = config.refresh * minute
outputdelay = refresh / len(config.feedURLs)
initstr = 'refresh delay is ' + str(config.refresh) + ' minutes\n'
initstr += 'output delay is ' + str(outputdelay) + ' seconds\n'
initstr += 'rss feeds in queue: ' + str(len(config.feedURLs)) + '\n'
initstr += 'newsbot ' + config.VERSION + ' initialized.\n'
print(initstr)

if(config.broadcast == True):
    mwh.send(initstr)

#raise BaseException('TESTBREAK')

def run():
    while True:
        allfeeds = []
        for url in config.feedURLs:
            feed = RSSfeed(url=url)
            allfeeds.append(feed)

        for feed in allfeeds:
            feed.refresh()
            output = ''
            if(config.broadcast == True):
                if(feed.unseen() > 0):
                    output = feed.text()
                    mwh.send(output)
                    print(output)
            sleep(outputdelay)
        sleep(refresh)

