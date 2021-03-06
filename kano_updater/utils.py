# utils.py
#
# Copyright (C) 2014-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Utilities for the updater and the pre and post update scripts


import os
import errno
import subprocess
import shutil
import pwd
import grp
import signal
import traceback

from kano.logging import logger
from kano.utils.shell import run_cmd, run_bg, run_cmd_log
from kano.utils.file_operations import chown_path, sed, open_locked
from kano.utils.user import get_user_unsudoed
from kano.timeout import timeout, TimeoutError

#
# WARNING do not import GUI modules here (like KanoDialog)
#

try:
    from kano_peripherals.pi_hat.driver.high_level import get_pihat_interface
    from kano_peripherals.ck2_pro_hat.driver.high_level import get_ck2_pro_hat_interface
except ImportError:
    '''
    Peripherals might not have been updated to a version which supports the
    interfaces so play it safe and wrap this
    '''
    pass

import kano_updater.apt_wrapper
import kano_updater.progress


UPDATER_CACHE_DIR = "/var/cache/kano-updater/"
STATUS_FILE = UPDATER_CACHE_DIR + "status"

REPO_SERVER = 'repo.kano.me'
PID_FILE = '/var/run/kano-updater.pid'

TRACKING_UUID_KEY = 'kano-updater'

# Pidfile handling taken from https://pypi.python.org/pypi/pid
# By trbs and Naveen Nathan (Apache licence)
# but we don't want to install a pip
# dependency here so I have just taken the relevent lines.


def pid_exists(pid):
    try:
        os.kill(int(pid), 0)
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            # this pid is not running
            return False
    return True


class pidData:
    # Read and write a pid in a read/write file
    def __init__(self, fh):
        self.fh = fh

    def write(self):
        # Clear any existing data
        self.fh.seek(0)
        self.fh.truncate()
        self.fh.write(str(os.getpid()) + '\n')

    def read(self):
        self.fh.seek(0)
        try:
            return int(self.fh.read(16).split("\n", 1)[0].strip())
        except:
            # if the pid file is corrupted, this is a big problem,
            # but the only chance of fixing the system is for
            # the updater to update
            # itself, so allow updates to go ahead.
            return None


def is_running():
    try:
        with open_locked(PID_FILE, 'a+', nonblock=True) as pid_file:
            pd = pidData(pid_file)
            old_pid = pd.read()
            if old_pid and pid_exists(old_pid):
                return True
            pd.write()

    except IOError:  # file was locked by another process
        return True
    return False


def remove_pid_file():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)


def get_users(minimum_id=1000):
    # TODO: this was taken from kano-greeter, but should be in toolset
    '''
    Returns a list of interactive users on the system
    as reported by Unix /etc/password database
    '''
    interactive_users = []
    system_users = pwd.getpwall()

    # special usernames to exlude from the list
    exclude = ('nobody')

    for user in system_users:
        if user.pw_uid >= minimum_id and user.pw_name not in exclude:
            # This is an interactive user created by Kano
            interactive_users.append(user.pw_name)

    return sorted(interactive_users, reverse=False)


def run_for_every_user(cmd):
    for user in get_users():
        run_cmd_log("sudo su -c '{cmd}' - {user}".format(cmd=cmd, user=user))


def is_server_available():
    """ Pings REPO_SERVER to diagnose packet loss
    and server availability.

    Args:
        REPO_SERVER: is the pre-set address
        count: Number of times to ping the server

    Returns: A boolean, True for server availability.
    """
    import ping

    lost_packet_percent = ping.quiet_ping(REPO_SERVER, timeout=3, count=5)[0]

    return lost_packet_percent < 50


def kill_apps():
    # since kano-updater is run as root, need to inform
    # kanolauncher about user
    user = get_user_unsudoed()
    home = os.path.join('/home/', user)
    variables = 'HOME={} USER={}'.format(home, user)
    run_cmd('{} /usr/bin/kano-launcher /bin/true kano-kill-apps'.format(
        variables))


def kill_flappy_judoka():
    """
    Kills Flappy Judoka game.

    This is mainly required due to the way we do window management. The game will
    set itself on top of the Updater (which has set_keep_above true), but if any
    dialogs are shown, it goes underneath, still capturing keyboard and mouse input.
    """
    try:
        os.system('pkill -KILL -f flappy-judoka')
    except Exception as e:
        logger.error("Unexpected error in kill_flappy_judoka()", exception=e)


