# Kano-updater

kano-updater is meant to be the easiest way to keep your Kanux system up to date. It not only performs upgrades of your python modules and Debian packages, but cleans the system and expands the SD Card if needed.

Check all the information on the [Wiki](https://github.com/KanoComputing/kano-updater/wiki)

### [Develop](https://github.com/KanoComputing/kano-updater/wiki/Development)

### [Collaborate](https://github.com/KanoComputing/kano-updater/wiki/Collaboration)

## expand-rootfs

Part of raspi-config http://github.com/asb/raspi-config

See LICENSE file for copyright and license details

Used in Kanux during interactive partition resizing - kano-update
rc=0 means resize scheduled for next reboot
rc=1 means partition already resized
any other value means error, look at syslog for details
