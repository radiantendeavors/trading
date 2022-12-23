#!/usr/bin/env python3
# ==================================================================================================
#
# pyTrader: Algorithmic Trading Program
#
#   Copyright (C) 2022  Geoff S. Derber
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# trading/libs/brokerclient/ibkrclient.py
#
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
from pytrader.libs.clients.mysql import etf_info, stock_info
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
        try:
            self.connect(address, port, client_id)
        except Exception as msg:
            logger.error("Failed to connect")
            logger.error(msg)

        self.orderId = 0
        self.con_id = 0
        self.exchange = ""

        # Launch client thread
        thread = Thread(target=self.run)
        thread.start()

    @iswrapper
    def accountSummary(self, req_id, account, tag, value, currency):
        """ Read information about the account """
        logger.info("Account {}: {} = {}".format(account, tag, value))

    @iswrapper
    def currentTime(self, cur_time):
        time_now = datetime.fromtimestamp(cur_time)
        logger.info("Current time: %s", time_now)

    @iswrapper
    def error(self, req_id, code, msg):
        logger.debug10(logger)
        logger.debug2("Interactive Brokers Error Messages")
        if req_id < 0:
            if code == 504 or code == 502:
                logger.error("%s: ID# %s (%s)", code, req_id, msg)
            else:
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
        self.contract_id = details.contract.conId
        logger.debug("Contract Info")
        logger.debug("Contract ID: %s", details.contract.conId)
        logger.debug("Symbol: %s", details.contract.symbol)
        logger.debug("Security Type: %s", details.contract.secType)
        logger.debug("Exchange: %s", details.contract.exchange)
        logger.debug("Primary Exchange: %s", details.contract.primaryExchange)
        logger.debug("Currency: %s", details.contract.currency)
        logger.debug("Local Symbol: %s", details.contract.localSymbol)
        logger.debug("Security ID Type: %s", details.contract.secIdType)
        logger.debug("Security ID: %s", details.contract.secId)
        #logger.debug("Description: %s", details.contract.description)
        #logger.debug("Issuer ID: %s", details.contract.issuerId)

        logger.debug("Contract Detail Info")
        logger.debug("Market name: %s", details.marketName)
        logger.debug("OrderTypes: %s", details.orderTypes)
        logger.debug("Valid Exchanges: %s", details.validExchanges)
        logger.debug("Underlying Contract ID: %s", details.underConId)
        logger.debug("Long name: %s", details.longName)
        logger.debug("Industry: %s", details.industry)
        logger.debug("Category: %s", details.category)
        logger.debug("Subcategory: %s", details.subcategory)
        logger.debug("Time Zone: %s", details.timeZoneId)
        logger.debug("Trading Hours: %s", details.tradingHours)
        logger.debug("Liquid Hours: %s", details.liquidHours)
        logger.debug("SecIdList: %s", details.secIdList)
        logger.debug("Underlying Symbol: %s", details.underSymbol)
        logger.debug("Stock Type: %s", details.stockType)
        logger.debug("Cusip", details.cusip)
        logger.debug("Next Option Date: %s", details.nextOptionDate)
        logger.debug("Details: %s", details)

        # if details.stockType == "ETF":
        #     db = etf_info.EtfInfo()
        #     row = db.select(details.contract.symbol)

    @iswrapper
    def contractDetailsEnd(self, reqId):
        logger.debug("Contract Details End")

    @iswrapper
    def nextValidId(self, orderId: int):
        """ Provides the next order ID """
        super().nextValidId(orderId)

        logger.debug("Setting nextValidOrderId: %s", orderId)
        self.nextValidOrderId = orderId
        logger.info("The next valid Order ID: %s", orderId)

    def tickPrice(self, reqId, tickType, price, attrib):
        logger.info("Request Id: %s TickType: %s Price: %s Attrib: %s", reqId,
                    tickType, price, attrib)

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
    def securityDefinitionOptionParameter(self, reqId, exchange,
                                          underlyingConId, tradingClass,
                                          multiplier, expirations, strikes):
        print("SecurityDefinitionOptionParameter.", "ReqId:", reqId,
              "Exchange:", exchange, "Underlying conId:", underlyingConId,
              "TradingClass:", tradingClass, "Multiplier:", multiplier,
              "Expirations:", expirations, "Strikes:", str(strikes))

    @iswrapper
    def securityDefinitionOptionParameterEnd(self, reqId: int):
        logger.debug("SecurityDefinitionOptionParameterEnd. ReqId: %s", reqId)


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