def bring_flappy_judoka_to_front():
    """
    Puts Flappy Judoka game on top of the updater.

    It works by asking the window manager to give focus back to the game when
    something else grabs it, i.e. when relaunching. This will happen in the
    game's signal for SIGUSR1.
    """
    try:
        os.system('pkill -USR1 -f flappy-judoka')
    except Exception as e:
        logger.error("Unexpected error in bring_flappy_judoka_to_front()", exception=e)


def make_low_prio():
    # set IO class of this process to Idle
    pid = os.getpid()
    unused1, unused2, rc = run_cmd_log("ionice -c 3 -p {}".format(pid))
    if rc != 0:
        logger.error("ionice command returned non-zero code: [{}]".format(rc))

    # Set the lowest scheduling priority
    unused1, unused2, rc = run_cmd_log("schedtool -D {}".format(pid))
    if rc != 0:
        logger.error(
            "schedtool command returned non-zero code: [{}]".format(rc))
    os.nice(19)


def make_normal_prio():
    # set IO class of this process to Idle
    pid = os.getpid()
    unused1, unused2, rc = run_cmd_log("ionice -c 0 -p {}".format(pid))
    if rc != 0:
        logger.error("ionice command returned non-zero code: [{}]".format(rc))

    # Set the lowest scheduling priority
    unused1, unused2, rc = run_cmd_log("schedtool -N {}".format(pid))
    if rc != 0:
        logger.error(
            "schedtool command returned non-zero code: [{}]".format(rc))
    try:
        current_niceness = os.nice(0)
        os.nice(-1 * current_niceness)
    except OSError as os_ex:
        logger.error("Can't renice to 0 due to permissions [{}]".format(os_ex))


def migrate_repository(apt_file, old_repo, new_repo):
    try:
        sed(old_repo, new_repo, apt_file, use_regexp=False)
    except IOError as exc:
        logger.warn("Changing repository URL failed ({})".format(exc))
        return

    # TODO: track progress of this
    apt_handle = kano_updater.apt_wrapper.AptWrapper.get_instance()
    apt_handle.clear_cache()
    apt_handle.update(kano_updater.progress.DummyProgress())


def _handle_sigusr1(signum, frame):
    pass


def show_relaunch_splash():
    # register a handler for SIGUSR1
    signal.signal(signal.SIGUSR1, _handle_sigusr1)

    cmd = ["kano-updater-internal", "ui", "relaunch-splash", str(os.getpid())]
    p = subprocess.Popen(cmd, shell=False)

    # wait until the child process signals that it's ready
    signal.pause()

    return p.pid

#
# wrappers for the notifications API to make sure it doesn't get stuck
#


def pause_notifications():
    @timeout(3)
    def _do_pause_notifications():
        import kano.notifications as notifications
        notifications.pause()

    try:
        _do_pause_notifications()
    except TimeoutError:
        pass


def resume_notifications():
    @timeout(3)
    def _do_resume_notifications():
        import kano.notifications as notifications
        notifications.resume()

    try:
        _do_resume_notifications()
    except TimeoutError:
        pass

# --------------------------------------


def install(pkgs, die_on_err=True):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    cmd = 'apt-get install --no-install-recommends -o Dpkg::Options::="--force-confdef" ' \
          '-o Dpkg::Options::="--force-confold" -y --force-yes ' + str(pkgs)
    _, _, rv = run_cmd_log(cmd)

    if die_on_err and rv != 0:
        msg = "Unable to install '{}'".format(pkgs)
        update_failed(msg)
        raise Exception(msg)

    return rv


def purge(pkgs, die_on_err=False):
    if isinstance(pkgs, list):
        pkgs = ' '.join(pkgs)

    _, _, rv = run_cmd_log('apt-get -y purge ' + str(pkgs))

    if die_on_err and rv != 0:
        msg = "Unable to purge '{}'".format(pkgs)
        update_failed(msg)
        raise Exception(msg)

    return rv


def update_failed(err):
    from kano.gtk3 import kano_dialog

    logger.error("Update failed: {}".format(err))

    msg = _(
        "We had a problem with the Update. Make sure you are connected"
        " to the Internet, and give it another go.\n\n"
        "If you still have problems, we can help at http://help.kano.me"
    )

    kill_flappy_judoka()
    kdialog = kano_dialog.KanoDialog(_("Update error"), msg)
    kdialog.run()


