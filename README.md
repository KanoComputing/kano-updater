# Kanux-updater

Utility to keep Kanux up to date

## Kanux-updater

Updates system packages, expands root partition if needed

## expand-rootfs

Part of raspi-config http://github.com/asb/raspi-config

See LICENSE file for copyright and license details

Used in Kanux during interactive partition resizing - kano-update
rc=0 means resize scheduled for next reboot
rc=1 means partition already resized
any other value means error, look at syslog for details