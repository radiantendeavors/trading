#!/usr/bin/env python3
# ==================================================================================================
#
# pytrader
#
# ==================================================================================================
# System Libraries
from datetime import datetime
from threading import Thread
import time
import sys

# IB API
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper

# System Library Overrides
from pytrader.libs.system import logging
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
class IbkrClient(EWrapper, EClient):
    """ Serves as the client and the wrapper"""

    def __init__(self, address, port, client_id):
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        # Connect to TWS or IB Gateway
        self.connect(address, port, client_id)

        self.orderId = 0
        self.con_id = 0
        self.exchange = ""

        # Launch client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper
    def currentTime(self, cur_time):
        time_now = datetime.fromtimestamp(cur_time)
        logger.info("Current time: %s", time_now)

    @iswrapper
    def error(self, req_id, code, msg):
        logger.debug10(logger)
        if req_id < 0:
            logger.debug("Error: ID# %s: Code %s: %s", req_id, code, msg)
        else:
            logger.error("Error %s: %s", code, msg)

    @iswrapper
    def symbolSamples(self, req_id, descs):

        logging.info("Number of descriptions: %s", len(descs))

        for desc in descs:
            logging.info("Symbol: %s", desc.contract.symbol)

        self.symbol = descs[0].contract.symbol

    @iswrapper
    def contractDetails(self, req_id, details):
        logging.info(
            "Long name: %s, Category: %s, Subcategory: %s, Contract ID: %s",
            details.longName, details.category, details.subcategory,
            details.contract.conId)
        logging.debug9(details)

    @iswrapper
    def contractDetailsEnd(self, reqId):
        logging.vinfo1("Contract Details End")

    @iswrapper
    def nextValidId(self, orderId: int):
        """ Provides the next order ID """
        super().nextValidId(orderId)

        logging.debug("Setting nextValidOrderId:", orderId)
        self.nextValidOrderId = orderId
        logging.info("The next valid Order ID: ", orderId)

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2:
            logging.info("The current ask price is:", price)

    @iswrapper
    def openOrder(self, orderId, contract, order, orderState):
        """ Called in response to the submitted order """
        logging.info("Order status: ", orderState.status)
        logging.info("Commission charged: ", orderState.commission)

    @iswrapper
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld,
                    mktCapPrice):
        """ Check the status of the subnitted order """
        logging.info("Number of filled positions: {}".format(filled))
        logging.info("Average fill price: {}".format(avgFillPrice))

    @iswrapper
    def position(self, account, contract, pos, avgCost):
        """ Read information about the account"s open positions """
        logging.info("Position in {}: {}".format(contract.symbol, pos))

    @iswrapper
    def accountSummary(self, req_id, account, tag, value, currency):
        """ Read information about the account """
        logging.info("Account {}: {} = {}".format(account, tag, value))


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
if __name__ == "__main__":
    sys.exit(main())
