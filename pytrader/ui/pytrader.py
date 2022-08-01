#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import sys
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
from pytrader.libs import brokerclient
from pytrader.libs import security
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
# Functions
#
# ==================================================================================================
def start_client(args):
    # Create the client and connect to TWS or IB Gateway
    logger.debug10("Begin Function")

    client = brokerclient.BrokerClient(args.address, args.port)

    if args.checkserver:
        logger.debug("Checking Server time")
        client.check_server()
        time.sleep(0.5)

    elif args.security:
        logger.debug("Security info")
        sec = security.Security(client, "AAPL")
        sec.set_security()
        sec.get_security_data()
        sec.get_security_pricing_data()
        sec.get_option_chain()

    elif args.order:
        sec = security.Security(client, "AAPL")
        logger.info("Ordering: %s", sec)
        sec.place_order("BUY", "LMT", 130.00, 1.0, args.transmit)
        time.sleep(20)
        client.get_open_positions()
        time.sleep(10)
        client.get_account_summary()
        time.sleep(10)
    else:
        logger.debug("No command specified")

    # Disconnect
    logger.debug("Disconnecting from server")
    client.disconnect()

    logger.debug("End Function")

    return None


# ==================================================================================================
#
# Function real_main
#
# ==================================================================================================
def real_main(args):
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

    parser.add_argument("-c", "--checkserver", action="store_true")
    parser.add_argument("-o", "--order", action="store_true")
    parser.add_argument("-s", "--security", action="store_true")
    parser.add_argument("-t",
                        "--transmit",
                        action="store_true",
                        default=False,
                        help="Transmit Order Automatically")

    parser.set_defaults(debug=False, verbosity=0, loglevel='INFO')

    args = parser.parse_args()

    configuration = config.main_configure(args)

    logger.debug2('Configuration set')
    logger.debug3('Configuration Settings: ' + str(configuration))
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


# ==================================================================================================
#
# Function main
#
# ==================================================================================================
def main(args=None):
    logger.debug("Begin Application")

    if DEBUG is False:
        try:
            real_main(args)
        except Exception as msg:
            logger.critical(msg)
    else:
        real_main(args)

    logger.debug("End Application")
    return 0


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == "__main__":
    sys.exit(main())
