#!/usr/bin/env python3
"""!@package pytrader.ui.pytrdownload

The user interface for downloading data.

@author Geoff S. Derber
@version HEAD
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

@file ui/pytrdownload.py

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
client_id = 2


# ==================================================================================================
#
# Function init
#
# ==================================================================================================
def init(args):
    import_path = "pytrader.plugins.download."

    epilog_text = """
    See man pytrader for more information.\n
    \n
    Report bugs to ...
    """

    parser = argparse.CommonParser(description="Automated trading system",
                                   epilog=epilog_text)

    parser.add_version_option()
    parser.add_ibapi_connection_options()
    parent_parser = parser.add_logging_option()
    subparsers = parser.create_subparsers()

    subcommands = ["broker", "init", "nasdaq", "yahoo"]

    for i in subcommands:
        subcommand = utilities.get_plugin_function(scmd='download',
                                                   program=i,
                                                   cmd='parser',
                                                   import_path=import_path)
        subcommand(subparsers, parent_parser)

    parser.set_defaults(func=False, debug=False, verbosity=0, loglevel='INFO')

    args = parser.parse_args()

    conf = config.Config()
    conf.read_config()
    conf.set_loglevel(args)

    logger.debug('Configuration set')
    logger.debug3('Configuration Settings: ' + str(conf))
    logger.debug3('Arguments: ' + str(args))

    logger.debug2("Desired Log Level: %s", conf.loglevel)

    level = logger.getEffectiveLevel()
    logger.debug2("Set Log Level: %s", level)

    # 'application' code
    if DEBUG is False:
        try:
            args.func(args)
        except Exception as msg:
            parser.print_help()
            logger.debug(msg)
            logger.error('No command was given')
    else:
        if args.func:
            args.func(args)
        else:
            parser.print_help()
            logger.debug("No command was given")

    logger.debug10("End Function")
    return None


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
