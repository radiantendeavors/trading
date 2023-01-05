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
import sys
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
from pytrader.libs.clients import broker
from pytrader.libs import utilities
from pytrader.libs.utilities import config
from pytrader import strategies

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)
client_id = 1
import_path = "pytrader.strategies."


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def start_client(args):
    """! Starts the broker client.

    @param args
    Provides the arguments from the command line.

    @return None
    """
    # Create the client and connect to TWS or IB Gateway
    logger.debug10("Begin Function")
    conf = config.Config()
    conf.read_config()

    if args.address:
        address = args.address
    else:
        address = conf.brokerclient_address

    if args.port:
        port = args.port
    else:
        port = conf.brokerclient_port

    brokerclient = broker.broker_connect(address, port, client_id=client_id)

    strategy_list = args.strategy

    for i in strategy_list:
        strategy = utilities.get_plugin_function(program=i,
                                                 cmd='run',
                                                 import_path=import_path)
        if args.security:
            strategy(brokerclient, args.security)
        else:
            strategy(brokerclient)

    brokerclient.disconnect()
    logger.debug10("End Function")
    return None

    return None


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
                        "--strategy",
                        nargs="+",
                        required=True,
                        help="Strategy to run, can run multiple strategies")
    parser.add_argument("-S",
                        "--security",
                        nargs="+",
                        help="Securities to use for strategy")

    parser.set_defaults(debug=False, verbosity=0, loglevel='INFO')

    args = parser.parse_args()

    conf = config.Config()
    conf.read_config()
    conf.set_loglevel(args)

    logger.debug2('Configuration set')
    logger.debug3('Configuration Settings: ' + str(conf))
    logger.debug4('Arguments: ' + str(args))

    # 'application' code
    if DEBUG is False:
        logger.debug("Attempting to start client")
        try:
            start_client(args)
        except Exception as msg:
            parser.print_help()
            logger.error('No command was given')
            logger.critical(msg)
    else:
        logger.debug("Starting Client")
        start_client(args)

    logger.debug("End real main")
    return 0


def main(args=None):
    """! The main program.

    @param args The input from the command line.
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
