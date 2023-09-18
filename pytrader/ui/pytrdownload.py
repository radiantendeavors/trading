#!/usr/bin/env python3
"""!@package pytrader.ui.pytrdownload

The user interface for downloading data.

@author G S Derber
@date 2022
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

@file pytrader/ui/pytrdownload.py

"""
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import sys

# Application Libraries
from pytrader import DEBUG
from pytrader.libs.system import argparse, logging
from pytrader.libs.utilities import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)
client_id = 2


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def start_process_manager(args):
    logger.debug("Args: %s", args)


def init(args) -> int:
    """! Initializates the program.

    @param args
    Provides the arguments from the command line.

    @return 0
    """
    logger.debug("Entered real main")

    epilog_text = """
    See man pytrader for more information.\n
    \n
    Report bugs to ...
    """

    parser = argparse.ArgParser(description="Automated trading system", epilog=epilog_text)

    parser.add_version_option()
    parser.add_broker_options()
    parser.add_logging_option()

    parser.set_defaults(debug=False, verbosity=0, loglevel='INFO')

    try:
        args = parser.parse_args()

        conf = config.Config()
        conf.read_config()
        conf.set_loglevel(args)

        logger.debug2('Configuration set')
        logger.debug8('Configuration Settings: ' + str(conf))
        logger.debug9('Arguments: ' + str(args))

        # 'application' code
        if DEBUG is False:
            logger.debug8("Attempting to start client")
            try:
                start_process_manager(args)
            except Exception as msg:
                parser.print_help()
                logger.critical(msg)
        else:
            logger.debug8("Starting Client")
            start_process_manager(args)
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
def main(args=None) -> int:
    """! The main program.

    @param args - The input from the command line.
    @return 0
    """
    return init(args)


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == "__main__":
    sys.exit(main())
