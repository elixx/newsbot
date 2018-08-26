import os
import random
import configparser

class Config(object):
    def __init__(self, filename='config.conf'):
        self.VERSION="v1.23a"
        self.ON = ["1","true","yes"]
        self.cp = configparser.ConfigParser()
        try:
            assert(os.path.isfile(filename) == True)
            self.filename = filename
            self.reload(filename)
        except:
            file = open(filename,'w')
            seed = str(random.randint(1000000000000, 9999999999999))
            file.write("[newsbot]\nSECRET_KEY = " + seed + "\n")
            file.write("[feeds]\n")
            file.close()
            SECRET_KEY = seed
            print("Default skeleton config created.")
            raise BaseException("BaseConfigGen")
        print('config __init__ done') ########################

    def reload(self,filename='config.conf'):
        try:
            assert(os.path.isfile(filename) == True)
            self.filename = filename
            self.cp.read(filename)
            print("reload continuing")
        except:
            print("reload config file failed!")
            print('punt!!')
            exit()

        feedURLstring = self.cp.get('feeds','feeds')
        self.feedURLs = feedURLstring.split(',')
        self.SECRET_KEY = self.cp.get('newsbot','SECRET_KEY')
        self.baseURL = self.cp.get('newsbot','baseURL')
        self.hook = self.cp.get('newsbot','hook')
        self.channelname = self.cp.get('newsbot','channelname')
        self.username = self.cp.get('newsbot','username')
        self.refresh = int(self.cp.get('newsbot','refresh'))
        self.maxi = int(self.cp.get('newsbot','max'))
 
        self.broadcast = True if self.cp.get('newsbot','broadcast').lower() in self.ON else False
        self.debug = True if self.cp.get('newsbot','debug').lower() in self.ON else False

        self.outputdelay = (self.refresh*60 / len(self.feedURLs))

        if(self.feedURLs is None):
            print('config: no feed URLs')
        else:
            print('config: loaded feeds:')
            for feed in self.feedURLs:
                print(feed)
