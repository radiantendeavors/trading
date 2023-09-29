"""!
@package pytrader.libs.clients.broker.ibkr.tws

Provides the client for Interactive Brokers TWSAPI.

@author G. S. Derber
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

@file pytrader/libs/clients/broker/ibkr/tws/__init__.py

Provides the client for Interactive Brokers TWSAPI.

This is the only file to not use snake_case for functions or variables.  This is to match TWSAPI
abstract function names, and their variables.
"""
# ==================================================================================================
#
# This file requires special pylint rules to match the API format.
#
# C0103: Invalid Name
# C0104: Bad name (bar)
# C0302: too many lines
# R0913: too many arguments
# R0904: too many public methods
#
# pylint: disable=C0103,C0104,C0302,R0913,R0904
#
# ==================================================================================================
# Standard Libraries
import datetime
import multiprocessing
import threading
from decimal import Decimal
from typing import Optional

# 3rd Party Libraries
from ibapi.client import EClient
from ibapi.commission_report import CommissionReport
from ibapi.common import BarData, TickAttrib, TickAttribBidAsk, TickAttribLast
from ibapi.contract import Contract, ContractDetails, DeltaNeutralContract
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.utils import iswrapper
from ibapi.wrapper import EWrapper

# Application Libraries
from pytrader.libs.clients.broker.baseclient import BaseBroker
from pytrader.libs.system import logging
from pytrader.libs.utilities.exceptions import BrokerNotAvailable

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## Instance of Logging class
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsReader(EWrapper, EClient, BaseBroker):
    """!
    Serves as the client interface for Interactive Brokers
    """
    ## Used to track the number of available market data lines
    __available_market_data_lines = 100

    ## Used to track available streams of level 2 data
    __available_deep_data_allotment = 3

    def __init__(self) -> None:
        """!
        Initialize the IbkrClient class

        @return None
        """
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        BaseBroker.__init__(self)

        self.history_begin_ids = {}
        self.req_id = 0

    def req_head_timestamp(self,
                           req_id: int,
                           contract: Contract,
                           what_to_show: Optional[str] = "TRADES",
                           use_regular_trading_hours: Optional[bool] = True,
                           format_date: Optional[bool] = True) -> None:
        """!
        Requests the earliest available bar data for a contract.

        @param contract: The contract
        @param what_to_show: Type of information to show, defaults to "TRADES"
        @param use_regular_trading_hours: Defaults to 'True'
        @param format_date: Defaults to 'True'

        @return req_id: The request identifier
        """
        logger.debug("Process Name: %s", multiprocessing.current_process().name)
        logger.debug("Thread Name: %s", threading.current_thread().name)
        self.history_begin_ids[req_id] = contract.localSymbol
        self.req_id += 1
        logger.debug(self)
        logger.debug(self.history_begin_ids)
        logger.debug(self.contract_history_begin_subjects)
        self.reqHeadTimeStamp(req_id, contract, what_to_show, use_regular_trading_hours,
                              format_date)

    # ==============================================================================================
    #
    # The following functions respond to data received from Interactive Brokers.  The function
    # names are defined as required by the IB API.
    #
    # The descriptions are largely copied from the IB API for local reference.
    #
    # ==============================================================================================
    @iswrapper
    def accountDownloadEnd(self, accountName: str) -> None:
        """!
        Notifies when all the account's information has finished.

        @param account: The Accounts Id

        @return None
        """
        logger.debug("Account Download Complete for Account: %s", accountName)

    @iswrapper
    def accountSummary(self, reqId: int, account: str, tag: str, value: str, currency: str) -> None:
        """!
        Receives the account information. This method will receive the account information just as
        it appears in the TWS' Account Summary Window.

        @param reqId: The Requests Unique ID.
        @param account: The Account ID.
        @param tag: The account's attribute being received.
            - AccountType — Identifies the IB account structure
            - NetLiquidation — The basis for determining the price of the assets in your account.
              Total cash value + stock value + options value + bond value
            - TotalCashValue — Total cash balance recognized at the time of trade + futures PNL
            - SettledCash — Cash recognized at the time of settlement - purchases at the time of
                            trade - commissions - taxes - fees
            - AccruedCash — Total accrued cash value of stock, commodities and securities
            - BuyingPower — Buying power serves as a measurement of the dollar value of securities
                            that one may purchase in a securities account without depositing
                            additional funds
            - EquityWithLoanValue — Forms the basis for determining whether a client has the
                                    necessary assets to either initiate or maintain security
                                    positions.
                                    EquityWithLoanValue = Cash + stocks + bonds + mutual funds
            - PreviousEquityWithLoanValue — Marginable Equity with Loan value as of 16:00 ET the
                                            previous day
            - GrossPositionValue — The sum of the absolute value of all stock and equity option
                                   positions
            - RegTEquity — Regulation T equity for universal account
            - RegTMargin — Regulation T margin for universal account
            - SMA — Special Memorandum Account: Line of credit created when the market value of
                    securities in a Regulation T account increase in value
            - InitMarginReq — Initial Margin requirement of whole portfolio
            - MaintMarginReq — Maintenance Margin requirement of whole portfolio
            - AvailableFunds — This value tells what you have available for trading
            - ExcessLiquidity — This value shows your margin cushion, before liquidation
            - Cushion — Excess liquidity as a percentage of net liquidation value
            - FullInitMarginReq — Initial Margin of whole portfolio with no discounts or intraday
                                  credits
            - FullMaintMarginReq — Maintenance Margin of whole portfolio with no discounts or
                                   intraday credits
            - FullAvailableFunds — Available funds of whole portfolio with no discounts or intraday
                                   credits
            - FullExcessLiquidity — Excess liquidity of whole portfolio with no discounts or
                                    intraday credits
            - LookAheadNextChange — Time when look-ahead values take effect
            - LookAheadInitMarginReq — Initial Margin requirement of whole portfolio as of next
                                       period's margin change
            - LookAheadMaintMarginReq — Maintenance Margin requirement of whole portfolio as of next
                                        period's margin change
            - LookAheadAvailableFunds — This value reflects your available funds at the next margin
                                        change
            - LookAheadExcessLiquidity — This value reflects your excess liquidity at the next
                                         margin change
            - HighestSeverity — A measure of how close the account is to liquidation
            - DayTradesRemaining — The Number of Open/Close trades a user could put on before
                                   Pattern Day Trading is detected. A value of "-1" means that the
                                   user can put on unlimited day trades.
            - Leverage — GrossPositionValue / NetLiquidation
        @param value: The account's attribute's value.

        @return None
        """
        logger.debug("Account Summary. ReqId: %s\nAccount: %s, Tag: %s, Value: %s, Currency: %s",
                     reqId, account, tag, value, currency)

    @iswrapper
    def accountSummaryEnd(self, reqId: int) -> None:
        """!
        Notifies when all the accounts' information has been received.

        @param reqId: The Request's identifier

        @return None
        """
        logger.debug("Account Summary Completed.  ReqId: %s", reqId)

    @iswrapper
    def accountUpdateMulti(self, reqId: int, account: str, modelCode: str, key: str, value: str,
                           currency: str):
        """!
        Provides the account updates.

        @param reqId: The unique request identifier
        @param account: The account with updates
        @param model_code: The model code with updates
        @param key: The name of the parameter
        @param value: The value of the parameter
        @param currency: The currency of the parameter

        @return
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Account Update for %s:", account)
        logger.debug("Model Code: %s", modelCode)
        logger.debug("Key: %s", key)
        logger.debug("Value: %s", value)
        logger.debug("Currency: %s", currency)

    @iswrapper
    def accountUpdateMultiEnd(self, reqId: int) -> None:
        """!
        Indicates all the account updates have been transmitted.

        @param reqId: The Request's identifier

        @return None
        """
        logger.debug("Account Update Completed.  ReqId: %s", reqId)

    @iswrapper
    def bondContractDetails(self, reqId: int, contractDetails: ContractDetails) -> None:
        """!
        Delivers the Bond contract data after this has been requested via reqContractDetails.

        @param reqId: The Unique Reuest Identifier
        @param contractDetails: The details for the contract

        @return None
        """
        logger.debug("Bond Contract Details: %s\n%s", reqId, contractDetails)

    @iswrapper
    def commissionReport(self, commissionReport: CommissionReport) -> None:
        """!
        provides the CommissionReport of an Execution

        @param commissionReport: The Report

        @return None
        """
        logger.debug("Commission Report: %s", commissionReport)

    @iswrapper
    def completedOrder(self, contract: Contract, order: Order, orderState: OrderState):
        """!
        Feeds in completed orders.

        @param contract: The Order's Contract
        @param order: The Completed Order
        @param order_state: The Order's State

        @return
        """
        logger.debug("Completed Order for %s\n%s\n%s", contract, order, orderState)

    @iswrapper
    def completedOrdersEnd(self):
        """!
        Notifies the end of the completed order's reception.

        @return
        """
        logger.debug("All data received for completed order")

    @iswrapper
    def connectionClosed(self) -> None:
        """!
        Callback to indicate the API connection has closed. Following a API <-> TWS broken socket
        connection, this function is not called automatically but must be triggered by API client
        code.

        @return None
        """
        # send_item = "ConnectionClosed"

        # reqId_list = list(self.bar_queue)
        # logger.debug("Sending Queue Item: %s", send_item)
        # for item in reqId_list:
        #     self.bar_queue[item].put(send_item)

        logger.warning("Connection Closed for client id: %s", self.clientId)

    @iswrapper
    def contractDetails(self, reqId: int, contractDetails: ContractDetails) -> None:
        """!
        Receives the full contract's definitions This method will return all contracts matching the
        requested via EClientSocket::reqContractDetails. For example, one can obtain the whole
        option chain with it.

        @param reqId: The Unique Reuest Identifier
        @param contractDetails: The details for the contract

        @return None
        """
        self.contract_subjects.set_contract_details(reqId, contractDetails)

    @iswrapper
    def contractDetailsEnd(self, reqId: int):
        """!
        After all contracts matching the request were returned, this method will mark the end of
        their reception.

        @param reqId: The requests identifier.

        @return
        """
        logger.debug6("Contract Details Received for request id: %s", reqId)

    @iswrapper
    def currentTime(self, time: int) -> None:
        """!
        TWS's current time. TWS is synchronized with the server (not local computer) using NTP and
        this function will receive the current time in TWS.

        @param time: The current time in Unix timestamp format.

        @return None
        """
        time_now = datetime.datetime.fromtimestamp(time)
        logger.debug6("Current time: %s", time_now)

    @iswrapper
    def deltaNeutralValidation(self, reqId: int,
                               deltaNeutralContract: DeltaNeutralContract) -> None:
        """!
        Upon accepting a Delta-Neutral DN RFQ(request for quote), the server sends a
        deltaNeutralValidation() message with the DeltaNeutralContract structure. If the delta and
        price fields are empty in the original request, the confirmation will contain the current
        values from the server. These values are locked when RFQ is processed and remain locked
        until the RFQ is cancelled.

        @param reqId: The request's Identifier
        @param delta_neutural_contract: Delta-Neutral Contract

        @return None
        """
        logger.debug("ReqId: %s  Delta Neutral Contract: %s", reqId, deltaNeutralContract)

    @iswrapper
    def displayGroupList(self, reqId: int, groups: str) -> None:
        """!
        A one-time response to querying the display groups.

        @param reqId: The request's Identifier
        @param groups: (IB API doesn't list a description, instead it lists a description for:
        @param lt: Returns a list of integers representing visible Group ID separated by the "|"
            character, and sorted by most used group first. )

        @return None
        """
        logger.debug("ReqId: %s  Groups: %s", reqId, groups)

    @iswrapper
    def displayGroupUpdated(self, reqId: int, contractInfo: str) -> None:
        """!
        Call triggered once after receiving the subscription request, and will be sent again if the
        selected contract in the subscribed * display group has changed.

        @param reqId: The request's identifier
        @param contractInfo: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("ReqId: %s  ContractInfo: %s", reqId, contractInfo)

    @iswrapper
    def error(self,
              reqId: int,
              errorCode: int,
              errorString: str,
              advanced_order_rejection: str = "") -> None:
        """!
        Errors sent by the TWS are received here.

        Error Code Descriptions can be found at:
        https://interactivebrokers.github.io/tws-api/message_codes.html

        @param reqId: The request identifier which generated the error. Note: -1 will indicate a
            notification and not true error condition.
        @param code: The Code identifying the error
        @param msg: The error's description
        @param advanced_order_rejection: Advanced Order Reject Description in JSON format.

        @return None
        """
        critical_codes = [1300]
        error_codes = [
            100, 102, 103, 104, 105, 106, 107, 109, 110, 111, 113, 116, 117, 118, 119, 120, 121,
            122, 123, 124, 125, 126, 129, 131, 132, 162, 200, 320, 321, 502, 503, 504, 1101, 2100,
            2101, 2102, 2103, 2168, 2169, 10038, 10147
        ]
        warning_codes = [101, 501, 1100, 2105, 2107, 2108, 2109, 2110, 2137]
        info_codes = [1102]
        debug_codes = [2104, 2106, 2158]

        if errorCode in critical_codes:
            self._process_critical_code(reqId, errorCode, errorString, advanced_order_rejection)
        elif errorCode in error_codes:
            self._process_error_code(reqId, errorCode, errorString, advanced_order_rejection)
        elif errorCode in warning_codes:
            self._process_warning_code(reqId, errorCode, errorString, advanced_order_rejection)
        elif errorCode in info_codes:
            self._process_info_code(reqId, errorCode, errorString, advanced_order_rejection)
        elif errorCode in debug_codes:
            self._process_debug_code(reqId, errorCode, errorString, advanced_order_rejection)
        else:
            logger.error("Error Code Level has not been identified")
            self._process_error_code(reqId, errorCode, errorString, advanced_order_rejection)

    @iswrapper
    def execDetails(self, reqId: int, contract: Contract, execution: Execution) -> None:
        """!
        Provides the executions which happened in the last 24 hours.

        @param reqId: The request's identifier
        @param contract: The contract of the order
        @param execution: The execution details

        @return None
        """
        logger.debug("Req Id: %s", reqId)
        msg = {"order_execution": {execution.OrderId: {contract.localSymbol: execution}}}
        logger.debug(msg)

    @iswrapper
    def execDetailsEnd(self, reqId: int) -> None:
        """!
        Indicates the end of the Execution reception.

        @param reqId: The request's identifier

        @return None
        """
        logger.debug("Ending Execution for reqId: %s", reqId)

    @iswrapper
    def familyCodes(self, familyCodes: list) -> None:
        """!
        Returns an array of family codes

        @param familyCodes: List of Family Codes

        @return None
        """
        logger.debug("Family Codes: %s", familyCodes)

    @iswrapper
    def fundamentalData(self, reqId: int, data: str) -> None:
        """!
        Returns fundamental data

        @param reqId: The request's identifier
        @param data: xml-formatted fundamental data

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Data: %s", data)

    @iswrapper
    def headTimestamp(self, reqId: int, headTimestamp: str) -> None:
        """!
        Returns beginning of data for contract for specified data type.

        @param reqId: The request's identifier
        @param head_time_stamp: String Identifying the earliest data date.

        @return None
        """
        logger.debug(self.req_id)
        logger.debug(self.history_begin_ids)
        self.contract_history_begin_subjects.history_begin_ids = self.history_begin_ids
        logger.debug(self.contract_history_begin_subjects)
        self.contract_history_begin_subjects.set_history_begin_date(reqId, headTimestamp)

    @iswrapper
    def histogramData(self, reqId: int, items: list) -> None:
        """!
        Returns data histogram

        @param reqId: The request's identifier
        @param items: Tuple of histogram data, number of trades at specified price level.
                      NOTE: Who the fuck though this name was a good idea?  Looking at you IBKR!

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Data: %s", items)

    @iswrapper
    def historicalData(self, reqId: int, bar: BarData) -> None:
        """!
        Returns the requested historical data bars.

        @param reqId: The request's identifier
        @param bar: The OHLC historical data Bar.  The time zone of the bar is the time zone chosen
        on the TWS login screen. Smallest bar size is 1 second.

        @return None
        """
        logger.debug6("ReqID: %s", reqId)
        logger.debug6("Bar: %s", bar)

        # msg = {"historical_bar": {reqId, bar}}

    @iswrapper
    def historicalDataEnd(self, reqId: int, start: str, end: str) -> None:
        """!
        Marks the ending of the historical bars reception.

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param start: FIXME: This is not documented by the TWSAPI
        @param end: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug6("Data Complete for ReqID: %s from: %s to: %s", reqId, start, end)
        # msg = {"historical_bar": {reqId: "complete"}}

    @iswrapper
    def historicalDataUpdate(self, reqId: int, bar: BarData) -> None:
        """!
        Receives bars in real time if keepUpToDate is set as True in reqHistoricalData. Similar to
        realTimeBars function, except returned data is a composite of historical data and real time
        data that is equivalent to TWS chart functionality to keep charts up to date. Returned bars
        are successfully updated using real time data.

        @param reqId: The request's identifier
        @param bar: The OHLC historical data Bar. The time zone of the bar is the time zone chosen
            on the TWS login screen. Smallest bar size is 1 second.

        @return None
        """
        logger.debug("Begin Function")
        logger.debug("ReqID: %s", reqId)
        logger.debug("Bar: %s", bar)
        date_time = datetime.datetime.now()

        send_item = [reqId, date_time, bar]
        logger.debug("Sending Queue Item: %s", send_item)
        self.queue.put(send_item)

        logger.debug("End Function")

    @iswrapper
    def historicalNews(self, requestId: int, time: str, providerCode: str, articleId: str,
                       headline: str) -> None:
        """!
        Ruturns news headlines

        IB API's description of the parameters is non-existant.
        @param requestId: The request's identifier
                          NOTE: This matches the API.  The fucking API is not consistent in its
                          naming conventions.
        @param time: FIXME: This is not documented by the TWSAPI
        @param provider_code: FIXME: This is not documented by the TWSAPI
        @param article_id: FIXME: This is not documented by the TWSAPI
        @param headline: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("ReqId: %s", requestId)
        logger.debug("Time: %s", time)
        logger.debug("Provider Code: %s", providerCode)
        logger.debug("ArticleId: %s", articleId)
        logger.debug("Headline: %s", headline)

    @iswrapper
    def historicalNewsEnd(self, requestId: int, hasMore: bool) -> None:
        """!
        Returns news headlines end marker

        @param requestId: The request's unique identifier
                          NOTE: This matches the API.  The fucking API is not consistent in its
                          naming conventions.
        @param hasMore: True if there are more results available, false otherwise.

        @return None
        """
        logger.debug("ReqId: %s", requestId)
        logger.debug("Has More: %s", hasMore)

    @iswrapper
    def historicalSchedule(self, reqId: int, startDateTime: str, endDateTime: str, timezone: str,
                           sessions: list) -> None:
        """!
        Returns historical Schedule when reqHistoricalData whatToShow="SCHEDULE"

        IB API's description of the parameters is non-existant.
        @param reqId: The request identifier used to call eClient.reqHistoricalData
        @param start_date_time: FIXME: This is not documented by the TWSAPI
        @param end_date_time: FIXME: This is not documented by the TWSAPI
        @param time_zone: FIXME: This is not documented by the TWSAPI
        @param sessions: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Start DateTime: %s", startDateTime)
        logger.debug("End DateTime: %s", endDateTime)
        logger.debug("Timezone: %s", timezone)
        logger.debug("Sessions: %s", sessions)

    @iswrapper
    def historicalTicks(self, reqId: int, ticks: list, done: bool) -> None:
        """!
        Returns historical tick data when whatToShow="MIDPOINT"

        @param reqId: The request identifier used to call eClient.reqHistoricalTicks
        @param ticks: list of HistoricalTick data
        @param done: Flag to indicate if all historical tick data has been received.

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Ticks: %s", ticks)
        logger.debug("Done: %s", done)

    @iswrapper
    def historicalTicksBidAsk(self, reqId: int, ticks: list, done: bool) -> None:
        """!
        Returns historical tick data when whatToShow="BID ASK"

        @param reqId: The request identifier used to call eClient.reqHistoricalTicks
        @param ticks: list of HistoricalTick data
        @param done: Flag to indicate if all historical tick data has been received.

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Ticks: %s", ticks)
        logger.debug("Done: %s", done)

    @iswrapper
    def historicalTicksLast(self, reqId: int, ticks: list, done: bool) -> None:
        """!
        Returns historical tick data when whatToShow="TRADES"

        @param reqId: The request identifier used to call eClient.reqHistoricalTicks
        @param ticks: list of HistoricalTick data
        @param done: Flag to indicate if all historical tick data has been received.

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Ticks: %s", ticks)
        logger.debug("Done: %s", done)

    @iswrapper
    def managedAccounts(self, accountsList: str) -> None:
        """!
        Receives a comma-separated string with the managed account ids. Occurs automatically on
        initial API client connection.

        @param accountsList: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug6("Accounts: %s", accountsList)
        # msg = {"accounts": self.accounts}

    @iswrapper
    def marketDataType(self, reqId: int, marketDataType: int):
        """!
        Returns the market data type (real-time, frozen, delayed, delayed-frozen) of ticker sent by
        EClientSocket::reqMktData when TWS switches from real-time to frozen and back and from
        delayed to delayed-frozen and back.

        IB API Descriptions: TODO: Validate
        @param reqId: The ticker identifier used to call eClient.reqMktData (I suspect this is
                       wrong, and that it should be the reqId for the request sent using
                       reqMktData)
        @param market_data_type: means that now API starts to tick with the following market data:
                     1 for real-time
                     2 for frozen
                     3 for delayed
                     4 for delayed-frozen

        @return
        """
        data_type_string = {1: "Real Time", 2: "Frozen", 3: "Delayed", 4: "Delayed and Frozen"}
        logger.debug6("Market Data type for req id %s currently set to '%s'", reqId,
                      data_type_string[marketDataType])

    @iswrapper
    def marketRule(self, marketRuleId: int, priceIncrements: list) -> None:
        """!
        Returns minimum price increment structure for a particular market rule ID market rule IDs
        for an instrument on valid exchanges can be obtained from the contractDetails object for
        that contract.

        IB API's description of the parameters is non-existant.
        @param market_rule_id: FIXME: This is not documented by the TWSAPI
        @param price_increments: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("Market Rule Id: %s", marketRuleId)
        logger.debug("Price Increments: %s", priceIncrements)

    @iswrapper
    def mktDepthExchanges(self, depthMktDataDescriptions: list) -> None:
        """!
        Called when receives Depth Market Data Descriptions.

        @param depth_market_data_descriptions: Stores a list of DepthMktDataDescription

        @return None
        """
        logger.debug("Depth Market Data Descriptions: %s", depthMktDataDescriptions)

    @iswrapper
    def newsArticle(self, requestId: int, articleType: int, articleText: str) -> None:
        """!
        called when receives News Article

        @param requestId: The request identifier used to call eClient.reqNewsArticle()
                          NOTE: This matches the API.  The fucking API is not consistent in its
                          naming conventions.
        @param article_type: The type of news article:
              - 0 - Plain Text or HTML
              - 1 - Binary Data / PDF
        @param article_text: The body of the article (if article_type == 1: the binary data is
              encoded using the Base64 scheme)

        @return None
        """
        logger.debug("ReqId: %s", requestId)
        logger.debug("Article Type: %s", articleType)
        logger.debug("Article Text: %s", articleText)

    @iswrapper
    def newsProviders(self, newsProviders: list) -> None:
        """!
        Returns array of subscribed API news providers for this user.

        @param newsProviders: Array of subscribed API news providers for this user.

        @return None
        """
        logger.debug("News Providers: %s", newsProviders)

    @iswrapper
    def nextValidId(self, orderId: int) -> None:
        """!
        Receives next valid order id. Will be invoked automatically upon successfull API client
        connection, or after call to EClient::reqIds Important: the next valid order ID is only
        valid at the time it is received.

        @param order_id: The next order id.

        @return None
        """
        self.order_id_subjects.send_order_id(orderId)

    @iswrapper
    def openOrder(self, orderId: int, contract: Contract, order: Order,
                  orderState: OrderState) -> None:
        """!
        Called in response to the submitted order.

        @param orderId: The order's unique identifier
        @param contract: The order's Contract
        @param order: The currently active Order
        @param orderState: The order's OrderState

        @return None
        """
        logger.debug9("Order Id: %s", orderId)
        logger.debug9("Contract: %s", contract.localSymbol)
        logger.debug9("Order: %s", order)
        logger.debug9("Order state: %s", orderState)

    @iswrapper
    def openOrderEnd(self) -> None:
        """!
        Notifies the end of the open orders' reception.

        @return None
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def orderBound(self, reqId: int, apiClientId: int, apiOrderId: int) -> None:
        """!
        Response to API Bind Order Control Message

        @param reqId: permId FIXME: TWSAPI is fucked.  API docs, the variable name is 'orderId'
                      Also, the API docs description tells me nothing.
        @param api_client_id: API client Id.
        @param api_order_id: API order id.

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("ApiClientId: %s", apiClientId)
        logger.debug("ApiOrderId: %s", apiOrderId)

    @iswrapper
    def orderStatus(self, orderId: int, status: str, filled: Decimal, remaining: Decimal,
                    avgFillPrice: float, permId: int, parentId: int, lastFillPrice: float,
                    clientId: int, whyHeld: str, mktCapPrice: float) -> None:
        """!
        Gives the up-to-date information of an order every time it changes. Often there are
        duplicate orderStatus messages.

        IB API Descriptions - TODO: Validate (I suspect they aren't accurate descriptions)
        @param orderId: The order's client id
        @param status: The current status of the order. Possible values:
            - PendingSubmit - indicates that you have transmitted the order, but have not yet
              received confirmation that it has been accepted by the order destination.
            - PendingCancel - indicates that you have sent a request to cancel the order but have
              not yet received cancel confirmation from the order destination. At this point, your
              order is not confirmed canceled. It is not guaranteed that the cancellation will be
              successful.
            - PreSubmitted - indicates that a simulated order type has been accepted by the IB
              system and that this order has yet to be elected. The order is held in the IB system
              until the election criteria are met. At that time the order is transmitted to the
              order destination as specified .
            - Submitted - indicates that your order has been accepted by the system.
            - ApiCancelled - after an order has been submitted and before it has been acknowledged,
              an API client client can request its cancelation, producing this state.
            - Cancelled - indicates that the balance of your order has been confirmed canceled by
              the IB system. This could occur unexpectedly when IB or the destination has rejected
              your order.
            - Filled - indicates that the order has been completely filled. Market orders executions
              will not always trigger a Filled status.
            - Inactive - indicates that the order was received by the system but is no longer active
              because it was rejected or canceled
        @param filled: The number of filled positions
        @param remaining: The remnant positions
        @param avgFillPrice: The Average filling price
        @param permId: The order's permId used by the TWS to identify orders
        @param parentId: Parent's id.  Used for bracket and auto trailing stop orders.
        @param lastFillPrice: Price at which the last position was filled.
        @param clientId: API client that submitted the order.
        @param whyHeld: this field is used to identify an order held when TWS is trying to locate
            shares for a short sell. The value used to indicate this is 'locate'.
        @param mktCapPrice: If an order has been capped, this indicates the current capped price.

        @return None
        """
        logger.debug9("Order Id: %s", orderId)
        logger.debug9("Status: %s", status)
        logger.debug9("Number of filled positions: %s", filled)
        logger.debug9("Number of unfilled positions: %s", remaining)
        logger.debug9("Average fill price: %s", avgFillPrice)
        logger.debug9("TWS ID: %s", permId)
        logger.debug9("Parent Id: %s", parentId)
        logger.debug9("Last Fill Price: %s", lastFillPrice)
        logger.debug9("Client Id: %s", clientId)
        logger.debug9("Why Held: %s", whyHeld)
        logger.debug9("Market Cap Price: %s", mktCapPrice)

        # msg = {
        #     "order_status": {
        #         orderId: {
        #             "status": status,
        #             "filled": filled,
        #             "remaining": remaining,
        #             "average_fill_price": avgFillPrice,
        #             "perm_id": permId,
        #             "parent_id": parentId,
        #             "last_fill_price": lastFillPrice,
        #             "client_id": clientId,
        #             "why_held": whyHeld,
        #             "market_cap_price": mktCapPrice
        #         }
        #     }
        # }

    @iswrapper
    def pnl(self, reqId: int, dailyPnL: float, unrealizedPnL: float, realizedPnL: float) -> None:
        """!
        Receives PnL updates in real time for the daily PnL and the total unrealized PnL for an
        account.

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param daily_pnl: dailyPnL updates for the account in real time
        @param unrealized_pnl: total unRealized PnL updates for the account in real time
        @param realized_pnl: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("ReqId %s", reqId)
        logger.debug("Daily PnL: %s", dailyPnL)
        logger.debug("Unrealized PnL: %s", unrealizedPnL)
        logger.debug("RealizedPnl: %s", realizedPnL)

    @iswrapper
    def pnlSingle(self, reqId: int, pos: Decimal, dailyPnL: float, unrealizedPnL: float,
                  realizedPnL: float, value: float) -> None:
        """!
        Receives real time updates for single position daily PnL values.

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param pos: The current size of the position
        @param dailyPnL: daily PnL for the position
        @param unrealizedPnL: FIXME: This is not documented by the TWSAPI
        @param realizedPnL: total unrealized PnL for the position (since inception) updating in
            real time
        @param value: Current market value of the position.

        @return None
        """
        logger.debug("ReqId %s", reqId)
        logger.debug("Position: %s", pos)
        logger.debug("Daily PnL: %s", dailyPnL)
        logger.debug("Unrealized PnL: %s", unrealizedPnL)
        logger.debug("RealizedPnl: %s", realizedPnL)
        logger.debug("Value: %s", value)

    @iswrapper
    def position(self, account: str, contract: Contract, position: Decimal, avgCost: float) -> None:
        """!
        Provides the portfolio's open positions.

        IB API's description.  TODO: Verify
        @param account: The account holding the position.
        @param contract: The position's Contract
        @param position: The number of positions held
        @param avg_cost: The average cost of the position

        @return None
        """
        logger.debug("%s Position in %s: %s (%s)", account, contract.symbol, position, avgCost)

    @iswrapper
    def positionEnd(self) -> None:
        """!
        Indicates all positions have been transmitted.

        @return None
        """
        logger.debug("All Positions Received")

    @iswrapper
    def positionMulti(self, reqId: int, account: str, modelCode: str, contract: Contract,
                      pos: Decimal, avgCost: float) -> None:
        """!
        provides the portfolio's open positions.

        @param reqId: the id of request
        @param account: the account holding the position.
        @param modelCode: the model code holding the position.
        @param contract: the position's Contract
        @param pos: the number of positions held.
        @param avgCost: the average cost of the position.

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Account: %s", account)
        logger.debug("Model Code: %s", modelCode)
        logger.debug("Contract: %s", contract)
        logger.debug("Positions: %s", pos)
        logger.debug("Ave Cost: %s", avgCost)

    @iswrapper
    def positionMultiEnd(self, reqId: int) -> None:
        """!
        Indicates all positions have been transmitted.

        @param reqId: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("Position Multi End for ReqId: %s", reqId)

    @iswrapper
    def realtimeBar(self, reqId: int, time: int, open_: float, high: float, low: float,
                    close: float, volume: Decimal, wap: Decimal, count: int) -> None:
        """!
        Updates the real time 5 seconds bars

        @param reqId: the request's identifier
        @param time: the bar's date and time (Epoch/Unix time)
        @param open_: the bar's open point
        @param high: the bar's high point
        @param low: the bar's low point
        @param close: the bar's closing point
        @param volume: the bar's traded volume (only returned for TRADES data)
        @param wap: the bar's Weighted Average Price rounded to minimum increment (only
            available for TRADES).
        @param count: the number of trades during the bar's timespan (only available for TRADES)

        @return None
        """
        ohlc_bar = [time, open_, high, low, close, volume, wap, count]
        msg = {"real_time_bars": {reqId: ohlc_bar}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def receiveFA(self, faData: int, cxml: str) -> None:
        """!
        Receives the Financial Advisor's configuration available in the TWS

        @param faData: one of:
            1. Groups: offer traders a way to create a group of accounts and apply a single
               allocation method to all accounts in the group.
            2. Profiles: let you allocate shares on an account-by-account basis using a predefined
               calculation value.
            3. Account Aliases: let you easily identify the accounts by meaningful names rather than
               account numbers.
        @param cxml: the xml-formatted configuration

        @return None
        """
        logger.debug("FA DataType: %s", faData)
        logger.debug("FA XML Data: %s", cxml)

    @iswrapper
    def replaceFAEnd(self, reqId: int, text: str):
        """!
        Notifies the end of the FA replace.

        @param reqId: The request's id.
        @param text: The message text.

        @return
        """
        logger.debug("ReqId: %s  Text: %s", reqId, text)

    @iswrapper
    def rerouteMktDataReq(self, reqId: int, conId: int, exchange: str) -> None:
        """!
        Returns con_id and exchange for CFD market data request re-route.

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param con_id: The underlying instrument which has market data.
        @param exchange: The underlying's exchange.

        @return None
        """
        logger.debug("ReqId: %s  ConId: %s  Exchange: %s", reqId, conId, exchange)

    @iswrapper
    def rerouteMktDepthReq(self, reqId: int, conId: int, exchange: str) -> None:
        """!
        Returns the conId and exchange for an underlying contract when a request is made for level 2
        data for an instrument which does not have data in IB's database. For example stock CFDs and
        index CFDs.

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param conId: FIXME: This is not documented by the TWSAPI
        @param exchange: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("ReqId: %s  ConId: %s  Exchange: %s", reqId, conId, exchange)

    @iswrapper
    def scannerData(self, reqId: int, rank: int, contractDetails: ContractDetails, distance: str,
                    benchmark: str, projection: str, legsStr: str) -> None:
        """!
        provides the data resulting from the market scanner request.

        @param reqid: the request's identifier.
        @param rank: the ranking within the response of this bar.
        @param contractDetails: the data's ContractDetails
        @param distance: according to query.
        @param benchmark: according to query.
        @param projection: according to query.
        @param legsStr: describes the combo legs when the scanner is returning EFP

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Rank: %s", rank)
        logger.debug("Contract Details: %s", contractDetails)
        logger.debug("Distance: %s", distance)
        logger.debug("Benchmark: %s", benchmark)
        logger.debug("Projection: %s", projection)
        logger.debug("Legs String: %s", legsStr)

    @iswrapper
    def scannerDataEnd(self, reqId: int) -> None:
        """!
        Indicates the scanner data reception has terminated.

        @param reqId: The request's id.

        @return None
        """
        logger.debug("Scanner Data Ended for ReqId: %s", reqId)

    @iswrapper
    def scannerParameters(self, xml: str) -> None:
        """!
        Provides the xml-formatted parameters available from TWS market scanners (not all available
        in API).

        @param xml: The xml-formatted string with the available parameters.

        @return None
        """
        logger.debug("Scanner Parameters: %s", xml)

    @iswrapper
    def securityDefinitionOptionParameter(self, reqId: int, exchange: str, underlyingConId: int,
                                          tradingClass: str, multiplier: str, expirations: set,
                                          strikes: set) -> None:
        """!
        Returns the option chain for an underlying on an exchange specified in reqSecDefOptParams
        There will be multiple callbacks to securityDefinitionOptionParameter if multiple exchanges
        are specified in reqSecDefOptParams

        @param reqId: ID of the request initiating the callback
        @param underlyingConId: The conID of the underlying security
        @param tradingClass: the option trading class
        @param multiplier: the option multiplier
        @param expirations: a list of the expiries for the options of this underlying on this
            exchange
        @param strikes: a list of the possible strikes for options of this underlying on this
            exchange

        @return None
        """
        logger.debug6("Security Definition Option Parameter:")
        logger.debug6("ReqId: %s", reqId)
        logger.debug6("Exchange: %s", exchange)
        logger.debug6("Underlying conId: %s", underlyingConId)
        logger.debug6("Trading Class: %s", tradingClass)
        logger.debug6("Multiplier: %s", multiplier)
        logger.debug6("Expirations: %s", expirations)
        logger.debug6("Strikes: %s", strikes)

        opt_params = {
            "exchange": exchange,
            "underlying_contract_id": underlyingConId,
            "trading_class": tradingClass,
            "multiplier": multiplier,
            "expirations": expirations,
            "strikes": strikes
        }
        self.contract_option_parameter_subjects.set_option_parameter(reqId, opt_params)

    @iswrapper
    def securityDefinitionOptionParameterEnd(self, reqId: int) -> None:
        """!
        called when all callbacks to securityDefinitionOptionParameter are complete

        @param reqId: the ID used in the call to securityDefinitionOptionParameter

        @return None
        """
        logger.debug9("SecurityDefinitionOptionParameterEnd. ReqId: %s", reqId)

    @iswrapper
    def smartComponents(self, reqId: int, smartComponentMap: dict) -> None:
        """!
        bit number to exchange + exchange abbreviation dictionary

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param smartComponentMap: sa eclient.reqSmartComponents

        @return None
        """
        logger.debug("ReqId: %s   Tiers: %s", reqId, smartComponentMap)

    @iswrapper
    def softDollarTiers(self, reqId: int, tiers: list) -> None:
        """!
        Called when receives Soft Dollar Tier configuration information

        @param reqId: The request ID used in the call to EClient::reqSoftDollarTiers
        @param tiers: Stores a list of SoftDollarTier that contains all Soft Dollar Tiers
                      information

        @return None
        """
        logger.debug("ReqId: %s   Tiers: %s", reqId, tiers)

    @iswrapper
    def symbolSamples(self, reqId: int, contractDescriptions: list) -> None:
        """!
        Returns array of sample contract descriptions.

        @param reqId: FIXME: This is not documented by the TWSAPI
        @param contractDescriptions: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("Begin Function")
        logger.info("Number of descriptions: %s", len(contractDescriptions))

        for description in contractDescriptions:
            logger.info("Req Id: %s  Symbol: %s", reqId, description.contract.symbol)

        logger.debug("End Function")

    @iswrapper
    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float, size: Decimal,
                          tickAttribLast: TickAttribLast, exchange: str,
                          specialConditions: str) -> None:
        """!
        Returns "Last" or "AllLast" tick-by-tick real-time tick

        @param reqId: unique identifier of the request
        @param tickType: tick-by-tick real-time tick type: "Last" or "AllLast"
        @param time: tick-by-tick real-time tick timestamp
        @param price: tick-by-tick real-time tick last price
        @param size: tick-by-tick real-time tick last size
        @param tickAttribLast: tick-by-tick real-time last tick attribs
            - bit 0 - past limit
            - bit 1 - unreported
        @param exchange: tick-by-tick real-time tick exchange
        @specialConditions: tick-by-tick real-time tick special conditions

        @return None
        """
        tick = [tickType, time, price, size, tickAttribLast, exchange, specialConditions]
        msg = {"tick": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickByTickBidAsk(self, reqId: int, time: int, bidPrice: float, askPrice: float,
                         bidSize: Decimal, askSize: Decimal,
                         tickAttribBidAsk: TickAttribBidAsk) -> None:
        """!
        Returns "BidAsk" tick-by-tick real-time tick

        @param reqId: unique identifier of the request
        @param time: tick-by-tick real-time tick timestamp
        @param bidPrice: tick-by-tick real-time tick bid price
        @param askPrice: tick-by-tick real-time tick ask price
        @param bidSize: tick-by-tick real-time tick bid size
        @param askSize: tick-by-tick real-time tick ask size
        @param tickAttribBidAsk:  tick-by-tick real-time bid/ask tick attribs
            - bit 0 - bid past low
            - bit 1 - ask past high

        @return None
        """
        tick = [time, bidPrice, askPrice, bidSize, askSize, tickAttribBidAsk]
        msg = {"tick": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickByTickMidPoint(self, reqId: int, time: int, midPoint: float) -> None:
        """!
        Returns "MidPoint" tick-by-tick real-time tick

        @param reqId: unique identifier of the request
        @param timestamp: tick-by-tick real-time tick timestamp
        @param mid_point: tick-by-tick real-time tick mid_point

        @return None
        """
        tick = [time, midPoint]
        msg = {"tick": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickEFP(self, reqId: int, tickType: int, basisPoints: float, formattedBasisPoints: str,
                totalDividends: float, holdDays: int, futureLastTradeDate: str,
                dividendImpact: float, dividendsToLastTradeDate: float) -> None:
        """!
        Exchange for Physicals.

        IB API's descriptions. TODO: Verify
        @param reqId: The request's identifier.
        @param tickType: The type of tick being received.
        @param basisPoints: Annualized basis points, which is representative of the financing rate
            that can be directly compared to broker rates.
        @param formattedBasisPoints: Annualized basis points as a formatted string that depicts
            them in percentage form.
        @param totalDividends: FIXME: TWSAPI docs state the variable name is 'impliedFuture' however
                               the parameter in the API is totalDividends
        @param holdDays: The number of hold days until the lastTradeDate of the EFP.
        @param futureLastTradeDate: The expiration date of the single stock future.
        @param dividendImpact: The dividend impact upon the annualized basis points interest rate.
        @param dividendsToLastTradeDate: The dividends expected until the expiration of the
            single stock future.

        @return None
        """
        tick = [
            "tick_efp", tickType, basisPoints, formattedBasisPoints, totalDividends, holdDays,
            futureLastTradeDate, dividendImpact, dividendsToLastTradeDate
        ]
        msg = {"market_data": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickGeneric(self, reqId: int, tickType: int, value: float) -> None:
        """!
        Market data callback.

        @param reqId: The request's unique identifier.
        @param tickType: The type of tick being received
        @param value: FIXME: This is not documented by the TWSAPI

        @return None
        """
        tick = ["tick_generic", tickType, value]
        msg = {"market_data": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickNews(self, tickerId: int, timeStamp: int, providerCode: str, articleId: str,
                 headline: str, extraData: str) -> None:
        """!
        Ticks with news headlines

        @param tickerId: The request's unique identifier.  NOTE: While TWSAPI has named this
                         'tickerId' it's really the 'reqId'.
        @param timeStamp: FIXME: This is not documented by the TWSAPI
        @param providerCode: FIXME: This is not documented by the TWSAPI
        @param articleId: FIXME: This is not documented by the TWSAPI
        @param headline: FIXME: This is not documented by the TWSAPI
        @param extraData: FIXME: This is not documented by the TWSAPI

        @return None
        """
        tick = ["tick_news", timeStamp, providerCode, articleId, headline, extraData]
        msg = {"market_data": {tickerId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickOptionComputation(self, reqId: int, tickType: int, tickAttrib: int, impliedVol: float,
                              delta: float, optPrice: float, pvDividend: float, gamma: float,
                              vega: float, theta: float, undPrice: float) -> None:
        """!
        Receive's option specific market data. This method is called when the market in an option or
        its underlier moves. TWS’s option model volatilities, prices, and deltas, along with the
        present value of dividends expected on that options underlier are received.

        IB API's descriptions.  TODO: Verify
        @param reqId: The request's unique identifier.
        @param tickType: Specifies the type of option computation. Pass the field value into
            TickType.getField(int tickType) to retrieve the field description. For example, a field
            value of 13 will map to modelOptComp, etc. 10 = Bid 11 = Ask 12 = Last
        @param impliedVol: The implied volatility calculated by the TWS option modeler,
            using the specified tick type value.
        @param tick_attrib:
            - 0 - return based
            - 1 - price based
        @param delta: The option delta value.
        @param optPrice: The option price.
        @param pvDividend: The present value of dividends expected on the option's underlying.
        @param gamma: The option gamma value.
        @param vega: The option vega value.
        @param theta: The option theta value.
        @param undPrice: The price of the underlying.

        @return None
        """
        tick = [
            "tick_option_computation", tickType, tickAttrib, impliedVol, delta, optPrice,
            pvDividend, gamma, vega, theta, undPrice
        ]
        msg = {"market_data": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickPrice(self, reqId: int, tickType: int, price: float, attrib: TickAttrib) -> None:
        """!
        Market data tick price callback. Handles all price related ticks. Every tickPrice callback
        is followed by a tickSize. A tickPrice value of -1 or 0 followed by a tickSize of 0
        indicates there is no data for this field currently available, whereas a tickPrice with a
        positive tickSize indicates an active quote of 0 (typically for a combo contract).

        @param reqId: The request's unique identifier.
        @param tickType: The type of the price being received (i.e. ask price).
        @param price: The actual price.
        @param attribs: An TickAttrib object that contains price attributes such as:
            - TickAttrib.CanAutoExecute
            - TickAttrib.PastLimit
            - TickAttrib.PreOpen

        @return None
        """
        tick = ["tick_price", tickType, price, attrib]
        msg = {"market_data": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickReqParams(self, tickerId: int, minTick: float, bboExchange: str,
                      snapshotPermissions: int) -> None:
        """!
        Tick with BOO exchange and snapshot permissions.

        @param tickerId: FIXME: This is not documented by the TWSAPI
        @param minTick: FIXME: This is not documented by the TWSAPI
        @param bboExchange: FIXME: This is not documented by the TWSAPI
        @param snapshotPermissions: FIXME: This is not documented by the TWSAPI

        @return None
        """
        tick = ["tick_req_params", minTick, bboExchange, snapshotPermissions]
        msg = {"market_data": {tickerId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickSize(self, reqId: int, tickType: int, size: Decimal) -> None:
        """!
        Market data tick size callback.  Handles all size-related ticks.

        TODO: Verify parameters
        @param ticker_id: The request's identifier.
        @param tickType: The type of size being received (i.e. bid size)
        @param size: The actual size.  US Stocks have a multiplier of 100.

        @return None
        """
        tick = ["tick_size", tickType, size]
        msg = {"market_data": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def tickString(self, reqId: int, tickType: int, value: str) -> None:
        """!
        Market data callback. Every tickPrice is followed by a tickSize. There are also independent
        tickSize callbacks anytime the tickSize changes, and so there will be duplicate tickSize
        messages following a tickPrice.

        WTF is the point of this callback? The data provided is complete gibberish!

        @param reqId: The request's identifier
        @param tickType: The type of tick being received.
        @param value: FIXME: This is not documented by the TWSAPI

        @return None
        """
        tick = ["tick_string", tickType, value]
        msg = {"market_data": {reqId: tick}}
        logger.debug("Message: %s", msg)

    @iswrapper
    def updateAccountTime(self, timeStamp: str) -> None:
        """!
        Receives the last time on which the account was updated.

        @param timeStamp: The last update system time.

        @return None
        """
        logger.debug("Time Stamp: %s", timeStamp)

    @iswrapper
    def updateAccountValue(self, key: str, val: str, currency: str, accountName: str) -> None:
        """!
        Receives the subscribed account's information. Only one account can be subscribed at a time.
        After the initial callback to updateAccountValue, callbacks only occur for values which have
        changed. This occurs at the time of a position change, or every 3 minutes at most. This
        frequency cannot be adjusted.

        @param key: the value being updated:
            - AccountCode: The account ID number
            - AccountOrGroup: "All" to return account summary data for all accounts, or set to a
                              specific Advisor Account Group name that has already been created in
                              TWS Global Configuration
            - AccountReady: For internal use only
            - AccountType: Identifies the IB account structure
            - AccruedCash: Total accrued cash value of stock, commodities and securities
            - AccruedCash-C: Reflects the current's month accrued debit and credit interest to date,
                             updated daily in commodity segment
            - AccruedCash-S: Reflects the current's month accrued debit and credit interest to date,
                             updated daily in security segment
            - AccruedDividend: Total portfolio value of dividends accrued
            - AccruedDividend-C: Dividends accrued but not paid in commodity segment
            - AccruedDividend-S: Dividends accrued but not paid in security segment
            - AvailableFunds: This value tells what you have available for trading
            - AvailableFunds-C: Net Liquidation Value - Initial Margin
            - AvailableFunds-S: Equity with Loan Value - Initial Margin
            - Billable: Total portfolio value of treasury bills
            - Billable-C: Value of treasury bills in commodity segment
            - Billable-S: Value of treasury bills in security segment
            - BuyingPower:
               - Cash Account: Minimum(EquityWithLoanValue, PreviousDayEquityWithLoanValue) -
                              Initial Margin
               - Standard Margin Account: Minimum (Equity with Loan Value, Previous Day Equity with
                                          Loan Value) - Initial Margin *4
            - CashBalance: Cash recognized at the time of trade + futures PNL
            - CorporateBondValue: Value of non-Government bonds such as corporate bonds and
                                  municipal bonds
            - Currency: Open positions are grouped by currency
            - Cushion: Excess liquidity as a percentage of net liquidation value
            - DayTradesRemaining: Number of Open/Close trades one could do before Pattern Day
                                  Trading is detected
            - DayTradesRemainingT+1: Number of Open/Close trades one could do tomorrow before
                                     Pattern Day Trading is detected
            - DayTradesRemainingT+2: Number of Open/Close trades one could do two days from today
                                     before Pattern Day Trading is detected
            - DayTradesRemainingT+3: Number of Open/Close trades one could do three days from today
                                      before Pattern Day Trading is detected
            - DayTradesRemainingT+4: Number of Open/Close trades one could do four days from today
                                      before Pattern Day Trading is detected
            - EquityWithLoanValue: Forms the basis for determining whether a client has the
                                    necessary assets to either initiate or maintain security
                                    positions
            - EquityWithLoanValue-C:
                - Cash account:
                    Total cash value + commodities option value - futures maintenance margin
                    requirement + minimum (0, futures PNL)
                - Margin account:
                    Total cash value + commodities option value - futures maintenance margin
                    requirement
            - EquityWithLoanValue-S:
                 - Cash account: Settled Cash
                 - Margin Account: Total cash value + stock value + bond value + (non-U.S. & Canada
                                   securities options value)
            - ExcessLiquidity: This value shows your margin cushion, before liquidation
            - ExcessLiquidity-C: Equity with Loan Value - Maintenance Margin
            - ExcessLiquidity-S: Net Liquidation Value - Maintenance Margin
            - ExchangeRate: The exchange rate of the currency to your base currency
            - FullAvailableFunds: Available funds of whole portfolio with no discounts or intraday
                                   credits
            - FullAvailableFunds-C: Net Liquidation Value - Full Initial Margin
            - FullAvailableFunds-S: Equity with Loan Value - Full Initial Margin
            - FullExcessLiquidity: Excess liquidity of whole portfolio with no discounts or
                                    intraday credits
            - FullExcessLiquidity-C: Net Liquidation Value - Full Maintenance Margin
            - FullExcessLiquidity-S: Equity with Loan Value - Full Maintenance Margin
            - FullInitMarginReq: Initial Margin of whole portfolio with no discounts or intraday
                                  credits
            - FullInitMarginReq-C: Initial Margin of commodity segment's portfolio with no
                                    discounts or intraday credits
            - FullInitMarginReq-S: Initial Margin of security segment's portfolio with no discounts
                                    or intraday credits
            - FullMaintMarginReq: Maintenance Margin of whole portfolio with no discounts or
                                   intraday credits
            - FullMaintMarginReq-C: Maintenance Margin of commodity segment's portfolio with no
                                     discounts or intraday credits
            - FullMaintMarginReq-S: Maintenance Margin of security segment's portfolio with no
                                     discounts or intraday credits
            - FundValue: Value of funds value (money market funds + mutual funds)
            - FutureOptionValue: Real-time market-to-market value of futures options
            - FuturesPNL: Real-time changes in futures value since last settlement
            - FxCashBalance: Cash balance in related IB-UKL account
            - GrossPositionValue: Gross Position Value in securities segment
            - GrossPositionValue-S: Long Stock Value + Short Stock Value + Long Option Value + Short
                                    Option Value
            - IndianStockHaircut: Margin rule for IB-IN accounts
            - InitMarginReq: Initial Margin requirement of whole portfolio
            - InitMarginReq-C: Initial Margin of the commodity segment in base currency
            - InitMarginReq-S: Initial Margin of the security segment in base currency
            - IssuerOptionValue: Real-time mark-to-market value of Issued Option
            - Leverage-S: GrossPositionValue / NetLiquidation in security segment
            - LookAheadNextChange: Time when look-ahead values take effect
            - LookAheadAvailableFunds: This value reflects your available funds at the next margin
                                       change
            - LookAheadAvailableFunds-C: Net Liquidation Value - look ahead Initial Margin
            - LookAheadAvailableFunds-S: Equity with Loan Value - look ahead Initial Margin
            - LookAheadExcessLiquidity: This value reflects your excess liquidity at the next
                                        margin change
            - LookAheadExcessLiquidity-C: Net Liquidation Value - look ahead Maintenance Margin
            - LookAheadExcessLiquidity-S: Equity with Loan Value - look ahead Maintenance Margin
            - LookAheadInitMarginReq: Initial margin requirement of whole portfolio as of next
                                      period's margin change
            - LookAheadInitMarginReq-C: Initial margin requirement as of next period's margin
                                        change in the base currency of the account
            - LookAheadInitMarginReq-S: Initial margin requirement as of next period's margin
                                        change in the base currency of the account
            - LookAheadMaintMarginReq: Maintenance margin requirement of whole portfolio as of next
                                       period's margin change
            - LookAheadMaintMarginReq-C: Maintenance margin requirement as of next period's margin
                                         change in the base currency of the account
            - LookAheadMaintMarginReq-S: Maintenance margin requirement as of next period's margin
                                         change in the base currency of the account
            - MaintMarginReq: Maintenance Margin requirement of whole portfolio
            - MaintMarginReq-C: Maintenance Margin for the commodity segment
            - MaintMarginReq-S: Maintenance Margin for the security segment
            - MoneyMarketFundValue: Market value of money market funds excluding mutual funds
            - MutualFundValue: Market value of mutual funds excluding money market funds
            - NetDividend: The sum of the Dividend Payable/Receivable Values for the securities and
                            commodities segments of the account
            - NetLiquidation: The basis for determining the price of the assets in your account
            - NetLiquidation-C: Total cash value + futures PNL + commodities options value
            - NetLiquidation-S: Total cash value + stock value + securities options value + bond
                                value
            - NetLiquidationByCurrency: Net liquidation for individual currencies
            - OptionMarketValue: Real-time mark-to-market value of options
            - PASharesValue: Personal Account shares value of whole portfolio
            - PASharesValue-C: Personal Account shares value in commodity segment
            - PASharesValue-S: Personal Account shares value in security segment
            - PostExpirationExcess: Total projected "at expiration" excess liquidity
            - PostExpirationExcess-C: Provides a projected "at expiration" excess liquidity based
                                      on the soon-to expire contracts in your portfolio in
                                      commodity segment
            - PostExpirationExcess-S: Provides a projected "at expiration" excess liquidity based
                                      on the soon-to expire contracts in your portfolio in security
                                      segment
            - PostExpirationMargin: Total projected "at expiration" margin
            - PostExpirationMargin-C: Provides a projected "at expiration" margin value based on
                                      the soon-to expire contracts in your portfolio in commodity
                                      segment
            - PostExpirationMargin-S: Provides a projected "at expiration" margin value based on
                                      the soon-to expire contracts in your portfolio in security
                                      segment
            - PreviousDayEquityWithLoanValue: Marginable Equity with Loan value as of 16:00 ET the
                                              previous day in securities segment
            - PreviousDayEquityWithLoanValue-S: IMarginable Equity with Loan value as of 16:00 ET
                                                the previous day
            - RealCurrency: Open positions are grouped by currency
            - RealizedPnL: Shows your profit on closed positions, which is the difference between
                           your entry execution cost and exit execution costs:
                           execution price to open the positions + commissions to open the
                           positions - execution price to close the position + commissions to close
                           the position
            - RegTEquity: Regulation T equity for universal account
            - RegTEquity-S: Regulation T equity for security segment
            - RegTMargin: Regulation T margin for universal account
            - RegTMargin-S: Regulation T margin for security segment
            - SMA: Line of credit created when the market value of securities in a Regulation T
                    account increase in value
            - SMA-S: Regulation T Special Memorandum Account balance for security segment
            - SegmentTitle: Account segment name
            - StockMarketValue: Real-time mark-to-market value of stock
            - TBondValue: Value of treasury bonds
            - TBillValue: Value of treasury bills
            - TotalCashBalance: Total Cash Balance including Future PNL
            - TotalCashValue: Total cash value of stock, commodities and securities
            - TotalCashValue-C: CashBalance in commodity segment
            - TotalCashValue-S: CashBalance in security segment
            - TradingType-S: Account Type
            - UnrealizedPnL: The difference between the current market value of your open positions
                             and the average cost, or Value - Average Cost
            - WarrantValue: Value of warrants
            - WhatIfPMEnabled: To check projected margin requirements under Portfolio Margin model
        @param val: up-to-date value
        @param currency: the currency on which the value is expressed.
        @param accountName: the account

        @return None
        """
        logger.debug("Key: %s", key)
        logger.debug("Value: %s", val)
        logger.debug("Currency: %s", currency)
        logger.debug("Account Name: %s", accountName)

    @iswrapper
    def updateMktDepth(self, reqId: int, position: int, operation: int, side: int, price: float,
                       size: Decimal):
        """!
        Returns the order book.

        @param ticker_id: The request's identifier
        @param position: The Order book's row being updated
        @param operation: How to refresh the row:
           : 0 = insert (insert this new order into the row identified by 'position')
            - 1 = update (update the existing order in the row identified by 'position')
            - 2 = delete (delete the existing order at the row identified by 'position').
        @param side:
            - 0 for ask
            - 1 for bid
        @param price - The order's price
        @param size - The order's size

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Position: %s", position)
        logger.debug("Operation: %s", operation)
        logger.debug("Side: %s", side)
        logger.debug("Price: %s", price)
        logger.debug("Size: %s", size)

    @iswrapper
    def updateMktDepthL2(self, reqId: int, position: int, marketMaker: str, operation: int,
                         side: int, price: float, size: Decimal, isSmartDepth: bool):
        """!
        Returns the order book.

        @param reqId: The request's identifier
        @param position: The Order book's row being updated
        @param marketMaker: The Exchange holding the order if is_smart_depth is True, otherwise
            the MPID of the market maker
        @param operation: How to refresh the row:
            - 0 = insert (insert this new order into the row identified by 'position')
            - 1 = update (update the existing order in the row identified by 'position')
            - 2 = delete (delete the existing order at the row identified by 'position').
        @param side:
            - 0 for ask
            - 1 for bid
        @param price: The order's price
        @param size: The order's size
        @param isSmartDepth: flag indicating if this is smart depth response (aggregate data from
            multiple exchanges)

        @return None
        """
        logger.debug("ReqId: %s", reqId)
        logger.debug("Position: %s", position)
        logger.debug("Market Maker: %s", marketMaker)
        logger.debug("Operation: %s", operation)
        logger.debug("Side: %s", side)
        logger.debug("Price: %s", price)
        logger.debug("Size: %s", size)
        logger.debug("Is Smart Depth: %s", isSmartDepth)

    @iswrapper
    def updateNewsBulletin(self, msgId: int, msgType: int, newsMessage: str, originExch: str):
        """!
        Provides IB's bulletins

        @param msgId: The Builtin's identifier
        @param msgType:
            - 1 - Regular news bulletin
            - 2 - Exchange no longer available for trading
            - 3 - Exchange is available for trading
        @param newsMessage - The message
        @param originExch: The exchange where the message comes from.

        @return None
        """
        logger.debug("MsgId: %s  MsgType: %s  Msg: %s  OriginExch: %s", msgId, msgType, newsMessage,
                     originExch)

    @iswrapper
    def updatePortfolio(self, contract: Contract, position: float, marketPrice: float,
                        marketValue: float, averageCost: float, unrealizedPNL: float,
                        realizedPNL: float, accountName: str):
        """!
        Receives the subscribed account's portfolio. This function will receive only the portfolio
        of the subscribed account. If the portfolios of all managed accounts are needed, refer to
        EClientSocket.reqPosition After the initial callback to updatePortfolio, callbacks only
        occur for positions which have changed.

        IB API's description is incomplete.
        @param contract: the Contract for which a position is held.
        @param position: the number of positions held.
        @param marketPrice: instrument's unitary price
        @param marketValue: total market value of the instrument.
        @param averageCost: FIXME: This is not documented by the TWSAPI
        @param unrealizedPNL: FIXME: This is not documented by the TWSAPI
        @param realizedPNL: FIXME: This is not documented by the TWSAPI
        @param accountName: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("Contract: %s", contract)
        logger.debug("Position: %s", position)
        logger.debug("Market Price: %s", marketPrice)
        logger.debug("Market Value: %s", marketValue)
        logger.debug("Average Cost: %s", averageCost)
        logger.debug("Unrealized PnL: %s", unrealizedPNL)
        logger.debug("Realized PnL: %s", realizedPNL)
        logger.debug("Account Name: %s", accountName)

    @iswrapper
    def userinfo(self, reqId: int, whiteBrandingId: str):
        """!
        Return user info

        @param reqId: The request's identifier
        @param whiteBrandingId: FIXME: This is not documented by the TWSAPI

        @return None
        """
        logger.debug("ReqId: %s  White Branding Id: %s", reqId, whiteBrandingId)

    @iswrapper
    def wshEventData(self, reqId: int, dataJson: str) -> None:
        """!
        Returns calendar events from the WSH.

        @param reqId: The request's identifier
        @param dataJson: Event data in JSON format.

        @return None
        """
        logger.debug("ReqId: %s  Data: %s", reqId, dataJson)

    @iswrapper
    def wshMetaData(self, reqId: int, dataJson: str) -> None:
        """!
        Returns meta data from the WSH calendar.

        @param reqId: The request's identifier
        @param datajson: Event data in JSON format.

        @return None
        """
        logger.debug("ReqId: %s  Data: %s", reqId, dataJson)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _process_critical_code(self, req_id: int, error_code, error_string,
                               advanced_order_rejection):
        if advanced_order_rejection:
            logger.critical("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                            error_code, error_string, advanced_order_rejection)
        else:
            logger.critical("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_error_code(self, req_id: int, error_code, error_string, advanced_order_rejection):
        if advanced_order_rejection:
            logger.error("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                         error_code, error_string, advanced_order_rejection)
        else:
            logger.error("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

        if error_code == 200:
            self.contract_subjects.set_contract_details(req_id, "Error")

        # match error_code:
        #     case 200:
        #         msg = {"Error": error_string}
        #         logger.debug("Message: %s", msg)
        #     case 103 | 10147:
        #         msg = {"order_status": {req_id: {"status": "TWS_CLOSED"}}}
        #         logger.debug("Message: %s", msg)
        #     case 502:
        #         raise BrokerNotAvailable(error_string)

    def _process_warning_code(self, req_id: int, error_code, error_string,
                              advanced_order_rejection):
        if advanced_order_rejection:
            logger.warning("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                           error_code, error_string, advanced_order_rejection)
        else:
            logger.warning("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_info_code(self, req_id: int, error_code, error_string, advanced_order_rejection):
        if advanced_order_rejection:
            logger.info("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                        error_code, error_string, advanced_order_rejection)
        else:
            logger.info("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_debug_code(self, req_id: int, error_code, error_string, advanced_order_rejection):
        if advanced_order_rejection:
            logger.debug("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                         error_code, error_string, advanced_order_rejection)
        else:
            logger.debug("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)
