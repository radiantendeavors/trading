#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System libraries
import logging
import sys
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse

# Application Libraries
from pytrader import DEBUG
from pytrader.libs import brokerclient

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def start_client(args):
    # Create the client and connect to TWS or IB Gateway
    client = brokerclient.BrokerClient(args.address, args.port)
    client.connect()

    if args.timecheck:
        client.check_server_time()
        time.sleep(0.5)

    elif args.order:
        client.place_order("AAPL", "LMT", 120.00, 1.0)
        time.sleep(20)

    # Disconnect
    client.disconnect()

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

    parser.add_argument("-t", "--timecheck", action='store_true')
    parser.add_argument("-o", "--order", action='store_true')

    args = parser.parse_args()

    # 'application' code
    if DEBUG is False:
        try:
            start_client(args)
        except Exception as msg:
            parser.print_help()
            logger.info(msg)
            logger.error('No command was given')
    else:
        start_client(args)

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

    logger.debug('End Application')
    return None


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == '__main__':
    sys.exit(main())
