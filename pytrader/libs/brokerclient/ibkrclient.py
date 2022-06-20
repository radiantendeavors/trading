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
        logger.debug2("Interactive Brokers Error Messages")
        if req_id < 0:
            logger.debug("%s: ID# %s (%s)", code, req_id, msg)
        elif code >= 1000 and code < 3000:
            logger.warning("%s: ID# %s (%s)", code, req_id, msg)
        else:
            logger.error("%s: ID# %s (%s)", code, req_id, msg)

    @iswrapper
    def symbolSamples(self, req_id, descs):

        logger.info("Number of descriptions: %s", len(descs))

        for desc in descs:
            logger.info("Symbol: %s", desc.contract.symbol)

        self.symbol = descs[0].contract.symbol

    @iswrapper
    def contractDetails(self, req_id, details):
        logger.info(
            "Long name: %s, Category: %s, Subcategory: %s, Contract ID: %s",
            details.longName, details.category, details.subcategory,
            details.contract.conId)
        logger.debug9(details)

    @iswrapper
    def contractDetailsEnd(self, reqId):
        logger.vinfo1("Contract Details End")

    @iswrapper
    def nextValidId(self, orderId: int):
        """ Provides the next order ID """
        super().nextValidId(orderId)

        logger.debug("Setting nextValidOrderId: %s", orderId)
        self.nextValidOrderId = orderId
        logger.info("The next valid Order ID: %s", orderId)

    def tickPrice(self, reqId, tickType, price, attrib):
        if tickType == 2:
            logger.info("The current ask price is: %s", price)

    @iswrapper
    def openOrder(self, orderId, contract, order, orderState):
        """ Called in response to the submitted order """
        logger.info("Order status: %s", orderState.status)
        logger.info("Commission charged: %s", orderState.commission)

    @iswrapper
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld,
                    mktCapPrice):
        """ Check the status of the subnitted order """
        logger.info("Order Id: %s", orderId)
        logger.info("Status: %s", status)
        logger.info("Number of filled positions: %s", filled)
        logger.info("Number of unfilled positions: %s", remaining)
        logger.info("Average fill price: %s", avgFillPrice)
        logger.info("TWS ID: %s", permId)
        logger.info("Parent Id: %s", parentId)
        logger.info("Last Fill Price: %s", lastFillPrice)
        logger.info("Client Id: %s", clientId)
        logger.info("Why Held: %s", whyHeld)
        logger.info("Market Cap Price: %s", mktCapPrice)

    @iswrapper
    def position(self, account, contract, pos, avgCost):
        """ Read information about the account"s open positions """
        logger.info("Position in {}: {}".format(contract.symbol, pos))

    @iswrapper
    def accountSummary(self, req_id, account, tag, value, currency):
        """ Read information about the account """
        logger.info("Account {}: {} = {}".format(account, tag, value))


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