# TODO: This function has been deprecated and should be removed in
# one of the next few releases. Don't use this one (check out the
# kano_apps.utils module for an equivalent).
def get_dpkg_dict(include_unpacked=False):
    logger.warn("get_dpkg_dict() has been deprecated.")
    apps_ok = dict()
    apps_other = dict()

    cmd = 'dpkg -l'
    o, _, _ = run_cmd(cmd)
    lines = o.splitlines()
    for l in lines[5:]:
        parts = l.split()
        state = parts[0]
        name = parts[1]
        version = parts[2]

        if state == 'ii' or (include_unpacked and state == 'iU'):
            apps_ok[name] = version
        else:
            apps_other[name] = version

    return apps_ok, apps_other


def reboot(title, description):
    from kano.gtk3 import kano_dialog
    kdialog = kano_dialog.KanoDialog(title, description)
    kdialog.run()
    run_cmd('systemctl reboot')


def remove_user_files(files):
    logger.info("utils / remove_user_files files:{}".format(files))
    for d in os.listdir("/home/"):
        if os.path.isdir("/home/{}/".format(d)):
            for f in files:
                file_path = "/home/{}/{}".format(d, f)
                if os.path.exists(file_path):
                    logger.info("trying to delete file: {}".format(file_path))
                    try:
                        os.remove(file_path)
                    except:
                        logger.warn("could not delete file: {}".format(file_path))


def update_home_folders_from_skel():
    home = '/home'
    home_folders = os.listdir(home)

    for folder in home_folders:
        full_path = os.path.join(home, folder)
        if os.path.isdir(full_path):
            user_name = folder
            try:
                pwd.getpwnam(user_name)
                grp.getgrnam(user_name)
                update_folder_from_skel(user_name)
            except:
                msg = "Home folder: {} doesn't match user: {}!".format(
                    full_path,
                    user_name
                )
                logger.error(msg)


def update_folder_from_skel(user_name):
    logger.warn("Updating home folder of user: {}".format(user_name))
    src_dir = '/etc/skel'
    dst_dir = os.path.join('/home', user_name)

    dirlinks = []
    filelinks = []
    files = []

    for root, dirs, filenames in os.walk(src_dir):
        for d in dirs:
            path_full = os.path.join(root, d)
            if os.path.islink(path_full):
                dirlinks.append(path_full)

        for f in filenames:
            path_full = os.path.join(root, f)
            if os.path.islink(path_full):
                filelinks.append(path_full)
            else:
                files.append(path_full)

    for path_full in dirlinks + filelinks + files:
        path_rel = os.path.relpath(path_full, src_dir)
        dir_path_rel = os.path.dirname(path_rel)

        dst_path = os.path.join(dst_dir, path_rel)
        dir_dst_path = os.path.join(dst_dir, dir_path_rel)

        # print 'path_full', path_full
        # print 'path_rel', path_rel
        # print 'dir_path_rel', dir_path_rel
        # print 'dst_path', dst_path
        # print 'dir_dst_path', dir_dst_path
        # print

        if os.path.exists(dst_path):
            if os.path.islink(dst_path):
                logger.info("removing link: {}".format(dst_path))
                os.unlink(dst_path)

            elif os.path.isdir(dst_path):
                logger.info("removing dir: {}".format(dst_path))
                shutil.rmtree(dst_path)

            elif os.path.isfile(dst_path):
                logger.info("removing file: {}".format(dst_path))
                os.remove(dst_path)

        # make sure that destination directory exists
        if os.path.exists(dir_dst_path):
            if not os.path.isdir(dir_dst_path):
                os.remove(dir_dst_path)
        else:
            logger.info("making needed dir: {}".format(dir_dst_path))
            os.makedirs(dir_dst_path)
            chown_path(dir_dst_path, user=user_name, group=user_name)

        # creating links
        if os.path.islink(path_full):
            linkto = os.readlink(path_full)
            msg = "creating link {} -> {}".format(dst_path, linkto)
            logger.info(msg)
            os.symlink(linkto, dst_path)
            chown_path(dst_path, user=user_name, group=user_name)

        elif os.path.isfile(path_full):
            msg = "copying file {} -> {}".format(path_full, dst_path)
            logger.info(msg)
            shutil.copy(path_full, dst_path)
            chown_path(dst_path, user=user_name, group=user_name)


def rclocal_executable():
    try:
        # Restablish execution bit: -rwxr-xr-x
        os.chmod('/etc/rc.local', 0755)
        return True
    except Exception:
        return False


