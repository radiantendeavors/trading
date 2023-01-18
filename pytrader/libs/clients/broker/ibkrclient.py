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
from threading import current_thread
from multiprocessing import current_process
import threading
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

        logger.debug("Broker: %s", args[0])

        ## Multiprocessing Queue
        self.process_queue = None

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

        ## Used to track available accounts
        self.accounts = []

        ## Used to store any data requested using a request ID.
        self.data = {}

        ## Used to store allowed intraday bar sizes
        self.intraday_bar_sizes = [
            "1 secs", "5 secs", "10 secs", "15 secs", "30 secs", "1 min",
            "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "20 mins",
            "30 mins", "1 hour", "2 hours", "3 hours", "4 hours", "8 hours"
        ]

        ## Used to store allowed bar sizes
        self.bar_sizes = self.intraday_bar_sizes + [
            "1 day", "1 week", "1 month"
        ]

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

    def get_next_order_id(self):
        logger.debug10("Begin Function")

        process_name = current_process().name
        thread_name = current_thread().name

        logger.debug("Thread %s in Process %s.", thread_name, process_name)

        while self.next_order_id is None:
            logger.debug("Waiting on the next order id")
            time.sleep(1)

        logger.debug("Next Order Id Received.  Next Order Id is: %s",
                     self.next_order_id)

        logger.debug10("End Function")
        return self.next_order_id

    def set_process_queue(self, process_queue):
        logger.debug10("Begin Function")
        self.process_queue = process_queue
        logger.debug10("End Function")
        return None

    def run_loop(self, process_queue):
        logger.debug10("Begin Function")
        self.process_queue = process_queue
        #self.api_thread = threading.Thread(target=self.run, deamon=True)
        logger.debug2("Start Broker Client Thread")
        #self.api_thread.start()
        logger.debug2("Broker Client Thread Started")
        logger.debug10("End Function")

    # ==============================================================================================
    #
    # The following functions are wrappers around the eClient functions.  All are lowercased, and
    # update the request id prior to calling the API function.  In addition, they provide any
    # formatting and error checking to ensure the API function receives the correct inputs.
    #
    # ==============================================================================================
    def cancel_head_timestamp(self, req_id):
        self.cancelHeadTimeStamp(req_id)

    def req_historical_data(self,
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

    def req_head_timestamp(self,
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

    def req_account_summary(self, account_types="ALL", tags=[]):
        self.req_id += 1
        tags_string = ", ".join([str(item) for item in tags])
        self.reqAccountSummary(self.req_id, account_types, tags_string)
        return self.req_id

    def req_contract_details(self, contract):
        logger.debug10("Begin Function")
        self.req_id += 1
        logger.debug("Requesting Contract Details for contract: %s", contract)
        self.reqContractDetails(self.req_id, contract)
        time.sleep(sleep_time)
        logger.debug10("End Function")
        return self.req_id

    def req_market_data(self, contract):
        logger.debug10("Begin Function")
        self.req_id += 1
        self.reqMktData(self.req_id, contract, "233", False, False, [])
        logger.debug10("End Function")
        return self.req_id

    def req_sec_def_opt_params(self, contract):
        """!
        Requests security definition option parameters for viewing a contract's option chain

        @param contract - The Contract for the request

        @return req_id - The Request's identifier
        """
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
            - AccountType — Identifies the IB account structure
            - NetLiquidation — The basis for determining the price of the assets in your account.
              Total cash value + stock value + options value + bond value
            - TotalCashValue — Total cash balance recognized at the time of trade + futures PNL
            - SettledCash — Cash recognized at the time of settlement - purchases at the time of trade - commissions - taxes - fees
            - AccruedCash — Total accrued cash value of stock, commodities and securities
            - BuyingPower — Buying power serves as a measurement of the dollar value of securities that one may purchase in a securities account without depositing additional funds
            - EquityWithLoanValue — Forms the basis for determining whether a client has the necessary assets to either initiate or maintain security positions. Cash + stocks + bonds + mutual funds
            - PreviousEquityWithLoanValue — Marginable Equity with Loan value as of 16:00 ET the previous day
            - GrossPositionValue — The sum of the absolute value of all stock and equity option positions
            - RegTEquity — Regulation T equity for universal account
            - RegTMargin — Regulation T margin for universal account
            - SMA — Special Memorandum Account: Line of credit created when the market value of securities in a Regulation T account increase in value
            - InitMarginReq — Initial Margin requirement of whole portfolio
            - MaintMarginReq — Maintenance Margin requirement of whole portfolio
            - AvailableFunds — This value tells what you have available for trading
            - ExcessLiquidity — This value shows your margin cushion, before liquidation
            - Cushion — Excess liquidity as a percentage of net liquidation value
            - FullInitMarginReq — Initial Margin of whole portfolio with no discounts or intraday credits
            - FullMaintMarginReq — Maintenance Margin of whole portfolio with no discounts or intraday credits
            - FullAvailableFunds — Available funds of whole portfolio with no discounts or intraday credits
            - FullExcessLiquidity — Excess liquidity of whole portfolio with no discounts or intraday credits
            - LookAheadNextChange — Time when look-ahead values take effect
            - LookAheadInitMarginReq — Initial Margin requirement of whole portfolio as of next period's margin change
            - LookAheadMaintMarginReq — Maintenance Margin requirement of whole portfolio as of next period's margin change
            - LookAheadAvailableFunds — This value reflects your available funds at the next margin change
            - LookAheadExcessLiquidity — This value reflects your excess liquidity at the next margin change
            - HighestSeverity — A measure of how close the account is to liquidation
            - DayTradesRemaining — The Number of Open/Close trades a user could put on before Pattern Day Trading is detected. A value of "-1" means that the user can put on unlimited day trades.
            - Leverage — GrossPositionValue / NetLiquidation
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

        IB API's Description.  TODO: Re-write

        @param req_id - The request's Identifier
        @param groups - (IB API doesn't list a description, instead it lists a description for:
        @param lt - Returns a list of integers representing visible Group ID separated by the "|"
            character, and sorted by most used group first. )

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
        Returns historical Schedule when reqHistoricalData whatToShow="SCHEDULE"

        IB API's description of the parameters is non-existant.
        @param req_id - The request identifier used to call eClient.reqHistoricalData
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
        Returns historical tick data when whatToShow="MIDPOINT"

        @param req_id - The request identifier used to call eClient.reqHistoricalTicks
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
        Returns historical tick data when whatToShow="BID ASK"

        @param req_id - The request identifier used to call eClient.reqHistoricalTicks
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
        Returns historical tick data when whatToShow="TRADES"

        @param req_id - The request identifier used to call eClient.reqHistoricalTicks
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
        TODO: Write Descriptions
        @param accounts -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("Accounts: %s", accounts)
        self.accounts = accounts.split(",")
        logger.debug("Accounts: %s", self.accounts)
        logger.debug10("End Function")
        return None

    @iswrapper
    def marketDataType(self, req_id: int, market_data_type: int):
        """!
        Returns the market data type (real-time, frozen, delayed, delayed-frozen) of ticker sent by
        EClientSocket::reqMktData when TWS switches from real-time to frozen and back and from
        delayed to delayed-frozen and back.

        IB API Descriptions - TODO: Validate
        @param req_id - The ticker identifier used to call eClient.reqMktData (I suspect this is wrong, and that
        it should be the req_id for the request sent using reqMktData)
        @param market_data_type - means that now API starts to tick with the following market data:
        1 for real-time, 2 for frozen, 3 for delayed, 4 for delayed-frozen

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def marketRule(self, market_rule_id: int, price_increments):
        """!
        Returns minimum price increment structure for a particular market rule ID market rule IDs
        for an instrument on valid exchanges can be obtained from the contractDetails object for
        that contract.

        IB API's description of the parameters is non-existant.
        @param market_rule_id
        @param price_increments

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def mktDepthExchanges(self, depth_market_data_sescriptions):
        """!
        Called when receives Depth Market Data Descriptions.

        @param depth_market_data_descriptions - Stores a list of DepthMktDataDescription

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def newsArticle(self, req_id: int, article_type: int, article_text: str):
        """!
        called when receives News Article

        @param req_id - The request identifier used to call eClient.reqNewsArticle()
        @param article_type - The type of news article:
              - 0 - Plain Text or HTML
              - 1 - Binary Data / PDF
        @param article_text - The body of the article (if article_type == 1: the binary dataa is
              encoded using the Base64 scheme)

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def newsProviders(self, news_priveders):
        """!
        Returns array of subscribed API news providers for this user.

        @param news_providers - Array of subscribed API news providers for this user.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def nextValidId(self, order_id: int):
        """!
        Receives next valid order id. Will be invoked automatically upon successfull API client
        connection, or after call to EClient::reqIds Important: the next valid order ID is only
        valid at the time it is received.

        @param order_id - The next order id.

        @return None
        """
        super().nextValidId(order_id)

        logger.debug("Setting next_valid_order: %s", order_id)
        self.next_order_id = order_id
        logger.info("The next valid Order ID: %s", self.next_order_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def openOrder(self, order_id: int, contract: Contract, order: Order,
                  order_state: OrderState):
        """!
        Called in response to the submitted order.

        @param order_id - The order's unique identifier
        @param contract - The order's Contract
        @param order - The currently active Order
        @param order_state - The order's OrderState

        @return None
        """
        logger.info("Order status: %s", order_state.status)
        logger.info("Commission charged: %s", order_state.commission)
        logger.debug10("End Function")
        return None

    @iswrapper
    def openOrderEnd(self):
        """!
        Notifies the end of the open orders' reception.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def orderBound(self, order_id, api_client_id: int, api_order_id: int):
        """!
        Response to API Bind Order Control Message

        @param order_id - permId
        @param api_client_id - API client Id.
        @param api_order_id - API order id.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def orderStatus(self, order_id: int, status: str, filled, remaining,
                    avg_fill_price, perm_id: int, parent_id: int,
                    last_fill_price, client_id: int, why_held: str,
                    mkt_cap_price):
        """!
        Gives the up-to-date information of an order every time it changes. Often there are
        duplicate orderStatus messages.

        IB API Descriptions - TODO: Validate (I suspect they aren't accurate descriptions)
        @param order_id - The order's client id
        @param status - The current status of the order. Possible values:
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
        @param filled - The number of filled positions
        @param remaining - The remnant positions
        @param avg_fill_price - The Average filling price
        @param perm_id - The order's permId used by the TWS to identify orders
        @param parent_id - Parent's id.  Used for bracket and auto trailing stop orders.
        @param last_fill_price - Price at which the last position was filled.
        @param client_id - API client that submitted the order.
        @param why_held - this field is used to identify an order held when TWS is trying to locate
            shares for a short sell. The value used to indicate this is 'locate'.
        @param mkt_cap_price - If an order has been capped, this indicates the current capped price.

        @return None
        """
        logger.debug10("Begin Function")
        logger.info("Order Id: %s", order_id)
        logger.info("Status: %s", status)
        logger.info("Number of filled positions: %s", filled)
        logger.info("Number of unfilled positions: %s", remaining)
        logger.info("Average fill price: %s", avg_fill_price)
        logger.info("TWS ID: %s", perm_id)
        logger.info("Parent Id: %s", parent_id)
        logger.info("Last Fill Price: %s", last_fill_price)
        logger.info("Client Id: %s", client_id)
        logger.info("Why Held: %s", why_held)
        logger.info("Market Cap Price: %s", mkt_cap_price)
        logger.debug10("End Function")
        return None

    @iswrapper
    def pnl(self, req_id: int, daily_pnl, unrealized_pnl, realized_pnl):
        """!
        Receives PnL updates in real time for the daily PnL and the total unrealized PnL for an
        account.

        IB API's descriptions are incomplete.  TODO - Write full descriptions

        @param req_id -
        @param daily_pnl - dailyPnL updates for the account in real time
        @param unrealized_pnl - total unRealized PnL updates for the account in real time
        @param realized_pnl -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def pnlSingle(self, req_id: int, pos, daily_pnl, unrealized_pnl,
                  realized_pnl, value):
        """!
        Receives real time updates for single position daily PnL values.

        @param req_id -
        @param pos - The current size of the position
        @param daily_pnl - daily PnL for the position
        @param unrealized_pnl -
        @param realized_pnl - total unrealized PnL for the position (since inception) updating in
            real time
        @param value - Current market value of the position.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def position(self, account: str, contract: Contract, pos, avg_cost):
        """!
        Provides the portfolio's open positions.

        IB API's description.  TODO: Verify
        @param account - The account holding the position.
        @param contract - The position's Contract
        @param pos - The number of positions held
        @param avg_cost - The average cost of the position

        @return None
        """
        logger.debug10("Begin Function")
        logger.info("Position in {}: {}".format(contract.symbol, pos))
        logger.debug10("End Function")
        return None

    @iswrapper
    def positionEnd(self, req_id: int):
        """!
        Indicates all positions have been transmitted.

        @param req_id -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def positionMulti(self, req_id: int, account: str, model_code: str,
                      contract: Contract, pos, avg_cost):
        """!
        provides the portfolio's open positions.

        @param req_id - the id of request
        @param account - the account holding the position.
        @param model_code - the model code holding the position.
        @param contract - the position's Contract
        @param pos - the number of positions held.
        @param avgCost - the average cost of the position.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def positionMultiEnd(self, req_id: int):
        """!
        Indicates all positions have been transmitted.

        @param req_id -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def realtimeBar(self, req_id: int, date, open_, high, low, close, volume,
                    wap, count: int):
        """!
        Updates the real time 5 seconds bars

        @param req_id - the request's identifier
        @param date - the bar's date and time (Epoch/Unix time)
        @param open_ - the bar's open point
        @param high - the bar's high point
        @param low - the bar's low point
        @param close - the bar's closing point
        @param volume - the bar's traded volume (only returned for TRADES data)
        @param WAP - the bar's Weighted Average Price rounded to minimum increment (only available
            for TRADES).
        @param count - the number of trades during the bar's timespan (only available for TRADES).

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def receiveFA(self, fa_data_type: int, fa_xml_data: str):
        """!
        receives the Financial Advisor's configuration available in the TWS

        @param faDataType - one of:
            1. Groups: offer traders a way to create a group of accounts and apply a single allocation method to all accounts in the group.
            2. Profiles: let you allocate shares on an account-by-account basis using a predefined calculation value.
            3. Account Aliases: let you easily identify the accounts by meaningful names rather than account numbers.
        @param faXmlData - the xml-formatted configuration

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def replaceFAEnd(self, req_id: int, text: str):
        """!
        Notifies the end of the FA replace.

        @param req_id - The request's id.
        @param text - The message text.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def rerouteMktDataReq(self, req_id: int, con_id: int, exchange: str):
        """!
        Returns con_id and exchange for CFD market data request re-route.

        @param req_id -
        @param con_id - The underlying instrument which has market data.
        @param exchange - The underlying's exchange.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def rerouteMktDepthReq(self, req_id: int, con_id: int, exchange: str):
        """!
        Returns the conId and exchange for an underlying contract when a request is made for level 2
        data for an instrument which does not have data in IB's database. For example stock CFDs and
        index CFDs.

        IB API's descriptions are non-existant
        TODO: Write descriptions (Presumably similar to rerouteMktDataReq)
        @param req_id -
        @param con_id -
        @param exchange -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def scannerData(self, req_id: int, rank: int,
                    contract_details: ContractDetails, distance: str,
                    benchmark: str, projection: str, legs_str: str):
        """!
        provides the data resulting from the market scanner request.

        @param reqid - the request's identifier.
        @param rank - the ranking within the response of this bar.
        @param contract_details - the data's ContractDetails
        @param distance - according to query.
        @param benchmark - according to query.
        @param projection - according to query.
        @param legs_str - describes the combo legs when the scanner is returning EFP

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def scannerDataEnd(self, req_id: int):
        """!
        Indicates the scanner data reception has terminated.

        @param req_id - The request's id.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def scannerParameters(self, xml: str):
        """!
        Provides the xml-formatted parameters available from TWS market scanners (not all available
        in API).

        @param xml - The xml-formatted string with the available parameters.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def securityDefinitionOptionParameter(self, req_id, exchange,
                                          underlying_con_id, tradingClass,
                                          multiplier, expirations, strikes):
        """!
        Returns the option chain for an underlying on an exchange specified in reqSecDefOptParams
        There will be multiple callbacks to securityDefinitionOptionParameter if multiple exchanges
        are specified in reqSecDefOptParams

        @param reqId - ID of the request initiating the callback
        @param underlyingConId - The conID of the underlying security
        @param tradingClass - the option trading class
        @param multiplier - the option multiplier
        @param expirations - a list of the expiries for the options of this underlying on this
            exchange
        @param strikes - a list of the possible strikes for options of this underlying on this
            exchange

        @return None
        """
        logger.debug10("Begin Function")
        print("SecurityDefinitionOptionParameter.", "ReqId:", req_id,
              "Exchange:", exchange, "Underlying conId:", underlying_con_id,
              "TradingClass:", tradingClass, "Multiplier:", multiplier,
              "Expirations:", expirations, "Strikes:", str(strikes))
        logger.debug10("End Function")
        return None

    @iswrapper
    def securityDefinitionOptionParameterEnd(self, req_id: int):
        """!
        called when all callbacks to securityDefinitionOptionParameter are complete

        @param req_id - the ID used in the call to securityDefinitionOptionParameter

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug("SecurityDefinitionOptionParameterEnd. ReqId: %s", req_id)
        logger.debug10("End Function")
        return None

    @iswrapper
    def smartComponents(self, req_id: int, the_map):
        """!
        bit number to exchange + exchange abbreviation dictionary

        IB API's descriptions aren't helpful
        @param req_id -
        @param the_map - sa eclient.reqSmartComponents

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def softDollarTiers(self, req_id: int, tiers):
        """!
        Called when receives Soft Dollar Tier configuration information

        @param reqId - The request ID used in the call to EClient::reqSoftDollarTiers
        @param tiers - Stores a list of SoftDollarTier that contains all Soft Dollar Tiers informatio

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def symbolSamples(self, req_id: int, contract_descriptions):
        """!
        Returns array of sample contract descriptions.

        IB API's descriptions are non-existant
        @param req_id -
        @param contract_descriptions -

        @return None
        """
        logger.debug10("Begin Function")
        logger.info("Number of descriptions: %s", len(contract_descriptions))

        self.data[req_id] = []
        for description in contract_descriptions:
            self.data[req_id].append(description)
            logger.info("Symbol: %s", description.contract.symbol)

        logger.debug10("End Function")

    @iswrapper
    def tickByTickAllLast(self, req_id: int, tick_type: int, time, price, size,
                          tick_attrib_last, exchange: str,
                          special_conditions: str):
        """!
        Returns "Last" or "AllLast" tick-by-tick real-time tick

        @param reqId - unique identifier of the request
        @param tickType - tick-by-tick real-time tick type: "Last" or "AllLast"
        @param time - tick-by-tick real-time tick timestamp
        @param price - tick-by-tick real-time tick last price
        @param size - tick-by-tick real-time tick last size
        @param tick_attrib_last - tick-by-tick real-time last tick attribs
            - bit 0 - past limit
            - bit 1 - unreported
        @param exchange - tick-by-tick real-time tick exchange
        @special_conditions - tick-by-tick real-time tick special conditions

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickByTickBidAsk(self, req_id: int, time, bid_price, ask_price,
                         bid_size, ask_size, tick_attrib_bid_ask):
        """!
        Returns "Last" or "AllLast" tick-by-tick real-time tick

        @param reqId - unique identifier of the request
        @param time - tick-by-tick real-time tick timestamp
        @param bid_price - tick-by-tick real-time tick bid price
        @param ask_price - tick-by-tick real-time tick ask price
        @param bid_size - tick-by-tick real-time tick bid size
        @param ask_size - tick-by-tick real-time tick ask size
        @param tick_attrib_bid_ask -  tick-by-tick real-time bid/ask tick attribs
            - bit 0 - bid past low
            - bit 1 - ask past high

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickByTickMidPoint(self, req_id: int, time, mid_point):
        """!
        Returns "Last" or "AllLast" tick-by-tick real-time tick

        @param reqId - unique identifier of the request
        @param time - tick-by-tick real-time tick timestamp
        @param mid_point - tick-by-tick real-time tick mid_point

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickEFP(self, ticker_id: int, tick_type: int, basis_points,
                formatted_basis_points: str, implied_future, hold_days: int,
                future_last_trade_date: str, dividend_impact,
                dividends_to_last_trade_date):
        """!
        Exchange for Physicals.

        IB API's descriptions. TODO: Verify
        @param ticker_id - The request's identifier.
        @param tick_type - The type of tick being received.
        @param basis_points - Annualized basis points, which is representative of the financing rate
            that can be directly compared to broker rates.
        @param formatted_basis_points - Annualized basis points as a formatted string that depicts
            them in percentage form.
        @param implied_future - The implied Futures price.
        @param hold_days - The number of hold days until the lastTradeDate of the EFP.
        @param future_last_trade_date - The expiration date of the single stock future.
        @param dividend_impact - The dividend impact upon the annualized basis points interest rate.
        @param dividends_to_last_trade_date - The dividends expected until the expiration of the
            single stock future.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickGeneric(self, ticker_id: int, field: int, value):
        """!
        Market data callback.

        IB API's description is incomplete and of questionable accuracy.
        TODO: Verify
        @param ticker_id: The request's identifier
        @param field - The type of tick being recieved
        @param value -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickNews(self, ticker_id: int, timestamp, provider_code: str,
                 article_id: str, headline: str, extra_data: str):
        """!
        Ticks with news headlines

        IB API's descriptions are non-existant.
        @param ticker_id -
        @param timestamp -
        @param provider_code -
        @param article_id -
        @param headline -
        @param extra_data -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickOptionComputation(self, ticker_id: int, field: int,
                              tick_attrib: int, implied_volatility, delta,
                              opt_price, pv_dividend, gamma, vega, theta,
                              und_price):
        """!
        Receive's option specific market data. This method is called when the market in an option or
        its underlier moves. TWS’s option model volatilities, prices, and deltas, along with the
        present value of dividends expected on that options underlier are received.

        IB API's descriptions.  TODO: Verify
        @param tickerId - The request's unique identifier.
        @param field - Specifies the type of option computation. Pass the field value into
            TickType.getField(int tickType) to retrieve the field description. For example, a field
            value of 13 will map to modelOptComp, etc. 10 = Bid 11 = Ask 12 = Last
        @param implied_volatility - The implied volatility calculated by the TWS option modeler,
            using the specified tick type value.
        @param tick_attrib:
            - 0 - return based
            - 1 - price based
        @param delta - The option delta value.
        @param opt_price - The option price.
        @param pv_dividend - The present value of dividends expected on the option's underlying.
        @param gamma - The option gamma value.
        @param vega - The option vega value.
        @param theta - The option theta value.
        @param und_price - The price of the underlying.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickPrice(self, req_id: int, field: int, price, attrib):
        """!
        Market data tick price callback. Handles all price related ticks. Every tickPrice callback
        is followed by a tickSize. A tickPrice value of -1 or 0 followed by a tickSize of 0
        indicates there is no data for this field currently available, whereas a tickPrice with a
        positive tickSize indicates an active quote of 0 (typically for a combo contract).

        @param req_id - the request's unique identifier.
        @param field - The type of the price being received (i.e. ask price).
        @param price - The actual price.
        @param attribs - An TickAttrib object that contains price attributes such as:
            - TickAttrib.CanAutoExecute
            - TickAttrib.PastLimit
            - TickAttrib.PreOpen

        @return None
        """
        logger.debug10("Begin Function")
        logger.info("Request Id: %s TickType: %s Price: %s Attrib: %s", req_id,
                    field, price, attrib)
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickReqParams(self, ticker_id: int, min_tick, bbo_exchange: str,
                      snapshot_permissions: int):
        """!
        Tick with BOO exchange and snapshot permissions.

        IB API's description is non-existant.
        TODO: Verify parameters
        @param ticker_id -
        @param min_tick -
        @param bbo_exchange -
        @param snampshot_permissions -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickSize(self, ticker_id: int, field: int, size):
        """!
        Market data tick size callback.  Handles all size-related ticks.

        TODO: Verify parameters
        @param ticker_id - The request's identifier.
        @param field - The type of size being received (i.e. bid size)
        @param size - The actual size.  US Stocks have a multiplier of 100.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def tickString(self, ticker_id: int, field: int, value: str):
        """!
        Market data callback. Every tickPrice is followed by a tickSize. There are also independent
        tickSize callbacks anytime the tickSize changes, and so there will be duplicate tickSize
        messages following a tickPrice.

        IB API's description is incomplete.
        TODO: Write descriptions
        TODO: Verify parameters
        @param ticker_id - The request's identifier
        @param field - The type of tick being received.
        @param value -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def updateAccountTime(self, timestamp: str):
        """!
        Receives the last time on which the account was updated.

        @param timestamp - The last update system time.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def updateAccountValue(self, key: str, value: str, currency: str,
                           account_name: str):
        """!
        Receives the subscribed account's information. Only one account can be subscribed at a time.
        After the initial callback to updateAccountValue, callbacks only occur for values which have
        changed. This occurs at the time of a position change, or every 3 minutes at most. This
        frequency cannot be adjusted.

        @param key - the value being updated:
            - AccountCode — The account ID number
            - AccountOrGroup — "All" to return account summary data for all accounts, or set to a
              specific Advisor Account Group name that has already been created in TWS Global
              Configuration
            - AccountReady — For internal use only
            - AccountType — Identifies the IB account structure
            - AccruedCash — Total accrued cash value of stock, commodities and securities
            - AccruedCash-C — Reflects the current's month accrued debit and credit interest to date, updated daily in commodity segment
            - AccruedCash-S — Reflects the current's month accrued debit and credit interest to date, updated daily in security segment
            - AccruedDividend — Total portfolio value of dividends accrued
            - AccruedDividend-C — Dividends accrued but not paid in commodity segment
            - AccruedDividend-S — Dividends accrued but not paid in security segment
            - AvailableFunds — This value tells what you have available for trading
            - AvailableFunds-C — Net Liquidation Value - Initial Margin
            - AvailableFunds-S — Equity with Loan Value - Initial Margin
            - Billable — Total portfolio value of treasury bills
            - Billable-C — Value of treasury bills in commodity segment
            - Billable-S — Value of treasury bills in security segment
            - BuyingPower — Cash Account: Minimum (Equity with Loan Value, Previous Day Equity with Loan Value)-Initial Margin, Standard Margin Account: Minimum (Equity with Loan Value, Previous Day Equity with Loan Value) - Initial Margin *4
            - CashBalance — Cash recognized at the time of trade + futures PNL
            - CorporateBondValue — Value of non-Government bonds such as corporate bonds and municipal bonds
            - Currency — Open positions are grouped by currency
            - Cushion — Excess liquidity as a percentage of net liquidation value
            - DayTradesRemaining — Number of Open/Close trades one could do before Pattern Day Trading is detected
            - DayTradesRemainingT+1 — Number of Open/Close trades one could do tomorrow before Pattern Day Trading is detected
            - DayTradesRemainingT+2 — Number of Open/Close trades one could do two days from today before Pattern Day Trading is detected
            - DayTradesRemainingT+3 — Number of Open/Close trades one could do three days from today before Pattern Day Trading is detected
            - DayTradesRemainingT+4 — Number of Open/Close trades one could do four days from today before Pattern Day Trading is detected
            - EquityWithLoanValue — Forms the basis for determining whether a client has the necessary assets to either initiate or maintain security positions
            - EquityWithLoanValue-C — Cash account: Total cash value + commodities option value - futures maintenance margin requirement + minimum (0, futures PNL) Margin account: Total cash value + commodities option value - futures maintenance margin requirement
            - EquityWithLoanValue-S — Cash account: Settled Cash Margin Account: Total cash value + stock value + bond value + (non-U.S. & Canada securities options value)
            - ExcessLiquidity — This value shows your margin cushion, before liquidation
            - ExcessLiquidity-C — Equity with Loan Value - Maintenance Margin
            - ExcessLiquidity-S — Net Liquidation Value - Maintenance Margin
            - ExchangeRate — The exchange rate of the currency to your base currency
            - FullAvailableFunds — Available funds of whole portfolio with no discounts or intraday credits
            - FullAvailableFunds-C — Net Liquidation Value - Full Initial Margin
            - FullAvailableFunds-S — Equity with Loan Value - Full Initial Margin
            - FullExcessLiquidity — Excess liquidity of whole portfolio with no discounts or intraday credits
            - FullExcessLiquidity-C — Net Liquidation Value - Full Maintenance Margin
            - FullExcessLiquidity-S — Equity with Loan Value - Full Maintenance Margin
            - FullInitMarginReq — Initial Margin of whole portfolio with no discounts or intraday credits
            - FullInitMarginReq-C — Initial Margin of commodity segment's portfolio with no discounts or intraday credits
            - FullInitMarginReq-S — Initial Margin of security segment's portfolio with no discounts or intraday credits
            - FullMaintMarginReq — Maintenance Margin of whole portfolio with no discounts or intraday credits
            - FullMaintMarginReq-C — Maintenance Margin of commodity segment's portfolio with no discounts or intraday credits
            - FullMaintMarginReq-S — Maintenance Margin of security segment's portfolio with no discounts or intraday credits
            - FundValue — Value of funds value (money market funds + mutual funds)
            - FutureOptionValue — Real-time market-to-market value of futures options
            - FuturesPNL — Real-time changes in futures value since last settlement
            - FxCashBalance — Cash balance in related IB-UKL account
            - GrossPositionValue — Gross Position Value in securities segment
            - GrossPositionValue-S — Long Stock Value + Short Stock Value + Long Option Value + Short Option Value
            - IndianStockHaircut — Margin rule for IB-IN accounts
            - InitMarginReq — Initial Margin requirement of whole portfolio
            - InitMarginReq-C — Initial Margin of the commodity segment in base currency
            - InitMarginReq-S — Initial Margin of the security segment in base currency
            - IssuerOptionValue — Real-time mark-to-market value of Issued Option
            - Leverage-S — GrossPositionValue / NetLiquidation in security segment
            - LookAheadNextChange — Time when look-ahead values take effect
            - LookAheadAvailableFunds — This value reflects your available funds at the next margin change
            - LookAheadAvailableFunds-C — Net Liquidation Value - look ahead Initial Margin
            - LookAheadAvailableFunds-S — Equity with Loan Value - look ahead Initial Margin
            - LookAheadExcessLiquidity — This value reflects your excess liquidity at the next margin change
            - LookAheadExcessLiquidity-C — Net Liquidation Value - look ahead Maintenance Margin
            - LookAheadExcessLiquidity-S — Equity with Loan Value - look ahead Maintenance Margin
            - LookAheadInitMarginReq — Initial margin requirement of whole portfolio as of next period's margin change
            - LookAheadInitMarginReq-C — Initial margin requirement as of next period's margin change in the base currency of the account
            - LookAheadInitMarginReq-S — Initial margin requirement as of next period's margin change in the base currency of the account
            - LookAheadMaintMarginReq — Maintenance margin requirement of whole portfolio as of next period's margin change
            - LookAheadMaintMarginReq-C — Maintenance margin requirement as of next period's margin change in the base currency of the account
            - LookAheadMaintMarginReq-S — Maintenance margin requirement as of next period's margin change in the base currency of the account
            - MaintMarginReq — Maintenance Margin requirement of whole portfolio
            - MaintMarginReq-C — Maintenance Margin for the commodity segment
            - MaintMarginReq-S — Maintenance Margin for the security segment
            - MoneyMarketFundValue — Market value of money market funds excluding mutual funds
            - MutualFundValue — Market value of mutual funds excluding money market funds
            - NetDividend — The sum of the Dividend Payable/Receivable Values for the securities and commodities segments of the account
            - NetLiquidation — The basis for determining the price of the assets in your account
            - NetLiquidation-C — Total cash value + futures PNL + commodities options value
            - NetLiquidation-S — Total cash value + stock value + securities options value + bond value
            - NetLiquidationByCurrency — Net liquidation for individual currencies
            - OptionMarketValue — Real-time mark-to-market value of options
            - PASharesValue — Personal Account shares value of whole portfolio
            - PASharesValue-C — Personal Account shares value in commodity segment
            - PASharesValue-S — Personal Account shares value in security segment
            - PostExpirationExcess — Total projected "at expiration" excess liquidity
            - PostExpirationExcess-C — Provides a projected "at expiration" excess liquidity based on the soon-to expire contracts in your portfolio in commodity segment
            - PostExpirationExcess-S — Provides a projected "at expiration" excess liquidity based on the soon-to expire contracts in your portfolio in security segment
            - PostExpirationMargin — Total projected "at expiration" margin
            - PostExpirationMargin-C — Provides a projected "at expiration" margin value based on the soon-to expire contracts in your portfolio in commodity segment
            - PostExpirationMargin-S — Provides a projected "at expiration" margin value based on the soon-to expire contracts in your portfolio in security segment
            - PreviousDayEquityWithLoanValue — Marginable Equity with Loan value as of 16:00 ET the previous day in securities segment
            - PreviousDayEquityWithLoanValue-S — IMarginable Equity with Loan value as of 16:00 ET the previous day
            - RealCurrency — Open positions are grouped by currency
            - RealizedPnL — Shows your profit on closed positions, which is the difference between your entry execution cost and exit execution costs, or (execution price + commissions to open the positions) - (execution price + commissions to close the position)
            - RegTEquity — Regulation T equity for universal account
            - RegTEquity-S — Regulation T equity for security segment
            - RegTMargin — Regulation T margin for universal account
            - RegTMargin-S — Regulation T margin for security segment
            - SMA — Line of credit created when the market value of securities in a Regulation T account increase in value
            - SMA-S — Regulation T Special Memorandum Account balance for security segment
            - SegmentTitle — Account segment name
            - StockMarketValue — Real-time mark-to-market value of stock
            - TBondValue — Value of treasury bonds
            - TBillValue — Value of treasury bills
            - TotalCashBalance — Total Cash Balance including Future PNL
            - TotalCashValue — Total cash value of stock, commodities and securities
            - TotalCashValue-C — CashBalance in commodity segment
            - TotalCashValue-S — CashBalance in security segment
            - TradingType-S — Account Type
            - UnrealizedPnL — The difference between the current market value of your open positions and the average cost, or Value - Average Cost
            - WarrantValue — Value of warrants
            - WhatIfPMEnabled — To check projected margin requirements under Portfolio Margin model
        @param value - up-to-date value
        @param currency - the currency on which the value is expressed.
        @param account_name - the account

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def updateMktDepth(self, ticker_id: int, position: int, operation: int,
                       side: int, price, size):
        """!
        Returns the order book.

        @param ticker_id - The request's identifier
        @param position - The Order book's row being updated
        @param operation - How to refresh the row:
            - 0 = insert (insert this new order into the row identified by 'position')
            - 1 = update (update the existing order in the row identified by 'position')
            - 2 = delete (delete the existing order at the row identified by 'position').
        @param side:
            - 0 for ask
            - 1 for bid
        @param price - The order's price
        @param size - The order's size

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def updateMktDepthL2(self, ticker_id: int, position: int,
                         market_maker: str, operation: int, side: int, price,
                         size, is_smart_depth):
        """!
        Returns the order book.

        @param ticker_id - The request's identifier
        @param position - The Order book's row being updated
        @param market_maker - The Exchange holding the order if is_smart_depth is True, otherwise
            the MPID of the market maker
        @param operation - How to refresh the row:
            - 0 = insert (insert this new order into the row identified by 'position')
            - 1 = update (update the existing order in the row identified by 'position')
            - 2 = delete (delete the existing order at the row identified by 'position').
        @param side:
            - 0 for ask
            - 1 for bid
        @param price - The order's price
        @param size - The order's size
        @param is_smart_depth - flag indicating if this is smart depth response (aggregate data from
            multiple exchanges)

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def updateNewsBulletin(self, msg_id: int, msg_type: int, message: str,
                           orig_exchange: str):
        """!
        Provides IB's bulletins

        @param msg_id - The Builtin's identifier
        @param msg_type:
            - 1 - Regular news bulletin
            - 2 - Exchange no longer available for trading
            - 3 - Exchange is available for trading
        @param message - The message
        @param orig_exchange - The exchange where the message comes from.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def updatePortfolio(self, contract: Contract, position, market_price,
                        market_value, average_cost, unrealized_pnl,
                        realized_pnl, account_name: str):
        """!
        Receives the subscribed account's portfolio. This function will receive only the portfolio
        of the subscribed account. If the portfolios of all managed accounts are needed, refer to
        EClientSocket.reqPosition After the initial callback to updatePortfolio, callbacks only
        occur for positions which have changed.

        IB API's description is incomplete.  TODO: Complete descriptions.
        @param contract - the Contract for which a position is held.
        @param position - the number of positions held.
        @param market_price - instrument's unitary price
        @param market_value - total market value of the instrument.
        @param average_cost -
        @param unrealized_pnl -
        @param realized_pnl -
        @param account_name -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def userinfo(self, req_id: int, white_branding_id: str):
        """!
        Return user info

        IB API's description is in complete.  TODO: Complete descriptions.
        @param req_id: The request's identifier
        @param white_branding_id: -

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def wshEventData(self, req_id: int, datajson: str):
        """!
        Returns calendar events from the WSH.

        @param req_id - The request's identifier
        @param datajson - Event data in JSON format.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

    @iswrapper
    def wshMetaData(self, req_id: int, datajson: str):
        """!
        Returns meta data from the WSH calendar.

        @param req_id - The request's identifier
        @param datajson - Event data in JSON format.

        @return None
        """
        logger.debug10("Begin Function")
        logger.debug10("End Function")
        return None

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
