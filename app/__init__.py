from .config import Config
from .nbtech import RSSfeed
from .nbtech import z

import datetime
import sys
import os
import pickle
from time import sleep
from matterhook import Webhook

def run():
    ######################## init ########################
    allfeeds = {}
    config = Config()

    # silly constants
    minute = 60
    hour = 60 * minute
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

    for url in config.feedURLs:
        found = False
        for feed in allfeeds.values():
            if(feed.source == url):
                found = True
                z("(main) added feed from .nbfeed: " + url,debug=config.debug)
        if(found == False):
            z("(main) new feed loaded from config: " + url,debug=config.debug)
            allfeeds[url] = RSSfeed(url=url,config=config)

    rmlist = []
    for feed in allfeeds.values():
        if(feed.source not in [url for url in config.feedURLs]):
            z("(main) going to rm " + feed.source + " from allfeeds.",debug=config.debug)
            rmlist.append(feed.source)
            continue
        feed.config = config
        feed.max = config.maxi
    for rm in rmlist:
        z('(main) del ' + rm,debug=config.debug) 
        del allfeeds[rm]

    file = open('.nbfeed','wb')
    pickle.dump(allfeeds,file,protocol=pickle.HIGHEST_PROTOCOL)
    file.close()

    initstr = '## NewsBot ' + config.VERSION + ' starting...\n'
    initstr += 'cache:`' + str(cacheloaded) + '` feeds:`' + str(len(config.feedURLs)) + '` ' + 'refresh:`' + str(config.refresh) + ' min` delay:`' + str(outputdelay) + ' sec` max:`' + str(config.maxi) + '`\n'

    print(initstr)
    if(config.broadcast == True):
        mwh = Webhook(config.baseURL, config.hook)
        mwh.send(initstr)

# for init process debug only, uncomment:
    # raise BaseException('InitCompleted') 

    ######################## main ########################
    while True:
        count = 0
        for feed in allfeeds.values():
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

