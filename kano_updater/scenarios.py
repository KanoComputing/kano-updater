
# scenarios.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

import os

from kano.logging import logger
from kano_updater.osversion import OSVersion
from kano_updater.utils import install, remove_user_files, update_failed, \
    purge, rclocal_executable, migrate_repository
from kano.utils import run_cmd_log, get_user_unsudoed, write_file_contents


class Scenarios(object):
    _type = ""

    def __init__(self, old, new):
        self._scenarios = {}

        if isinstance(old, OSVersion):
            self._old = old
        else:
            self._old = OSVersion.from_version_string(old)

        if isinstance(new, OSVersion):
            self._new = new
        else:
            self._new = OSVersion.from_version_string(new)

        self._mapping()

    def _mapping(self):
        pass

    def covers_update(self):
        min_v = str(self._old)
        max_v = str(self._new)

        current_v = min_v
        while current_v < max_v:
            next_step = None
            for from_v, to_v in self._scenarios.iterkeys():
                if current_v == from_v:
                    next_step = to_v
                    break

            if next_step is None:
                return False
            else:
                current_v = next_step

        return True

    def add_scenario(self, from_v, to_v, func):
        self._scenarios[(str(from_v), str(to_v))] = func

    def run(self):
        log = 'Running the {}-update scripts...'.format(self._type)
        logger.info(log)

        current_v = str(self._old)
        while current_v < str(self._new):
            step_found = False
            for (from_v, to_v), func in self._scenarios.iteritems():
                if current_v == from_v:
                    msg = "Running {}-update from {} to {}.".format(
                        self._type,
                        from_v,
                        to_v
                    )
                    logger.info(msg)
                    func()
                    current_v = to_v
                    step_found = True
                    break

            if not step_found:
                msg = "{}-update step missing".format(self._type)
                update_failed(msg)
                raise Exception(msg)


class PreUpdate(Scenarios):
    _type = "pre"

    def _mapping(self):
        self.add_scenario("Kanux-Beta-1.0.3", "Kanux-Beta-1.1.0",
                          self.beta_103_to_beta_110)

        self.add_scenario("Kanux-Beta-1.1.0", "Kanux-Beta-1.1.1",
                          self.beta_110_to_beta_111)

        self.add_scenario("Kanux-Beta-1.1.1", "Kanux-Beta-1.2.0",
                          self.beta_111_to_beta_120)

        # v1.2.1 is the first image sent to China (+18K units)
        self.add_scenario("Kanux-Beta-1.2.0", "Kanux-Beta-1.2.1",
                          self.beta_120_to_beta_121)

        self.add_scenario("Kanux-Beta-1.2.1", "Kanux-Beta-1.2.2",
                          self.beta_121_to_beta_122)

        self.add_scenario("Kanux-Beta-1.2.2", "Kanux-Beta-1.2.3",
                          self.beta_122_to_beta_123)

        self.add_scenario("Kanux-Beta-1.2.3", "Kanux-Beta-1.2.4",
                          self.beta_123_to_beta_124)

        self.add_scenario("Kanux-Beta-1.2.4", "Kanux-Beta-1.2.5",
                          self.beta_124_to_beta_125)

        self.add_scenario("Kanux-Beta-1.2.5", "Kanux-Beta-1.3.1",
                          self.beta_125_to_beta_131)

        self.add_scenario("Kanux-Beta-1.3.1", "Kanux-Beta-1.3.2",
                          self.beta_131_to_beta_132)

    def beta_103_to_beta_110(self):
        pass

    def beta_110_to_beta_111(self):
        pass

    def beta_111_to_beta_120(self):
        purge("kano-unlocker")
        repo_url = "deb http://mirrordirector.raspbian.org/raspbian/ wheezy main contrib non-free rpi"
        write_file_contents('/etc/apt/sources.list', repo_url + '\n')
        run_cmd_log('apt-get -y clean')
        run_cmd_log('apt-get -y update')

    def beta_120_to_beta_121(self):
        pass

    def beta_121_to_beta_122(self):
        pass

    def beta_122_to_beta_123(self):
        # Migrate users from the official RaspberryPI repo to Kano mirrored site
        migrate_repository('/etc/apt/sources.list.d/raspi.list',
                           'archive.raspberrypi.org/debian',
                           'repo.kano.me/raspberrypi')

    def beta_123_to_beta_124(self):
        pass

    def beta_124_to_beta_125(self):
        pass

    def beta_125_to_beta_131(self):
        pass

    def beta_131_to_beta_132(self):
        pass

    # Not used at the moment: dev.kano.me > repo.kano.me
    def _migrate_repo_url(self):
        migrate_repository('/etc/apt/sources.list.d/kano.list',
                           'dev.kano.me',
                           'repo.kano.me')


