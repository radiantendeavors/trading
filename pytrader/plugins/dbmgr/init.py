"""!@package pytrader.plugins.dbmgr.init

Initializes the database

@author Geoff S. Derber
@version HEAD
@date 2022-2023
@copyright GNU Affero General Public License

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

@file pytrader/plugins/dbmgr/init.py

Initializes the database

"""

# System Libraries
# import os
# import sys

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import database

# Conditional Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## An instance of the logging class
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def initialize(args):
    logger.debug10("Begin Function")
    db = database.Database()

    db.create_engine()
    db_session = db.create_session()

    db.create_tables()
    logger.debug10("End Funuction")


def parser(*args, **kwargs):
    subparsers = args[0]
    parent_parsers = list(args[1:])

    cmd = subparsers.add_parser("init",
                                aliases=["i"],
                                parents=parent_parsers,
                                help="Initial data download")

    cmd.set_defaults(func=initialize)

    return cmd
