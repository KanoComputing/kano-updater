# autologin_checks.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Fixture and helpers for LightDM autologin policy functions.


import pytest


_g_function_calls = dict()
_g_function_calls_order = dict()


def all_functions_called(autologin_checks_dict):
    """Helper for checking all autologin functions were called.

    This is a helper function to work with the return value of the
    :func:`.autologin_checks` fixture.

    Returns:
        bool: Whether all four functions were called:
        :func:`kano_init.utils.enable_console_autologin`
        :func:`kano_init.utils.set_ldm_autologin`
        :func:`kano_init.utils.enable_ldm_autostart`
        :func:`kano_init.utils.reconfigure_autostart_policy`
    """
    all_functions_called = True
    for was_function_called in autologin_checks_dict['function_calls'].values():
        all_functions_called = all_functions_called and was_function_called

    return all_functions_called


def finally_reconfigured(autologin_checks_dict):
    """Helper for checking the last function called.

    This is a helper function to work with the return value of the
    :func:`.autologin_checks` fixture.

    Returns:
        bool: Whether the last function called was
        :func:`kano_init.utils.reconfigure_autostart_policy`
    """
    return (
        len(autologin_checks_dict['function_calls_order']) > 0 and
        autologin_checks_dict['function_calls_order'][-1] ==
        'reconfigure_autostart_policy'
    )


def all_checks(autologin_checks_dict):
    """Compress all helper checks into one call.

    This is a helper function to work with the return value of the
    :func:`.autologin_checks` fixture. It executes both
    :func:`.all_functions_called` ``and`` :func:`.finally_reconfigured`.

    Returns:
        bool: All helper checks ``and`` ed together.
    """
    return (
        all_functions_called(autologin_checks_dict) and
        finally_reconfigured(autologin_checks_dict)
    )


@pytest.fixture(scope='function')
def autologin_checks(monkeypatch):
    """Update install autologin mocking and tracking setup.

    This fixture allows for tracking function calls that change the LightDM
    login policy through ``kano_init.utils``. It is recommended that the
    return value is used in conjunction with helper functions in this module
    rather than explicitly using them.

    Args:
        monkeypatch: Standard pytest mocking fixture

    Returns:
        dict: Contains tracking of function calls.
    """
    import kano_init.utils

    global _g_function_calls, _g_function_calls_order

    _g_function_calls = {
        'enable_console_autologin': False,
        'set_ldm_autologin': False,
        'enable_ldm_autostart': False,
        'reconfigure_autostart_policy': False,
    }
    _g_function_calls_order = list()

    def tick_function_call(function_name):
        _g_function_calls[function_name] = True
        _g_function_calls_order.append(function_name)

    monkeypatch.setattr(
        kano_init.utils, 'enable_console_autologin',
        lambda x: tick_function_call('enable_console_autologin')
    )
    monkeypatch.setattr(
        kano_init.utils, 'set_ldm_autologin',
        lambda x: tick_function_call('set_ldm_autologin')
    )
    monkeypatch.setattr(
        kano_init.utils, 'enable_ldm_autostart',
        lambda: tick_function_call('enable_ldm_autostart')
    )
    monkeypatch.setattr(
        kano_init.utils, 'reconfigure_autostart_policy',
        lambda: tick_function_call('reconfigure_autostart_policy')
    )

    yield {
        'function_calls': _g_function_calls,
        'function_calls_order': _g_function_calls_order
    }
