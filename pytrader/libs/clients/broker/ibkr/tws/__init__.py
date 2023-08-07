"""!
@package pytrader.libs.clients.broker.ibkrclient

Provides the client for Interactive Brokers

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

@file pytrader/libs/clients/broker/ibrkrclient.py

Provides the client for Interactive Brokers
"""
# Standard Libraries
import datetime
import threading
import time

from decimal import Decimal
from queue import Queue

# 3rd Party Libraries
from ibapi.client import EClient
from ibapi.commission_report import CommissionReport
from ibapi.common import (BarData, TickAttribLast, TickAttribBidAsk, TickAttrib)
from ibapi.contract import Contract, ContractDetails, DeltaNeutralContract
from ibapi.execution import Execution
from ibapi.order import Order
from ibapi.order_state import OrderState
from ibapi.utils import (iswrapper)
from ibapi.wrapper import EWrapper

# Standard Library Overrides
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
HISTORICAL_DATA_SLEEP_TIME = 0

##
CONTRACT_DETAILS_SLEEP_TIME = 0

## Sleep time to avoid pacing violations
SMALL_BAR_SLEEP_TIME = 15

## Used to store bar sizes with pacing violations
SMALL_BAR_SIZES = ["1 secs", "5 secs", "10 secs", "15 secs", "30 secs"]

## Used to store allowed intraday bar sizes
INTRADAY_BAR_SIZES = SMALL_BAR_SIZES + [
    "1 min", "2 mins", "3 mins", "5 mins", "10 mins", "15 mins", "20 mins", "30 mins", "1 hour",
    "2 hours", "3 hours", "4 hours", "8 hours"
]

