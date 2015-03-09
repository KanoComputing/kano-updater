#
# Managing the upgrade procedure
#
# Copyright (C) 2015 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#


class ProgressError(Exception):
    pass


class Phase(object):
    def __init__(self, name, label, weight=1):
        self.name = name
        self.label = label
        self.weight = weight

        self.start = 0
        self.length = 100
        self.parents = []

        self.step_count = 1
        self._step = 0

    def get_phase_percent(self):
        factor = float(self.step) / self.step_count
        return int(factor * 100)

    def get_global_percent(self):
        factor = float(self.step) / self.step_count
        return int(self.start + factor * self.length)

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, step):
        if step < self.step_count:
            self._step = step
        else:
            self._step = self.step_count


class Progress(object):
    """
        The base class for progress reporting of both downloads and
        installations. Subclass it and pass an instance to either
        the download() or install() functions to be notified of
        what's going on.
    """

    def __init__(self):
        root_phase = Phase('root', 'The root phase', 1)

        self._phases = [root_phase]
        self._current_phase_idx = 0

    def start(self, phase_name):
        """
            Starts a certain phase of the progress.

            This doesn't need to be called for steps.

            :param phase_name: A string that identifies the current phase.
            :type phase_name: str
        """
        phase = self._get_phase_by_name(phase_name)

        self._current_phase_idx = self._phases.index(phase)

        # Calculate current progres and emitt an event
        self._call_change(phase)

    def get_current_phase(self):
        return self._phases[self._current_phase_idx]

    def split(self, *subphases, **kwargs):
        if 'phase_name' not in kwargs:
            phase = self.get_current_phase()
        else:
            phase = self._get_phase_by_name(kwargs['phase_name'])

        start = phase.start
        weight_sum = sum([p.weight for p in subphases])
        for subphase in subphases:
            if self._get_phase_by_name(subphase.name, False):
                msg = "Phase '{}' already exists".format(phase.name)
                raise ValueError(msg)

            weight_factor = float(subphase.weight) / weight_sum

            subphase.length = weight_factor * phase.length

            subphase.start = start
            start += subphase.length

            subphase.parents = [phase.name] + phase.parents

        # Implant the subphases into the phase list in place of the parent
        idx = self._phases.index(phase)
        self._phases = self._phases[0:idx] + list(subphases) + \
            self._phases[idx + 1:]

    def init_steps(self, phase_name, step_count):
        phase = self._get_phase_by_name(phase_name)
        phase.step_count = step_count
        phase.step = 0

    def set_step(self, phase_name, step, msg):
        phase = self._get_phase_by_name(phase_name)
        phase.step = step

        self._call_change(phase, msg=msg)

    def next_step(self, phase_name, msg):
        phase = self._get_phase_by_name(phase_name)
        self.set_step(phase_name, phase.step + 1, msg)

    def _get_phase_by_name(self, name, do_raise=True):
        for phase in self._phases:
            if phase.name == name:
                return phase

        if do_raise:
            raise ValueError("Phase '{}' doesn't exist".format(name))

    def fail(self, msg):
        phase = self._phases[self._current_phase_idx]
        self._call_change(phase, -1, -1, "ERROR: {}".format(msg))

    def finish(self, msg):
        phase = self._phases[self._current_phase_idx]
        self._call_change(phase, 100, 100, msg)

    def _call_change(self, phase, global_percent=None,
                     phase_percent=None, msg=None):
        if not global_percent:
            global_percent = phase.get_global_percent()

        if not phase_percent:
            phase_percent = phase.get_phase_percent()

        if not msg:
            msg = phase.label

        self._change(global_percent, msg)
        self._change_per_phase(phase_percent, phase, msg)

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

    def _change_per_phase(self, phase_percent, phase, msg):
        pass


class DummyProgress(Progress):
    def start(self, phase_name):
        pass

    def split(self, phase_name, *subphases):
        pass

    def init_steps(self, phase_name, step_count):
        pass

    def set_step(self, phase_name, step, msg):
        pass

    def next_step(self, phase_name, msg):
        pass

    def fail(self, msg):
        pass

    def finish(self, msg):
        pass


class CLIProgress(Progress):
    def _change(self, percent, msg):
        print "{}%: {}".format(percent, msg)
        pass

    def _change_per_phase(self, percent, phase, msg):
        pass
        #print "[{}] {}%: {}".format(phase.label, percent, msg)
