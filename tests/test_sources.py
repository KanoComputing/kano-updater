#
# test_sources.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the repository sources files
#


import os
import re


def test_paths_matches_install(apt_sources_install):
    from kano_updater.paths import KANO_SOURCES_LIST

    assert os.path.exists(KANO_SOURCES_LIST)


def test_installed_sources_are_correct(apt_sources_install):
    from kano_updater.paths import KANO_SOURCES_LIST

    with open(KANO_SOURCES_LIST, 'r') as src_f:
        sources = src_f.read()

    assert re.compile(
        r'^deb http://repo.kano.me/archive-jessie/ release main$',
        re.MULTILINE
    ).search(sources)
    assert re.compile(
        r'^deb http://repo.kano.me/archive-jessie/ release-urgent main$',
        re.MULTILINE
    ).search(sources)
    assert re.compile(
        r'^deb http://repo.kano.me/raspberrypi-jessie/ jessie main ui$',
        re.MULTILINE
    ).search(sources)
    assert re.compile(
        r'^deb http://jessie.raspbian.repo.os.kano.me/ jessie main contrib non-free rpi$',
        re.MULTILINE
    ).search(sources)

    assert re.compile(r'.*\brelease\b.*', re.MULTILINE).search(sources)
    assert not re.compile(r'.*\bdevel\b.*', re.MULTILINE).search(sources)
    assert not re.compile(r'.*\brc\b.*', re.MULTILINE).search(sources)
    assert not re.compile(r'.*\bscratch\b.*', re.MULTILINE).search(sources)

    assert 'dev.kano.me' not in sources


def test_reference_sources(apt_sources_install):
    from kano_updater.paths import OS_SOURCES_REFERENCE, REFERENCE_STRETCH_LIST

    assert os.path.exists(OS_SOURCES_REFERENCE)
    assert os.path.isdir(OS_SOURCES_REFERENCE)
    assert os.path.exists(REFERENCE_STRETCH_LIST)
    assert os.path.isfile(REFERENCE_STRETCH_LIST)