## Used to store allowed bar sizes
BAR_SIZES = INTRADAY_BAR_SIZES + ["1 day", "1 week", "1 month"]


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsApiClient(EWrapper, EClient):
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

        ## Used to track when the last historical data request was made
        self.__historical_data_req_timestamp = datetime.datetime(year=1970,
                                                                 month=1,
                                                                 day=1,
                                                                 hour=0,
                                                                 minute=0,
                                                                 second=0)

        ## Used to track when the last contract details data request was made
        self.__contract_details_data_req_timestamp = datetime.datetime(year=1970,
                                                                       month=1,
                                                                       day=1,
                                                                       hour=0,
                                                                       minute=0,
                                                                       second=0)

        self.__small_bar_data_req_timestamp = datetime.datetime(year=1970,
                                                                month=1,
                                                                day=1,
                                                                hour=0,
                                                                minute=0,
                                                                second=0)

        ## Used to track the number of active historical data requests.
        self.__active_historical_data_requests = 0

        ## Used to track the number of available market data lines
        self.__available_market_data_lines = 100

        ## Used to track available streams of level 2 data
        self.__available_deep_data_allotment = 3

        ## Used to track the latest request_id
        self.req_id = 0

        ## Used to track the next order id
        self.next_order_id = None

        ## Used to track if the next valid id is available
        self.next_valid_id_available = threading.Event()

        ## Used to track available accounts
        self.accounts = []

        ## Used to track if account list is available
        self.accounts_available = threading.Event()

        ## Used to store any data requested using a request ID.
        self.data = {}

        ## Used to track if requested data is available
        self.data_available = {}

        ##
        self.__counter = 0

        ##
        self.queue = None

        ##
        self.rtb_queue = {}

        ##
        self.tick_queue = {}

        self.mkt_data_queue = {}

    def get_account_list(self):
        """!
        Returns the list of accounts

        @return accounts: List of accounts
        """
        self.accounts_available.wait()
        return self.accounts

    def get_client_id(self):
        """!
        Returns the client id

        @return clientId: The id of the connected client.
        """
        return self.clientId

    def get_data(self, req_id: int = 0):
        """!
        Returns the data received from the request.

        @param req_id: The Request ID of the originating request.

        @return self.data[req_id]: The data from the specific request.
        @return self.data: If no req_id is provided, returns all data from all requests.
        """
        if req_id > 0:
            self.data_available[req_id].wait()
            logger.debug6("Data: %s", self.data[req_id])

            # We pop this data to prevent the amount of data from constantly growing.
            return self.data.pop(req_id)
        else:
            return self.data

    def get_next_order_id(self):
        self.next_valid_id_available.wait()
        return self.next_order_id

    def start_thread(self, queue):
        self.queue = queue
        self.api_thread = threading.Thread(target=self.run, daemon=True)
        self.api_thread.start()

    def stop_thread(self):
        self.api_thread.join()

    # ==============================================================================================
    #
    # The following functions are wrappers around the eClient functions.  All are lowercased, and
    # update the request id prior to calling the API function.  In addition, they provide any
    # formatting and error checking to ensure the API function receives the correct inputs.
    #
    # All functions in alphabetical order.
    #
    # ==============================================================================================
    def calculate_implied_volatility(self,
                                     contract: Contract,
                                     option_price: float,
                                     under_price: float,
                                     implied_option_volatility_options: list = []):
        """!
        Calculate the volatility for an option.
        Request the calculation of the implied volatility based on hypothetical option and its
        underlying prices.  The calculation will be return in EWrapper's tickOptionComputation
        callback.

        @param contract: The option's contract for which the volatility is to be calculated.
        @param option_price: Hypothetical Option Price
        @param under_price: Hypothetical option's underlying price.

        @return
        """
        self.req_id += 1

    def calculate_option_price(self,
                               contract: Contract,
                               volatility: float,
                               under_price: float,
                               option_price_options: list = []):
        """!
        Calculates an option's price based on the provided volatility and its underlying's price.
        The calculation will be return in EWrapper's tickOptionComputation callback.

        @param contract: The option's contract for which the price wants to be calculated.
        @param volatility: Hypothetical volatility.
        @param under_price: Hypothetical underlying's price.

        @return
        """
        self.req_id += 1

    def cancel_account_summary(self):
        """!
        Cancels the account's summary request. After requesting an account's summary, invoke this
        function to cancel it.

        @param req_id: The identifier of the previously performed account request.

        @return
        """
        self.req_id += 1

    def cancel_account_updates_multi(self):
        """!
        Cancels account updates request for account and/or model.

        @param req_id: The account subscription to cancel.

        @return
        """
        self.req_id += 1

    def cancel_calculate_implied_volatility(self):
        self.req_id += 1

    def cancel_head_timestamp(self):
        self.req_id += 1
        self.cancelHeadTimeStamp(self.req_id)

    def cancel_historical_data(self):
        self.req_id += 1
        self.__active_historical_data_requests -= 1
        self.cancelHistoricalData(self.req_id)

    def cancel_mkt_data(self):
        self.req_id += 1

    def cancel_mkt_depth(self, is_smart_depth: bool):
        self.req_id += 1
        self.cancelMktDepth(self.req_id, is_smart_depth)

    def cancel_news_bulletin(self):
        self.cancelNewsBulletin()

    def cancel_order(self, order_id: int, manual_order_cancel_time: str = ""):
        """!
        Cancels an active order placed by from the same API client ID.
        Note: API clients cannot cancel individual orders placed by other clients. Only
        reqGlobalCancel is available.

        @param order_id: The Order Id to cancel.
        @param manual_order_cancel_time - IBAPI does not provide a definition.  IBAPI says to set
               the value to an empty string.

        @return None
        """
        self.cancelOrder(order_id, manual_order_cancel_time)

    def is_connected(self):
        """!
        Indicates whether the API-TWS connection has been closed. NOTE: This function is not
        automatically invoked and must be by the API client.

        @return status
        """
        return self.isConnected()

    def place_order(self, contract: Contract, order: Order, order_id=None):
        logger.debug("Order: %s", order)
        if order_id is None:
            self.next_valid_id_available.wait()
            order_id = self.next_order_id

        self.placeOrder(order_id, contract, order)
        self.req_ids()
        return order_id

    def req_account_summary(self, account_types: str = "ALL", tags: list = []):
        self.req_id += 1
        tags_string = ", ".join([str(item) for item in tags])
        self.data_available[self.req_id] = threading.Event()
        self.reqAccountSummary(self.req_id, account_types, tags_string)
        return self.req_id

    def req_account_updates(self, subscribe: bool, account_code: str):
        """!
        Subscribes to a specific account's information and portfolio. Through this method, a single
        account's subscription can be started/stopped. As a result from the subscription, the
        account's information, portfolio and last update time will be received at
        EWrapper::updateAccountValue, EWrapper::updateAccountPortfolio, EWrapper::updateAccountTime
        respectively. All account values and positions will be returned initially, and then there
        will only be updates when there is a change in a position, or to an account value every 3
        minutes if it has changed. Only one account can be subscribed at a time. A second
        subscription request for another account when the previous one is still active will cause
        the first one to be canceled in favour of the second one. Consider user reqPositions if you
        want to retrieve all your accounts' portfolios directly.

        @param subscribe: Set to true to start the subscription, and false to stop it
        @param account_code: the account id (i.e. U123456) for which the information is requested.

        @return
        """
        self.reqAccountUpdates(subscribe, account_code)

    def req_contract_details(self, contract: Contract):
        """!
        Requests contract information.
        This method will provide all the contracts matching the contract provided. It can also be
        used to retrieve complete options and futures chains. This information will be returned at
        EWrapper:contractDetails. Though it is now (in API version > 9.72.12) advised to use
        reqSecDefOptParams for that purpose.


        @param contract: The contract used as sample to query the available contracts.  Typically,
            it will contain the Contract::Symbol, Contract::Currency, Contract::SecType,
            Contract::Exchange

        @return req_id: The unique request identifier.
        """
        self.req_id += 1
        self._contract_details_data_wait()
        self.data_available[self.req_id] = threading.Event()
        self.reqContractDetails(self.req_id, contract)
        self.__contract_details_data_req_timestamp = datetime.datetime.now()
        return self.req_id

    def req_global_cancel(self):
        """!
        Cancels all active orders.

        This method will cancel ALL open orders including those placed directly from TWS.

        @return
        """
        self.reqGlobalCancel()

    def req_head_timestamp(self,
                           contract: Contract,
                           what_to_show: str = "TRADES",
                           use_regular_trading_hours: bool = True,
                           format_date: bool = True):
        """!
        Requests the earliest available bar data for a contract.

        @param contract: The contract
        @param what_to_show: Type of information to show, defaults to "TRADES"
        @param use_regular_trading_hours: Defaults to 'True'
        @param format_date: Defaults to 'True'

        @return req_id: The request identifier
        """
        logger.debug("Ticker: %s", contract.symbol)

        self.req_id += 1

        # This request seems to trigger the historical data pacing restrictions.  So, we wait.
        self._historical_data_wait()

        self.data_available[self.req_id] = threading.Event()
        self.reqHeadTimeStamp(self.req_id, contract, what_to_show, use_regular_trading_hours,
                              format_date)

        # This is updated here, rather than in the _historical_data_wait function because we want
        # to actually make the request before setting a new timer.
        self.__historical_data_req_timestamp = datetime.datetime.now()

        return self.req_id

    def req_historical_data(self,
                            contract: Contract,
                            bar_size_setting: str,
                            end_date_time: str = "",
                            duration_str: str = "",
                            what_to_show: str = "TRADES",
                            use_regular_trading_hours: bool = True,
                            format_date: bool = True,
                            keep_up_to_date: bool = False,
                            chart_options: list = []):
        """!
        Requests contracts' historical data. When requesting historical data, a finishing time and
        date is required along with a duration string. For example, having:

        - endDateTime: 20130701 23:59:59 GMT
        - durationStr: 3 D

        will return three days of data counting backwards from July 1st 2013 at 23:59:59 GMT
        resulting in all the available bars of the last three days until the date and time
        specified. It is possible to specify a timezone optionally. The resulting bars will be
        returned in EWrapper::historicalData

        @param contract: The contract for which we want to retrieve the data.
        @param bar_size_setting: The size of the bar:
          - 1 sec   - (NOTE: While listed as a valid bar size, this size has NEVER worked for me)
          - 5 secs  - (NOTE: While listed as a valid bar size, this size has NEVER worked for me)
          - 15 secs - (NOTE: While listed as a valid bar size, this size has NEVER worked for me)
          - 30 secs
          - 1 min
          - 2 mins
          - 3 mins
          - 5 mins
          - 15 mins
          - 30 mins
          - 1 hr
          - 1 day

              NOTE: IB TWS-API documentation contradicts itself here.
                - https://interactivebrokers.github.io/tws-api/historical_bars.html states that
                  there are also two more bar sizes: 1 week, and 1 month
                - https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#aad87a15294377608e59aec1d87420594
                  does not list those bar sizes
        @param end_date_time: request's ending time with format yyyyMMdd HH:mm:ss {TMZ}
        @param duration_str: the amount of time for which the data needs to be retrieved:
          - "S (seconds) - " D (days)
          - "W (weeks) - " M (months)
          - " Y (years)
        @param what_to_show: The kind of information being retreived
          - TRADES
          - MIDPOINT
          - BID
          - ASK
          - BID_ASK
          - HISTORICAL_VOLATILITY
          - OPTION_IMPLIED_VOLATILITY
          - FEE_RATE
          - SCHEDULE
        @param use_regular_trading_hours:
          - set to 0 to obtain the data which was also generated outside of the Regular Trading
            Hours
          - set to 1 to obtain only the RTH data
        @param format_date:
          - set to 1 to obtain the bars' time as yyyyMMdd HH:mm:ss
          - set to 2 to obtain it like system time format in seconds
        @param keep_up_to_date: set to True to received continuous updates on most recent bar data.
        If True, and endDateTime cannot be specified.
        @param chart_options: FIXME: TWS API does not document this parameter

        @return req_id: The request identifier
        """

        # ==========================================================================================
        #
        # The maximum number of simultaneous open historical data requests from the API is 50. In
        # practice, it will probably be more efficient to have a much smaller number of requests
        # pending at a time.
        #
        # https://interactivebrokers.github.io/tws-api/historical_limitations.html
        #
        # ==========================================================================================
        if self.__active_historical_data_requests <= 50:
            self.__active_historical_data_requests += 1

            logger.debug6("Contract: %s", contract)
            logger.debug6("Bar Size: %s", bar_size_setting)
            logger.debug6("End Date Time: %s", end_date_time)
            logger.debug6("Duration: %s", duration_str)
            logger.debug6("What to show: %s", what_to_show)
            logger.debug6("Use Regular Trading Hours: %s", use_regular_trading_hours)
            logger.debug6("Format date: %s", format_date)
            logger.debug6("Keep Up to Date: %s", keep_up_to_date)
            logger.debug6("Chart Options: %s", chart_options)
            self.req_id += 1

            # if keep_up_to_date is true, end_date_time must be blank.
            # https://interactivebrokers.github.io/tws-api/historical_bars.html
            if keep_up_to_date:
                end_date_time = ""

            if bar_size_setting in SMALL_BAR_SIZES:
                self._small_bar_data_wait()
            else:
                self._historical_data_wait()

            logger.debug6("Requesting Historical Bars for: %s", contract.localSymbol)

            self.data_available[self.req_id] = threading.Event()
            self.reqHistoricalData(self.req_id, contract, end_date_time, duration_str,
                                   bar_size_setting, what_to_show, use_regular_trading_hours,
                                   format_date, keep_up_to_date, chart_options)

            # This is updated here, rather than in the _historical_data_wait function because we
            # want to actually make the request before setting a new timer.
            if bar_size_setting in SMALL_BAR_SIZES:
                self.__small_bar_data_req_timestamp = datetime.datetime.now()
            else:
                self.__historical_data_req_timestamp = datetime.datetime.now()

            self.data[self.req_id] = []
            return self.req_id
        else:
            raise Exception("Too many open historical data requests")

    def req_historical_ticks(self,
                             contract: Contract,
                             start_date_time: str,
                             end_date_time: str,
                             number_of_ticks: int,
                             what_to_show: str,
                             use_regular_trading_hours: int,
                             ignore_size: bool,
                             misc_options: list = []):
        """!
        Requests historical Time&Sales data for an instrument.

        @param contract: Contract object that is subject of query
        @param start_date_time,i.e.: "20170701 12:01:00". Uses TWS timezone specified at login.
        @param end_date_time,i.e.: "20170701 13:01:00". In TWS timezone. Exactly one of start time
               and end time has to be defined.
        @param number_of_ticks: Number of distinct data points. Max currently 1000 per request.
        @param what_to_show: (Bid_Ask, Midpoint, Trades) Type of data requested.
        @param use_regular_trading_hours: Data from regular trading hours (1), or all available
               hours (0)
        @param ignore_size: A filter only used when the source price is Bid_Ask
        @param misc_options: should be defined as null, reserved for internal use

        @return req_id: The request's identifier
        """
        self.req_id += 1

        # The maximum allowed is 1000 per request
        if number_of_ticks > 1000:
            number_of_ticks = 1000

        self.reqHistoricalTicks(self.req_id, contract, start_date_time, end_date_time,
                                number_of_ticks, what_to_show, use_regular_trading_hours,
                                ignore_size, misc_options)
        return self.req_id

    def req_ids(self):
        """!
        Requests the next valid order ID at the current moment.

        @return
        """

        # NOTE: TWS API reqIds has a required parameter 'numIds'.  The API Docs say it is
        # depreciated, however, an error message will occur if one is not set.
        self.next_valid_id_available.clear()
        self.reqIds(1)

    def req_managed_accounts(self):
        """!
        Requests the accounts to which the logged user has access to.

        NOTE: This data is already provided during the initial connection, and stored in
        self.accounts.
        """
        self.reqManagedAccounts()

    def req_market_data(
            self,
            contract: Contract,
            generic_tick_list:
        str = "221, 232, 233, 236, 258, 293, 294, 295, 318, 375, 411, 456, 595, 619",
            snapshot: bool = False,
            regulatory_snapshot: bool = False,
            market_data_options: list = []):
        """!
        Requests real time market data. Returns market data for an instrument either in real time or
        10-15 minutes delayed (depending on the market data type specified)

        IB API's description of the parameters is incomplete.
        @param contract: The contract for which the data is being requested.
        @param generic_tick_list: Comma Separated ids of the available generic ticks:
            - 100 Option Volume (currently for stocks)
            - 101 Option Open Interest (currently for stocks)
            - 104 Historical Volatility (currently for stocks)
            - 105 Average Option Volume (currently for stocks)
            - 106 Option Implied Volatility (currently for stocks)
            - 162 Index Future Premium (TODO: Futures Only?)
            - 165 Miscellaneous Stats
            - 221 Mark Price (used in TWS P&L computations)
            - 225 Auction values (volume, price and imbalance)
            - 232 TBD
            - 233 RTVolume - contains the last trade price, last trade size, last trade time, total
              volume, VWAP, and single trade flag.
            - 236 Shortable
            - 256 Inventory
            - 258 Fundamental Ratios
            - 292 Wide_news
            - 293 TradeCount
            - 294 TradeRate
            - 295 VolumeRate
            - 318 LastRTHTrade
            - 375 RTTrdVolume
            - 411 Realtime Historical Volatility
            - 456 IBDividends
            - 460 Bond Factor Multiplier
            - 576 EtfNavBidAsk(navbidask)
            - 577 EtfNavLast(navlast)
            - 578 EtfNavClose(navclose)
            - 586 IPOHLMPRC
            - 587 Pl Price Delayed
            - 588 Futures Open Interest
            - 595 Short-Term Volume X Mins
            - 614 EtfNavMisc(high/low)
            - 619 Creditman Slow Mark Price
            - 623 EtfFrozenNavLast(fznavlast)
        @param snapshot: for users with corresponding real time market data subscriptions:
            - True will return a one-time snapshot
            - False will provide streaming data
        @param regulatory_snapshot: snapshot for US stocks requests NBBO snapshots for users which
            have "US Securities Snapshot Bundle" subscription but not corresponding Network A, B, or
            C subscription necessary for streaming * market data. One-time snapshot of current
            market price that will incur a fee of 1 cent to the account per snapshot
        @param market_data_options -

        @return req_id: The rquest's identifier
        """
        self.req_id += 1

        if contract.secType == "STK":
            """
            Legal ones for (STK) are:
              - 100(Option Volume)
              - 101(Option Open Interest)
              - 105(Average Opt Volume)
              - 106(impvolat)
              - 165(Misc. Stats)
              - 221/220(Creditman Mark Price)
              - 225(Auction)
              - 232/221(Pl Price)
              - 233(RTVolume)
              - 236(inventory)
              - 258/47(Fundamentals)
              - 292(Wide_news)
              - 293(TradeCount)
              - 294(TradeRate)
              - 295(VolumeRate)
              - 318(LastRTHTrade)
              - 375(RTTrdVolume)
              - 411(rthistvol)
              - 456/59(IBDividends)
              - 460(Bond Factor Multiplier)
              - 576(EtfNavBidAsk(navbidask))
              - 577(EtfNavLast(navlast))
              - 578(EtfNavClose(navclose))
              - 586(IPOHLMPRC)
              - 587(Pl Price Delayed)
              - 588(Futures Open Interest)
              - 595(Short-Term Volume X Mins)
              - 614(EtfNavMisc(high/low))
              - 619(Creditman Slow Mark Price)
              - 623(EtfFrozenNavLast(fznavlast)
            """
            if generic_tick_list == "":
                generic_tick_list = "100, 101, 104, 105, 106, 165, 292"
            else:
                generic_tick_list += ", 100, 101, 104, 105, 106, 165, 292"

        self.reqMktData(self.req_id, contract, generic_tick_list, snapshot, regulatory_snapshot,
                        market_data_options)

        return self.req_id

    def req_real_time_bars(self,
                           contract: Contract,
                           bar_size_setting: int = 5,
                           what_to_show: str = "TRADES",
                           use_regular_trading_hours: bool = True,
                           real_time_bar_options: list = []):
        """!
        Requests real time bars
        Currently, only 5 seconds bars are provided. This request is subject to the same pacing as
        any historical data request: no more than 60 API queries in more than 600 seconds.
        Real time bars subscriptions are also included in the calculation of the number of Level 1
        market data subscriptions allowed in an account.

        IB API's parameter description is incomplete.
        @param contract: The Contract Being Requested
        @param bar_size_setting: Currently being ignored
               (https://interactivebrokers.github.io/tws-api/classIBApi_1_1EClient.html#a644a8d918f3108a3817e8672b9782e67)
        @param what_to_show: The nature of the data being retreived:
            - TRADES
            - MIDPOINT
            - BID
            - ASK
        @param use_regular_trading_hours:
            - 0 to obtain the data which was also generated ourside of the Regular Trading Hours
            - 1 to obtain only the RTH data
        @param real_time_bar_options -

        @return req_id: The request's identifier
        """
        logger.debug6("Contract: %s", contract)
        logger.debug6("Bar Size: %s", bar_size_setting)
        logger.debug6("What to show: %s", what_to_show)
        logger.debug6("Use Regular Trading Hours: %s", use_regular_trading_hours)
        logger.debug6("Real time bar options: %s", real_time_bar_options)

        self.req_id += 1

        self._small_bar_data_wait()

        self.reqRealTimeBars(self.req_id, contract, bar_size_setting, what_to_show,
                             use_regular_trading_hours, real_time_bar_options)

        # This is updated here, rather than in the _historical_data_wait function because we
        # want to actually make the request before setting a new timer.
        self.__small_bar_data_req_timestamp = datetime.datetime.now()
        return self.req_id

    def req_sec_def_opt_params(self, contract: Contract):
        """!
        Requests security definition option parameters for viewing a contract's option chain

        @param contract: The Contract for the request

        @return req_id: The Request's identifier
        """
        self.req_id += 1
        self.data_available[self.req_id] = threading.Event()

        # The 3rd parameter, futFopExchange, is set to "" which the API uses to select
        # ALL exchanges.
        self.reqSecDefOptParams(self.req_id, contract.symbol, "", contract.secType, contract.conId)
        return self.req_id

    def req_tick_by_tick_data(self,
                              tick_queue: Queue,
                              contract: Contract,
                              tick_type: str = "Last",
                              number_of_ticks: int = 0,
                              ignore_size: bool = False):
        """!
        Requests tick-by-tick data.

        @param contract: the contract for which tick-by-tick data is requested.
        @param tick_type: tick-by-tick data type: "Last", "AllLast", "BidAsk" or "MidPoint".
        @param numberOfTicks: number of ticks.
        @param ignoreSize: ignore size flag.

        @return req_id: The request's identifier
        """
        allowed_tick_types = ["Last", "AllLast", "BidAsk", "MidPoint"]

        if tick_type in allowed_tick_types:
            self.req_id += 1
            self._historical_data_wait()

            self.tick_queue[self.req_id] = tick_queue

            self.reqTickByTickData(self.req_id, contract, tick_type, number_of_ticks, ignore_size)
            self.__historical_data_req_timestamp = datetime.datetime.now()
            logger.debug("End Function")
            return self.req_id
        else:
            raise Exception("Invalid Tick Type")

    def set_server_loglevel(self, log_level: int = 2):
        """!
        Changes the TWS/GW log level. The default is 2 = ERROR
        5 = DETAIL is required for capturing all API messages and troubleshooting API programs

        @param log level: Valid values are:
            - 1 = SYSTEM
            - 2 = ERROR
            - 3 = WARNING
            - 4 = INFORMATION
            - 5 = DETAIL

        @return
        """
        self.setServerLogLevel(log_level)

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

        @param account: The Accounts Id

        @return
        """
        logger.debug("Account Download Complete for Account: %s", account)

    @iswrapper
    def accountSummary(self, req_id: int, account: str, tag: str, value: str, currency: str):
        """!
        Receives the account information. This method will receive the account information just as
        it appears in the TWS' Account Summary Window.

        @param req_id: The Requests Unique ID.
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

        @return
        """
        self.data[req_id] = {"account": account, "tag": tag, "value": value, "currency": currency}
        self.data_available[req_id].set()

        logger.debug("Account Summary. ReqId: %s\nAccount: %s, Tag: %s, Value: %s, Currency: %s",
                     req_id, account, tag, value, currency)

    @iswrapper
    def accountSummaryEnd(self, req_id: int):
        """!
        Notifies when all the accounts' information has been received.

        @param req_id: The Request's identifier

        @return
        """
        logger.debug("Account Summary Completed.  ReqId: %s", req_id)

    @iswrapper
    def accountUpdateMulti(self, req_id: int, account: str, model_code: str, key: str, value: str,
                           currency: str):
        """!
        Provides the account updates.

        @param req_id: The unique request identifier
        @param account: The account with updates
        @param model_code: The model code with updates
        @param key: The name of the parameter
        @param value: The value of the parameter
        @param currency -The currency of the parameter

        @return
        """
        logger.debug("Account Update for %s:", account)
        logger.debug("Model Code: %s", model_code)
        logger.debug("Key: %s", key)
        logger.debug("Value: %s", value)
        logger.debug("Currency: %s", currency)

    @iswrapper
    def accountUpdateMultiEnd(self, req_id: int):
        """!
        Indicates all the account updates have been transmitted.

        @param req_id: The Request's identifier

        @return
        """
        logger.debug("Account Update Completed.  ReqId: %s", req_id)

    @iswrapper
    def bondContractDetails(self, req_id: int, details: ContractDetails):
        """!
        Delivers the Bond contract data after this has been requested via reqContractDetails.

        @param req_id: The Unique Reuest Identifier
        @param details: The details for the contract

        @return
        """
        logger.debug("Bond Contract Details: %s\n%s", req_id, details)

    @iswrapper
    def commissionReport(self, commission_report: CommissionReport):
        """!
        provides the CommissionReport of an Execution

        @param commission_report: The Report

        @return
        """
        logger.debug("Commission Report: %s", commission_report)

    @iswrapper
    def completedOrder(self, contract: Contract, order: Order, order_state: OrderState):
        """!
        Feeds in completed orders.

        @param contract: The Order's Contract
        @param order: The Completed Order
        @param order_state: The Order's State

        @return
        """
        logger.debug("Completed Order for %s\n\%s\n%s", contract, order, order_state)

    @iswrapper
    def completedOrdersEnd(self):
        """!
        Notifies the end of the completed order's reception.

        @return
        """
        logger.debug("All data received for completed order")

    @iswrapper
    def connectionClosed(self):
        """!
        Callback to indicate the API connection has closed. Following a API <-> TWS broken socket
        connection, this function is not called automatically but must be triggered by API client
        code.

        @return
        """
        # send_item = "ConnectionClosed"

        # req_id_list = list(self.bar_queue.keys())
        # logger.debug("Sending Queue Item: %s", send_item)
        # for item in req_id_list:
        #     self.bar_queue[item].put(send_item)

        logger.debug("End Function")

    @iswrapper
    def contractDetails(self, req_id: int, details: ContractDetails):
        """!
        Receives the full contract's definitions This method will return all contracts matching the
        requested via EClientSocket::reqContractDetails. For example, one can obtain the whole
        option chain with it.

        @param req_id: The Unique Reuest Identifier
        @param details: The details for the contract

        @return
        """
        logger.debug6("Contract Info Received")
        logger.debug6("Contract ID: %s", details.contract.conId)
        logger.debug6("Symbol: %s", details.contract.symbol)
        logger.debug6("Security Type: %s", details.contract.secType)
        logger.debug6("Exchange: %s", details.contract.exchange)
        logger.debug6("Currency: %s", details.contract.currency)
        logger.debug6("Local Symbol: %s", details.contract.localSymbol)
        logger.debug6("Primary Exchange: %s", details.contract.primaryExchange)
        logger.debug6("Trading Class: %s", details.contract.tradingClass)
        logger.debug6("Security ID Type: %s", details.contract.secIdType)
        logger.debug6("Security ID: %s", details.contract.secId)
        #logger.debug("Description: %s", details.contract.description)

        logger.debug6("Contract Detail Info")
        logger.debug6("Market name: %s", details.marketName)
        logger.debug6("Min Tick: %s", details.minTick)
        logger.debug6("OrderTypes: %s", details.orderTypes)
        logger.debug6("Valid Exchanges: %s", details.validExchanges)
        logger.debug6("Underlying Contract ID: %s", details.underConId)
        logger.debug6("Long name: %s", details.longName)
        logger.debug6("Industry: %s", details.industry)
        logger.debug6("Category: %s", details.category)
        logger.debug6("Subcategory: %s", details.subcategory)
        logger.debug6("Time Zone: %s", details.timeZoneId)
        logger.debug6("Trading Hours: %s", details.tradingHours)
        logger.debug6("Liquid Hours: %s", details.liquidHours)
        logger.debug6("SecIdList: %s", details.secIdList)
        logger.debug6("Underlying Symbol: %s", details.underSymbol)
        logger.debug6("Stock Type: %s", details.stockType)
        logger.debug6("Next Option Date: %s", details.nextOptionDate)
        logger.debug6("Details: %s", details)

        self.data[req_id] = details
        self.data_available[req_id].set()

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

    @iswrapper
    def contractDetailsEnd(self, req_id: int):
        """!
        After all contracts matching the request were returned, this method will mark the end of
        their reception.

        @param req_id: The requests identifier.

        @return
        """
        logger.debug6("Contract Details Received for request id: %s", req_id)

    @iswrapper
    def currentTime(self, current_time: int):
        """!
        TWS's current time. TWS is synchronized with the server (not local computer) using NTP and
        this function will receive the current time in TWS.

        @param current_time: The current time in Unix timestamp format.
        @return
        """
        time_now = datetime.datetime.fromtimestamp(current_time)
        logger.debug6("Current time: %s", time_now)

    @iswrapper
    def deltaNeutralValidation(self, req_id: int, delta_neutral_contract: DeltaNeutralContract):
        """!
        Upon accepting a Delta-Neutral DN RFQ(request for quote), the server sends a
        deltaNeutralValidation() message with the DeltaNeutralContract structure. If the delta and
        price fields are empty in the original request, the confirmation will contain the current
        values from the server. These values are locked when RFQ is processed and remain locked
        until the RFQ is cancelled.

        @param req_id: The request's Identifier
        @param delta_neutural_contract: Delta-Neutral Contract

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def displayGroupList(self, req_id: int, groups: str):
        """!
        A one-time response to querying the display groups.

        IB API's Description.  TODO: Re-write

        @param req_id: The request's Identifier
        @param groups: (IB API doesn't list a description, instead it lists a description for:
        @param lt: Returns a list of integers representing visible Group ID separated by the "|"
            character, and sorted by most used group first. )

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def displayGroupUpdated(self, req_id: int, contract_info: str):
        """!
        Call triggered once after receiving the subscription request, and will be sent again if the
        selected contract in the subscribed * display group has changed.

        @param req_id: The request's identifier
        @param contract_info: TBD.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def error(self, req_id: int, code: int, msg: str, advanced_order_rejection: str = ""):
        """!
        Errors sent by the TWS are received here.

        Error Code Descriptions can be found at:
        https://interactivebrokers.github.io/tws-api/message_codes.html

        @param req_id: The request identifier which generated the error. Note: -1 will indicate a
            notification and not true error condition.
        @param code: The Code identifying the error
        @param msg: The error's description
        @param advanced_order_rejection: Advanced Order Reject Description in JSON format.

        @return
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

        if code in critical_codes:
            if advanced_order_rejection:
                logger.critical("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                                code, msg, advanced_order_rejection)
            else:
                logger.critical("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        elif code in error_codes:
            if advanced_order_rejection:
                logger.error("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id, code,
                             msg, advanced_order_rejection)
            else:
                logger.error("ReqID# %s, Code: %s (%s)", req_id, code, msg)

            if code == 200:
                self.data[req_id] = {"Error": msg}
                self.data_available[req_id].set()

            elif code == 10147:
                msg = {"order_status": {req_id: {"status": "TWS_CLOSED"}}}
                self.queue.put(msg)

        elif code in warning_codes:
            if advanced_order_rejection:
                logger.warning("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                               code, msg, advanced_order_rejection)
            else:
                logger.warning("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        elif code in info_codes:
            if advanced_order_rejection:
                logger.info("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id, code,
                            msg, advanced_order_rejection)
            else:
                logger.info("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        elif code in debug_codes:
            if advanced_order_rejection:
                logger.debug("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id, code,
                             msg, advanced_order_rejection)
            else:
                logger.debug("ReqID# %s, Code: %s (%s)", req_id, code, msg)
        else:
            if advanced_order_rejection:
                logger.error("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id, code,
                             msg, advanced_order_rejection)
            else:
                logger.error("ReqID# %s, Code: %s (%s)", req_id, code, msg)

    @iswrapper
    def execDetails(self, req_id: int, contract: Contract, execution: Execution):
        """!
        Provides the executions which happened in the last 24 hours.

        @param req_id: The request's identifier
        @param contract: The contract of the order
        @param execution: The execution details

        @return
        """
        msg = {"order_execution": {contract.localSymbol: execution}}
        logger.debug(msg)

    @iswrapper
    def execDetailsEnd(self, req_id: int):
        """!
        indicates the end of the Execution reception.

        @param req_id: The request's identifier

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def familyCodes(self, family_codes: list):
        """!
        Returns an array of family codes

        @param family_codes: List of Family Codes

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def fundamentalData(self, req_id: int, data: str):
        """!
        Returns fundamental data

        @param req_id: The request's identifier
        @param data: xml-formatted fundamental data

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def headTimestamp(self, req_id: int, head_time_stamp: str):
        """!
        Returns beginning of data for contract for specified data type.

        @param req_id: The request's identifier
        @param head_time_stamp: String Identifying the earliest data date.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("ReqID: %s, IPO Date: %s", req_id, head_time_stamp)
        self.data[req_id] = head_time_stamp
        self.data_available[req_id].set()

        logger.debug("End Function")

    @iswrapper
    def histogramData(self, req_id: int, data: list):
        """!
        Returns data histogram

        @param req_id: The request's identifier
        @param data: Tuple of histogram data, number of trades at specified price level.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def historicalData(self, req_id: int, bar: BarData):
        """!
        Returns the requested historical data bars.

        @param req_id: The request's identifier
        @param bar: The OHLC historical data Bar.  The time zone of the bar is the time zone chosen
        on the TWS login screen. Smallest bar size is 1 second.

        @return
        """
        logger.debug6("ReqID: %s", req_id)
        logger.debug6("Bar: %s", bar)

        self.data[req_id].append(bar)

    @iswrapper
    def historicalDataEnd(self, req_id: int, start: str, end: str):
        logger.debug6("Data Complete for ReqID: %s from: %s to: %s", req_id, start, end)
        self.data_available[req_id].set()
        self.__active_historical_data_requests -= 1

    @iswrapper
    def historicalDataUpdate(self, req_id: int, bar: BarData):
        """!
        Receives bars in real time if keepUpToDate is set as True in reqHistoricalData. Similar to
        realTimeBars function, except returned data is a composite of historical data and real time
        data that is equivalent to TWS chart functionality to keep charts up to date. Returned bars
        are successfully updated using real time data.

        @param req_id: The request's identifier
        @param bar: The OHLC historical data Bar. The time zone of the bar is the time zone chosen
            on the TWS login screen. Smallest bar size is 1 second.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("ReqID: %s", req_id)
        logger.debug("Bar: %s", bar)
        self.__counter += 1
        date_time = datetime.datetime.now()

        send_item = [req_id, self.__counter, date_time, bar]
        logger.debug("Sending Queue Item: %s", send_item)
        self.queue.put(send_item)

        logger.debug("End Function")

    @iswrapper
    def historicalNews(self, req_id: int, time: str, provider_code: str, article_id: str,
                       headline: str):
        """!
        Ruturns news headlines

        IB API's description of the parameters is non-existant.
        @param req_id: The request's identifier
        @param time -
        @param provider_code -
        @param article_id -
        @param headline -

        @return
        """
        logger.debug("Begin Function")
        logger.debug("ReqId: %s", req_id)
        logger.debug("End Function")

    @iswrapper
    def historicalNewsEnd(self, req_id: int, has_more: bool):
        """!
        Returns news headlines end marker

        @param req_id: The request's identifier
        @param has_more: True if there are more results available, false otherwise.

        @return
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug("End Function")

    @iswrapper
    def historicalSchedule(self, req_id: int, start_date_time: str, end_date_time: str,
                           timezone: str, sessions: list):
        """!
        Returns historical Schedule when reqHistoricalData whatToShow="SCHEDULE"

        IB API's description of the parameters is non-existant.
        @param req_id: The request identifier used to call eClient.reqHistoricalData
        @param start_date_time -
        @param end_date_time -
        @param time_zone -
        @param sessions -

        @return
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug("End Function")

    @iswrapper
    def historicalTicks(self, req_id: int, ticks: list, done: bool):
        """!
        Returns historical tick data when whatToShow="MIDPOINT"

        @param req_id: The request identifier used to call eClient.reqHistoricalTicks
        @param ticks: list of HistoricalTick data
        @param done: Flag to indicate if all historical tick data has been received.

        @return
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug("End Function")

    @iswrapper
    def historicalTicksBidAsk(self, req_id: int, ticks: list, done: bool):
        """!
        Returns historical tick data when whatToShow="BID ASK"

        @param req_id: The request identifier used to call eClient.reqHistoricalTicks
        @param ticks: list of HistoricalTick data
        @param done: Flag to indicate if all historical tick data has been received.

        @return
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug("End Function")

    @iswrapper
    def historicalTicksLast(self, req_id: int, ticks: list, done: bool):
        """!
        Returns historical tick data when whatToShow="TRADES"

        @param req_id: The request identifier used to call eClient.reqHistoricalTicks
        @param ticks: list of HistoricalTick data
        @param done: Flag to indicate if all historical tick data has been received.

        @return
        """
        logger.debug("ReqId: %s", req_id)
        logger.debug("End Function")

    @iswrapper
    def managedAccounts(self, accounts: str):
        """!
        Receives a comma-separated string with the managed account ids. Occurs automatically on
        initial API client connection.

        IB API's description of the parameters is non-existant.
        TODO: Write Descriptions
        @param accounts -

        @return
        """
        logger.debug6("Accounts: %s", accounts)
        self.accounts = accounts.split(",")
        self.accounts_available.set()
        logger.debug("Accounts: %s", self.accounts)

    @iswrapper
    def marketDataType(self, req_id: int, market_data_type: int):
        """!
        Returns the market data type (real-time, frozen, delayed, delayed-frozen) of ticker sent by
        EClientSocket::reqMktData when TWS switches from real-time to frozen and back and from
        delayed to delayed-frozen and back.

        IB API Descriptions: TODO: Validate
        @param req_id: The ticker identifier used to call eClient.reqMktData (I suspect this is
                       wrong, and that it should be the req_id for the request sent using
                       reqMktData)
        @param market_data_type: means that now API starts to tick with the following market data:
                     1 for real-time
                     2 for frozen
                     3 for delayed
                     4 for delayed-frozen

        @return
        """
        data_type_string = {1: "Real Time", 2: "Frozen", 3: "Delayed", 4: "Delayed and Frozen"}
        logger.debug6("Market Data type for req id %s currently set to '%s'", req_id,
                      data_type_string[market_data_type])

    @iswrapper
    def marketRule(self, market_rule_id: int, price_increments: list):
        """!
        Returns minimum price increment structure for a particular market rule ID market rule IDs
        for an instrument on valid exchanges can be obtained from the contractDetails object for
        that contract.

        IB API's description of the parameters is non-existant.
        @param market_rule_id
        @param price_increments

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def mktDepthExchanges(self, depth_market_data_sescriptions: list):
        """!
        Called when receives Depth Market Data Descriptions.

        @param depth_market_data_descriptions: Stores a list of DepthMktDataDescription

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def newsArticle(self, req_id: int, article_type: int, article_text: str):
        """!
        called when receives News Article

        @param req_id: The request identifier used to call eClient.reqNewsArticle()
        @param article_type: The type of news article:
              - 0 - Plain Text or HTML
              - 1 - Binary Data / PDF
        @param article_text: The body of the article (if article_type == 1: the binary data is
              encoded using the Base64 scheme)

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def newsProviders(self, news_priveders: list):
        """!
        Returns array of subscribed API news providers for this user.

        @param news_providers: Array of subscribed API news providers for this user.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def nextValidId(self, order_id: int):
        """!
        Receives next valid order id. Will be invoked automatically upon successfull API client
        connection, or after call to EClient::reqIds Important: the next valid order ID is only
        valid at the time it is received.

        @param order_id: The next order id.

        @return
        """
        # Do I need this here?
        super().nextValidId(order_id)

        self.next_order_id = order_id

        msg = {"next_order_id": order_id}
        self.queue.put(msg)

        self.next_valid_id_available.set()

    @iswrapper
    def openOrder(self, order_id: int, contract: Contract, order: Order, order_state: OrderState):
        """!
        Called in response to the submitted order.

        @param order_id: The order's unique identifier
        @param contract: The order's Contract
        @param order: The currently active Order
        @param order_state: The order's OrderState

        @return
        """
        logger.debug9("Order Id: %s", order_id)
        logger.debug9("Contract: %s", contract.localSymbol)
        logger.debug9("Order: %s", order)
        logger.debug9("Order state: %s", order_state)

    @iswrapper
    def openOrderEnd(self):
        """!
        Notifies the end of the open orders' reception.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def orderBound(self, order_id: int, api_client_id: int, api_order_id: int):
        """!
        Response to API Bind Order Control Message

        @param order_id: permId
        @param api_client_id: API client Id.
        @param api_order_id: API order id.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def orderStatus(self, order_id: int, status: str, filled: Decimal, remaining: Decimal,
                    avg_fill_price: float, perm_id: int, parent_id: int, last_fill_price: float,
                    client_id: int, why_held: str, mkt_cap_price: float):
        """!
        Gives the up-to-date information of an order every time it changes. Often there are
        duplicate orderStatus messages.

        IB API Descriptions - TODO: Validate (I suspect they aren't accurate descriptions)
        @param order_id: The order's client id
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
        @param avg_fill_price: The Average filling price
        @param perm_id: The order's permId used by the TWS to identify orders
        @param parent_id: Parent's id.  Used for bracket and auto trailing stop orders.
        @param last_fill_price: Price at which the last position was filled.
        @param client_id: API client that submitted the order.
        @param why_held: this field is used to identify an order held when TWS is trying to locate
            shares for a short sell. The value used to indicate this is 'locate'.
        @param mkt_cap_price: If an order has been capped, this indicates the current capped price.

        @return
        """
        logger.debug9("Order Id: %s", order_id)
        logger.debug9("Status: %s", status)
        logger.debug9("Number of filled positions: %s", filled)
        logger.debug9("Number of unfilled positions: %s", remaining)
        logger.debug9("Average fill price: %s", avg_fill_price)
        logger.debug9("TWS ID: %s", perm_id)
        logger.debug9("Parent Id: %s", parent_id)
        logger.debug9("Last Fill Price: %s", last_fill_price)
        logger.debug9("Client Id: %s", client_id)
        logger.debug9("Why Held: %s", why_held)
        logger.debug9("Market Cap Price: %s", mkt_cap_price)

        msg = {
            "order_status": {
                order_id: {
                    "status": status,
                    "filled": filled,
                    "remaining": remaining,
                    "average_fill_price": avg_fill_price,
                    "perm_id": perm_id,
                    "parent_id": parent_id,
                    "last_fill_price": last_fill_price,
                    "client_id": client_id,
                    "why_held": why_held,
                    "market_cap_price": mkt_cap_price
                }
            }
        }
        self.queue.put(msg)

    @iswrapper
    def pnl(self, req_id: int, daily_pnl: float, unrealized_pnl: float, realized_pnl: float):
        """!
        Receives PnL updates in real time for the daily PnL and the total unrealized PnL for an
        account.

        IB API's descriptions are incomplete.  TODO: Write full descriptions

        @param req_id -
        @param daily_pnl: dailyPnL updates for the account in real time
        @param unrealized_pnl: total unRealized PnL updates for the account in real time
        @param realized_pnl -

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def pnlSingle(self, req_id: int, pos: Decimal, daily_pnl: float, unrealized_pnl: float,
                  realized_pnl: float, value: float):
        """!
        Receives real time updates for single position daily PnL values.

        @param req_id -
        @param pos: The current size of the position
        @param daily_pnl: daily PnL for the position
        @param unrealized_pnl -
        @param realized_pnl: total unrealized PnL for the position (since inception) updating in
            real time
        @param value: Current market value of the position.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def position(self, account: str, contract: Contract, pos: Decimal, avg_cost: float):
        """!
        Provides the portfolio's open positions.

        IB API's description.  TODO: Verify
        @param account: The account holding the position.
        @param contract: The position's Contract
        @param pos: The number of positions held
        @param avg_cost: The average cost of the position

        @return
        """
        logger.debug("Begin Function")
        logger.info("Position in {}: {}".format(contract.symbol, pos))
        logger.debug("End Function")

    @iswrapper
    def positionEnd(self, req_id: int):
        """!
        Indicates all positions have been transmitted.

        @param req_id -

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def positionMulti(self, req_id: int, account: str, model_code: str, contract: Contract,
                      pos: Decimal, avg_cost: float):
        """!
        provides the portfolio's open positions.

        @param req_id: the id of request
        @param account: the account holding the position.
        @param model_code: the model code holding the position.
        @param contract: the position's Contract
        @param pos: the number of positions held.
        @param avgCost: the average cost of the position.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def positionMultiEnd(self, req_id: int):
        """!
        Indicates all positions have been transmitted.

        @param req_id -

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def realtimeBar(self, req_id: int, timestamp: int, bar_open: float, bar_high: float,
                    bar_low: float, bar_close: float, bar_volume: Decimal, bar_wap: Decimal,
                    bar_count: int):
        """!
        Updates the real time 5 seconds bars

        @param req_id: the request's identifier
        @param timestamp: the bar's date and time (Epoch/Unix time)
        @param bar_open: the bar's open point
        @param bar_high: the bar's high point
        @param bar_low: the bar's low point
        @param bar_close: the bar's closing point
        @param bar_volume: the bar's traded volume (only returned for TRADES data)
        @param bar_wap: the bar's Weighted Average Price rounded to minimum increment (only
            available for TRADES).
        @param bar_count: the number of trades during the bar's timespan (only available for TRADES)

        @return
        """
        bar = [timestamp, bar_open, bar_high, bar_low, bar_close, bar_volume, bar_wap, bar_count]
        msg = {"real_time_bars": {req_id: bar}}
        self.queue.put(msg)

    @iswrapper
    def receiveFA(self, fa_data_type: int, fa_xml_data: str):
        """!
        receives the Financial Advisor's configuration available in the TWS

        @param faDataType: one of:
            1. Groups: offer traders a way to create a group of accounts and apply a single
               allocation method to all accounts in the group.
            2. Profiles: let you allocate shares on an account-by-account basis using a predefined
               calculation value.
            3. Account Aliases: let you easily identify the accounts by meaningful names rather than
               account numbers.
        @param faXmlData: the xml-formatted configuration

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def replaceFAEnd(self, req_id: int, text: str):
        """!
        Notifies the end of the FA replace.

        @param req_id: The request's id.
        @param text: The message text.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def rerouteMktDataReq(self, req_id: int, con_id: int, exchange: str):
        """!
        Returns con_id and exchange for CFD market data request re-route.

        @param req_id -
        @param con_id: The underlying instrument which has market data.
        @param exchange: The underlying's exchange.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

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

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def scannerData(self, req_id: int, rank: int, contract_details: ContractDetails, distance: str,
                    benchmark: str, projection: str, legs_str: str):
        """!
        provides the data resulting from the market scanner request.

        @param reqid: the request's identifier.
        @param rank: the ranking within the response of this bar.
        @param contract_details: the data's ContractDetails
        @param distance: according to query.
        @param benchmark: according to query.
        @param projection: according to query.
        @param legs_str: describes the combo legs when the scanner is returning EFP

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def scannerDataEnd(self, req_id: int):
        """!
        Indicates the scanner data reception has terminated.

        @param req_id: The request's id.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def scannerParameters(self, xml: str):
        """!
        Provides the xml-formatted parameters available from TWS market scanners (not all available
        in API).

        @param xml: The xml-formatted string with the available parameters.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def securityDefinitionOptionParameter(self, req_id: int, exchange: str, underlying_con_id: int,
                                          tradingClass: str, multiplier: str, expirations: set,
                                          strikes: set):
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

        @return
        """
        logger.debug6(
            "Security Definition Option Parameter:\nReqId: %s\nExchange: %s\nUnderlying conId: %s\nTrading Class: %s\nMultiplier: %s\nExpirations: %s\nStrikes: %s",
            req_id, exchange, underlying_con_id, tradingClass, multiplier, expirations, strikes)

        opt_params = {
            "exchange": exchange,
            "underlying_contract_id": underlying_con_id,
            "trading_class": tradingClass,
            "mulitplier": multiplier,
            "expirations": expirations,
            "strikes": strikes
        }
        self.data[req_id] = opt_params

    @iswrapper
    def securityDefinitionOptionParameterEnd(self, req_id: int):
        """!
        called when all callbacks to securityDefinitionOptionParameter are complete

        @param req_id: the ID used in the call to securityDefinitionOptionParameter

        @return
        """
        logger.debug6("SecurityDefinitionOptionParameterEnd. ReqId: %s", req_id)
        self.data_available[req_id].set()

    @iswrapper
    def smartComponents(self, req_id: int, the_map: dict):
        """!
        bit number to exchange + exchange abbreviation dictionary

        IB API's descriptions aren't helpful
        @param req_id:
        @param the_map: sa eclient.reqSmartComponents

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def softDollarTiers(self, req_id: int, tiers: list):
        """!
        Called when receives Soft Dollar Tier configuration information

        @param reqId: The request ID used in the call to EClient::reqSoftDollarTiers
        @param tiers: Stores a list of SoftDollarTier that contains all Soft Dollar Tiers
                      information

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def symbolSamples(self, req_id: int, contract_descriptions: list):
        """!
        Returns array of sample contract descriptions.

        FIXME: IB API's descriptions are non-existant
        @param req_id:
        @param contract_descriptions:

        @return
        """
        logger.debug("Begin Function")
        logger.info("Number of descriptions: %s", len(contract_descriptions))

        self.data[req_id] = []
        for description in contract_descriptions:
            self.data[req_id].append(description)
            logger.info("Symbol: %s", description.contract.symbol)

        logger.debug("End Function")

    @iswrapper
    def tickByTickAllLast(self, req_id: int, tick_type: int, timestamp: int, price: float,
                          size: Decimal, tick_attrib_last: TickAttribLast, exchange: str,
                          special_conditions: str):
        """!
        Returns "Last" or "AllLast" tick-by-tick real-time tick

        @param reqId: unique identifier of the request
        @param tickType: tick-by-tick real-time tick type: "Last" or "AllLast"
        @param timestamp: tick-by-tick real-time tick timestamp
        @param price: tick-by-tick real-time tick last price
        @param size: tick-by-tick real-time tick last size
        @param tick_attrib_last: tick-by-tick real-time last tick attribs
            - bit 0 - past limit
            - bit 1 - unreported
        @param exchange: tick-by-tick real-time tick exchange
        @special_conditions: tick-by-tick real-time tick special conditions

        @return
        """
        tick = [tick_type, timestamp, price, size, tick_attrib_last, exchange, special_conditions]

        msg = {"tick": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickByTickBidAsk(self, req_id: int, timestamp: int, bid_price: float, ask_price: float,
                         bid_size: Decimal, ask_size: Decimal,
                         tick_attrib_bid_ask: TickAttribBidAsk):
        """!
        Returns "BidAsk" tick-by-tick real-time tick

        @param req_id: unique identifier of the request
        @param timestamp: tick-by-tick real-time tick timestamp
        @param bid_price: tick-by-tick real-time tick bid price
        @param ask_price: tick-by-tick real-time tick ask price
        @param bid_size: tick-by-tick real-time tick bid size
        @param ask_size: tick-by-tick real-time tick ask size
        @param tick_attrib_bid_ask:  tick-by-tick real-time bid/ask tick attribs
            - bit 0 - bid past low
            - bit 1 - ask past high

        @return
        """
        tick = [timestamp, bid_price, ask_price, bid_size, ask_size, tick_attrib_bid_ask]

        msg = {"tick": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickByTickMidPoint(self, req_id: int, timestamp: int, mid_point: float):
        """!
        Returns "MidPoint" tick-by-tick real-time tick

        @param reqId: unique identifier of the request
        @param timestamp: tick-by-tick real-time tick timestamp
        @param mid_point: tick-by-tick real-time tick mid_point

        @return
        """
        tick = [timestamp, mid_point]
        msg = {"tick": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickEFP(self, req_id: int, tick_type: int, basis_points: float, formatted_basis_points: str,
                implied_future: float, hold_days: int, future_last_trade_date: str,
                dividend_impact: float, dividends_to_last_trade_date: float):
        """!
        Exchange for Physicals.

        IB API's descriptions. TODO: Verify
        @param req_id: The request's identifier.
        @param tick_type: The type of tick being received.
        @param basis_points: Annualized basis points, which is representative of the financing rate
            that can be directly compared to broker rates.
        @param formatted_basis_points: Annualized basis points as a formatted string that depicts
            them in percentage form.
        @param implied_future: The implied Futures price.
        @param hold_days: The number of hold days until the lastTradeDate of the EFP.
        @param future_last_trade_date: The expiration date of the single stock future.
        @param dividend_impact: The dividend impact upon the annualized basis points interest rate.
        @param dividends_to_last_trade_date: The dividends expected until the expiration of the
            single stock future.

        @return
        """
        tick = [
            "tick_efp", tick_type, basis_points, formatted_basis_points, implied_future, hold_days,
            future_last_trade_date, dividend_impact, dividends_to_last_trade_date
        ]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickGeneric(self, req_id: int, field: int, value: float):
        """!
        Market data callback.

        IB API's description is incomplete and of questionable accuracy.
        TODO: Verify
        @param ticker_id: The request's identifier
        @param field: The type of tick being recieved
        @param value:

        @return
        """
        tick = ["tick_generic", field, value]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickNews(self, req_id: int, timestamp: int, provider_code: str, article_id: str,
                 headline: str, extra_data: str):
        """!
        Ticks with news headlines

        IB API's descriptions are non-existant.
        @param ticker_id:
        @param timestamp:
        @param provider_code:
        @param article_id:
        @param headline:
        @param extra_data:

        @return
        """
        logger.debug("Begin Function")
        tick = ["tick_news", timestamp, provider_code, article_id, headline, extra_data]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickOptionComputation(self, req_id: int, field: int, tick_attrib: int,
                              implied_volatility: float, delta: float, opt_price: float,
                              pv_dividend: float, gamma: float, vega: float, theta: float,
                              und_price: float):
        """!
        Receive's option specific market data. This method is called when the market in an option or
        its underlier moves. TWS’s option model volatilities, prices, and deltas, along with the
        present value of dividends expected on that options underlier are received.

        IB API's descriptions.  TODO: Verify
        @param tickerId: The request's unique identifier.
        @param field: Specifies the type of option computation. Pass the field value into
            TickType.getField(int tickType) to retrieve the field description. For example, a field
            value of 13 will map to modelOptComp, etc. 10 = Bid 11 = Ask 12 = Last
        @param implied_volatility: The implied volatility calculated by the TWS option modeler,
            using the specified tick type value.
        @param tick_attrib:
            - 0 - return based
            - 1 - price based
        @param delta: The option delta value.
        @param opt_price: The option price.
        @param pv_dividend: The present value of dividends expected on the option's underlying.
        @param gamma: The option gamma value.
        @param vega: The option vega value.
        @param theta: The option theta value.
        @param und_price: The price of the underlying.

        @return
        """
        tick = [
            "tick_option_computation", field, tick_attrib, implied_volatility, delta, opt_price,
            pv_dividend, gamma, vega, theta, und_price
        ]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickPrice(self, req_id: int, field: int, price: float, attrib: TickAttrib):
        """!
        Market data tick price callback. Handles all price related ticks. Every tickPrice callback
        is followed by a tickSize. A tickPrice value of -1 or 0 followed by a tickSize of 0
        indicates there is no data for this field currently available, whereas a tickPrice with a
        positive tickSize indicates an active quote of 0 (typically for a combo contract).

        @param req_id: the request's unique identifier.
        @param field: The type of the price being received (i.e. ask price).
        @param price: The actual price.
        @param attribs: An TickAttrib object that contains price attributes such as:
            - TickAttrib.CanAutoExecute
            - TickAttrib.PastLimit
            - TickAttrib.PreOpen

        @return
        """
        tick = ["tick_price", field, price, attrib]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickReqParams(self, req_id: int, min_tick: float, bbo_exchange: str,
                      snapshot_permissions: int):
        """!
        Tick with BOO exchange and snapshot permissions.

        IB API's description is non-existant.
        TODO: Verify parameters
        @param ticker_id -
        @param min_tick -
        @param bbo_exchange -
        @param snampshot_permissions -

        @return
        """
        tick = ["tick_req_params", min_tick, bbo_exchange, snapshot_permissions]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickSize(self, req_id: int, field: int, size: Decimal):
        """!
        Market data tick size callback.  Handles all size-related ticks.

        TODO: Verify parameters
        @param ticker_id: The request's identifier.
        @param field: The type of size being received (i.e. bid size)
        @param size: The actual size.  US Stocks have a multiplier of 100.

        @return
        """
        tick = ["tick_size", field, size]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def tickString(self, req_id: int, field: int, value: str):
        """!
        Market data callback. Every tickPrice is followed by a tickSize. There are also independent
        tickSize callbacks anytime the tickSize changes, and so there will be duplicate tickSize
        messages following a tickPrice.

        WTF is the point of this callback? The data provided is complete gibberish!

        IB API's description is incomplete.
        TODO: Write descriptions
        TODO: Verify parameters
        @param ticker_id: The request's identifier
        @param field: The type of tick being received.
        @param value:

        @return
        """
        tick = ["tick_string", field, value]
        msg = {"market_data": {req_id: tick}}
        self.queue.put(msg)

    @iswrapper
    def updateAccountTime(self, timestamp: str):
        """!
        Receives the last time on which the account was updated.

        @param timestamp: The last update system time.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def updateAccountValue(self, key: str, value: str, currency: str, account_name: str):
        """!
        Receives the subscribed account's information. Only one account can be subscribed at a time.
        After the initial callback to updateAccountValue, callbacks only occur for values which have
        changed. This occurs at the time of a position change, or every 3 minutes at most. This
        frequency cannot be adjusted.

        @param key: the value being updated:
            - AccountCode — The account ID number
            - AccountOrGroup — "All" to return account summary data for all accounts, or set to a
              specific Advisor Account Group name that has already been created in TWS Global
              Configuration
            - AccountReady — For internal use only
            - AccountType — Identifies the IB account structure
            - AccruedCash — Total accrued cash value of stock, commodities and securities
            - AccruedCash-C — Reflects the current's month accrued debit and credit interest to
                              date, updated daily in commodity segment
            - AccruedCash-S — Reflects the current's month accrued debit and credit interest to
                              date, updated daily in security segment
            - AccruedDividend — Total portfolio value of dividends accrued
            - AccruedDividend-C — Dividends accrued but not paid in commodity segment
            - AccruedDividend-S — Dividends accrued but not paid in security segment
            - AvailableFunds — This value tells what you have available for trading
            - AvailableFunds-C — Net Liquidation Value - Initial Margin
            - AvailableFunds-S — Equity with Loan Value - Initial Margin
            - Billable — Total portfolio value of treasury bills
            - Billable-C — Value of treasury bills in commodity segment
            - Billable-S — Value of treasury bills in security segment
            - BuyingPower:
               - Cash Account: Minimum (Equity with Loan Value, Previous Day Equity with Loan Value)
                               - Initial Margin
               - Standard Margin Account: Minimum (Equity with Loan Value, Previous Day Equity with
                               Loan Value) - Initial Margin *4
            - CashBalance — Cash recognized at the time of trade + futures PNL
            - CorporateBondValue — Value of non-Government bonds such as corporate bonds and
                                   municipal bonds
            - Currency — Open positions are grouped by currency
            - Cushion — Excess liquidity as a percentage of net liquidation value
            - DayTradesRemaining — Number of Open/Close trades one could do before Pattern Day
                                   Trading is detected
            - DayTradesRemainingT+1 — Number of Open/Close trades one could do tomorrow before
                                      Pattern Day Trading is detected
            - DayTradesRemainingT+2 — Number of Open/Close trades one could do two days from today
                                      before Pattern Day Trading is detected
            - DayTradesRemainingT+3 — Number of Open/Close trades one could do three days from today
                                      before Pattern Day Trading is detected
            - DayTradesRemainingT+4 — Number of Open/Close trades one could do four days from today
                                      before Pattern Day Trading is detected
            - EquityWithLoanValue — Forms the basis for determining whether a client has the
                                    necessary assets to either initiate or maintain security
                                    positions
            - EquityWithLoanValue-C —
                Cash account:
                    Total cash value
                  + commodities option value
                  - futures maintenance margin requirement
                  + minimum (0, futures PNL)
                Margin account:
                    Total cash value
                  + commodities option value
                 - futures maintenance margin requirement
            - EquityWithLoanValue-S —
                 Cash account: Settled Cash
                 Margin Account:
                    Total cash value
                  + stock value + bond value
                  + (non-U.S. & Canada securities options value)
            - ExcessLiquidity — This value shows your margin cushion, before liquidation
            - ExcessLiquidity-C — Equity with Loan Value - Maintenance Margin
            - ExcessLiquidity-S — Net Liquidation Value - Maintenance Margin
            - ExchangeRate — The exchange rate of the currency to your base currency
            - FullAvailableFunds — Available funds of whole portfolio with no discounts or intraday
                                   credits
            - FullAvailableFunds-C — Net Liquidation Value - Full Initial Margin
            - FullAvailableFunds-S — Equity with Loan Value - Full Initial Margin
            - FullExcessLiquidity — Excess liquidity of whole portfolio with no discounts or
                                    intraday credits
            - FullExcessLiquidity-C — Net Liquidation Value - Full Maintenance Margin
            - FullExcessLiquidity-S — Equity with Loan Value - Full Maintenance Margin
            - FullInitMarginReq — Initial Margin of whole portfolio with no discounts or intraday
                                  credits
            - FullInitMarginReq-C — Initial Margin of commodity segment's portfolio with no
                                    discounts or intraday credits
            - FullInitMarginReq-S — Initial Margin of security segment's portfolio with no discounts
                                    or intraday credits
            - FullMaintMarginReq — Maintenance Margin of whole portfolio with no discounts or
                                   intraday credits
            - FullMaintMarginReq-C — Maintenance Margin of commodity segment's portfolio with no
                                     discounts or intraday credits
            - FullMaintMarginReq-S — Maintenance Margin of security segment's portfolio with no
                                     discounts or intraday credits
            - FundValue — Value of funds value (money market funds + mutual funds)
            - FutureOptionValue — Real-time market-to-market value of futures options
            - FuturesPNL — Real-time changes in futures value since last settlement
            - FxCashBalance — Cash balance in related IB-UKL account
            - GrossPositionValue — Gross Position Value in securities segment
            - GrossPositionValue-S —
                   Long Stock Value
                 + Short Stock Value
                 + Long Option Value
                 + Short Option Value
            - IndianStockHaircut — Margin rule for IB-IN accounts
            - InitMarginReq — Initial Margin requirement of whole portfolio
            - InitMarginReq-C — Initial Margin of the commodity segment in base currency
            - InitMarginReq-S — Initial Margin of the security segment in base currency
            - IssuerOptionValue — Real-time mark-to-market value of Issued Option
            - Leverage-S — GrossPositionValue / NetLiquidation in security segment
            - LookAheadNextChange — Time when look-ahead values take effect
            - LookAheadAvailableFunds — This value reflects your available funds at the next margin
                                        change
            - LookAheadAvailableFunds-C — Net Liquidation Value - look ahead Initial Margin
            - LookAheadAvailableFunds-S — Equity with Loan Value - look ahead Initial Margin
            - LookAheadExcessLiquidity — This value reflects your excess liquidity at the next
                                         margin change
            - LookAheadExcessLiquidity-C — Net Liquidation Value - look ahead Maintenance Margin
            - LookAheadExcessLiquidity-S — Equity with Loan Value - look ahead Maintenance Margin
            - LookAheadInitMarginReq — Initial margin requirement of whole portfolio as of next
                                       period's margin change
            - LookAheadInitMarginReq-C — Initial margin requirement as of next period's margin
                                         change in the base currency of the account
            - LookAheadInitMarginReq-S — Initial margin requirement as of next period's margin
                                         change in the base currency of the account
            - LookAheadMaintMarginReq — Maintenance margin requirement of whole portfolio as of next
                                        period's margin change
            - LookAheadMaintMarginReq-C — Maintenance margin requirement as of next period's margin
                                          change in the base currency of the account
            - LookAheadMaintMarginReq-S — Maintenance margin requirement as of next period's margin
                                          change in the base currency of the account
            - MaintMarginReq — Maintenance Margin requirement of whole portfolio
            - MaintMarginReq-C — Maintenance Margin for the commodity segment
            - MaintMarginReq-S — Maintenance Margin for the security segment
            - MoneyMarketFundValue — Market value of money market funds excluding mutual funds
            - MutualFundValue — Market value of mutual funds excluding money market funds
            - NetDividend — The sum of the Dividend Payable/Receivable Values for the securities and
                            commodities segments of the account
            - NetLiquidation — The basis for determining the price of the assets in your account
            - NetLiquidation-C — Total cash value + futures PNL + commodities options value
            - NetLiquidation-S —
                   Total cash value
                 + stock value
                 + securities options value
                 + bond value
            - NetLiquidationByCurrency — Net liquidation for individual currencies
            - OptionMarketValue — Real-time mark-to-market value of options
            - PASharesValue — Personal Account shares value of whole portfolio
            - PASharesValue-C — Personal Account shares value in commodity segment
            - PASharesValue-S — Personal Account shares value in security segment
            - PostExpirationExcess — Total projected "at expiration" excess liquidity
            - PostExpirationExcess-C — Provides a projected "at expiration" excess liquidity based
                                       on the soon-to expire contracts in your portfolio in
                                       commodity segment
            - PostExpirationExcess-S — Provides a projected "at expiration" excess liquidity based
                                       on the soon-to expire contracts in your portfolio in security
                                       segment
            - PostExpirationMargin — Total projected "at expiration" margin
            - PostExpirationMargin-C — Provides a projected "at expiration" margin value based on
                                       the soon-to expire contracts in your portfolio in commodity
                                       segment
            - PostExpirationMargin-S — Provides a projected "at expiration" margin value based on
                                       the soon-to expire contracts in your portfolio in security
                                       segment
            - PreviousDayEquityWithLoanValue — Marginable Equity with Loan value as of 16:00 ET the
                                               previous day in securities segment
            - PreviousDayEquityWithLoanValue-S — IMarginable Equity with Loan value as of 16:00 ET
                                                 the previous day
            - RealCurrency — Open positions are grouped by currency
            - RealizedPnL — Shows your profit on closed positions, which is the difference between
                            your entry execution cost and exit execution costs:
                            execution price to open the positions
                          + commissions to open the positions
                          - execution price to close the position
                          + commissions to close the position
            - RegTEquity — Regulation T equity for universal account
            - RegTEquity-S — Regulation T equity for security segment
            - RegTMargin — Regulation T margin for universal account
            - RegTMargin-S — Regulation T margin for security segment
            - SMA — Line of credit created when the market value of securities in a Regulation T
                    account increase in value
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
            - UnrealizedPnL — The difference between the current market value of your open positions
                              and the average cost, or Value - Average Cost
            - WarrantValue — Value of warrants
            - WhatIfPMEnabled — To check projected margin requirements under Portfolio Margin model
        @param value: up-to-date value
        @param currency: the currency on which the value is expressed.
        @param account_name: the account

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def updateMktDepth(self, ticker_id: int, position: int, operation: int, side: int, price: float,
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

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def updateMktDepthL2(self, ticker_id: int, position: int, market_maker: str, operation: int,
                         side: int, price: float, size: Decimal, is_smart_depth: bool):
        """!
        Returns the order book.

        @param ticker_id: The request's identifier
        @param position: The Order book's row being updated
        @param market_maker: The Exchange holding the order if is_smart_depth is True, otherwise
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
        @param is_smart_depth: flag indicating if this is smart depth response (aggregate data from
            multiple exchanges)

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def updateNewsBulletin(self, msg_id: int, msg_type: int, message: str, orig_exchange: str):
        """!
        Provides IB's bulletins

        @param msg_id: The Builtin's identifier
        @param msg_type:
            - 1 - Regular news bulletin
            - 2 - Exchange no longer available for trading
            - 3 - Exchange is available for trading
        @param message - The message
        @param orig_exchange: The exchange where the message comes from.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def updatePortfolio(self, contract: Contract, position: float, market_price: float,
                        market_value: float, average_cost: float, unrealized_pnl: float,
                        realized_pnl: float, account_name: str):
        """!
        Receives the subscribed account's portfolio. This function will receive only the portfolio
        of the subscribed account. If the portfolios of all managed accounts are needed, refer to
        EClientSocket.reqPosition After the initial callback to updatePortfolio, callbacks only
        occur for positions which have changed.

        IB API's description is incomplete.  TODO: Complete descriptions.
        @param contract: the Contract for which a position is held.
        @param position: the number of positions held.
        @param market_price: instrument's unitary price
        @param market_value: total market value of the instrument.
        @param average_cost:
        @param unrealized_pnl:
        @param realized_pnl:
        @param account_name:

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def userinfo(self, req_id: int, white_branding_id: str):
        """!
        Return user info

        IB API's description is in complete.  TODO: Complete descriptions.
        @param req_id: The request's identifier
        @param white_branding_id: FIXME: IB API does not provide a description

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def wshEventData(self, req_id: int, datajson: str):
        """!
        Returns calendar events from the WSH.

        @param req_id: The request's identifier
        @param datajson: Event data in JSON format.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    @iswrapper
    def wshMetaData(self, req_id: int, datajson: str):
        """!
        Returns meta data from the WSH calendar.

        @param req_id: The request's identifier
        @param datajson: Event data in JSON format.

        @return
        """
        logger.debug("Begin Function")
        logger.debug("End Function")

    # ==============================================================================================
    #
    # Internal Helper Functions
    #
    # ==============================================================================================
    def _data_wait(self, timestamp, sleep_time):
        time_diff = datetime.datetime.now() - timestamp

        # TODO: Why is this a loop?
        while time_diff.total_seconds() < sleep_time:

            logger.debug6("Now: %s", datetime.datetime.now())
            logger.debug6("Last Request: %s", timestamp)
            logger.debug6("Time Difference: %s seconds", time_diff.total_seconds())
            remaining_sleep_time = sleep_time - time_diff.total_seconds()
            logger.debug6("Sleep Time: %s", remaining_sleep_time)
            time.sleep(sleep_time - time_diff.total_seconds())
            time_diff = datetime.datetime.now() - timestamp

    def _historical_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.__historical_data_req_timestamp, HISTORICAL_DATA_SLEEP_TIME)

    def _small_bar_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.__small_bar_data_req_timestamp, SMALL_BAR_SLEEP_TIME)

    def _contract_details_data_wait(self):
        """!
        Ensure that we wait between historical data requests.

        @param self

        @return
        """
        self._data_wait(self.__contract_details_data_req_timestamp, CONTRACT_DETAILS_SLEEP_TIME)

    def _calculate_deep_data_allotment(self):
        """!
        Caclulates the allowed dep data requests available.
        """
        min_allotment = 3
        max_allotment = 60

        basic_allotment = self.__available_market_data_lines % 100

        if basic_allotment < min_allotment:
            self.__available_deep_data_allotment = min_allotment
        elif basic_allotment > max_allotment:
            self.__available_deep_data_allotment = max_allotment
        else:
            self.__available_deep_data_allotment = basic_allotment
