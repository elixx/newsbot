from .config import Config
from .nbtech import RSSfeed
from .nbtech import z

import datetime
import sys
import pickle
from time import sleep
from matterhook import Webhook

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
        if(config.debug==True): z("(main) loading RSSfeeds from feedURLs: " + url)
        feed = RSSfeed(url=url,config=config)
        allfeeds.append(feed)

    try:
        file = open('.nbfeed','rb')
        allfeeds = pickle.load(file)
        file.close()
    except:
        print("No persistent data found.")

    while True:
        for feed in allfeeds:
            if(config.debug==True): z("(main) refreshing " + feed.source)
            feed.refresh()
            if(feed.unseen() > 0):
                if(config.debug==True): z("(main) unseen > 0, calling output()...")
                output = feed.output()
                print(output)
                if(config.broadcast == True):
                    mwh.send(output)
            if(config.debug==True): z("(main) sleeping outputdelay",outputdelay,"...")
            sleep(outputdelay)
        if(config.debug==True): z("(main) sleeping refresh",refresh,"...")
        file = open('.nbfeed','wb')
        pickle.save(allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
        file.close()
        sleep(refresh)

