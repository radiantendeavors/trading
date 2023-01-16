"""!
@package pytrader.libs.clients.broker.ibkrclient

Provides the client for Interactive Brokers

@author Geoff S. Derber
@version HEAD
@date 2022-2023
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

@file pytrader/libs/clients/broker/ibrkrclient.py

Provides the client for Interactive Brokers
"""
# System Libraries
import sys
import time
import datetime

# IB API
from ibapi.client import EClient
from ibapi.commission_report import CommissionReport
from ibapi.contract import Contract, ContractDetails, DeltaNeutralContract
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
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
## Instance of Logging class
logger = logging.getLogger(__name__)

# ==================================================================================================
#
# Pacing Violations
#
# 1. To avoid pacing violations, historical data can be requested no more than 60 requests in any 10
# minute period.
# 2. There are 600 seconds in 10 minutes.
# 3. Therefore, 1 request every 15 seconds to ensure we don't cross the threshold.
#
# https://interactivebrokers.github.io/tws-api/historical_limitations.html#pacing_violations
#
# ==================================================================================================
## Amount of time to sleep to avoid pacing violations.
sleep_time = 15


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IbkrClient(EWrapper, EClient):
    """!
    Serves as the client interface for Interactive Brokers
    """

    def __init__(self, *args, **kwargs):
        """!@fn __init__

        Initialize the IbkrClient class

        @param *args
        @param **kwargs

        @return An instance of the IbkrClient class.
        """
        EWrapper.__init__(self)
        EClient.__init__(self, self)

        ## Used as a way to track when the last historical data request was made
        self.__historical_data_req_timestamp = datetime.datetime(year=1980,
                                                                 month=1,
                                                                 day=1,
                                                                 hour=0,
                                                                 minute=0,
                                                                 second=0)

        ## Used to track the latest request_id
        self.req_id = 0

        ## Used to track the next order id
        self.next_order_id = None

        ## Used to store any data requested using a request ID.
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

    def get_client_id(self):
        return self.clientId

    def get_data(self, req_id=None):
        """!
        Returns the data received from the request.

        @param req_id - The Request ID of the originating request.

        @return self.data[req_id] - The data from the specific request.
        @return self.data - If no req_id is provided, returns all data from all requests.
        """
        logger.debug10("Begin Function")

        if req_id:
            logger.debug("Data: %s", self.data)

            # We want to ensure that the data has been received.
            if isinstance(self.data[req_id], list):
                while len(self.data[req_id]) == 0:
                    logger.debug("Waiting on response for Request ID: %s",
                                 req_id)
                    time.sleep(1)
            else:
                while req_id not in self.data:
                    logger.debug("Waiting on response for Request ID: %s",
                                 req_id)
                    time.sleep(1)

            logger.debug3("Data After Waiting: %s", self.data)
            logger.debug3("Returning: %s", self.data[req_id])
            return self.data[req_id]
        else:
            return self.data

    def get_historical_bars(self,
                            contract,
                            bar_size_setting,
                            end_date_time="",
                            duration_str=None,
                            what_to_show="TRADES",
                            use_regular_trading_hours=1,
                            format_date=1,
                            keep_up_to_date=False,
                            chart_options=[]):
        logger.debug10("Begin Function")
        self.req_id += 1

        # if keep_up_to_date is true, end_date_time must be blank.
        # https://interactivebrokers.github.io/tws-api/historical_bars.html
        if keep_up_to_date:
            end_date_time = ""

        self._historical_data_wait()

        logger.debug("Requesting Historical Bars: %s", bar_size_setting)

        self.reqHistoricalData(self.req_id, contract, end_date_time,
                               duration_str, bar_size_setting, what_to_show,
                               use_regular_trading_hours, format_date,
                               keep_up_to_date, chart_options)

        # This is updated here, rather than in the _historical_data_wait function because we want
        # to actually make the request before setting a new timer.
        self.__historical_data_req_timestamp = datetime.datetime.now()

        logger.debug("Request Timestamp: %s",
                     self.__historical_data_req_timestamp)
        self.data[self.req_id] = []
        logger.debug4("Data: %s", self.data)
        logger.debug10("End Funuction")
        return self.req_id

    def get_ipo_date(self,
                     contract,
                     what_to_show="TRADES",
                     use_regular_trading_hours=1,
                     format_date=1):
        """!
        Requests the earliest available bar data for a contract.

        @param contract - The contract
        @param what_to_show -
        @param use_regular_trading_hours - Defaults to 'True'
        @param format_date - Defaults to 'True'

        @return req_id - The request identifier
        """
        logger.debug10("Begin Function")
        logger.debug("Ticker: %s", contract.symbol)

        self.req_id += 1

        # This request seems to trigger the historical data pacing restrictions.  So, we wait.
        self._historical_data_wait()
        self.reqHeadTimeStamp(self.req_id, contract, what_to_show,
                              use_regular_trading_hours, format_date)

        # This is updated here, rather than in the _historical_data_wait function because we want
        # to actually make the request before setting a new timer.
        self.__historical_data_req_timestamp = datetime.datetime.now()

        logger.debug10("End Function")
        return self.req_id

    def get_account_summary(self, account_types="ALL", tags=[]):
        self.req_id += 1
        tags_string = ", ".join([str(item) for item in tags])
        self.reqAccountSummary(self.req_id, account_types, tags_string)
        return self.req_id

    def get_next_order_id(self):
        logger.debug10("Begin Function")
        while self.next_order_id is None:
            logger.debug("Waiting on the next order id")
            time.sleep(1)

        logger.debug("Next Order Id Received.  Next Order Id is: %s",
                     self.next_order_id)

        logger.debug10("End Function")
        return self.next_order_id

    def get_security_data(self, contract):
        logger.debug10("Begin Function")
        self.req_id += 1
        logger.debug("Requesting Contract Details for contract: %s", contract)
        self.reqContractDetails(self.req_id, contract)
        time.sleep(sleep_time)
        logger.debug10("End Function")
        return self.req_id

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

    def place_order(self, contract, order):
        logger.debug("Order: %s", order)
        self.placeOrder(self.next_order_id, contract, order)
        return self.next_order_id

    # ==============================================================================================
    #
    # The following functions respond to data received from Interactive Brokers.  The function
    # names are defined as required by the IB API.  The function parameters have been renamed to
    # lower case formatting.
    #
    # The descriptions are largely copied from the IB API for local reference.
    #
    # ==============================================================================================
    @iswrapper
    def accountDownloadEnd(self, account: str):
        """!
        Notifies when all the account's information has finished.

        @param account - The Accounts Id

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("Account Download Complete for Account: %s", account)
        logger.debug10("End Function")
        return None

    @iswrapper
    def accountSummary(self, req_id: int, account: str, tag: str, value: str,
                       currency: str):
        """!
        Receives the account information. This method will receive the account information just as
        it appears in the TWS' Account Summary Window.

        @param req_id - The Requests Unique ID.
        @param account - The Account ID.
        @param tag - The account's attribute being received.
                     - 	AccountType — Identifies the IB account structure
                     -  NetLiquidation — The basis for determining the price of the assets in your account. Total cash value + stock value + options value + bond value
                     -  TotalCashValue — Total cash balance recognized at the time of trade + futures PNL
                     -  SettledCash — Cash recognized at the time of settlement - purchases at the time of trade - commissions - taxes - fees
                     -  AccruedCash — Total accrued cash value of stock, commodities and securities
                     -  BuyingPower — Buying power serves as a measurement of the dollar value of securities that one may purchase in a securities account without depositing additional funds
                     -  EquityWithLoanValue — Forms the basis for determining whether a client has the necessary assets to either initiate or maintain security positions. Cash + stocks + bonds + mutual funds
                     -  PreviousEquityWithLoanValue — Marginable Equity with Loan value as of 16:00 ET the previous day
                     -  GrossPositionValue — The sum of the absolute value of all stock and equity option positions
                     -  RegTEquity — Regulation T equity for universal account
                     -  RegTMargin — Regulation T margin for universal account
                     -  SMA — Special Memorandum Account: Line of credit created when the market value of securities in a Regulation T account increase in value
                     -  InitMarginReq — Initial Margin requirement of whole portfolio
                     -  MaintMarginReq — Maintenance Margin requirement of whole portfolio
                     -  AvailableFunds — This value tells what you have available for trading
                     -  ExcessLiquidity — This value shows your margin cushion, before liquidation
                     -  Cushion — Excess liquidity as a percentage of net liquidation value
                     -  FullInitMarginReq — Initial Margin of whole portfolio with no discounts or intraday credits
                     -  FullMaintMarginReq — Maintenance Margin of whole portfolio with no discounts or intraday credits
                     -  FullAvailableFunds — Available funds of whole portfolio with no discounts or intraday credits
                     -  FullExcessLiquidity — Excess liquidity of whole portfolio with no discounts or intraday credits
                     -  LookAheadNextChange — Time when look-ahead values take effect
                     -  LookAheadInitMarginReq — Initial Margin requirement of whole portfolio as of next period's margin change
                     -  LookAheadMaintMarginReq — Maintenance Margin requirement of whole portfolio as of next period's margin change
                     -  LookAheadAvailableFunds — This value reflects your available funds at the next margin change
                     -  LookAheadExcessLiquidity — This value reflects your excess liquidity at the next margin change
                     -  HighestSeverity — A measure of how close the account is to liquidation
                     -  DayTradesRemaining — The Number of Open/Close trades a user could put on before Pattern Day Trading is detected. A value of "-1" means that the user can put on unlimited day trades.
                     -  Leverage — GrossPositionValue / NetLiquidation
        @param value - The account's attribute's value.

        @return None
        """
        logger.debug10("Begin Function")
        self.data[req_id] = {
            "account": account,
            "tag": tag,
            "value": value,
            "currency": currency
        }

        logger.debug(
            "Account Summary. ReqId: %s\nAccount: %s, Tag: %s, Value: %s, Currency: %s",
            req_id, account, tag, value, currency)
        logger.debug10("End Function")
        return None

    @iswrapper
    def accountSummaryEnd(self, req_id: int):
        """!
        Notifies when all the accounts' information has been received.

        @param req_id - The Request's identifier

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("Account Summary Completed.  ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def accountUpdateMulti(self, req_id: int, account: str, model_code: str,
                           key: str, value: str, currency: str):
        """!
        Provides the account updates.

        @param req_id - The unique request identifier
        @param account - The account with updates
        @param model_code - The model code with updates
        @param key - The name of the parameter
        @param value - The value of the parameter
        @param currency -The currency of the parameter
        """
        logger.debug10("Begin Function")
        logger.debug("Account Update for %s:", account)
        logger.debug("Model Code: %s", model_code)
        logger.debug("Key: %s", key)
        logger.debug("Value: %s", value)
        logger.debug("Currency: %s", currency)
        logger.debug10("End Function")
        return None

    def accountUpdateMultiEnd(self, req_id: int):
        """!
        Indicates all the account updates have been transmitted.

        @param req_id - The Request's identifier

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("Account Update Completed.  ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def bondContractDetails(self, req_id: int, details: ContractDetails):
        """!
        Delivers the Bond contract data after this has been requested via reqContractDetails. 

        @param req_id - The Unique Reuest Identifier
        @param details - The details for the contract

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def commissionReport(self, commission_report: CommissionReport):
        """!
        provides the CommissionReport of an Execution

        @param commission_report - The Report

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def completedOrder(self, contract: Contract, order: Order,
                       order_state: OrderState):
        """!
        Feeds in completed orders.

        @param contract - The Order's Contract
        @param order - The Completed Order
        @param order_state - The Order's State

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def completedOrderEnd(self):
        """!
        Notifies the end of the completed order's reception.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def connectionClosed(self):
        """!
        Callback to indicate the API connection has closed. Following a API <-> TWS broken socket
        connection, this function is not called automatically but must be triggered by API client
        code.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def contractDetails(self, req_id: int, details: ContractDetails):
        """!
        Receives the full contract's definitions This method will return all contracts matching the
        requested via EClientSocket::reqContractDetails. For example, one can obtain the whole
        option chain with it.

        @param req_id - The Unique Reuest Identifier
        @param details - The details for the contract

        @return None
        """
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

        logger.debug10("End Function")
        return None

    @iswrapper
    def contractDetailsEnd(self, req_id: int):
        """!
        After all contracts matching the request were returned, this method will mark the end of
        their reception.

        @param req_id - The requests identifier.

        @return None
        """
        logger.debug("Contract Details End")
        return None

    @iswrapper
    def currentTime(self, current_time: int):
        """!
        TWS's current time. TWS is synchronized with the server (not local computer) using NTP and
        this function will receive the current time in TWS.

        @param current_time - The current time in Unix timestamp format.
        @return None
        """
        time_now = datetime.datetime.fromtimestamp(current_time)
        logger.info("Current time: %s", time_now)

        return None

    @iswrapper
    def deltaNeutralValidation(self, req_id: int,
                               delta_neutral_contract: DeltaNeutralContract):
        """!
        Upon accepting a Delta-Neutral DN RFQ(request for quote), the server sends a
        deltaNeutralValidation() message with the DeltaNeutralContract structure. If the delta and
        price fields are empty in the original request, the confirmation will contain the current
        values from the server. These values are locked when RFQ is processed and remain locked
        until the RFQ is cancelled.

        @param req_id - The request's Identifier
        @param delta_neutural_contract - Delta-Neutral Contract

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def displayGroupList(self, req_id: int, groups: str):
        """!
        A one-time response to querying the display groups.

        IB API's description doesn't make sense.

        @param req_id - The request's Identifier
        @param groups - TBD.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def displayGroupUpdated(self, req_id: int, contract_info: str):
        """!
        Call triggered once after receiving the subscription request, and will be sent again if the
        selected contract in the subscribed * display group has changed.

        @param req_id - The request's identifier
        @param contract_info - TBD.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def error(self, req_id, code, msg, advanced_order_rejection=""):
        """!
        Errors sent by the TWS are received here.

        Error Code Descriptions can be found at:
        https://interactivebrokers.github.io/tws-api/message_codes.html

      	@param req_id - The request identifier which generated the error. Note: -1 will indicate a
        notification and not true error condition.
        @param code - The Code identifying the error
        @param msg - The error's description
        @param advanced_order_rejection - Advanced Order Reject Description in JSON format.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug2("Interactive Brokers Error Messages")
        critical_codes = [1300]
        error_codes = [
            100, 102, 103, 104, 105, 106, 107, 109, 110, 111, 113, 116, 117,
            118, 119, 120, 121, 122, 123, 124, 125, 126, 129, 131, 132, 162,
            200, 320, 321, 502, 503, 504, 1101, 2100, 2101, 2102, 2103, 2168,
            2169, 10038
        ]
        warning_codes = [101, 501, 1100, 2105, 2107, 2108, 2109, 2110, 2137]
        info_codes = [1102]
        debug_codes = [2104, 2106, 2158]

        if code in critical_codes:
            if advanced_order_rejection:
                logger.critical(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.critical("ReqID# %s, Code: %s (%s)", req_id, code, msg)
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
        elif code in info_codes:
            if advanced_order_rejection:
                logger.info(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.info("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        elif code in debug_codes:
            if advanced_order_rejection:
                logger.debug(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.debug("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        else:
            if advanced_order_rejection:
                logger.error(
                    "ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s",
                    req_id, code, msg, advanced_order_rejection)
            else:
                logger.error("ReqID# %s, Code: %s (%s)", req_id, code, msg)

        logger.debug10("End Function")
        return None

    @iswrapper
    def execDetails(self, req_id: int, contract: Contract,
                    execution: Execution):
        """!
        Provides the executions which happened in the last 24 hours.

        @param req_id - The request's identifier
        @param contract - The contract of the order
        @param execution - The execution details

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def execDetailsEnd(self, req_id: int):
        """!
        indicates the end of the Execution reception.

        @param req_id - The request's identifier

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def familyCodes(self, family_codes):
        """!
        Returns an array of family codes

        @param family_codes - List of Family Codes

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def fundamentalData(self, req_id: int, data: str):
        """!
        Returns fundamental data

        @param req_id - The request's identifier
        @param data - xml-formatted fundamental data

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def headTimestamp(self, req_id: int, head_time_stamp: str):
        """!
        Returns beginning of data for contract for specified data type.

        @param req_id - The request's identifier
        @param head_time_stamp - String Identifying the earliest data date.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("ReqID: %s, IPO Date: %s", req_id, head_time_stamp)
        self.data[req_id] = head_time_stamp

        logger.debug10("End Function")
        return None

    @iswrapper
    def histogramData(self, req_id: int, data):
        """!
        Returns data histogram

        @param req_id - The request's identifier
        @param data - Tuple of histogram data, number of trades at specified price level.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalData(self, req_id: int, bar):
        """!
        Returns the requested historical data bars.

        @param req_id - The request's identifier
        @param bar - The OHLC historical data Bar.  The time zone of the bar is the time zone chosen
        on the TWS login screen. Smallest bar size is 1 second.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug3("ReqID: %s", req_id)
        logger.debug2("Bar: %s", bar)

        self.data[req_id].append(bar)

        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalDataEnd(self, req_id, start, end):
        logger.debug10("Begin Function")
        logger.debug("Data Complete for ReqID: %s from: %s to: %s", req_id,
                     start, end)
        logger.debug10("End Function")

    @iswrapper
    def historicalDataUpdate(self, req_id: int, bar):
        """!
        Receives bars in real time if keepUpToDate is set as True in reqHistoricalData. Similar to
        realTimeBars function, except returned data is a composite of historical data and real time
        data that is equivalent to TWS chart functionality to keep charts up to date. Returned bars
        are successfully updated using real time data.

        @param req_id - The request's identifier
        @param bar - The OHLC historical data Bar. The time zone of the bar is the time zone chosen
        on the TWS login screen. Smallest bar size is 1 second.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug3("ReqID: %s", req_id)
        logger.debug2("Bar: %s", bar)

        #self.data[req_id].
        logger.debug10("End Function")

    @iswrapper
    def historicalNews(self, req_id: int, time: str, provider_code: str,
                       article_id: str, headline: str):
        """!
        Ruturns news headlines

        IB API's description of the parameters is non-existant.

        @param req_id - The request's identifier
        @param time -
        @param provider_code -
        @param article_id -
        @param headline -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalNewsEnd(self, req_id: int, has_more: bool):
        """!
        Returns news headlines end marker

        @param req_id - The request's identifier
        @param has_more - True if there are more results available, false otherwise.

        @return None
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalSchedule(self, req_id: int, start_date_time: str,
                           end_date_time: str, timezone: str, sessions):
        """!
        Returns historical Schedule

        IB API's description of the parameters is non-existant.
        @param req_id - The request's identifier
        @param start_date_time -
        @param end_date_time -
        @param time_zone -
        @param sessions -

        @return None
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalTicks(self, req_id: int, ticks, done: bool):
        """!
        Returns historical tick data when whatToShow=MIDPOINT

        @param req_id - The request's identifier
        @param ticks - list of HistoricalTick data
        @param done - Flag to indicate if all historical tick data has been received.

        @return None
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalTicksBidAsk(self, req_id: int, ticks, done: bool):
        """!
        Returns historical tick data when whatToShow=

        @param req_id - The request's identifier
        @param ticks - list of HistoricalTick data
        @param done - Flag to indicate if all historical tick data has been received.

        @return None
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def historicalTicksLast(self, req_id: int, ticks, done: bool):
        """!
        Returns historical tick data when whatToShow=

        @param req_id - The request's identifier
        @param ticks - list of HistoricalTick data
        @param done - Flag to indicate if all historical tick data has been received.

        @return None
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def managedAccounts(self, accounts: str):
        """!
        Receives a comma-separated string with the managed account ids. Occurs automatically on
        initial API client connection.

        IB API's description of the parameters is non-existant.
        @param accounts -

        @return None
        """
        logger.debug("Accounts: %s", accounts)
        logger.debug10("End Function")
        return None

    @iswrapper
    def marketDataType(self, req_id: int, market_data_type: int):
        """!
        Returns the market data type (real-time, frozen, delayed, delayed-frozen) of ticker sent by
        EClientSocket::reqMktData when TWS switches from real-time to frozen and back and from
        delayed to delayed-frozen and back.

        @param req_id - The id of the ticker sent in reqMktData (I suspect this is wrong, and that
        it should be the req_id for the request sent using reqMktData)
        @param market_data_type - means that now API starts to tick with the following market data:
        1 for real-time, 2 for frozen, 3 for delayed, 4 for delayed-frozen

        @return None
        """
        logger.debug10("End Function")
        return None

    @iswrapper
    def nextValidId(self, order_id: int):
        """ Provides the next order ID """
        super().nextValidId(order_id)

        logger.debug("Setting next_valid_order: %s", order_id)
        self.next_order_id = order_id
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
    def symbolSamples(self, req_id, contract_descriptions):
        logger.debug("Begin Function")
        logger.info("Number of descriptions: %s", len(contract_descriptions))

        self.data[req_id] = []
        for description in contract_descriptions:
            self.data[req_id].append(description)
            logger.info("Symbol: %s", description.contract.symbol)

        logger.debug10("End Function")

    def tickPrice(self, reqId, tickType, price, attrib):
        logger.info("Request Id: %s TickType: %s Price: %s Attrib: %s", reqId,
                    tickType, price, attrib)

    # ==============================================================================================
    #
    # Internal Helper Functions
    #
    # ==============================================================================================
    def _historical_data_wait(self):
        """!
        Ensure that we wait 15 seconds between historical data requests.

        @param self

        @return None
        """
        time_diff = datetime.datetime.now(
        ) - self.__historical_data_req_timestamp
        while time_diff.total_seconds() < sleep_time:
            logger.debug("Now: %s", datetime.datetime.now())
            logger.debug("Last Request: %s",
                         self.__historical_data_req_timestamp)
            logger.debug("Time Difference: %s seconds",
                         time_diff.total_seconds())
            remaining_sleep_time = sleep_time - time_diff.total_seconds()
            logger.debug("Sleep Time: %s", remaining_sleep_time)
            time.sleep(sleep_time - time_diff.total_seconds())
            time_diff = datetime.datetime.now(
            ) - self.__historical_data_req_timestamp
        return None


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
