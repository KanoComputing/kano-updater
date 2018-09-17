#!/usr/bin/env python
#
# monitor_wrap.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2x
#
# Wrapper for when the monitor needs to be tested in a separate process to pytest
#
import sys
import os
sys.path.append(os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'fixtures/mock_imports'
))
import kano_updater.monitor
import sys
test_cmd = sys.argv[1:]
sys.exit(kano_updater.monitor.run(test_cmd))
