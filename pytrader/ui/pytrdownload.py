# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import logging
import sys
import pkg_resources

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs import utilities

# Application Libraries
from pytrader import DEBUG

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Function real_main
#
# ==================================================================================================
def real_main(args):
    logger.debug("Entered real main")

    plugin_path = pkg_resources.resource_filename('pytrader',
                                                  'plugins/download/')
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

    # 'application' code
    # 'application' code
    if DEBUG is False:
        try:
            args.func(args)
        except:
            parser.print_help()
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
