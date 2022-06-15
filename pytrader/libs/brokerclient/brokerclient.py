#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System Libraries
import logging
from datetime import datetime
from threading import Thread
import time
import sys

# IB API
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class BrokerClient(EWrapper, EClient):
    """ Serves as the client and the wrapper"""

    def __init__(self, address, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        # Connect to TWS or IB Gateway
        self.connect(address, port, client_id)

        # Launch client thread
        thread = Thread(target=self.run)
        thread.start()

        return None

    @iswrapper
    def currentTime(self, cur_time):
        time_now = datetime.fromtimestamp(cur_time)
        print("Current time: {}".format(time_now))

        return None

    @iswrapper
    def error(self, req_id, code, msg):
        if req_id < 0:
            logger.debug("Error {}: {}".format(code, msg))
        else:
            print("Error {}: {}".format(code, msg))

        return None


# ==================================================================================================
#
# Baseline main used for testing
#
# ==================================================================================================
def main():
    # Create the client and connect to TWS or IB Gateway

    client = BrokerClient("127.0.0.1", 7497, 0)

    # Request the current time
    client.reqCurrentTime()

    time.sleep(0.5)

    client.disconnect()

    return None


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == '__main__':
    sys.exit(main())
