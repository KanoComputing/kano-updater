#
# Managing the upgrade procedure
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


class ProgressError(Exception):
    pass


class Phase(object):
    def __init__(self, name, label, percent_length):
        self._name = name
        self._label = label
        self._percent_length = percent_length

    @property
    def name(self):
        return self._name

    @property
    def label(self):
        return self._label

    @property
    def percent_length(self):
        return self._percent_length

    def start(self, step_count=0):
        self._current_step = 0
        self._steps = step_count

    def next_step(self):
        return self.set_step(self._current_step + 1)

    def set_step(self, step):
        if step < self._steps:
            self._current_step = step

            progress = float(self._current_step) / self._steps
            return int(self._percent_length * progress)
        else:
            self._current_step = self._steps
            return self._percent_length


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
        phase = self._get_phase_by_name(phase_name)
        if not phase:
            raise ProgressError(_('Not a valid phase name'))

        phase.start(step_count)
        self._current_phase = phase

        percent = self._get_phase_percentage(phase_name)

        # Trigger a progress change
        self._change(percent, "{}".format(phase.label))

    def next_step(self, msg):
        step_percent = self._current_phase.next_step()

        phase_percent = self._get_phase_percentage(self._current_phase.name)
        self._change(phase_percent + step_percent, msg)

    def set_step(self, step, msg):
        step_percent = self._current_phase.set_step(step)

        phase_percent = self._get_phase_percentage(self._current_phase.name)
        self._change(phase_percent + step_percent, msg)


    def fail(self, msg):
        self._change(-1, "ERROR: {}".format(msg))

    def finish(self, msg):
        self._change(100, "{}".format(msg))

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
            if phase.name == name:
                return phase

    def _get_phase_percentage(self, name):
        phase = self._get_phase_by_name(name)
        index = self._phases.index(phase)

        return sum([p.percent_length for p in self._phases[0:index]])


class DummyProgress(Progress):
    def start_phase(self, phase_name, step_count=0):
        pass

    def next_step(self, msg):
        pass

    def fail(self, msg):
        pass

    def finish(self, msg):
        pass


class DownloadProgress(Progress):
    def __init__(self):
        self._phases = [
            Phase(
                'downloading-pip-pkgs',
                'Downloading Python packages',
                10
            ),
            Phase(
                'updating-apt-sources',
                'Updating apt sources',
                30
            ),
            Phase(
                'apt-cache-init',
                'Initialising apt cache',
                10
            ),
            Phase(
                'downloading-apt-packages',
                'Downloading apt packages',
                50
            ),
        ]


class InstallProgress(Progress):
    def __init__(self):
        self._phases = [
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
    def _change(self, percent, msg):
        print "{}%: {}".format(percent, msg)


class CLIInstallProgress(InstallProgress):
    pass
