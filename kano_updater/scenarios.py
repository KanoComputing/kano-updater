
# scenarios.py
#
# Copyright (C) 2014-2016 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#

import os

from kano.logging import logger

from kano_updater.os_version import OSVersion, TARGET_VERSION
from kano_updater.utils import install, remove_user_files, update_failed, \
    purge, rclocal_executable, migrate_repository, get_users, run_for_every_user
from kano.utils import run_cmd_log, get_user_unsudoed, write_file_contents, \
    is_installed


class Scenarios(object):
    _type = ""

    def __init__(self, old):
        self._scenarios = {}

        if isinstance(old, OSVersion):
            self._old = old
        else:
            self._old = OSVersion.from_version_string(old)

        self._mapping()

    def _mapping(self):
        pass

    def covers_update(self):
        min_v = str(self._old)
        max_v = str(TARGET_VERSION)

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
        while current_v < str(TARGET_VERSION):
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

        self.add_scenario("Kanux-Beta-1.3.2", "Kanux-Beta-1.3.3",
                          self.beta_132_to_beta_133)

        self.add_scenario("Kanux-Beta-1.3.3", "Kanux-Beta-1.3.4",
                          self.beta_133_to_beta_134)

        self.add_scenario("Kanux-Beta-1.3.4", "Kanux-Beta-2.0.0",
                          self.beta_134_to_beta_200)

        self.add_scenario("Kanux-Beta-2.0.0", "Kanux-Beta-2.0.1",
                          self.beta_200_to_beta_201)

        self.add_scenario("Kanux-Beta-2.0.1", "Kanux-Beta-2.1.0",
                          self.beta_201_to_beta_210)

        self.add_scenario("Kanux-Beta-2.1.0", "Kanux-Beta-2.2.0",
                          self.beta_210_to_beta_220)

        self.add_scenario("Kanux-Beta-2.2.0", "Kanux-Beta-2.3.0",
                          self.beta_220_to_beta_230)

        self.add_scenario("Kanux-Beta-2.3.0", "Kanux-Beta-2.4.0",
                          self.beta_230_to_beta_240)

        self.add_scenario("Kanux-Beta-2.4.0", "Kanux-Beta-3.0.0",
                          self.beta_240_to_beta_300)

        self.add_scenario("Kanux-Beta-3.0.0", "Kanux-Beta-3.1.0",
                          self.beta_300_to_beta_310)

        self.add_scenario("Kanux-Beta-3.1.0", "Kanux-Beta-3.2.0",
                          self.beta_310_to_beta_320)

        self.add_scenario("Kanux-Beta-3.2.0", "Kanux-Beta-3.3.0",
                          self.beta_320_to_beta_330)

        self.add_scenario("Kanux-Beta-3.3.0", "Kanux-Beta-3.4.0",
                          self.beta_330_to_beta_340)

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

    def beta_132_to_beta_133(self):
        # Downgrade the improved FBTurbo X11 driver
        # to the official stable version
        run_cmd_log('apt-get -y remove xf86-video-fbturbo-improved')
        run_cmd_log('apt-get -y install xserver-xorg-video-fbturbo')

    def beta_133_to_beta_134(self):
        pass

    def beta_134_to_beta_200(self):
        pass

    def beta_200_to_beta_201(self):
        # All users upgrading from KanoOS 1.* should have their
        # users home directory permissions fixed
        run_cmd_log('/usr/bin/repair-homedir-permissions')

    def beta_201_to_beta_210(self):
        pass

    def beta_210_to_beta_220(self):
        pass

    def beta_220_to_beta_230(self):
        out, err, rv = run_cmd_log('apt-mark showauto | grep modemmanager')
        # If the user has manually installed modemmanager, it will be marked as
        # manually installed.
        # Return value will be 0 if modemmanager is marked as an auto installed
        if rv == 0:
            out, err, rv = run_cmd_log('apt-get -y purge modemmanager')
            if rv == 0:
                run_cmd_log('apt-get -y autoremove')

    def beta_230_to_beta_240(self):
        run_cmd_log('apt-get install bluez')

    def beta_240_to_beta_300(self):
        pass

    def beta_300_to_beta_310(self):
        pass

    def beta_310_to_beta_320(self):
        pass

    def beta_320_to_beta_330(self):
        pass

    def beta_330_to_beta_340(self):
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

        self.add_scenario("Kanux-Beta-1.3.2", "Kanux-Beta-1.3.3",
                          self.beta_132_to_beta_133)

        self.add_scenario("Kanux-Beta-1.3.3", "Kanux-Beta-1.3.4",
                          self.beta_133_to_beta_134)

        self.add_scenario("Kanux-Beta-1.3.4", "Kanux-Beta-2.0.0",
                          self.beta_134_to_beta_200)

        self.add_scenario("Kanux-Beta-2.0.0", "Kanux-Beta-2.0.1",
                          self.beta_200_to_beta_201)

        self.add_scenario("Kanux-Beta-2.0.1", "Kanux-Beta-2.1.0",
                          self.beta_201_to_beta_210)

        self.add_scenario("Kanux-Beta-2.1.0", "Kanux-Beta-2.2.0",
                          self.beta_210_to_beta_220)

        self.add_scenario("Kanux-Beta-2.2.0", "Kanux-Beta-2.3.0",
                          self.beta_220_to_beta_230)

        self.add_scenario("Kanux-Beta-2.3.0", "Kanux-Beta-2.4.0",
                          self.beta_230_to_beta_240)

        self.add_scenario("Kanux-Beta-2.4.0", "Kanux-Beta-3.0.0",
                          self.beta_240_to_beta_300)

        self.add_scenario("Kanux-Beta-3.0.0", "Kanux-Beta-3.1.0",
                          self.beta_300_to_beta_310)

        self.add_scenario("Kanux-Beta-3.1.0", "Kanux-Beta-3.2.0",
                          self.beta_310_to_beta_320)

        self.add_scenario("Kanux-Beta-3.2.0", "Kanux-Beta-3.3.0",
                          self.beta_320_to_beta_330)

        self.add_scenario("Kanux-Beta-3.3.0", "Kanux-Beta-3.4.0",
                          self.beta_330_to_beta_340)

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
        run_cmd_log("kano-apps install --no-gui painter epdfview geany " \
                    "codecademy calculator leafpad vnc")

    def beta_120_to_beta_121(self):
        install('espeak')

    def beta_121_to_beta_122(self):
        run_cmd_log("kano-apps install --no-gui --icon-only xbmc")

        if not os.path.exists("/etc/apt/sources.list.d/kano-xbmc.list"):
            run_cmd_log("apt-key adv --keyserver keyserver.ubuntu.com " \
                        "--recv-key 5243CDED")
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
            except Exception:
                pass

    def beta_124_to_beta_125(self):
        pass

    def beta_125_to_beta_131(self):
        install('kano-draw')

    def beta_131_to_beta_132(self):
        pass

    def beta_132_to_beta_133(self):
        run_cmd_log('kano-apps install --no-gui terminal-quest')

    def beta_133_to_beta_134(self):
        pass

    def beta_134_to_beta_200(self):
        if not is_installed('kano-character-cli'):
            logger.info(
                "kano-character-cli not installed, "\
                "attempt to install kano-profile"
            )
            install('kano-profile')
        run_cmd_log(
            'kano-character-cli -c "judoka" "Hair_Black" "Skin_Orange" -s'
        )

    def beta_200_to_beta_201(self):
        remove_user_files(['.kdesktop/YouTube.lnk'])

    def beta_201_to_beta_210(self):
        from kano_settings.system.advanced import set_everyone_cookies
        set_everyone_cookies()

    def beta_210_to_beta_220(self):
        install('telnet python-serial')
        try:
            from kano_profile.apps import save_app_state_variable_all_users

            save_app_state_variable_all_users("init-flow-completed", "level", 1)

        except ImportError:
            logger.error(
                "Could not award Computer Commander badge, import error"
            )

    def beta_220_to_beta_230(self):
        # A few helper fns to keep the scenario tidy
        def ensure_system_group_exists(group):
            if(os.system('getent group {}'.format(group)) != 0):
                rc = os.system('groupadd -f -r {}'.format(group))
                if rc != 0:
                    logger.error("could not create group")

        def add_users_to_group(group):
            try:
                linux_users = get_users()
                if not linux_users:
                    logger.error('beta_220_to_beta_230: linux_users is empty!')

                for user in linux_users:
                    os.system('sudo usermod -a -G {} {}'.format(group, user))

            except Exception as e:
                logger.error(
                    "Couldn't add users to {} group - [{}]".format(group, e)
                )

        def add_i2c_module_to_auto_loaded():
            try:
                found_i2c_dev = False

                with open('/etc/modules', 'r') as f:
                    for line in f:
                        if line.strip() == 'i2c_dev':
                            found_i2c_dev = True

                if not found_i2c_dev:
                    with open('/etc/modules', 'a') as f:
                        f.write('\ni2c_dev\n')

            except Exception as e:
                logger.error(
                    "Couldn't add i2c_dev to /etc/modules - [{}]".format(e)
                )

        def remove_powerup_lnk_file():
            try:
                linux_users = get_users()
                if not linux_users:
                    logger.error('beta_220_to_beta_230: linux_users is empty!')

                lnk_dir_template = os.path.join(
                    os.sep,
                    'home',
                    '{user}',
                    '.kdesktop',
                    'Powerup.lnk'
                )
                for user in linux_users:
                    lnk_dir = lnk_dir_template.format(user=user)
                    if os.path.exists(lnk_dir):
                        os.remove(lnk_dir)
            except Exception as e:
                logger.error("Couldn't remove Powerup.lnk - [{}]".format(e))

        def enable_spi_device():
            from kano_settings.boot_config import set_config_value
            set_config_value("dtparam=spi", "on")
            try:
                from kano_settings.boot_config import end_config_transaction
                end_config_transaction()
            except ImportError:
                logger.error("end_config_transaciton not present - update to kano-settings failed?")

        # Scenario work starts here
        install('rsync')
        run_cmd_log('kano-apps install --no-gui powerup')

        remove_powerup_lnk_file()

        ensure_system_group_exists('gpio')
        ensure_system_group_exists('spi')
        add_users_to_group('i2c')
        add_users_to_group('gpio')
        add_users_to_group('spi')
        add_i2c_module_to_auto_loaded()

        # enable spi device
        enable_spi_device()

    def beta_230_to_beta_240(self):
        pass

    def beta_240_to_beta_300(self):
        def enable_audio_device():
            from kano_settings.boot_config import set_config_value
            set_config_value("dtparam=audio", "on")
            try:
                from kano_settings.boot_config import end_config_transaction
                end_config_transaction()
            except ImportError:
                logger.error("end_config_transaction not present - update to kano-settings failed?")
        enable_audio_device()

        # tell kano-overworld to skip onboarding stage
        run_for_every_user('/usr/bin/luajit /usr/share/kano-overworld/bin/skip-onboarding.lua')

        # tell dashboard to skip Overworld and kit setup onboarding phase
        run_for_every_user('touch ~/.dashboard-click-onboarding-done')

    def beta_300_to_beta_310(self):
        pass

    def beta_310_to_beta_320(self):
        config_path = '/boot/config.txt'
        use_transactions = False
        # if we can't use transactions, fall back to editting the file directly
        tmp_path = config_path

        try:
            try:
                # append uart config to config.txt
                from kano_settings.boot_config import _trans, \
                    end_config_transaction

                use_transactions = True
                tmp_path = '/tmp/config.tmp'
                _trans().copy_to(tmp_path)

            except ImportError:
                pass

            from textwrap import dedent
            extra_config = dedent("""
            [pi3]
            # for light board
            enable_uart=1
            [all]
            """)

            with open(tmp_path, 'a') as tmp_config:
                tmp_config.write(extra_config)

            if use_transactions:
                _trans().copy_from(tmp_path)

                end_config_transaction()
        except:
            logger.error("failed to update config")

    def beta_320_to_beta_330(self):
        def disable_audio_dither():
            from kano_settings.boot_config import set_config_value
            set_config_value("disable_audio_dither", "1")
            try:
                from kano_settings.boot_config import end_config_transaction
                end_config_transaction()
            except ImportError:
                logger.error("end_config_transaction not present")
        disable_audio_dither()

    def beta_330_to_beta_340(self):
        pass
