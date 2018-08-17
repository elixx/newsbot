from .config import Config
from .nbtech import RSSfeed
from .nbtech import z

import datetime
import sys
import os
import pickle
from time import sleep
from matterhook import Webhook

class NewsBot(object):
    def __init__(self,filename='config.conf'):
        self.config = Config(filename)
        self.allfeeds = {}
        self.conf()

    def conf(self):
        self.allfeeds = {}
        self.config = Config()
        self.config.reload()
        self.config.outputdelay = self.config.refresh*60 / len(self.config.feedURLs) # each feed broadcast is distributed evenly across the refresh time window
        try:
            assert(os.path.isfile('.nbfeed') == True)
            file = open('.nbfeed','rb')
            self.allfeeds = pickle.load(file)
            file.close()
            z("(NewsBot) conf(): Loaded article cache from .nbfeed!",debug=self.config.debug)
            cacheloaded=True
        except:
            z("(NewsBot) conf():  No persistent data found.",debug=self.config.debug)
            cacheloaded=False

        for url in self.config.feedURLs:
            found = False
            for feed in self.allfeeds.values():
                if(feed.source == url):
                    found = True
                    z("(NewsBot) conf(): added feed from .nbfeed: " + url,debug=self.config.debug)
            if(found == False):
                z("(NewsBot) conf(): new feed loaded from config: " + url,debug=self.config.debug)
                self.allfeeds[url] = RSSfeed(url=url,config=self.config)

        rmlist = []
        for feed in self.allfeeds.values():
            if(feed.source not in [url for url in self.config.feedURLs]):
                z("(NewsBot) conf(): going to rm " + feed.source + " from allfeeds.",debug=self.config.debug)
                rmlist.append(feed.source)
                continue
            feed.config = self.config
            feed.max = self.config.maxi
        for rm in rmlist:
            z('(NewsBot) conf():  del ' + rm,debug=self.config.debug) 
            del self.allfeeds[rm]

        file = open('.nbfeed','wb')
        pickle.dump(self.allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
        file.close()

        initstr = '## NewsBot ' + self.config.VERSION + ' starting...\n'
        initstr += 'cache:`' + str(cacheloaded) + '` feeds:`' + str(len(self.config.feedURLs)) + '` ' + 'refresh:`'
        initstr += str(self.config.refresh) + ' min` delay:`' + str(self.config.outputdelay/60) + ' min` max:`' + str(self.config.maxi) + '`\n'
        if(self.config.broadcast == True):
            self.mwh = Webhook(self.config.baseURL, self.config.hook)
            self.mwh.send(initstr)

    def run(self):
        while True:
            count = 0
            for feed in self.allfeeds.values():
                count += 1
                z("(run) refreshing feed " + str(count) + ' - ' + feed.source,debug=self.config.debug)
                feed.refresh()
                if(feed.unseen() > 0):
                    z("(run) unseen > 0, calling output()...",debug=self.config.debug)
                    output = feed.output()
                    print(output)
                    if self.config.broadcast: self.mwh.send(output)
                    z("(run) Storing state to .nbfeed",debug=self.config.debug)
                    file = open('.nbfeed','wb')
                    pickle.dump(self.allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
                    file.close()
                z("(run) sleeping outputdelay",self.config.outputdelay,"...",debug=self.config.debug)
                sleep(self.config.outputdelay)
