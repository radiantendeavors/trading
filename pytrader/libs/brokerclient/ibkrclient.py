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
        print("Current time: {}".format(time_now))

    @iswrapper
    def error(self, req_id, code, msg):
        if req_id < 0:
            logger.debug("Error: ID# {}: Code {}: {}".format(
                req_id, code, msg))
            print("Error: ID# {}: Code {}: {}".format(req_id, code, msg))
        else:
            print("Error {}: {}".format(code, msg))

    @iswrapper
    def symbolSamples(self, req_id, descs):

        print("Number of descriptions: {}:".format(len(descs)))

        for desc in descs:
            print("Symbol: {}".format(desc.contract.symbol))

        self.symbol = descs[0].contract.symbol

    @iswrapper
    def contractDetails(self, req_id, details):
        print("Long name: {}".format(details.longName))
        print("Category: {}".format(details.category))
        print("Subcategory: {}".format(details.subcategory))
        print("Contract ID: {}\n".format(details.contract.conId))

    @iswrapper
    def contractDetailsEnd(self, reqId):
        print("Contract Details End")

    @iswrapper
    def nextValidId(self, orderId):
        """ Provides the next order ID """
        super().nextValidId(orderId)
        self.nextorderId = orderId
        print("The next valid Order ID: ", self.nextorderId)

    @iswrapper
    def openOrder(self, orderId, contract, order, orderState):
        """ Called in response to the submitted order """
        print("Order status: ", orderState.status)
        print("Commission charged: ", orderState.commission)

    @iswrapper
    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeld,
                    mktCapPrice):
        """ Check the status of the subnitted order """
        print("Number of filled positions: {}".format(filled))
        print("Average fill price: {}".format(avgFillPrice))

    @iswrapper
    def position(self, account, contract, pos, avgCost):
        """ Read information about the account"s open positions """
        print("Position in {}: {}".format(contract.symbol, pos))

    @iswrapper
    def accountSummary(self, req_id, account, tag, value, currency):
        """ Read information about the account """
        print("Account {}: {} = {}".format(account, tag, value))


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
