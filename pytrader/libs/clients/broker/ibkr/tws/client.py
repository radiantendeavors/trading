"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsreal
Creates a basic interface for interacting with a broker

@file pytrader/libs/clients/broker/ibkr/tws/twsreal.py

Creates a basic interface for interacting with a broker

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

"""
import datetime
from typing import Optional

from ibapi.contract import Contract
from ibapi.order import Order

from pytrader.libs.clients.broker.ibkr.tws.twspacemngr import TwsPacingMngr
from pytrader.libs.system import logging
from pytrader.libs.utilities.exceptions import InvalidExchange, InvalidTickType

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base Logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsApiClient(TwsPacingMngr):
    """!
    The Command interface for the TWS API Client.
    """

    # ==============================================================================================
    #
    # The following functions are wrappers around the eClient functions.  All are lowercased.  Their
    # primary purpose is to provide any formatting and error checking to ensure the API function
    # receives the correct inputs.
    #
    # All functions in alphabetical order.
    #
    # ==============================================================================================
    def calculate_implied_volatility(
            self,
            contract: Contract,
            option_price: float,
            under_price: float,
            implied_option_volatility_options: Optional[list] = None) -> int:
        """!
        Calculate the volatility for an option.
        Request the calculation of the implied volatility based on hypothetical option and its
        underlying prices.  The calculation will be return in EWrapper's tickOptionComputation
        callback.

        @param contract: The option's contract for which the volatility is to be calculated.
        @param option_price: Hypothetical Option Price
        @param under_price: Hypothetical option's underlying price.
        @param implied_option_volatility_options: FIXME: This is not documented by the TWSAPI

        @return req_id: The request identifier used.
        """
        self.req_id += 1

        # TWSAPI will crash if implied_option_volatility_options is NoneType.  Since setting the
        # default value to and empty list '[]' is dangerous, we do this instead.
        if implied_option_volatility_options is None:
            implied_option_volatility_options = []
        self.calculateImpliedVolatility(self.req_id, contract, option_price, under_price,
                                        implied_option_volatility_options)

        return self.req_id

    def calculate_option_price(self,
                               contract: Contract,
                               volatility: float,
                               under_price: float,
                               option_price_options: Optional[list] = None) -> int:
        """!
        Calculates an option's price based on the provided volatility and its underlying's price.
        The calculation will be return in EWrapper's tickOptionComputation callback.

        @param contract: The option's contract for which the price wants to be calculated.
        @param volatility: Hypothetical volatility.
        @param under_price: Hypothetical underlying's price.
        @param option_price_options: FIXME: This is not documented by the TWSAPI

        @return req_id: The request identifier used
        """
        self.req_id += 1
        if option_price_options is None:
            option_price_options = []
        self.calculateOptionPrice(self.req_id, contract, volatility, under_price,
                                  option_price_options)

        return self.req_id

    def cancel_account_summary(self, req_id: int) -> None:
        """!
        Cancels the account's summary request. After requesting an account's summary, invoke this
        function to cancel it.

        @param req_id: The identifier of the previously performed account request.

        @return None
        """
        self.cancelAccountSummary(req_id)

    def cancel_account_updates_multi(self, req_id: int) -> None:
        """!
        Cancels account updates request for account and/or model.

        @param req_id: The account subscription to cancel.

        @return None
        """
        self.cancelAccountUpdatesMulti(req_id)

    def cancel_calculate_implied_volatility(self, req_id: int) -> None:
        """!
        Cancels an option's implied volatility calculation request

        @param req_id: The request id to cancel

        @return None
        """
        self.cancelCalculateImpliedVolatility(req_id)

    def cancel_head_timestamp(self, req_id: int) -> None:
        """!
        Cancels a pending reqHeadTimeStamp request.

        @param req_id: The request id to cancel.

        @return None
        """
        self.cancelHeadTimeStamp(req_id)

    def cancel_historical_data(self, req_id: int) -> None:
        """!
        Cancels a historical data request.

        @param req_id: The requeust id to cancel.

        @return None
        """
        self.cancelHistoricalData(req_id)

    def cancel_mkt_data(self, req_id: int) -> None:
        """!
        Cancels a RT Market Data request.

        @param req_id: The request id to cancel.

        @return None
        """
        self.cancelMktData(req_id)

    def cancel_mkt_depth(self, req_id: int, is_smart_depth: bool) -> None:
        """!
        Cancels a market depth request.

        @param req_id: The request id to cancel.
        @param is_smart_depth: FIXME: This is not documented by the TWSAPI.

        @return None
        """
        self.cancelMktDepth(req_id, is_smart_depth)

    def cancel_news_bulletins(self) -> None:
        """!
        Cancels IB's news bulletin subscription.

        @return None
        """
        self.cancelNewsBulletins()

    def cancel_order(self, order_id: int, manual_order_cancel_time: str = "") -> None:
        """!
        Cancels an active order placed by from the same API client ID.
        Note: API clients cannot cancel individual orders placed by other clients. Only
        reqGlobalCancel is available.

        @param order_id: The Order Id to cancel.
        @param manual_order_cancel_time: FIXME: This is not documented by the TWSAPI.  IBAPI says to
                                         set the value to an empty string.

        @return None
        """
        # Ensure that manual_order_cancel_time is an empty string
        manual_order_cancel_time = ""

        self.cancelOrder(order_id, manual_order_cancel_time)

    def is_connected(self):
        """!
        Indicates whether the API-TWS connection has been closed. NOTE: This function is not
        automatically invoked and must be by the API client.

        @return status
        """
        return self.isConnected()

    def place_order(self, contract: Contract, order: Order, order_id: Optional[int] = None):
        """!
        Places or modifies an order.

        @param contract: The contract for the order.
        @param order: The order
        @param order_id: The order's unique identifier.  Use a sequential id starting with the id
               received at the nextValidId method. If a new order is placed with an order ID less
               than or equal to the order ID of a previous order an error will occur.

        @return order_id:  The order_id that was used.
        """
        logger.debug("Order: %s", order)
        if order_id is None:
            self.next_valid_id_available.wait()
            order_id = self.next_order_id

        self.placeOrder(order_id, contract, order)
        self.req_ids()
        return order_id

    def req_account_summary(self, account_types: str = "ALL", tags: Optional[list] = None) -> int:
        """!
        Requests a specific account's summary.
        This method will subscribe to the account summary as presented in the TWS' Account Summary
        tab. The data is returned at EWrapper::accountSummary
        https://www.interactivebrokers.com/en/software/tws/accountwindowtop.htm.

        @param account_types: Set to "All" to return account summary data for all accounts, or set
               to a specific Advisor Account Group name that has already been created in TWS
               Global Configuration.
        @param tags: A comma separated list with the desired tags
               AccountType — Identifies the IB account structure
               NetLiquidation — The basis for determining the price of the assets in your account.
                                Total cash value + stock value + options value + bond value
               TotalCashValue — Total cash balance recognized at the time of trade + futures PNL
               SettledCash — Cash recognized at the time of settlement
                             - purchases at the time of trade
                             - commissions
                             - taxes
                             - fees
               AccruedCash — Total accrued cash value of stock, commodities and securities
               BuyingPower — Buying power serves as a measurement of the dollar value of securities
                             that one may purchase in a securities account without depositing
                             additional funds
               EquityWithLoanValue — Forms the basis for determining whether a client has the
                                     necessary assets to either initiate or maintain security
                                     positions.
                                     Cash + stocks + bonds + mutual funds
               PreviousEquityWithLoanValue — Marginable Equity with Loan value as of 16:00 ET the
                                             previous day
               GrossPositionValue — The sum of the absolute value of all stock and equity option
                                    positions
               RegTEquity — Regulation T equity for universal account
               RegTMargin — Regulation T margin for universal account
               SMA — Special Memorandum Account: Line of credit created when the market value of
                     securities in a Regulation T account increase in value
               InitMarginReq — Initial Margin requirement of whole portfolio
               MaintMarginReq — Maintenance Margin requirement of whole portfolio
               AvailableFunds — This value tells what you have available for trading
               ExcessLiquidity — This value shows your margin cushion, before liquidation
               Cushion — Excess liquidity as a percentage of net liquidation value
               FullInitMarginReq — Initial Margin of whole portfolio with no discounts or intraday
                                   credits
               FullMaintMarginReq — Maintenance Margin of whole portfolio with no discounts or
                                    intraday credits
               FullAvailableFunds — Available funds of whole portfolio with no discounts or intraday
                                    credits
               FullExcessLiquidity — Excess liquidity of whole portfolio with no discounts or
                                     intraday credits
               LookAheadNextChange — Time when look-ahead values take effect
               LookAheadInitMarginReq — Initial Margin requirement of whole portfolio as of next
                                        period's margin change
               LookAheadMaintMarginReq — Maintenance Margin requirement of whole portfolio as of
                                         next period's margin change
               LookAheadAvailableFunds — This value reflects your available funds at the next margin
                                         change
               LookAheadExcessLiquidity — This value reflects your excess liquidity at the next
                                          margin change
               HighestSeverity — A measure of how close the account is to liquidation
               DayTradesRemaining — The Number of Open/Close trades a user could put on before
                                    Pattern Day Trading is detected. A value of "-1" means that the
                                    user can put on unlimited day trades.
               Leverage — GrossPositionValue / NetLiquidation
               $LEDGER — Single flag to relay all cash balance tags*, only in base currency.
               $LEDGER:CURRENCY — Single flag to relay all cash balance tags*, only in the specified
                                  currency.
               $LEDGER:ALL — Single flag to relay all cash balance tags* in all currencies.

        @return req_id: The request identifier used.
        """
        self.req_id += 1
        tags_string = ", ".join([str(item) for item in tags])
        self.reqAccountSummary(self.req_id, account_types, tags_string)
        return self.req_id

    def req_account_updates(self, subscribe: bool, account_code: str) -> None:
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

        @return None
        """
        self.reqAccountUpdates(subscribe, account_code)

    def req_contract_details(self, req_id: int, contract: Contract):
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
        self.add_command(req_id, "contract_details")
        self.contract_details_data_wait()
        self.reqContractDetails(req_id, contract)
        self.contract_details_data_req_timestamp = datetime.datetime.now()

    def req_global_cancel(self) -> None:
        """!
        Cancels all active orders.

        This method will cancel ALL open orders including those placed directly from TWS.

        @return None
        """
        self.reqGlobalCancel()

    def req_head_timestamp(self,
                           req_id: int,
                           contract: Contract,
                           what_to_show: Optional[str] = "TRADES",
                           use_regular_trading_hours: Optional[bool] = True,
                           format_date: Optional[bool] = True) -> None:
        """!
        Requests the earliest available bar data for a contract.

        @param req_id: The request id to use for this request.
        @param contract: The contract
        @param what_to_show: Type of information to show, defaults to "TRADES"
        @param use_regular_trading_hours: Defaults to 'True'
        @param format_date: Defaults to 'True'

        @return req_id: The request identifier
        """
        self.add_command(req_id, "history_begin")
        self.contract_history_begin_data_wait()
        self.reqHeadTimeStamp(req_id, contract, what_to_show, use_regular_trading_hours,
                              format_date)
        self.contract_details_data_req_timestamp = datetime.datetime.now()

    # pylint: disable=C0301
    def req_historical_data(self,
                            contract: Contract,
                            bar_size_setting: str,
                            end_date_time: str = "",
                            duration_str: str = "",
                            what_to_show: str = "TRADES",
                            use_regular_trading_hours: bool = True,
                            format_date: bool = True,
                            keep_up_to_date: bool = False,
                            chart_options: Optional[list] = None) -> int:
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
        @param chart_options: FIXME: This is not documented by the TWSAPI

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

        self._historical_data_wait()

        logger.debug6("Requesting Historical Bars for: %s", contract.localSymbol)

        # TWSAPI expects chart_options type to be a list.
        if chart_options is None:
            chart_options = []

        self.reqHistoricalData(self.req_id, contract, end_date_time, duration_str, bar_size_setting,
                               what_to_show, use_regular_trading_hours, format_date,
                               keep_up_to_date, chart_options)

        self.data[self.req_id] = []
        return self.req_id

    def req_historical_ticks(self,
                             contract: Contract,
                             start_date_time: str,
                             end_date_time: str,
                             number_of_ticks: int,
                             what_to_show: str,
                             use_regular_trading_hours: int,
                             ignore_size: bool,
                             misc_options: Optional[list] = None) -> int:
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
        number_of_ticks = min(number_of_ticks, 1000)

        # TWSAPI expects misc_options type to be a list
        if misc_options is None:
            misc_options = []

        self.reqHistoricalTicks(self.req_id, contract, start_date_time, end_date_time,
                                number_of_ticks, what_to_show, use_regular_trading_hours,
                                ignore_size, misc_options)
        return self.req_id

    def req_ids(self) -> None:
        """!
        Requests the next valid order ID at the current moment.

        @return None
        """
        # NOTE: TWS API reqIds has a required parameter 'numIds'.  The API Docs say it is
        # depreciated, however, an error message will occur if one is not set.
        self.reqIds(1)

    def req_managed_accounts(self) -> None:
        """!
        Requests the accounts to which the logged user has access to.

        NOTE: This data is already provided during the initial connection, and stored in
        self.accounts.
        """
        self.reqManagedAccts()

    def req_market_data(self,
                        req_id: int,
                        contract: Contract,
                        generic_tick_list: Optional[str] = None,
                        snapshot: Optional[bool] = False,
                        regulatory_snapshot: Optional[bool] = False,
                        market_data_options: Optional[list] = None):
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
        @param market_data_options: FIXME: This is not documented by the TWSAPI

        @return req_id: The rquest's identifier
        """
        if not generic_tick_list:
            generic_tick_list = "221, 232, 233, 236, 258, 293, 294, 295,"
            generic_tick_list += " 318, 375, 411, 456, 595, 619"

        if contract.secType == "STK":
            # Legal ones for (STK) are:
            #   - 100(Option Volume)
            #   - 101(Option Open Interest)
            #   - 105(Average Opt Volume)
            #   - 106(impvolat)
            #   - 165(Misc. Stats)
            #   - 221/220(Creditman Mark Price)
            #   - 225(Auction)
            #   - 232/221(Pl Price)
            #   - 233(RTVolume)
            #   - 236(inventory)
            #   - 258/47(Fundamentals)
            #   - 292(Wide_news)
            #   - 293(TradeCount)
            #   - 294(TradeRate)
            #   - 295(VolumeRate)
            #   - 318(LastRTHTrade)
            #   - 375(RTTrdVolume)
            #   - 411(rthistvol)
            #   - 456/59(IBDividends)
            #   - 460(Bond Factor Multiplier)
            #   - 576(EtfNavBidAsk(navbidask))
            #   - 577(EtfNavLast(navlast))
            #   - 578(EtfNavClose(navclose))
            #   - 586(IPOHLMPRC)
            #   - 587(Pl Price Delayed)
            #   - 588(Futures Open Interest)
            #   - 595(Short-Term Volume X Mins)
            #   - 614(EtfNavMisc(high/low))
            #   - 619(Creditman Slow Mark Price)
            #   - 623(EtfFrozenNavLast(fznavlast)
            if generic_tick_list == "":
                generic_tick_list = "100, 101, 104, 105, 106, 165, 292"
            else:
                generic_tick_list += ", 100, 101, 104, 105, 106, 165, 292"

        self.reqMktData(req_id, contract, generic_tick_list, snapshot, regulatory_snapshot,
                        market_data_options)

    def req_real_time_bars(self,
                           contract: Contract,
                           bar_size_setting: int = 5,
                           what_to_show: str = "TRADES",
                           use_regular_trading_hours: bool = True,
                           real_time_bar_options: Optional[list] = None) -> int:
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
        @param real_time_bar_options: FIXME: This is not documented by the TWSAPI

        @return req_id: The request's identifier
        """
        # Make sure whatever we receive is upper case.
        what_to_show = what_to_show.upper()
        allowed_bar_types = ["TRADES", "MIDPOINT", "BID", "ASK"]

        if what_to_show in allowed_bar_types:
            self.req_id += 1

            # TWSAPI expects real_time_bar_options type to be a list
            if real_time_bar_options is None:
                real_time_bar_options = []

            self.reqRealTimeBars(self.req_id, contract, bar_size_setting, what_to_show,
                                 use_regular_trading_hours, real_time_bar_options)

            # This is updated here, rather than in the _historical_data_wait function because we
            # want to actually make the request before setting a new timer.
            return self.req_id

    def req_sec_def_opt_params(self,
                               req_id: int,
                               contract: Contract,
                               exchange: Optional[str] = None):
        """!
        Requests security definition option parameters for viewing a contract's option chain

        @param req_id: The Request Id
        @param contract: The Contract for the request
        @param exchange: The exchange on which the returned options are trading.  Can be set to the
                         empty string "" for all exchanges.

        @return req_id: The Request's identifier
        """
        if exchange is None:
            exchange = ""
        elif exchange not in contract.Exchange:
            raise InvalidExchange(f"Invalid Exchange: {exchange} not in {contract.Exchange}")
        self.reqSecDefOptParams(req_id, contract.symbol, exchange, contract.secType, contract.conId)

    def req_tick_by_tick_data(self,
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
        # Ensure we have the tick type formatted correctly for TWSAPI
        # match tick_type.lower():
        #     case "last":
        #         tick_type = "Last"
        #     case "alllast":
        #         tick_type = "AllLast"
        #     case "bidask":
        #         tick_type = "BidAsk"
        #     case "midpoint":
        #         tick_type = "MidPoint"
        #     case _:
        #         raise InvalidTickType("Invalid Tick Type")

        logger.debug("Req Tick-by-Tick %s %s %s %s", contract, tick_type, number_of_ticks,
                     ignore_size)

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
