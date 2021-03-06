#!/usr/bin/env python

# monitor-stub.py
#
# Copyright (C) 2015-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2

"""
A program for testing the updater monitor

Usage:
  monitor-stub.py [--forking] [--signal] [--gui] <time> <rc>


"""
import docopt
import time
import os
from kano_updater.monitor_heartbeat import heartbeat
args = docopt.docopt(__doc__)
wait = int(args['<time>'])
start = time.time()

while time.time() < start + wait:
    if args['--forking']:
        os.system('sleep 1')
    else:
        time.sleep(1)
    if args['--signal']:
        heartbeat()


exit(int(args['<rc>']))
