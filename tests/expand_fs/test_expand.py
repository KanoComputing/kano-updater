import imp
import mock

# Import errors in the code under test when this is imported with the fake fs
# initialised
import jsonschema


def test_resize(disk_config, monkeypatch):
    disk = disk_config['info']['partitiontable']['device']
    sfdisk_cmd = 'sfdisk --json {disk}'.format(disk=disk)
    parted_cmd = 'parted {disk} unit s print'.format(disk=disk)

    def mock_exec(cmd):
        if cmd == sfdisk_cmd:
            return disk_config['dumps']['sfdisk-dump'], '', 0

        if cmd == parted_cmd:
            return disk_config['dumps']['parted-dump'], '', 0

        return '', '', 0

    exe_patch = mock.Mock(side_effect=mock_exec)

    import kano.utils.shell
    monkeypatch.setattr(
        kano.utils.shell,
        'run_cmd',
        exe_patch
    )

    from kano_updater.expand_fs.return_codes import RC
    import kano_updater.expand_fs.expand as expand
    import kano_updater.expand_fs.disk as disk
    import kano_updater.expand_fs.partitions as partitions

    # The fake fs doesn't get updated with each disk parameter so reimport
    imp.reload(disk)
    imp.reload(partitions)
    imp.reload(expand)

    assert expand.expand_fs() == RC.SUCCESS

    # Filter out query commands
    calls = [
        calls for calls in exe_patch.call_args_list
        if calls not in [mock.call(sfdisk_cmd), mock.call(parted_cmd)]
    ]
    expected_calls = [
        mock.call(cmd) for cmd in disk_config['expected']['commands']
    ]

    assert calls == expected_calls
