#
# test_scenarios.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Tests for the scenario coverage
#


def test_preupdate_covers_upgrade_to_later_versions(upgrade_version_pairs, apt):
    start_version, dummy_upgrade_version = upgrade_version_pairs

    from kano_updater.scenarios import PreUpdate
    pre = PreUpdate(start_version)

    assert pre.covers_update()


def test_postupdate_covers_upgrade_to_later_versions(upgrade_version_pairs,
                                                     apt):
    start_version, dummy_upgrade_version = upgrade_version_pairs

    from kano_updater.scenarios import PostUpdate
    post = PostUpdate(start_version)

    assert post.covers_update()


def test_preupdate_scenarios_version_naming(add_scenario_verifier):
    from kano_updater.scenarios import PreUpdate
    from kano_updater.version import VERSION
    PreUpdate(VERSION)


def test_postupdate_scenarios_version_naming(add_scenario_verifier):
    from kano_updater.scenarios import PostUpdate
    from kano_updater.version import VERSION
    PostUpdate(VERSION)