class PostUpdate(Scenarios):
    _type = "post"

    def _mapping(self):
        self.add_scenario("Kanux-Beta-1.0.3", "Kanux-Beta-1.1.0",
                          self.beta_103_to_beta_110)

        self.add_scenario("Kanux-Beta-1.1.0", "Kanux-Beta-1.1.1",
                          self.beta_110_to_beta_111)

        self.add_scenario("Kanux-Beta-1.1.1", "Kanux-Beta-1.2.0",
                          self.beta_111_to_beta_120)

        self.add_scenario("Kanux-Beta-1.2.0", "Kanux-Beta-1.2.1",
                          self.beta_120_to_beta_121)

        self.add_scenario("Kanux-Beta-1.2.1", "Kanux-Beta-1.2.2",
                          self.beta_121_to_beta_122)

        self.add_scenario("Kanux-Beta-1.2.2", "Kanux-Beta-1.2.3",
                          self.beta_122_to_beta_123)

        self.add_scenario("Kanux-Beta-1.2.3", "Kanux-Beta-1.2.4",
                          self.beta_123_to_beta_124)

        self.add_scenario("Kanux-Beta-1.2.4", "Kanux-Beta-1.2.5",
                          self.beta_124_to_beta_125)

        self.add_scenario("Kanux-Beta-1.2.5", "Kanux-Beta-1.3.1",
                          self.beta_125_to_beta_131)

        self.add_scenario("Kanux-Beta-1.3.1", "Kanux-Beta-1.3.2",
                          self.beta_131_to_beta_132)

    def beta_103_to_beta_110(self):
        rclocal_executable()
        remove_user_files(['.kdeskrc'])
        install('kano-widgets')

    def beta_110_to_beta_111(self):
        install('kano-sound-files kano-init-flow')
        # Create first boot file so we don't annoy existent users
        username = get_user_unsudoed()
        first_boot = '/home/%s/.kano-settings/first_boot' % username
        try:
            open(first_boot, 'w').close()
        except:
            pass

    def beta_111_to_beta_120(self):
        run_cmd_log("kano-apps install --no-gui painter epdfview geany codecademy calculator leafpad vnc")

    def beta_120_to_beta_121(self):
        install('espeak')

    def beta_121_to_beta_122(self):
        run_cmd_log("kano-apps install --no-gui --icon-only xbmc")

        if not os.path.exists("/etc/apt/sources.list.d/kano-xbmc.list"):
            run_cmd_log("apt-key adv --keyserver keyserver.ubuntu.com --recv-key 5243CDED")
            with open("/etc/apt/sources.list.d/kano-xbmc.list", "w") as f:
                f.write("deb http://repo.kano.me/xbmc/ wheezy contrib\n")

    def beta_122_to_beta_123(self):
        pass

    def beta_123_to_beta_124(self):
        # Rename Snake custom theme
        username = get_user_unsudoed()
        path = '/home/%s/Snake-content/' % username
        old_name = 'custom_theme'
        if os.path.exists(path + old_name):
            new_name = 'custom-theme.xml'
            try:
                os.rename(path + old_name, path + new_name)
            except:
                pass

    def beta_124_to_beta_125(self):
        pass

    def beta_125_to_beta_131(self):
        install('kano-draw')
        
    def beta_131_to_beta_132(self):
        pass
