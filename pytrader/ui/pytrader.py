"""!@package pytrader.ui.pytrader

The main user interface for the trading program.

@author G. S. Derber
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

@file pytrader/ui/pytrader.py

"""
# System libraries
import sys

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import BROKER_ID, CLIENT_ID, DEBUG
from pytrader.libs.applications import trader
from pytrader.libs.utilities import config

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def broker_address(args, conf):
    """!
    Returns the address to be used by the broker.

    @param args - Provides the arguments from the command line
    @param conf - Provides the configuration information from config files.

    @return address - The brokeclient's address
    """
    if args.address:
        return args.address

    return conf.brokerclient_address


def init(args):
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
    parser.add_ibapi_connection_options()
    parser.add_logging_option()

    parser.add_argument("-s",
                        "--strategies",
                        nargs="+",
                        default=[],
                        help="Strategies to run.  If not specified no strategies will run.")
    parser.add_argument("-b", "--broker", choices=["twsapi"], default=BROKER_ID, help="Broker")
    parser.add_argument("-c", "--client-id", default=CLIENT_ID, help="Broker Client Id")

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
                address = broker_address(args, conf)
                process_manager = trader.ProcessManager()

                process_manager.run_processes(address, args.broker, args.client_id, args.strategies)
            except Exception as msg:
                parser.print_help()
                logger.critical(msg)
        else:
            logger.debug8("Starting Client")
            address = broker_address(args, conf)
            process_manager = trader.ProcessManager()
            process_manager.run_processes(address, args.broker, args.client_id, args.strategies)
        return 0

    except argparse.ArgumentError as msg:
        logger.critical("Invalid Argument: %s", msg)
        parser.print_help()
        return 2


def main(args=None):
    """! The main program.

    @param args - The input from the command line.
    @return 0
    """
    logger.debug("Begin Application")

    return init(args)


if __name__ == "__main__":
    sys.exit(main())
