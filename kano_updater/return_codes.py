# return_codes.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Return codes of binaries used throughout this project.


from kano.logging import logger


class RC(object):
    """Return codes of binaries used throughout this project.

    Rather than doing an ``exit`` with an RC from here, it is preferable to set
    the RCState.rc. The ``main`` function should perform the exit with that.

    Note:
        ``kano-updater-recovery`` uses it's own RC class, see that source file.
    """

    SUCCESS = 0

    NO_UPDATES_AVAILABLE = 10
    CHECK_QUIET_PERIOD = 11

    UNEXPECTED_ERROR = 20
    WRONG_ARGUMENTS = 21  # TODO
    INCORRECT_PERMISSIONS = 22  # TODO
    MULTIPLE_INSTANCES = 23
    NOT_PLUGGED_IN = 24

    NO_NETWORK = 30
    CANNOT_REACH_KANO = 31
    HANGED_INDEFINITELY = 32
    SIG_TERM = 33
    NOT_ENOUGH_SPACE = 34



class RCState(object):
    """Application RC state to set and exit with specific return codes."""

    _singleton_instance = None

    @staticmethod
    def get_instance():
        """Get an instance to the singleton class."""

        logger.debug("Getting RCState instance")
        if not RCState._singleton_instance:
            RCState()

        return RCState._singleton_instance

    def __init__(self):
        """Class constructor.

        Note:
            This class is a singleton. Use the :func:`.get_instance` method
            to get an instance of this class.

        Raises:
            Exception: When the constructor is explicitly called.
        """

        logger.debug("Creating new RCState instance")
        if RCState._singleton_instance:
            raise Exception("This class is a singleton!")

        RCState._singleton_instance = self

        self._rc = RC.SUCCESS

    @property
    def rc(self):
        """The return code property.

        This should be a value from the :class:`RC` class.
        The application should exit with this value.
        """

        return self._rc

    @rc.setter
    def rc(self, value):
        """Setter for the property."""

        logger.debug("Setting RCState.rc to: {}".format(value))
        self._rc = value
