#!/usr/bin/env python3
"""!@package pytrader.ui.pytrdatabase

The user interface for managing the databases

@author G S Derber
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

@file pytrader/ui/pytrdatabase.py

"""
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import sys

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
from pytrader.libs import utilities
from pytrader.libs.applications.database import DatabaseManager
from pytrader.libs.utilities import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.
"""
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def start_database_process():
    dbmgr = DatabaseManager()
    dbmgr.run()


def init(args):
    epilog_text = """
    See man pytrader for more information.\n
    \n
    Report bugs to ...
    """

    parser = argparse.ArgParser(description="Database manager for pytrader", epilog=epilog_text)

    parser.add_version_option()
    parser.add_broker_options()
    parser.add_logging_option()

    parser.set_defaults(func=False, debug=False, verbosity=0, loglevel='INFO')

    try:
        args = parser.parse_args()

        conf = config.Config()
        conf.read_config()
        conf.set_loglevel(args)

        logger.debug('Configuration set')
        logger.debug3('Configuration Settings: ' + str(conf))
        logger.debug3('Arguments: ' + str(args))

        # 'application' code
        if DEBUG is False:
            logger.debug8("Attempting to start client")
            try:
                start_database_process()
            except Exception as msg:
                parser.print_help()
                logger.critical(msg)
        else:
            logger.debug8("Starting Client")
            start_database_process()
        return 0

    except argparse.ArgumentError as msg:
        logger.critical("Invalid Argument: %s", msg)
        parser.print_help()
        return 2


# ==================================================================================================
#
# Function main
#
# ==================================================================================================
def main(args=None):
    logger.debug("Begin Application")
    if DEBUG is False:
        try:
            init(args)
        except Exception as msg:
            logger.critical(msg)
    else:
        init(args)

    logger.debug("End Application")
    return 1


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == "__main__":
    sys.exit(main())
