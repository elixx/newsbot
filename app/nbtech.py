import datetime
import dateutil.parser
import feedparser
from hashids import Hashids
from random import shuffle

def __init__():
    print("nbtech.py")

########### this is how we do debug output ###########
def z(*text, debug=True):
    if(debug==True):
        s=''
        for n in text: s += str(n) + ' '
        print('debug | ',str(datetime.datetime.now())+'  ',s)

########### arbitrarily hashid a string with salt from config SECRET_KEY ###########
def id_from_string(string,key):
    val = []
    if(len(string) > 64):
        string = string[0:63]
    if(len(string) < 64):
        string += (64-len(string))*"."
    for char in string:
        tempstr = char.encode("utf-8")
        val.append(tempstr.hex())
    tmp = ''.join(val)
    hashids = Hashids(salt=key)
    return(hashids.encode_hex(tmp))

########### article object to be retrieved rss feed ###########
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
            self.id = id_from_string(self.title,str(self.stamp),key)
        else:
            self.id = id

    # return article entry as markdown string
    def tostr(self):
#        dumpstr = '* **' + self.title + '** @`' + self.stamp.strftime("%Y-%m-%d %H:%M:%S") + '` ' + self.link + '\n' # original format
#        dumpstr = '* `' + self.stamp.strftime("%Y-%m-%d %H:%M") + '` **' +  self.title + '** [link]('+ self.link + ')\n' # this is nice but no link previews
#        dumpstr = '* `' + self.stamp.strftime("%Y-%m-%d %H:%M") + '` **' +  self.title + '** - '+ self.link + '\n' # leading timestamp
        dumpstr = '* **' +  self.title + '** - '+ self.link + '\n' # most concise
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
        #a = '### ' + str(self.title) + ' ###' + '\n'
        a = '#### :newspaper: ' + str(self.title) + '\n'
        count = 1
        for arti in self.articles.values():
            if(arti.seen == False):
                a += arti.tostr()
                arti.seen = True
                count += 1
        return(a)

    # update articles from feedparser
    def refresh(self):
        count = 0
        d = feedparser.parse(self.source)
        self.last_updated = datetime.datetime.now()
        for entry in d['entries']:
            if(count >= self.max): break
            try:
                stamp = dateutil.parser.parse(entry['published'])
                nostamp = False
            except (KeyError, ValueError):
                stamp = self.last_updated
                nostamp = True
            if 'id' in entry.keys():
                id = id_from_string(str(entry['id']),self.config.SECRET_KEY)
            elif 'guid' in entry.keys():
                id = id_from_string(str(entry['guid']),self.config.SECRET_KEY)
            elif 'link' in entry.keys():
                id = id_from_string(str(entry['link']),self.config.SECRET_KEY)
            elif 'title' in entry.keys():
                id = id_from_string(str(entry['title']),self.config.SECRET_KEY)

            art = article(id=id,title=str(entry['title']), link=str(entry['link']),source=str(self.source),stamp=stamp)
            try:
                assert(self.articles[id] is not None)
                newentry = False
            except KeyError:
                self.articles[id] = art
                newentry = True
            z("(RSSfeed) refresh() " + ' new:' + str(newentry) + ' ' + id + ' ' + str(stamp) + ' ' + str(nostamp) + ' ' + entry['title'][:18],debug=self.config.debug)
            count += 1

    # count unseen articles
    def unseen(self):
        count = 0
        for arti in self.articles.values():
            if(arti.seen == False):
                count += 1
        z("(RSSfeed) unseen() "+str(count),debug=self.config.debug)
        return(count)
