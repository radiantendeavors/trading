"""!
@package pytrader.libs.clients.broker.ibkr.tws.twsclient

Provides wrappers around TWSAPI Client functions.  These are mostly used to provide sanity checks on
the parameters to ensure they are properly formatted for the API, and implement any required pauses
to avoid pacing violations.

In addition, all functions are named using more modern python naming conventions (snake_case)

@author G S Derber
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

@file pytrader/libs/clients/broker/ibkr/tws/twsclient.py

Implements the TWSAPI Client functions
"""
from datetime import datetime
from typing import Optional

from ibapi.common import WshEventData
from ibapi.contract import Contract
from ibapi.execution import ExecutionFilter
from ibapi.order import Order
from ibapi.scanner import ScannerSubscription

from pytrader.libs.clients.broker.ibkr.tws.twspacemngr import TwsPacingMngr
from pytrader.libs.system import logging
from pytrader.libs.utilities.exceptions import InvalidExchange

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
#pylint: disable=R0904
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
    # pylint: disable=R0913
    def calculate_implied_volatility(
            self,
            req_id: int,
            contract: Contract,
            option_price: float,
            under_price: float,
            implied_option_volatility_options: Optional[list] = None) -> None:
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
        # TWSAPI will crash if implied_option_volatility_options is NoneType.  Since setting the
        # default value to and empty list '[]' is dangerous, we do this instead.
        if implied_option_volatility_options is None:
            implied_option_volatility_options = []
        self.calculateImpliedVolatility(req_id, contract, option_price, under_price,
                                        implied_option_volatility_options)

    # pylint: disable=R0913
    def calculate_option_price(self,
                               req_id: int,
                               contract: Contract,
                               volatility: float,
                               under_price: float,
                               option_price_options: Optional[list] = None) -> None:
        """!
        Calculates an option's price based on the provided volatility and its underlying's price.
        The calculation will be return in EWrapper's tickOptionComputation callback.

        @param contract: The option's contract for which the price wants to be calculated.
        @param volatility: Hypothetical volatility.
        @param under_price: Hypothetical underlying's price.
        @param option_price_options: FIXME: This is not documented by the TWSAPI

        @return req_id: The request identifier used
        """
        if option_price_options is None:
            option_price_options = []
        self.calculateOptionPrice(req_id, contract, volatility, under_price, option_price_options)

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

    def cancel_order(self, order_id: int, manual_order_cancel_time: Optional[str] = "") -> None:
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

    def cancel_pnl(self, req_id: int) -> None:
        """!
        Cancels subscription for real time updated daily PnL.

        @param req_id:

        @return None.
        """
        self.cancelPnL(req_id)

    def cancel_pnl_single(self, req_id: int) -> None:
        """!
        Cancels real time subscription for a positions daily PnL information.

        @param req_id:

        @return None.
        """
        self.cancelPnLSingle(req_id)

    def cancel_positions(self) -> None:
        """!
        Cancels a previous position subscription request made with req_positions.

        @return None.
        """
        self.cancelPositions()

    def cancel_positions_multi(self, req_id: int) -> None:
        """!
        Cancels positions request for account and/or model.

        @param req_id:


        @return None
        """
        self.cancelPositionsMulti(req_id)

    def cancel_real_time_bars(self, req_id: int) -> None:
        """!
        Cancels Real Time Bars' subscription.

        @param req_id:  The request used for the real time bar request.

        @return None.
        """
        self.cancelRealTimeBars(req_id)

    def cancel_scanner_subscription(self, req_id: int) -> None:
        """!
        Cancels Scanner Subscription.

        @param req_id:

        @return None
        """
        self.cancelScannerSubscription(req_id)

    def cancel_tick_by_tick_data(self, req_id: int) -> None:
        """!
        Cancels tick-by-tick data.

        @param req_id:

        @return None.
        """
        self.cancelTickByTickData(req_id)

    def cancel_wsh_event_data(self, req_id: int) -> None:
        """!
        Cancels pending WSH event data request.

        @param req_id:

        @return None
        """
        self.cancelWshEventData(req_id)

    def cancel_wsh_meta_data(self, req_id: int) -> None:
        """!
        Cancels pending request for WSH metadata.

        @param req_id:

        @return None
        """
        self.cancelWshMetaData(req_id)

    def exercise_options(self, req_id: int, contract: Contract, exercise_action: int,
                         exercise_quantity: int, account: str, override: int) -> None:
        """!
        Exercises an options contract.

        NOTE: This function is affected by a TWS setting which specifies if an exercise request must
        be finalized.

        @param req_id: Exercise Request Identifier
        @param contract: The option Contract to be exercised.
        @param exercise_action:
               - 1: Exercise the option
               - 2: Let the option lapse
        @param exercise_quanity: The number of contracts to be exercised.
        @param account: Destination Account
        @param override: Specifies whether your setting will override the system's natural action.
                         For example, if your action is "exercise" and the option is not
                         in-the-money, by natural action the option would not exercise. If you have
                         override set to "yes" the natural action would be overridden and the
                         out-of-the money option would be exercised. Set to 1 to override, set to 0
                         not to.

        @return None
        """
        self.exerciseOptions(req_id, contract, exercise_action, exercise_quantity, account,
                             override)

    def is_connected(self) -> bool:
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

    def query_display_groups(self, req_id: int) -> None:
        """!
        Requests all available Display Groups in TWS.

        https://www.ibkrguides.com/tws/usersguidebook/thetradingwindow/colorgrouping.htm

        @param req_id:

        @return None
        """
        self.queryDisplayGroups(req_id)

    def replace_fa(self, req_id: int, fa_data_type: int, xml: str) -> None:
        """!
        Replaces Financial Advisor's settings A Financial Advisor can define three different
        configurations:
          - Groups: offer traders a way to create a group of accounts and apply a single allocation
            method to all accounts in the group.
          - Account Aliases: let you easily identify the accounts by meaningful names rather than
            account numbers. More information at:
            https://www.interactivebrokers.com/en/?f=%2Fen%2Fsoftware%2Fpdfhighlights%2FPDF-AdvisorAllocations.php%3Fib_entity%3Dllc
          - FIXME: TWAPI WTF is the third configuration?

        @param req_id:
        @param fa_data_type: The Configuration to change.  Set to 1 or? (FIXME) 3 as defined above.
        @param xml: The xml formatted configuration string.

        @return None
        """
        self.replaceFA(req_id, fa_data_type, xml)

    def req_account_summary(self,
                            req_id: int,
                            account_types: str = "ALL",
                            tags: Optional[list] = None) -> None:
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
        tags_string = ", ".join([str(item) for item in tags])
        self.reqAccountSummary(req_id, account_types, tags_string)

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

    def req_account_updates_multi(self, req_id: int, account: str, model_code: str,
                                  ledger_and_nlv: bool) -> None:
        """!
        Request account updates for account and / or model.

        @param req_id:
        @param account: Account values can be requested for a particular account.
        @param model_code: Values can also be requested for a model.
        @param ledger_and_nlv: Returns light-weight request: only currency positions as opposed to
                               account values and currency positions.

        @return None
        """
        self.reqAccountUpdatesMulti(req_id, account, model_code, ledger_and_nlv)

    def req_all_open_orders(self) -> None:
        """!
        Requests all current open orders in associated accounts at the current moment. The existing
        orders will be received via the openOrder and orderStatus events. Open orders are returned
        once; this function does not initiate a subscription.

        @return None
        """
        self.reqAllOpenOrders()

    def req_auto_open_orders(self, auto_bind: bool) -> None:
        """!
        Requests status updates about future orders placed from TWS. Can only be used with client ID
        0.

        @param auto_bind:
               - True: The newly created orders will be assigned an API order ID and implicitly
                       associated with this client.
               - False: Future orders will not be.

        @return None
        """
        self.reqAutoOpenOrders(auto_bind)

    def req_completed_orders(self, api_only: bool) -> None:
        """!
        Request Completed Orders.

        @param api_only: Request only API Orders.

        @return None
        """
        self.reqCompletedOrders(api_only)

    def req_contract_details(self, req_id: int, contract: Contract) -> None:
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
        self.contract_details_data_req_timestamp = datetime.now()

    def req_current_time(self) -> None:
        """!
        Requests TWS's current time.

        @return None
        """
        self.reqCurrentTime()

    def req_executions(self, req_id: int, execution_filter: ExecutionFilter) -> None:
        """!
        Requests current day's (since midnight) executions matching the filter. Only the current
        day's executions can be retrieved. Along with the executions, the CommissionReport will also
        be returned. The execution details will arrive at EWrapper:execDetails.

        @param req_id: The requests unique Id.
        @param execution_filter: The filter criteria used to determine which execution reports are
                                 returned.

        @return None
        """
        self.reqExecutions(req_id, execution_filter)

    def req_fa(self, fa_data_type: int) -> None:
        """!
        Requests the FA configuration A Financial Advisor can define three different configurations:
            1. Groups: offer traders a way to create a group of accounts and apply a single
               allocation method to all accounts in the group.
            3. Account Aliases: let you easily identify the accounts by meaningful names
               rather than account numbers.

        More information at:
        https://www.interactivebrokers.com/en/?f=%2Fen%2Fsoftware%2Fpdfhighlights%2FPDF-AdvisorAllocations.php%3Fib_entity%3Dllc

        FIXME: The 3rd option is not documented by TWSAPI

        @param fa_data_type: The configureation to change.  Set to 1 or 3 as defined above.

        @return None
        """
        self.requestFA(fa_data_type)

    def req_family_codes(self) -> None:
        """!
        Requests family codes for an account, for instance if it is a FA, iBroker, or associated
        account.
        """
        self.reqFamilyCodes()

    def req_global_cancel(self) -> None:
        """!
        Cancels all active orders.

        This method will cancel ALL open orders including those placed directly from TWS.

        @return None
        """
        self.reqGlobalCancel()

    # pylint: disable=R0913
    def req_head_timestamp(self,
                           req_id: int,
                           contract: Contract,
                           what_to_show: Optional[str] = "TRADES",
                           use_regular_trading_hours: Optional[bool] = False,
                           format_date: Optional[bool] = True) -> None:
        """!
        Requests the earliest available bar data for a contract.

        @param req_id: The request id to use for this request.
        @param contract: The contract
        @param what_to_show: Type of information to show, defaults to "TRADES"
        @param use_regular_trading_hours: Limit to regular trading hourse.
                                          Defaults to 'False' because I only want to get this once
                                          due to rate limitations.
        @param format_date: Defaults to 'True'

        @return req_id: The request identifier
        """
        self.add_command(req_id, "history_begin")
        logger.debug("Waiting to avoid pacing violation.  Request to be made is for %s",
                     contract.localSymbol)
        self.contract_history_begin_data_wait()
        self.reqHeadTimeStamp(req_id, contract, what_to_show, use_regular_trading_hours,
                              format_date)
        logger.debug("Head Timestamp requested for %s", contract.localSymbol)
        self.contract_history_begin_data_req_timestamp = datetime.now()

    def req_histogram_data(self, req_id: int, contract: Contract, use_regular_trading_hours: bool,
                           period: str) -> None:
        """!
        Returns data histogram of specified contract.

        @param req_id: The request unique Id.
        @param contract: Contract object for which histogram is being requested.
        @param use_regular_trading_hours: Use Regular Trading Hours only:
                                          - 1: Yes
                                          - 0: No
        @param period: The period of which data is being requested, e.g. "3 days"

        @return None
        """
        self.reqHistogramData(req_id, contract, use_regular_trading_hours, period)

    # pylint: disable=C0301
    def req_historical_data(self,
                            req_id: int,
                            contract: Contract,
                            bar_size_setting: str,
                            end_date_time: str = "",
                            duration_str: str = "",
                            what_to_show: str = "TRADES",
                            use_regular_trading_hours: bool = True,
                            format_date: bool = True,
                            keep_up_to_date: bool = False,
                            chart_options: Optional[list] = None) -> None:
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

        # if keep_up_to_date is true, end_date_time must be blank.
        # https://interactivebrokers.github.io/tws-api/historical_bars.html
        if keep_up_to_date:
            end_date_time = ""

        self.historical_data_wait()

        logger.debug6("Requesting Historical Bars for: %s", contract.localSymbol)

        # TWSAPI expects chart_options type to be a list.
        if chart_options is None:
            chart_options = []

        self.reqHistoricalData(req_id, contract, end_date_time, duration_str, bar_size_setting,
                               what_to_show, use_regular_trading_hours, format_date,
                               keep_up_to_date, chart_options)

    def req_historical_news(self,
                            req_id: int,
                            contract_id: int,
                            provider_codes: str,
                            start_date_time: datetime,
                            end_date_time: datetime,
                            total_results: int = 300) -> None:
        """!
        Request historical news headlines.

        @param req_id: FIXME: This is not documented by the TWSAPI
        @param contract_id: contract id of ticker.
        @param provider_codes: A '+' separated list of provider codes
        @param start_date_time: Markes the exclused start date of the range.
        @param end_date_time: Markes the inclusive end date of the range.
        @param total_results: The maximum number of headlines to fetch (1-300)

        @return None
        """
        # The format is yyyy-MM-dd HH:mm:ss.0
        start = start_date_time.strftime("%Y-%m-%d %H:%M:%S") + ".0"

        # The format is yyyy-MM-dd HH:mm:ss.0
        end = end_date_time.strftime("%Y-%m-%d %H:%M:%S") + ".0"

        # historical_news_options: Reserved for internal use.  Per TWSAPI docs it should be defined
        # as Null, however, it expects a list type.  (WTF Interactive Brokers!)
        historical_news_options = []

        # Ensure the total results is within the proper range.
        if total_results > 300:
            total_results = 300
        elif total_results < 1:
            total_results = 1

        self.reqHistoricalNews(req_id, contract_id, provider_codes, start, end, total_results,
                               historical_news_options)

    # pylint: disable=R0913
    def req_historical_ticks(self,
                             req_id: int,
                             contract: Contract,
                             start_date_time: str,
                             end_date_time: str,
                             number_of_ticks: int,
                             what_to_show: str,
                             use_regular_trading_hours: int,
                             ignore_size: bool,
                             misc_options: Optional[list] = None) -> None:
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
        # The maximum allowed is 1000 per request
        number_of_ticks = min(number_of_ticks, 1000)

        # TWSAPI expects misc_options type to be a list
        if misc_options is None:
            misc_options = []

        self.reqHistoricalTicks(req_id, contract, start_date_time, end_date_time, number_of_ticks,
                                what_to_show, use_regular_trading_hours, ignore_size, misc_options)

    def req_ids(self) -> None:
        """!
        Requests the next valid order ID at the current moment.

        @return None
        """
        # NOTE: TWS API reqIds has a required parameter 'numIds'.  The API Docs say it is
        # depreciated, however an error message will occur if one is not set.
        self.reqIds(1)

    def req_managed_accounts(self) -> None:
        """!
        Requests the accounts to which the logged user has access to.

        NOTE: This data is already provided during the initial connection, and stored in
        self.accounts.
        """
        self.reqManagedAccts()

    # pylint: disable=R0913
    def req_market_data(self,
                        req_id: int,
                        contract: Contract,
                        generic_tick_list: Optional[str] = None,
                        snapshot: Optional[bool] = False,
                        regulatory_snapshot: Optional[bool] = False,
                        market_data_options: Optional[list] = None) -> None:
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

    def req_market_data_type(self, market_data_type: int) -> None:
        """!
        Switches data type returned from reqMktData request to "frozen", "delayed" or
        "delayed-frozen" market data. Requires TWS/IBG v963+.  The API can receive frozen market
        data from Trader Workstation. Frozen market data is the last data recorded in our system.
        During normal trading hours, the API receives real-time market data. Invoking this function
        with argument 2 requests a switch to frozen data immediately or after the close.  When the
        market reopens, the market data type will automatically switch back to real time if
        available.

        @param market_data_type: Defaults to 1
               - 1 (real-time) disables frozen, delayed and delayed-frozen market data
               - 2 (frozen) enables frozen market data
               - 3 (delayed) enables delayed and disables delayed-frozen market data
               - 4 (delayed-frozen) enables delayed and delayed-frozen market data

        @return None
        """
        if market_data_type in [1, 2, 3, 4]:
            self.reqMarketDataType(market_data_type)

    def req_market_depth(self, req_id: int, contract: Contract, num_rows: int,
                         is_smart_depth: bool) -> None:
        """!
        Requests the contract's market depth (order book).

        This request must be direct-routed to an exchange and not smart-routed. The number of
        simultaneous market depth requests allowed in an account is calculated based on a formula
        that looks at an accounts equity, commissions, and quote booster packs.

        @param req_id: The requests unique id.
        @param contract: The Contract for which the the depths is being requested.
        @param num_rows: The number of rows on each side of the order book.
        @param is_smart_depth: Flag indicates that this is a smart depth request.

        @return None
        """
        if contract.exchange != "SMART":
            # NOTE: While twsapi docs say this should be 'reqMarketDepth' the function in twsapi is
            # reqMktDepth (WTF Interactive Brokers!)
            self.reqMktDepth(req_id, contract, num_rows, is_smart_depth, [])

    def req_market_depth_exchanges(self) -> None:
        """!
        Requeusts venues for which market data is returned to updateMktDepthL2 (those with market
        makers)

        @return None
        """
        self.reqMktDepthExchanges()

    def req_market_rule(self, market_rule_id: int) -> None:
        """!
        Requests details about a given market rule.

        The market rule for an instrument on a particular exchange provides details about how the
        minimum price increment changes with price.  A list of market rule ids can be obtained by
        invoking reqContractDetails on a particular contract. The returned market rule ID list will
        provide the market rule ID for the instrument in the correspond valid exchange list in
        contractDetails.

        @param market_rule_id: The id of the market rule.

        @return None
        """
        self.reqMarketRule(market_rule_id)

    def req_matching_symbols(self, req_id: int, pattern: str) -> None:
        """!
        Requeust matching stock symbols.

        @param req_id: The request's unique id.
        @param pattern: The start of a ticker symbol or (for larger strings) company name.

        @return None.
        """
        self.reqMatchingSymbols(req_id, pattern)

    def req_news_article(self, req_id: int, provider_code: str, article_id: str) -> None:
        """!
        Requests news article body given article id.

        @param req_id: The request's unique id.
        @param provider_code: Short code indicating news provider, e.g. FLY
        @param article_id: The specific article id.

        @return None
        """
        # newsArticleOptions is reservered for internal use.  Per twsapi docs, this should be null,
        # but it expects a list.
        news_article_options = []

        self.reqNewsArticle(req_id, provider_code, article_id, news_article_options)

    def req_news_bulletins(self, all_messages: bool) -> None:
        """!
        Subscribes to IB's News Bulletins.

        @param all_messages:
               - True: Return all existing bulletins for the current day.
               - False: Receive only the new bulletins.

        @return None
        """
        self.reqNewsBulletins(all_messages)

    def req_news_providers(self) -> None:
        """!
        Requeusts availeble news providers.

        These are the providers that the user has subscribed to in their account.
        """
        self.reqNewsProviders()

    def req_open_orders(self) -> None:
        """!
        Requests all open orders placed by this specific API client (identified by the API client
        id).  For client id 0, this will bind previous manual TWS orders.

        @return None
        """
        self.reqOpenOrders()

    def req_pnl(self, req_id: int, account: str, model_code: str) -> None:
        """!
        Creates a subscription for real time daily PnL and unrealized PnL updates.

        @param req_id: The request's unique id.
        @param account: The account for which to receive PnL updates.
        @param model_code: Specify to request PnL updates for a specific model.

        @return None
        """
        self.reqPnL(req_id, account, model_code)

    def req_pnl_single(self, req_id: int, account: str, model_code: str, contract_id: int) -> None:
        """!
        Requests real time updates for daily PnL of individual positions.

        @param req_id: The request's uniquue id.
        @param account: Account in which eth position exists.
        @param model_code: Model in which the position exists.
        @param contract_id: The contract id of the contract to receive daily PnL updates for.  Note:
                            It does not return a message if invalid contract_id is entered.

        @return None
        """
        self.reqPnLSingle(req_id, account, model_code, contract_id)

    def req_positions(self) -> None:
        """!
        Subscribes to position updates for all accessible accounts. All positions sent initially,
        and then only updates as positions change.

        @return None
        """
        self.reqPositions()

    def req_positions_multi(self, req_id: int, account: str, model_code: str) -> None:
        """!
        Requests position subscription for account and/or model Initially all positions are
        returned, and then updates are returned for any position changes in real time.

        @param req_id: The request's unique id.
        @param account: If an account Id is provided, only the account's positions belonging to the
                        specified model will be delivered.
        @param modelCode: The code of the model's positions we are interested in.

        @return None
        """
        self.reqPositionsMulti(req_id, account, model_code)

    def req_real_time_bars(self,
                           req_id: int,
                           contract: Contract,
                           bar_size_setting: int = 5,
                           what_to_show: str = "TRADES",
                           use_regular_trading_hours: bool = True,
                           real_time_bar_options: Optional[list] = None) -> None:
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
            # TWSAPI expects real_time_bar_options type to be a list
            if real_time_bar_options is None:
                real_time_bar_options = []

            self.reqRealTimeBars(req_id, contract, bar_size_setting, what_to_show,
                                 use_regular_trading_hours, real_time_bar_options)

    def req_scanner_parameters(self) -> None:
        """!
        Requests an XML list of scanner parameters valid in TWS.
        Not all parameters are valid from API scanner.

        @return None
        """
        self.reqScannerParameters()

    def req_scanner_subscription(self, req_id: int, subscription: ScannerSubscription) -> None:
        """!
        Starts a subscription to market scan results based on the provided parameters.

        @param req_id: The request's unique id.
        @param subscribed: The summary of the scanner subscription including its filters.

        @return None
        """
        # These two parameters are not documented, other than that they expect a list.
        scanner_subscription_options = []
        scanner_subscription_filter_options = []
        self.reqScannerSubscription(req_id, subscription, scanner_subscription_options,
                                    scanner_subscription_filter_options)

    def req_sec_def_opt_params(self,
                               req_id: int,
                               contract: Contract,
                               exchange: Optional[str] = None) -> None:
        """!
        Requests security definition option parameters for viewing a contract's option chain

        @param req_id: The Request Id
        @param contract: The Contract for the request
        @param exchange: The exchange on which the returned options are trading.  Can be set to the
                         empty string "" for all exchanges.

        @return None
        """
        if exchange is None:
            exchange = ""
        elif exchange not in contract.Exchange:
            raise InvalidExchange(f"Invalid Exchange: {exchange} not in {contract.Exchange}")
        self.reqSecDefOptParams(req_id, contract.symbol, exchange, contract.secType, contract.conId)

    def req_smart_components(self, req_id: int, bbo_exchange: str) -> None:
        """!
        Returns the mapping of single letter codes to exchange names given the mapping identifier.

        @param req_id: The request's unique id.
        @param bbo_exchange: Mapping identifier received from EWrapper.tickReqparams

        @return None
        """
        self.reqSmartComponents(req_id, bbo_exchange)

    def req_soft_dollar_tiers(self, req_id: int) -> None:
        """!
        Requests pre-defined Soft Dollar Tiers. This is only supported for registered professional
        advisors and hedge and mutual funds who have configured Soft Dollar Tiers in Account
        Management. Refer to:
        https://www.interactivebrokers.com/en/software/am/am/manageaccount/requestsoftdollars.htm?Highlight=soft%20dollar%20tier.

        @param req_id: The request's unique id

        @return None
        """
        self.reqSoftDollarTiers(req_id)

    def req_tick_by_tick_data(self,
                              req_id: int,
                              contract: Contract,
                              tick_type: str = "Last",
                              number_of_ticks: int = 0,
                              ignore_size: bool = False) -> None:
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

        logger.debug("ReqId %s Tick-by-Tick %s %s %s %s", req_id, contract, tick_type,
                     number_of_ticks, ignore_size)

    def req_user_info(self, req_id: int) -> None:
        """!
        Requests user info.

        @param req_id: The request's unique id.

        @return None
        """
        self.reqUserInfo(req_id)

    def req_wsh_event_data(self, req_id: int, wsh_event_data: WshEventData) -> None:
        """!
        Requests event data from the wSH calendar.

        @param req_id: The request's unique id.
        @param wsh_event_data: FIXME This is not documented by TWSAPI.

        @return None
        """
        self.reqWshEventData(req_id, wsh_event_data)

    def req_wsh_meta_data(self, req_id: int) -> None:
        """!
        Requeusts metadata from the WSH calendar.

        @param req_id: The request's unique id.

        @return None.
        """
        self.reqWshMetaData(req_id)

    def set_server_loglevel(self, log_level: int = 2) -> None:
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

    def subscribe_to_group_events(self, req_id: int, group_id: int) -> None:
        """
        Integrates API client and TWS window grouping.

        @param req_id: The request's unique id.
        @param group_id: The display group for integration.

        @return None.
        """
        self.subscribeToGroupEvents(req_id, group_id)

    def update_display_group(self, req_id: int, contract_info: Optional[str] = "") -> None:
        """!
        Updates the contract displayed in a TWS Window Group.

        @param req_id:
        @param contract_info: An encoded value designating a unique IB contract. Possible values
                              include:
                              - "": empty selection
                              - contract_id: Any non-combination contract. Examples:
                                   - 8314 for IBM SMART
                                   - 8314 for IBM ARCA
                              - combo: If any combo is selected (TWSAPI, what does that mean?)

        NOTE: This request from the API does not get a TWS response unless an error occurs.

        @return None
        """
        self.updateDisplayGroup(req_id, contract_info)

    def unsubscribe_from_group_events(self, req_id: int) -> None:
        """!
        Cancels a TWS Window Group subscription.

        @param req_id: The subription's request id.

        @return None
        """
        self.unsubscribeFromGroupEvents(req_id)
