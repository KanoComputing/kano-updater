#
# Managing the upgrade procedure
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


class ProgressError(Exception):
    pass

class Progress(object):
    """
        The base class for progress reporting of both downloads and
        installations. Subclass it and pass an instance to either
        the download() or install() functions to be notified of
        what's going on.
    """

    def __init__(self):
        self._phases = []

    def start_phase(self, phase_name, step_count=0):
        """
            Starts a certain phase of the progress.

            :param phase: A string that identifies the current phase.
            :type phase: str

            :param step_count: How many steps there are in this phase (zero
                               for no substeps)
            :type step_count: int
        """

        # look up the phase
        phase = self._get_phase_by_name()
        if not phase:
            raise Exceptiaon(_('Not a valid phase'))

        self._current_phase_name = phase_name
        self._current_phase = phase
        self._steps_left = self._steps = step_count

        percent = self._get_phase_percentage(phase_name)

        # Trigger a progress change
        self._change(percent, "{}: {}".format(phase['label'], msg))

    def next_step(self, msg):
        if self._steps_left > 0:
            self._steps_left -= 1

        # Trigger a progress change
        percent = self._get_phase_percentage(phase_name)
        steps_ratio = 1 - float(self._steps_left ) /self._steps
        percent += int(self._phase['length'] * steps_ratio)

        self._change(percent, msg)

    def failed(self, msg):
        self._change(-1, "ERROR: {}".format(msg))

    def finished(self, msg):
        self._change(100, "Finished: {}".format(msg))

    def _change(self, percent, msg):
        """
            The callback that is triggered for each progress change.

            IMPORTANT: This needs to be implemented by child.

            :param percent: The status of the progress (special values:
                            0: starting, -1: error, 100: done). -1 and 100
                            are triggered just before the worker returns.
            :type percent: int

            :param msg: Message for the UI.
            :type msg: str
        """

        pass

    def _get_phase_by_name(self, name):
        for phase in self._phases:
            if phase['name'] == name:
                return phase

    def _get_phase_percentage(self, name):
        phase = self._get_phase_by_name(name)
        index = self._phases.index(phase)

        return sum([p['length'] for p in self._phases[0:index]])


class DownloadProgress(Progress):
    def __init__(self):
        self._phases = [
            {
                'name': 'downloading-pip-pkgs',
                'label': 'Downloading python packages',
                'length': 10
            },
            {
                'name': 'apt-cache-init',
                'label': 'Initialising apt cache',
                'length': 20
            },
            {
                'name': 'updating-apt-sources',
                'label': 'Updating apt sources',
                'length': 10
            },
            {
                'name': 'downloading-apt-packages',
                'label': 'Downloading apt packages',
                'length': 60
            },
        ]


class InstallProgress(Progress):
    def __init__(self):
        self._phases = [
            {
                'name': 'downloading-pip-pkgs',
                'label': 'Downloading python packages',
                'length': 10
            },
            # TODO: fill in!
        ]
    # updating itself
    #  - apt updating packages here too
    # relaunching
    # runing the preupdate scripts - per script
    # pip:
    #  - just going
    # apt:
    #  - unpacking per package
    #  - installing per package
    #  - configuring per package
    # some dodgy business just before the end that always takes the longest
    # finishing up


class CLIDownloadProgress(DownloadProgress):
    pass


class CLIInstallProgress(InstallProgress):
    pass
