from .config import Config
from .nbtech import RSSfeed
from .nbtech import z

import datetime
import sys
import os
import pickle
from time import sleep
from matterhook import Webhook

######################## init ########################

config = Config()

# silly constants
minute = 60
hour = 60 * minute
refresh = config.refresh * minute
outputdelay = refresh / len(config.feedURLs) # each feed broadcast is distributed evenly across the refresh time window

initstr = '## NewsBot ' + config.VERSION + ' restarting...\n'
initstr += '(init) refresh delay is `' + str(config.refresh) + ' minutes`, output delay is `' + str(outputdelay) + ' seconds`\n'
initstr += '(init) rss feeds in queue: `' + str(len(config.feedURLs)) + '`\n'
initstr += '(init) newsbot initialized.\n'

print(initstr)
if(config.broadcast == True):
    mwh = Webhook(config.baseURL, config.hook)
    mwh.send(initstr)

# for init process debug only, uncomment:
# raise BaseException('InitCompleted') 
######################## main ########################

def run():
    allfeeds = []

    try:
        assert(os.path.isfile('.nbfeed') == True)
        file = open('.nbfeed','rb')
        allfeeds = pickle.load(file)
        file.close()
        z("(main) Loaded article cache from .nbfeed!",debug=config.debug)
    except:
        z("(main) No persistent data found.",debug=config.debug)

    for url in config.feedURLs:
        found = False
        z("(main) loading RSSfeeds from feedURLs: " + url,debug=config.debug)
        for feed in allfeeds:
            if(feed.source == url):
                found = True 
        if(found == False):
            z("(main) new feed detected " + url,debug=config.debug)
            feed = RSSfeed(url=url,config=config)
            allfeeds.append(feed)

    while True:
        count = 0
        for feed in allfeeds:
            count += 1
            z("(main) refreshing feed " + str(count) + ' - ' + feed.source,debug=config.debug)
            feed.refresh()
            if(feed.unseen() > 0):
                z("(main) unseen > 0, calling output()...",debug=config.debug)
                output = feed.output()
                print(output)
                if(config.broadcast == True):
                    mwh.send(output)
                z("(main) Storing state to .nbfeed",debug=config.debug)
                file = open('.nbfeed','wb')
                pickle.dump(allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
                file.close()
            z("(main) sleeping outputdelay",outputdelay,"...",debug=config.debug)
            sleep(outputdelay)
        z("(main) sleeping refresh",refresh,"...",debug=config.debug)
        sleep(refresh)

