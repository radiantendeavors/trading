"""
@package pytrader.libs.clients.broker.ibrkrclient

Provides the client for Interactive Brokers

@author Geoff S. derber
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

  Creates a basic interface for interacting with Interactive Brokers.

"""
# System Libraries
import sys
import time
from datetime import datetime

# IB API
from ibapi.client import EClient
from ibapi.utils import iswrapper
from ibapi.wrapper import EWrapper

# System Library Overrides
from pytrader.libs.clients.mysql import etf_info, index_info, stock_info
from pytrader.libs.system import logging

# Other Libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
logger = logging.getLogger(__name__)

# To avoid pacing violations, data can be requested no more than 60 requests in any 10 minute period.
# There are 600 seconds in 10 minutes.
# So, 1 request every 10 seconds, and add 1 second to ensure we don't cross the threshold.
sleep_time = 15


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrClient(EWrapper, EClient):
    """IbkrClient

    Serves as the client and the wrapper
    """

    def __init__(self, *args, **kwargs):
        """!@fn __init__

        Initialize the IbkrClient class

        @param *args
        @param **kwargs
        """
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        self.req_id = 0
        self.data = {}

    def cancel_head_timestamp(self, req_id):
        self.cancelHeadTimeStamp(req_id)

    def check_server(self):
        """check_server

        Checks the connection by asking the server it's time.
        """
        self.reqCurrentTime()
        if self.serverVersion() is not None:
            logger.info("Server Version: %s", self.serverVersion())
        else:
            logger.error(
                "Failed to connect to the server: Server Version Unknown")
        if self.twsConnectionTime() is not None:
            logger.info("Connection time: %s",
                        self.twsConnectionTime().decode())
        else:
            logger.error(
                "Failed to connect to the server: Connection Time Unknown")

    def get_data(self, req_id=None):
        logger.debug10("Begin Function")

        if req_id:
            # Pop the key because otherwise this variable could become large with many requests
            while True:
                if req_id in self.data:
                    return self.data.pop(req_id)
                    break
                else:
                    logger.debug("Waiting on response for Request ID: %s",
                                 req_id)
                    time.sleep(1)

        else:
            return self.data

    def get_ipo_date(self,
                     contract,
                     what_to_show="TRADES",
                     use_regular_trading_hours=1,
                     format_date=1):
        self.req_id += 1

        logger.debug("Ticker: %s", contract.symbol)
        self.reqHeadTimeStamp(self.req_id, contract, what_to_show,
                              use_regular_trading_hours, format_date)
        time.sleep(sleep_time)
        return self.req_id

    def get_account_summary(self):
        self.req_id += 1
        self.reqAccountSummary(self.req_id, "ALL",
                               "AccountType, AvailableFunds")
        time.sleep(sleep_time)
        return self.req_id

    def get_security_data(self, contract):
        logger.debug10("Begin Function")
        self.req_id += 1
        logger.debug("Requesting Contract Details for contract: %s", contract)
        self.reqContractDetails(self.req_id, contract)
        time.sleep(sleep_time)
        logger.debug10("End Function")
        return self.req_id

    def get_security_historical_bars(self,
                                     contract,
                                     duration_str,
                                     bar_size_setting,
                                     what_to_show,
                                     chart_options,
                                     end_date_time="",
                                     use_regular_trading_hours=1,
                                     format_date=1,
                                     keep_up_to_date=False):
        self.req_id += 1
        self.reqHistoricalData(self.req_id, contract, end_date_time,
                               duration_str, bar_size_setting, what_to_show,
                               use_regular_trading_hours, format_date,
                               keep_up_to_date, chart_options)

    def get_security_pricing_data(self, contract):
        logger.debug10("Begin Function")
        self.req_id += 1
        self.reqMktData(self.req_id, contract, "233", False, False, [])
        logger.debug10("End Function")
        return self.req_id

    def get_option_chain(self, contract):
        logger.debug10("Begin Function")
        self.req_id += 1
        security = contract.symbol
        security_type = contract.secType
        logger.debug("Contract ID: %s", contract.contract_id)
        contract_id = contract.contract_id

        logger.debug10("Get the Option Chain")
        logger.debug2("Request ID: %s", self.req_id)
        logger.debug("Security:%s", security)
        logger.debug("Security Type: %s", security_type)
        logger.debug("Contract ID: %s", contract_id)
        self.reqSecDefOptParams(self.req_id, security, "", security_type,
                                contract_id)
        time.sleep(60)
        logger.debug10("End Function")
        return self.req_id

    @iswrapper
    def accountSummary(self, req_id, account, tag, value, currency):
        """ Read information about the account """
        logger.info("Account {}: {} = {}".format(account, tag, value))

    @iswrapper
    def contractDetails(self, req_id, details):
        logger.debug("Begin Function")
        self.data[req_id] = details

        # logger.debug("Contract Info")
        # logger.debug("Contract ID: %s", details.contract.conId)
        # logger.debug("Symbol: %s", details.contract.symbol)
        # logger.debug("Security Type: %s", details.contract.secType)
        # logger.debug("Exchange: %s", details.contract.exchange)
        # logger.debug("Primary Exchange: %s", details.contract.primaryExchange)
        # logger.debug("Currency: %s", details.contract.currency)
        # logger.debug2("Local Symbol: %s", details.contract.localSymbol)
        # logger.debug("Security ID Type: %s", details.contract.secIdType)
        # logger.debug("Security ID: %s", details.contract.secId)

        # logger.debug("Contract Detail Info")
        # logger.debug2("Market name: %s", details.marketName)
        # logger.debug2("OrderTypes: %s", details.orderTypes)
        # logger.debug2("Valid Exchanges: %s", details.validExchanges)
        # logger.debug2("Underlying Contract ID: %s", details.underConId)
        # logger.debug("Long name: %s", details.longName)
        # logger.debug("Industry: %s", details.industry)
        # logger.debug("Category: %s", details.category)
        # logger.debug("Subcategory: %s", details.subcategory)
        # logger.debug2("Time Zone: %s", details.timeZoneId)
        # logger.debug2("Trading Hours: %s", details.tradingHours)
        # logger.debug2("Liquid Hours: %s", details.liquidHours)
        # logger.debug2("SecIdList: %s", details.secIdList)
        # logger.debug2("Underlying Symbol: %s", details.underSymbol)
        # logger.debug("Stock Type: %s", details.stockType)
        # logger.debug("Next Option Date: %s", details.nextOptionDate)
        # logger.debug3("Details: %s", details)

        # if details.contract.secType == "Bond":
        #     logger.debug("Description: %s", details.contract.description)
        #     logger.debug("Issuer ID: %s", details.contract.issuerId)
        #     logger.debug("Cusip", details.cusip)

        # elif details.contract.secType == "IND":
        #     db = index_info.IndexInfo()
        #     db.update_ibkr_info(details.contract.symbol,
        #                         details.contract.conId,
        #                         details.contract.primaryExchange,
        #                         details.contract.exchange, details.longName)

        # if details.stockType == "ETF" or details.stockType == "ETN":
        #     db = etf_info.EtfInfo()
        #     db.update_ibkr_info(details.contract.symbol,
        #                         details.contract.conId,
        #                         details.contract.primaryExchange,
        #                         details.contract.exchange)

        # elif details.stockType == "STK":
        #     db = stock_info.EtfInfo()
        #     db.update_ibkr_info(details.contract.symbol,
        #                         details.contract.conId,
        #                         details.contract.primaryExchange,
        #                         details.contract.exchange)

        logger.debug("End Function")

    @iswrapper
    def contractDetailsEnd(self, req_id):
        logger.debug("Contract Details End")

    @iswrapper
    def currentTime(self, cur_time):
        time_now = datetime.fromtimestamp(cur_time)
        logger.info("Current time: %s", time_now)

    @iswrapper
    def error(self, req_id, code, msg, advanced_order_rejection=""):
        logger.debug2("Interactive Brokers Error Messages")
        critical_codes = [1300]
        error_codes = [
            100, 102, 103, 104, 105, 106, 107, 109, 110, 111, 113, 116, 117,
            118, 119, 120, 121, 122, 123, 124, 125, 126, 129, 131, 132, 162,
            200, 320, 502, 503, 504, 1101, 2100, 2101, 2102, 2103, 2168, 2169,
            10038
        ]
        warning_codes = [101, 501, 1100, 2105, 2107, 2108, 2109, 2110, 2137]
        info_codes = [1102]
        debug_codes = [2104, 2106, 2158]

        if code in error_codes:
            if advanced_order_rejection:
                logger.error(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.error("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        elif code in warning_codes:
            if advanced_order_rejection:
                logger.warning(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.warning("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        else:
            if advanced_order_rejection:
                logger.debug(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.debug("ReqID# %s, Code: %s (%s)", req_id, code, msg)

        logger.debug10("End Function")
        return None

    @iswrapper
    def headTimestamp(self, req_id, head_time_stamp):
        logger.debug("ReqID: %s, IPO Date: %s", req_id, head_time_stamp)
        self.data[req_id] = head_time_stamp

    @iswrapper
    def nextValidId(self, order_id: int):
        """ Provides the next order ID """
        super().nextValidId(order_id)

        logger.debug("Setting nextValidOrderId: %s", order_id)
        self.nextValidOrderId = order_id
        logger.info("The next valid Order ID: %s", order_id)

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

    @iswrapper
    def symbolSamples(self, req_id, descs):

        logger.info("Number of descriptions: %s", len(descs))

        for desc in descs:
            logger.info("Symbol: %s", desc.contract.symbol)

        self.symbol = descs[0].contract.symbol

    def tickPrice(self, reqId, tickType, price, attrib):
        logger.info("Request Id: %s TickType: %s Price: %s Attrib: %s", reqId,
                    tickType, price, attrib)


# class IbkrInit(IbkrClient):

#     def __init__(self, address=None, port=None, client_id=0):
#         conf = config.Config()
#         conf.read_config()
#         logger.debug("Client ID Initial: %s", client_id)

#         if address:
#             self.address = address
#         else:
#             self.address = conf.brokerclient_address

#         if port:
#             self.port = port
#         else:
#             self.port = conf.brokerclient_port

#         logger.debug("Address: %s Port: %s", self.address, self.port)

#         self.client_id = client_id

#         if self.client_id < 1:
#             logger.warning("Self.Client ID: %s", self.client_id)

#     def run_loop(self):
#         self.app.run()

#     def begin_connect(self):
#         self.app = IbkrClient(client_id=self.client_id)
#         # Connect to TWS or IB Gateway
#         try:
#             self.app.connect(self.address, self.port, self.client_id)
#         except Exception as msg:
#             logger.error("Failed to connect")
#             logger.error(msg)
#             sys.exit(1)

#         logger.debug("Start Threads")
#         # Launch client thread
#         thread = threading.Thread(target=self.run_loop)
#         thread.start()
#         logger.debug("Threads Started")

#         time.sleep(1)

#         # Check if API is connected
#         # while True:
#         #     if isinstance(self.nextValidOrderId, int):
#         #         logger.debug("Connected")
#         #     else:
#         #         logger.info("Waiting on connection")
#         #         time.sleep(1)

#     def end_connect(self):
#         self.app.disconnect()


# ==================================================================================================
#
# Baseline main used for testing
#
# ==================================================================================================
def main():
    """!@fn main

    Function used to test connectivity
    """
    # Create the client and connect to TWS or IB Gateway

    client = IbkrClient("127.0.0.1", 7497, 0)

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
