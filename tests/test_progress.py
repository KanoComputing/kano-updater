#
# test_progress.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests of the progress objects
#


def test_heartbeat(mocker, monkeypatch):
    import kano_updater.monitor_heartbeat

    heartbeat = mocker.MagicMock()
    monkeypatch.setattr(kano_updater.monitor_heartbeat, 'heartbeat', heartbeat)

    from kano_updater.progress import CLIProgress, Phase
    progress = CLIProgress()

    phase_count = 7
    phases = [
        Phase(
            'phase-{}'.format(phase + 1),
            'Phase {}'.format(phase + 1),
            100 / phase_count,
            is_main=True
        )
        for phase in xrange(phase_count)
    ]
    progress.split(*phases)

    for phase in xrange(phase_count):
        progress.start('phase-{}'.format(phase + 1))

    step_count = 5
    progress.init_steps(
        'phase-{}'.format(phase_count),
        step_count
    )

    for step in xrange(step_count):
        progress.next_step(
            'phase-{}'.format(phase_count),
            'Transitioning to step {}'.format(step + 1)
        )

    assert heartbeat.call_count == phase_count + step_count
