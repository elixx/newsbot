import os
import random
import configparser


class Config(object):
    filename = 'config.conf'
    VERSION="v1.1"
    ON = ["1","true","yes"]

    config = configparser.ConfigParser()

    try:
        assert(os.path.isfile(filename) == True)
        config.read(filename)
        SECRET_KEY = config.get('newsbot','SECRET_KEY')
        print("config loaded")
    except:
        file = open(filename,'w')
        seed = str(random.randint(1000000000000, 9999999999999))
        file.write("[newsbot]\nSECRET_KEY = " + seed + "\n")
        file.write("[feeds]\n")
        file.close()
        SECRET_KEY = seed
        print("Default skeleton config created.")
        exit("punt!")

    baseURL = config.get('newsbot','baseURL')
    hook = config.get('newsbot','hook')
    channelname = config.get('newsbot','channelname')
    username = config.get('newsbot','username')
    refresh = int(config.get('newsbot','refresh'))
    maxi = int(config.get('newsbot','max'))

    if(config.get('newsbot','broadcast').lower() in ON):
        broadcast = True
    else:
        broadcast = False

    if(config.get('newsbot','debug').lower() in ON):
        debug = True
    else:
        debug = False
    print("config: config.debug is " + str(debug))

    feedURLstring = config.get('feeds','feeds')
    feedURLs = feedURLstring.split(',')

    if(feedURLs is None):
        print('config: no feed URLs')
    else:
        print('config: loaded feeds:')
        for feed in feedURLs:
                print(feed)
        print()

