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
    def __init__(self):
        self.config = Config()
        self.allfeeds = {}
        self.conf()

def conf(signum=0, frame=0, firstrun=False):
    config = Config()
    refresh = config.refresh * minute
    outputdelay = refresh / len(config.feedURLs) # each feed broadcast is distributed evenly across the refresh time window
    try:
        assert(os.path.isfile('.nbfeed') == True)
        file = open('.nbfeed','rb')
        allfeeds = pickle.load(file)
        file.close()
        z("(main) Loaded article cache from .nbfeed!",debug=config.debug)
        cacheloaded=True
    except:
        z("(main) No persistent data found.",debug=config.debug)
        cacheloaded=False

    def conf(self):
        self.allfeeds = {}
        self.config = Config()
        self.config.reload()
        self.config.outputdelay = self.config.refresh / len(self.config.feedURLs) # each feed broadcast is distributed evenly across the refresh time window
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

    print(initstr)
    if(firstrun==True):
        if(config.broadcast == True):
            mwh = Webhook(config.baseURL, config.hook)
            mwh.send(initstr)

        print(initstr)
        if(self.config.broadcast == True):
            mwh = Webhook(self.config.baseURL, self.config.hook)
            mwh.send(initstr)
