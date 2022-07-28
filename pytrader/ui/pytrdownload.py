#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import sys
import pkg_resources

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
from pytrader.libs import utilities
from pytrader.libs.utilities import config
from pytrader.libs.utilities import text

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)
# Allow Color text on console
colortext = text.ConsoleText()


# ==================================================================================================
#
# Function real_main
#
# ==================================================================================================
def real_main(args):
    logger.debug("Entered real main")

    import_path = "pytrader.plugins.download."

    epilog_text = """
    See man pytrader for more information.\n
    \n
    Report bugs to ...
    """

    parser = argparse.ArgParser(description="Automated trading system",
                                epilog=epilog_text)

    parser.add_version_option()
    parser.add_ibapi_connection_options()
    parent_parser = parser.add_logging_option()
    subparsers = parser.create_subparsers()

    subcommands = ["broker", "init", "nasdaq"]

    for i in subcommands:
        subcommand = utilities.get_plugin_function(scmd='download',
                                                   program=i,
                                                   cmd='parser',
                                                   import_path=import_path)
        subcommand(subparsers, parent_parser)

    parser.set_defaults(func=False, debug=False, verbosity=0, loglevel='INFO')

    parser.add_logging_option()

    args = parser.parse_args()

    configuration = config.main_configure(args)

    logger.debug2('Configuration set')
    logger.debug3('Configuration Settings: ' + str(configuration))
    logger.debug4('Arguments: ' + str(args))

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

    logger.debug("End real main")
    return None


# ==================================================================================================
#
# Function main
#
# ==================================================================================================
def main(args=None):
    if DEBUG is False:
        try:
            real_main(args)
        except Exception as msg:
            logger.critical(msg)
    else:
        real_main(args)

    logger.debug("End Application")
    return None


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == "__main__":
    sys.exit(main())
