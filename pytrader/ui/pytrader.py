"""!@package pytrader.ui.pytrader

The main user interface for the trading program.

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

@file ui/pytrader.py

"""
# System libraries
import queue
import random
import sys
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
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
    else:
        return conf.brokerclient_address


def process_arguments(args, conf):
    """!
    Processes the arguments received from the command line.

    @param args - Provides the arguments from the command line.
    @param conf - Provides the configuration from config files.

    @return None
    """
    # Create the client and connect to TWS or IB Gateway
    address = broker_address(args, conf)
    strategy_list = args.strategies
    broker = args.broker
    processed_args = (address, strategy_list, broker)

    return processed_args


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

    parser = argparse.ArgParser(description="Automated trading system",
                                epilog=epilog_text)

    parser.add_version_option()
    parser.add_ibapi_connection_options()
    parser.add_logging_option()

    parser.add_argument("-s",
                        "--strategies",
                        nargs="+",
                        required=True,
                        help="One or more strategies to run.")
    parser.add_argument("-b",
                        "--broker",
                        choices=["twsapi"],
                        default="twsapi",
                        help="Broker")
    parser.add_argument("-c", "--client-id", help="Broker Client Id")

    parser.set_defaults(debug=False, verbosity=0, loglevel='INFO')

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
            processed_args = process_arguments(args, conf)
            process_manager = trader.ProcessManager()
            if args.client_id:
                process_manager.run_processes(processed_args[0],
                                              processed_args[1],
                                              processed_args[2],
                                              args.client_id)
            else:
                process_manager.run_processes(processed_args[0],
                                              processed_args[1],
                                              processed_args[2])
        except Exception as msg:
            parser.print_help()
            logger.error('No command was given')
            logger.critical(msg)
    else:
        logger.debug8("Starting Client")
        processed_args = process_arguments(args, conf)
        process_manager = trader.ProcessManager()
        if args.client_id:
            process_manager.run_processes(processed_args[0], processed_args[1],
                                          processed_args[2], args.client_id)
        else:
            process_manager.run_processes(processed_args[0], processed_args[1],
                                          processed_args[2])

    return 0


def main(args=None):
    """! The main program.

    @param args - The input from the command line.
    @return 0
    """
    logger.debug("Begin Application")

    if DEBUG is False:
        try:
            init(args)
        except Exception as msg:
            logger.critical(msg)
    else:
        init(args)

    logger.debug("End Application")
    return 0


if __name__ == "__main__":
    sys.exit(main())
