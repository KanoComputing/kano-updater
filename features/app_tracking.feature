# app_tracking.feature
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Specification of data and events tracking.


Feature: Tracking of application data and events

    The Updater and Recovery processes track data about the state of the
    application to tell version upgrades and flow integrity. Events that
    contain UUID codes and/or are uploaded to the servers right after their
    creation are intended to provide visibility over update and recovery flows
    and to group them into a single installation/atempt session.

    Scenario: Update install started
        Given the Updater is started to install updates
         When the Updater starts installing updates
         Then an event named "update-install-started" is created
          And the event contains the same UUID code for the update session
          And the events are uploaded to the servers

    Scenario: Updater hanged indefinitely
        Given the Updater is started
         When the Updater is interrupted due to it hanging
         Then an event named "updater-hanged-indefinitely" is created
          And the event contains the same UUID code for the update session
          And the events are uploaded to the servers

    Scenario: Update install finished
        Given the Updater is started to install updates
         When the Updater finishes installing updates
         Then an event named "update-install-finished" is created
          And the event contains the same UUID code for the update session
          And the events are uploaded to the servers

    Scenario: Update Recovery started
        Given the update Recovery is started
         When the Recovery starts
         Then an event named "update-recovery-started" is created
          And the event contains the same UUID code for the update session
          And the events are uploaded to the servers

    Scenario: Update Recovery failed
        Given the update Recovery is started
         When the Recovery shows an error
         Then an event named "update-recovery-failed" is created
          And the event contains the UF error code
          And the event contains the same UUID code for the update session
          And the events are uploaded to the servers

    Scenario: Update Recovery successful
        Given the update Recovery is started
         When the Updater finishes successfully
         Then an event named "update-recovery-finished" is created
          And the event contains the same UUID code for the update session
          And the events are uploaded to the servers

    Scenario: Update installation ends and UUID is cleared
        Given the Updater is started
         When the Updater terminates
         Then the Updater tracking UUID code is cleared

    Scenario: Update Recovery installation ends and UUID is cleared
        Given the update Recovery is started
         When the Recovery flow ends
         Then the Updater tracking UUID code is cleared

