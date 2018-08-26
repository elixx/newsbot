from .config import Config
from .nbtech import RSSfeed
from .nbtech import z

import datetime
import sys
import os
import pickle
import signal
from time import sleep
from matterhook import Webhook

class NewsBot(object):
    def __init__(self,filename='config.conf'):
        signal.signal(signal.SIGINT, self.signal_handler)
        self.config = Config(filename)
        self.firstrun = True
        self.conf()
        self.kill = False # for SIGHUP handler to tell whether we are actially trying to exit.

    ## reload config object from file and propgate settings into allfeeds{}.
    def conf(self):
        self.allfeeds = {}
        self.config.reload()
        self.config.outputdelay = self.config.refresh*60 / len(self.config.feedURLs) # each feed broadcast is distributed evenly across the refresh time window

        # config has been [re]loaded. check for and load .nbfeed cache
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

        # add all feeds that are listed in config; pickle may have already loaded .nbfeed into allfeeds.
        for url in self.config.feedURLs:
            found = False
            for feed in self.allfeeds.values():
                if(feed.source == url):
                    found = True
                    z("(NewsBot) conf(): added feed from .nbfeed: " + url,debug=self.config.debug)
            if(found == False):
                z("(NewsBot) conf(): new feed loaded from config: " + url,debug=self.config.debug)
                self.allfeeds[url] = RSSfeed(url=url,config=self.config)

        # remove any feeds not present in config file's feeds
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

        # write out allfeeds to .nbfeed, to reflect any cleanup that may have occurred.
        file = open('.nbfeed','wb')
        pickle.dump(self.allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
        file.close()

        # announce startup
        initstr = '### :skull: NewsBot ' + self.config.VERSION + ' starting...\n'
        initstr += 'feeds:`' + str(len(self.config.feedURLs)) + '` ' + 'refresh:`'
        initstr += str(self.config.refresh) + ' min` delay:`' + str(self.config.outputdelay) + ' sec` maxfetch:`' + str(self.config.maxi) + '`\n'
        if(cacheloaded != True):
            initstr += "#### :skull_and_crossbones: Creating new `.nbfeed`.\n"
        if(self.config.broadcast == True and self.firstrun == True):
            self.firstrun = False
            self.mwh = Webhook(self.config.baseURL, self.config.hook)
            self.mwh.send(initstr)


    ## tight loop through allfeeds{} - refresh and output the feeds
    def run(self):
        while True:
            count = 0
            for feed in self.allfeeds.values():
                count += 1
                z("(run) refreshing feed " + str(count) + ' of ' + str(len(self.allfeeds)) + ' - ' + feed.source,debug=self.config.debug)
                feed.refresh()
                self.kill = False
                if(feed.unseen() > 0):
                    output = feed.output() + "\n:hourglass_flowing_sand: _" + str(count) + '/' + str(len(self.allfeeds)) + "_\n"
                    print(output)
                    if self.config.broadcast: self.mwh.send(output)
                    z("(run) Storing state to .nbfeed",debug=self.config.debug)
                    file = open('.nbfeed','wb')
                    pickle.dump(self.allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
                    file.close()
                z("(run) sleeping outputdelay",self.config.outputdelay,"...",debug=self.config.debug)
                sleep(self.config.outputdelay)

    ## handler for when a SIGHUP (or ctrl-c) is received
    def signal_handler(self,sig=0,frame=0):
        if(self.kill):
            exit()
        else:
            print("SIGHUP! reloading config. ^C twice to exit.")
            self.conf()
            self.kill=True
            self.run()
