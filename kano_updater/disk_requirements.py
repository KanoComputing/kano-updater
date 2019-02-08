# disk_requirements.py
#
# Copyright (C) 2018-2019 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Variables pertaining to required disk usage for upgrade


from kano.logging import logger


SPACE_BUFFER = 850  # MB
UPGRADE_3_8_0_SPACE = 1000  # MB


def check_disk_space(priority):
    '''
    Check for available disk space before updating
    '''

    from kano.utils.disk import get_free_space

    from kano_updater.apt_wrapper import AptWrapper
    from kano_updater.os_version import get_system_version, OSVersion

    apt_handle = AptWrapper.get_instance()
    mb_free = get_free_space()
    required_space = apt_handle.get_required_upgrade_space() + SPACE_BUFFER

    # Allowance for installing extra packages in the postupdate scenarios
    # during the update to 3.8.0
    system_version = get_system_version()
    if system_version < OSVersion.from_version_string("Kanux-Beta-3.8.0"):
        required_space += UPGRADE_3_8_0_SPACE

    logger.info('Final upgrade required size is {} MB'.format(required_space))

    if mb_free < required_space:
        err_msg = N_("Only {}MB free, at least {}MB is needed.").format(
            mb_free, required_space
        )
        return False, err_msg

    return True, None
