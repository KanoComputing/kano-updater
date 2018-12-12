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


def test_postupdate_scenario_beta_4_1_1_to_beta_4_2_0_ensures_netifnames(cmdline_txt, apt):
    from kano_updater.scenarios import PostUpdate

    post_update = PostUpdate('Kanux-Beta-4.1.1-Hopper')
    post_update.beta_4_1_1_to_beta_4_2_0(None)

    assert 'net.ifnames=0' in cmdline_txt.contents
