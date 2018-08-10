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

########### arbitrarily hashid a string with salt from config SECRET_KEY ###########
def id_from_string(string):
    val = []
    for char in string:
        tempstr = char.encode("utf-8")
        val.append(tempstr.hex())
    tmp = ''.join(val)
    hashids = Hashids(salt=config.SECRET_KEY)
    return(hashids.encode_hex(tmp))

########### take article data and arbitrarily generate hashid ###########
def id_from_arti(title, source):
    if(len(title)<16): title += "................"
    if(len(source)<9): source += "........."
    return(id_from_string(title[-16]+source[1:9]))

########### article object from rss feed ###########
class article(object):
    def __init__(self, title="none",stamp='',text='Lorem Ipsum',link='',source='',id=''):
        self.title=title
        self.stamp=stamp
        self.text=text
        self.link=link
        self.source=source
        self.seen=False
        self.id=id
        if(stamp==''):
            self.stamp=datetime.datetime.now()
        else:
            self.stamp = stamp
        if(self.id == ''):
            self.id = id_from_arti(self.title,self.source)
        else:
            self.id = id
# return article entry as markdown string
    def tostr(self):
        dumpstr = '[' + self.source + '] "' + self.title + '" @' + str(self.stamp) + '\n' + '\t' + self.link + '\n'
        return(dumpstr)

########### rss feed object ###########
class RSSfeed(object):
    def __init__(self, url,maxi=15):
        if(config.debug==True): print("RSSfeed init()")
        self.articles = {}
        d = feedparser.parse(url)
        self.source = url
        self.title = d['feed']['title']
        self.max = maxi
# return all articles as markdown string and mark articles as seen
    def output(self):
        a = '## ' + str(self.title) + ' ##' + '\n'
        count = 1
        for arti in self.articles.values():
            if(arti.seen == False):
                a += '* ' + str(count) + ': ' + str(arti.title) + ' ' + arti.link +'\n'
                arti.seen = True
                count += 1
        return(a)
# update articles[] from feedparser
    def refresh(self):
        if(config.debug==True): print("feed.refresh()",self.source)
        count = 0
        d = feedparser.parse(self.source)
        for entry in d['entries']:
            if(config.debug==True): print("refresh() Processing entry " + str(count))
            if(count > self.max): break
            try:
                stamp = entry['published']
            except KeyError:
                stamp = ''
            if(config.debug==True): print("\t Timestamp is " + str(stamp))
            id = id_from_arti(str(entry['title']),self.source)
            if(config.debug==True): print("\trefresh id is " + id)
            if(config.debug==True): print("\trefresh title is " + entry['title'])
            art = article(id=id,title=str(entry['title']), link=str(entry['link']),source=str(self.source),stamp=stamp)
            try:
                assert(self.articles[id] is not None)
                if(config.debug==True): print("\trefresh: Article exists")
            except KeyError:
                self.articles[id] = art
                if(config.debug==True): print("\trefresh: New article created",id)
            count += 1
        self.last_updated = datetime.datetime.now()
# count unseen articles
    def unseen(self):
        count = 0
        for arti in self.articles.values():
            if(config.debug==True): print("RSSfeed.unseen(): " + arti.id,arti.seen,arti.tostr())
            if(arti.seen == False):
                count += 1
        if(config.debug==True): print("Unseen articles:",count)
        return(count)

######################## init ########################

config = Config()

# only create webhook guy if we are broadcasting live
if(config.broadcast == True):
    mwh = Webhook(config.baseURL, config.hook)

# silly constants
minute = 60
hour = 60 * minute
refresh = config.refresh * minute
outputdelay = refresh / len(config.feedURLs) # each feed broadcast is distributed evenly across the refresh time window

initstr = '(newsbot init) refresh delay is ' + str(config.refresh) + ' minutes\n'
initstr += '(newsbot init) output delay is ' + str(outputdelay) + ' seconds\n'
initstr += '(newsbot init) rss feeds in queue: ' + str(len(config.feedURLs)) + '\n'
initstr += '(newsbot init) newsbot ' + config.VERSION + ' initialized.\n'

print(initstr)
if(config.broadcast == True):
    mwh.send(initstr)

# for init process debug only, uncomment:
# raise BaseException('InitCompleted') 
######################## main ########################

def run():
    allfeeds = []
    for url in config.feedURLs:
        if(config.debug==True): print("(main) loading RSSfeeds from feedURLs: " + url)
        feed = RSSfeed(url=url)
        allfeeds.append(feed)

    while True:
        for feed in allfeeds:
            if(config.debug==True): print("(main) refreshing " + feed.source)
            feed.refresh()
            if(feed.unseen() > 0):
                if(config.debug==True): print("(main) unseen > 0, calling output()...")
                output = feed.output()
                print(output)
                if(config.broadcast == True):
                    mwh.send(output)
            if(config.debug==True): print("(main) sleeping outputdelay",outputdelay,"...")
            sleep(outputdelay)
        if(config.debug==True): print("(main) sleeping refresh",refresh,"...")
        sleep(refresh)

