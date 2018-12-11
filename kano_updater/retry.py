#
# retry.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Retry decorators
#
# Original:
#     https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python
#


import time
from functools import wraps

from kano.logging import logger

from kano_updater.monitor_heartbeat import heartbeat


RETRIES = 5


def retry(ExceptionToCheck, tries=RETRIES, delay=3, backoff=2):
    """Retry calling the decorated function using an exponential backoff.


    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    heartbeat()
                    return f(*args, **kwargs)
                except ExceptionToCheck, err:
                    logger.warn(
                        "{}, Retrying in {} seconds..."
                        .format(str(err), mdelay)
                    )
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            heartbeat()
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
