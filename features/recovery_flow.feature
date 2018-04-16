# recovery_flow.feature
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Specification of actions taken during Recovery Mode to repair broken updates.


Feature: Flow of Recovery Mode actions to repair interrupted updates

    The Updater should be able to repair and recover the system after
    interrupting an update installation. This prevents system-wide corruption
    eliminating broken and half installed software. The following specification
    describes the recovery procedure and user feedback during Recovery Mode.
    See recovery_mode.feature for prior steps to this.

    Background:
        Given the update Recovery is started

    Scenario: Starting the Recovery flow and updating UI
         When the Recovery starts
         Then the recovery boot animation is switched to the recovery running one
          And the Updater is started to install updates in the background

    Scenario: Updater terminates due to an unknown error
         When the Updater terminates due to an unknown error
         Then UF2 error screen is shown indefinitely

    Scenario: Updater terminates due to network connectivity issues
         When the Updater terminates due to network connectivity issues
         Then UF3 error screen is shown indefinitely
          And a count of the number of times this happens is kept

    Scenario: Updater exceeds the maximum number of network connectivity tries
         When the Updater terminates due to network connectivity issues
          And the number of tries reached 4
         Then UF4 error screen is shown indefinitely

    Scenario: Updater terminates due to the processing hanging
         When the Updater terminates due to the processing hanging
         Then UF5 error screen is shown indefinitely

    Scenario: Updater exceeds the maximum time duration
         When the Updater had been running for more than 2 hours
         Then UF6 error screen is shown indefinitely

    Scenario: Updater terminates successfully
         When the Updater finishes successfully
         Then the recovery successful screen is shown for 10 seconds
          And the system then reboots
