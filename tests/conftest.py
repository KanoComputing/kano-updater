#
# conftest.py
#
# Copyright (C) 2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The pytest conftest file
#
# Import fixtures and setup the tests
#


from tests.fixtures.autologin_checks import *
from tests.fixtures.debian import *
from tests.fixtures.disk_config import *
from tests.fixtures.fake_apt import *
from tests.fixtures.free_space import *
from tests.fixtures.network import *
from tests.fixtures.run_cmd import *
from tests.fixtures.scenarios import *
from tests.fixtures.state import *
from tests.fixtures.version import *
from tests.fixtures.environ import *