def add_text_to_end(text_buffer, text, tag=None):
    end = text_buffer.get_end_iter()
    if tag is None:
        text_buffer.insert(end, text)
    else:
        text_buffer.insert_with_tags(end, text, tag)


def show_kano_dialog(title, description, buttons, blocking=True):
    retval = None
    cmd = 'kano-dialog title="{}" description="{}" buttons="{}" no-taskbar'.format(
          title, description, buttons)

    if blocking:
        _, _, retval = run_cmd(cmd)
    else:
        retval = run_bg('exec ' + cmd)

    return retval


def set_power_button(enabled):
    """
    Enables or disables any power button that might be attached via a Kano hat.
    This is for when we return to the OS and not reboot / shutdown.
    """
    try:
        pihat_iface = get_pihat_interface(retry_count=0)
        if pihat_iface:
            pihat_iface.set_power_button_enabled(enabled)

        pro_hat_iface = get_ck2_pro_hat_interface(retry_count=0)
        if pro_hat_iface:
            pro_hat_iface.set_power_button_enabled(enabled)
    except Exception:
        # Kano Peripherals doesn't support this function
        pass


def enable_power_button():
    set_power_button(True)


def disable_power_button():
    set_power_button(False)


def verify_kit_is_plugged():
    """
    On Computer Kit 2 Pro, verify that the battery is plugged in and not depleting.
    For now, we rely on the user to tell us.

    Returns:
        is_plugged - bool whether the kit is plugged in (and battery isn't low) or not.
    """
    has_battery = False
    is_battery_low = False
    is_plugged = True

    try:
        from kano_peripherals.wrappers.detection import is_ck2_pro, is_ckt
        has_battery = is_ck2_pro(retry_count=0) or is_ckt(retry_count=0)
    except:
        # Kano Peripherals doesn't support this function
        pass

    if has_battery:
        from kano.gtk3.kano_dialog import KanoDialog
        # Run the first dialog asking the user a question.
        dialog = KanoDialog(
            title_text=_("Power Required"),
            description_text=_("Is your computer plugged in?"),
            button_dict={
                _("Yes"): {'color': 'green', 'return_value': True},
                _("No"): {'color': 'red', 'return_value': False}
            }
        )
        is_plugged = dialog.run()

        try:
            from kano_peripherals.ck2_pro_hat.driver.high_level import get_ck2_pro_hat_interface
            ck2pro_iface = get_ck2_pro_hat_interface(retry_count=0)
            is_battery_low = (ck2pro_iface and ck2pro_iface.is_battery_low())
        except:
            # Kano Peripherals doesn't support this function
            pass

        header = ""
        if is_battery_low:
            header = _("Low Battery")
        else:
            header = _("Power Required")

        # If the answer was negative, show another message.
        if not is_plugged or is_battery_low:
            KanoDialog(
                title_text=header,
                description_text=_(
                    "Sorry! You cannot update unless your computer is plugged in.\n"
                    "Plug it in and try again!"
                ),
                button_dict={
                    _("Continue"): {'color': 'green'}
                }
            ).run()

    return is_plugged and not is_battery_low


def track_data_and_sync(event_name, event_data):
    """Create a tracking event with data and upload it to the servers.

    This function also appends a uuid to the event data such that these
    immediate events can be grouped more easily.
    See :func:`kano_profile.tracker.tracking_uuids.get_tracking_uuid`.

    Note:
        This is a slow function, requires a network connection and the user
        being logged into Kano World.

    Args:
        event_name (str): See :func:`kano_profile.tracker.track_data`
        event_data (dict): See :func:`kano_profile.tracker.track_data`
    """

    try:
        from kano_profile.tracker import track_data
        from kano_profile.tracker.tracking_uuids import get_tracking_uuid

        event_data['uuid'] = get_tracking_uuid(TRACKING_UUID_KEY)
        track_data(event_name, event_data)
        rc = os.system('kano-sync --skip-kdesk --upload-tracking-data --silent')
        logger.debug(
            'track_data_and_sync: {} {} and sync rc {}'
            .format(event_name, event_data, rc)
        )
    except:
        logger.error('Unexpected error:\n{}'.format(traceback.format_exc()))


def clear_tracking_uuid():
    """Remove the namespaced tracking uuid for this app.

    Note:
        This function must be reliably called before the app exits.
    """

    try:
        from kano_profile.tracker.tracking_uuids import remove_tracking_uuid
        remove_tracking_uuid(TRACKING_UUID_KEY)
    except:
        logger.error('Unexpected error:\n{}'.format(traceback.format_exc()))
