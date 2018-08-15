#!/usr/bin/python3

import signal
from app import *

signal.signal(signal.SIGHUP, conf)

if __name__ == '__main__':
  conf(firstrun=True)
  run()
