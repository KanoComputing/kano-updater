#
# test_progress.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests of the progress objects
#

import imp


def test_heartbeat(mocker, monkeypatch):
    import kano_updater.monitor_heartbeat

    heartbeat = mocker.MagicMock()
    monkeypatch.setattr(kano_updater.monitor_heartbeat, 'heartbeat', heartbeat)

    # Reload required to prevent contamination between these tests
    import kano_updater.progress as progress
    imp.reload(progress)
    prog = progress.CLIProgress()

    phase_count = 7
    phases = [
        progress.Phase(
            'phase-{}'.format(phase + 1),
            'Phase {}'.format(phase + 1),
            100 / phase_count,
            is_main=True
        )
        for phase in xrange(phase_count)
    ]
    prog.split(*phases)

    for phase in xrange(phase_count):
        prog.start('phase-{}'.format(phase + 1))

    step_count = 5
    prog.init_steps(
        'phase-{}'.format(phase_count),
        step_count
    )

    for step in xrange(step_count):
        prog.next_step(
            'phase-{}'.format(phase_count),
            'Transitioning to step {}'.format(step + 1)
        )

    assert heartbeat.call_count == phase_count + step_count


def test_progress_failure_issues_crash_report(send_crash_report):
    # Reload required to prevent contamination between these tests
    import kano_updater.progress as progress
    imp.reload(progress)
    prog = progress.CLIProgress()

    fail_msg = 'test-fail'
    prog.fail(fail_msg)

    assert send_crash_report.call_count == 1
    send_crash_report.assert_called_once_with(
        'Updater failure',
        'Failed with error: {}'.format(fail_msg)
    )


def test_progress_abort_issues_crash_report(send_crash_report):
    # Reload required to prevent contamination between these tests
    import kano_updater.progress as progress
    imp.reload(progress)
    prog = progress.CLIProgress()

    abort_msg = 'test-abort'
    prog.abort(abort_msg)

    assert send_crash_report.call_count == 1
    send_crash_report.assert_called_once_with(
        'Updater aborted',
        'Aborted with error: {}'.format(abort_msg)
    )
