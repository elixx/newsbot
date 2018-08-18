import datetime
import dateutil.parser
import feedparser
from hashids import Hashids
from random import shuffle

def __init__():
    print("nbtech.py")

def z(*text, debug=True):
    if(debug==True):
        s=''
        for n in text: s += str(n) + ' '
        print('debug | ',str(datetime.datetime.now())+'  ',s)

########### arbitrarily hashid a string with salt from config SECRET_KEY ###########
def id_from_string(string,key):
    val = []
    for char in string:
        tempstr = char.encode("utf-8")
        val.append(tempstr.hex())
    tmp = ''.join(val)
    hashids = Hashids(salt=key)
    return(hashids.encode_hex(tmp))

########### take article data and arbitrarily generate hashid ###########
def id_from_arti(title, salt, key):
    if(len(title)<16):
        title += (16-len(title))*"."
    if(len(salt)<12):
        salt += (12-len(salt))*"."
    return(id_from_string(title[-16]+salt[6:18],key))

########### article object from rss feed ###########
class article(object):
    def __init__(self, title="none",stamp='',text='Lorem Ipsum',link='',source='',id='',key='DEADBEEFF00D'):
        self.title=title
        self.stamp=stamp
        self.text=text
        self.link=link
        self.source=source
        self.seen=False
        self.id=id
        if(self.id == ''):
            if(self.title==''): self.title=self.link
            self.id = id_from_arti(self.title,str(self.stamp),key)
        else:
            self.id = id
# return article entry as markdown string
    def tostr(self):
        dumpstr = '* **' + self.title + '** @`' + self.stamp.strftime("%Y-%m-%d %H:%M:%S") + '` ' + self.link + '\n'
        return(dumpstr)

########### rss feed object ###########
class RSSfeed(object):
    def __init__(self, url, config):
        self.articles = {}
        d = feedparser.parse(url)
        self.source = url
        self.max = config.maxi
        self.config=config
        try:
            self.title = d['feed']['title']
        except KeyError:
            self.title = url
# return all articles as markdown string and mark articles as seen
    def output(self):
        a = '### ' + str(self.title) + ' ###' + '\n'
        count = 1
        for arti in self.articles.values():
            if(arti.seen == False):
                a += arti.tostr()
                arti.seen = True
                count += 1
        return(a)
# update articles from feedparser
    def refresh(self):
        z("feed.refresh(): "+self.source,debug=self.config.debug)
        count = 0
        d = feedparser.parse(self.source)
        for entry in d['entries']:
            if(count >= self.max): break
            try:
                stamp = entry['published']
                stamp = dateutil.parser.parse(stamp)
            except (KeyError, ValueError):
                stamp = datetime.datetime.now()
                z("(RSSfeed)    refresh(): datetime assumed to be now.",debug=self.config.debug)
            id = id_from_arti(str(entry['title']),self.source,self.config.SECRET_KEY)
            art = article(id=id,title=str(entry['title']), link=str(entry['link']),source=str(self.source),stamp=stamp)
            try:
                assert(self.articles[id] is not None)
                newentry = False
            except KeyError:
                self.articles[id] = art
                newentry = True
            z("(RSSfeed)  refresh() " + str(count) + ' new:' + str(newentry) + ' ' + id + '@' + str(stamp) + ' ' + entry['title'][:16],debug=self.config.debug)
            count += 1
        self.last_updated = datetime.datetime.now()
# count unseen articles
    def unseen(self):
        count = 0
        for arti in self.articles.values():
            if(arti.seen == False):
                count += 1
        z("(RSSfeed) " + self.source + " Unseen articles: "+str(count),debug=self.config.debug)
        return(count)
