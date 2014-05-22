#!/usr/bin/env python

# scenarios.py
#
# Copyright (C) 2014 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU General Public License v2
#

from kano_updater.osversion import OSVersion
from kano_updater.utils import install
from kano.utils import run_cmd, zenity_show_progress, \
    run_print_output_error, kill_child_processes

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
        print 'Running the {}-update scripts...'.format(self._type)
        current_v = str(self._old)
        while current_v < str(self._new):
            step_found = False
            for (from_v, to_v), func in self._scenarios.iteritems():
                if current_v == from_v:
                    func()
                    current_v = to_v
                    step_found = True
                    break

            if not step_found:
                raise Exception("{}-update step missing".format(self._type))


class PreUpdate(Scenarios):
    _type = "pre"

    def _mapping(self):
        self.add_scenario("Kanux-Beta-1.0.1", "Kanux-Beta-1.0.2",
                          self.beta_101_to_beta_102)

        self.add_scenario("Kanux-Beta-1.0.2", "Kanux-Beta-1.0.3",
                          self.beta_102_to_beta_103)

    def beta_101_to_beta_102(self):
        pass
        
    def beta_102_to_beta_103(self):
        self.migrate_repo_url()
        # We need to remove kano-youtube manually due to a conflict
        run_print_output_error('apt-get -y purge kano-youtube')

    def migrate_repo_url(self):
        change_items = {
            'apt_file': '/etc/apt/sources.list.d/kano.list',
            'old_repo': 'dev.kano.me',
            'new_repo': 'repo.kano.me'
        }

        sed_cmd = "sed -i 's/%(old_repo)s/%(new_repo)s/g' %(apt_file)s" % change_items
        o, e, rc = run_cmd(sed_cmd)
        if rc != 0:
            print 'Error changing repository, error: {}'.format(e)
        else:
            # We need to run update again since we have changed the repo
            progress_bar = zenity_show_progress("Downloading package lists")
            run_print_output_error('apt-get -y clean')
            run_print_output_error('apt-get -y update')
            kill_child_processes(progress_bar)
        return


class PostUpdate(Scenarios):
    _type = "post"

    def _mapping(self):
        self.add_scenario("Kanux-Beta-1.0.1", "Kanux-Beta-1.0.2",
                          self.beta_101_to_beta_102)

        self.add_scenario("Kanux-Beta-1.0.2", "Kanux-Beta-1.0.3",
                          self.beta_102_to_beta_103)

    def beta_101_to_beta_102(self):
        install('gnome-paint kano-fonts kano-themes zd1211-firmware')

    def beta_102_to_beta_103(self):
        install('kano-apps kano-screenshot kano-video')
