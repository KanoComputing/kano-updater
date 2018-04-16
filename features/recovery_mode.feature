# recovery_mode.feature
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Specification of Recovery Mode for interrupted installation of updates.


Feature: Recovery Mode setup for interrupted installation of updates

    The Updater should be able to repair and recover the system after
    interrupting an update installation. This prevents system-wide corruption
    eliminating broken and half installed software. The following specification
    describes the setup of Recovery Mode. See recovery_flow.feature for what
    happens during a recovery process.

    Scenario: Updater starts installing updates
        Given the Updater is started to install updates
         When the Updater starts installing updates
         Then the Updater sets Recovery Mode for the next boot

    Scenario: Updater finishes installing updates
        Given the Updater is started to install updates
         When the Updater finishes installing updates
         Then the Updater cancels Recovery Mode for the next boot

    # TODO: Add tracking

    Scenario: Normal boot animation
        Given the system has booted
          And the Updater has previously not set Recovery Mode
         When the boot animation starts
         Then the default boot animation is used

    Scenario: System boots normally
        Given the system has booted
          And the Updater has previously not set Recovery Mode
         When the user session starts
         Then the Updater recovery process is started
          And the process terminates immediately

    Scenario: Recovery Mode boot animation
        Given the system has booted
          And the Updater has previously set Recovery Mode
         When the boot animation starts
         Then the recovery boot animation is used

    Scenario Outline: System boots in Recovery Mode
        Given the system has booted
          And the Updater has previously set Recovery Mode
          And there are "<user_count>" number of user accounts
         When the user session starts
         Then the Updater recovery process is started

        Examples: Number of user accounts
            | user_count |
            | 1          |
            | 2          |
