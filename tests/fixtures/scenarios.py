#
# scenarios.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixtures for scenarios
#

import pytest


CMDLINE_TXT = [
    'dwc_otg.lpm_enable=0 net.ifnames=0 logo.nologo console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 usbcore.autosuspend=-1 elevator=deadline ipv6.disable=1 fsck.repair=yes rootwait quiet',
    'dwc_otg.lpm_enable=0 logo.nologo console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 usbcore.autosuspend=-1 elevator=deadline ipv6.disable=1 fsck.repair=yes rootwait quiet net.ifnames=0',
    'dwc_otg.lpm_enable=0 logo.nologo console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 usbcore.autosuspend=-1 elevator=deadline ipv6.disable=1 fsck.repair=yes rootwait quiet',
]


@pytest.fixture(scope='function')
def add_scenario_verifier(monkeypatch, apt):
    '''
    Mocks out the Scenarios::add_scenario() function to verify that the
    supplied versions are valid
    '''

    from tests.fixtures.version import VERSIONS
    version_strings = [v.to_version_string() for v in VERSIONS]

    from kano_updater.scenarios import Scenarios

    def add_scenario_version_tester(dummy_self, from_v, to_v, dummy_func):
        assert from_v in version_strings
        assert to_v in version_strings

    monkeypatch.setattr(Scenarios, 'add_scenario', add_scenario_version_tester)


@pytest.fixture(scope='function', params=(CMDLINE_TXT))
def cmdline_txt(request, fs):
    """TODO"""

    from kano_updater.paths import CMDLINE_TXT_PATH

    # Create a fake file for the cmdline.txt in memory.
    cmdline_txt = fs.CreateFile(CMDLINE_TXT_PATH)
    cmdline_txt.SetContents(request.param)
    yield cmdline_txt

    # Clean up code, remove the file altogether.
    fs.RemoveFile(CMDLINE_TXT_PATH)
