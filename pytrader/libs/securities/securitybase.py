"""!
@package pytrader.libs.securitybase

Provides the broker client

@author Geoff S. Derber
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


@file pytrader/libs/securitybase.py
"""
# System libraries
import datetime
import locale
import multiprocessing
import pandas

# 3rd Party libraries
from ibapi.contract import Contract

# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs import bars
from pytrader.libs import orders
from pytrader.libs.clients.mysql import ibkr_etf_info
from pytrader.libs.clients import database
from pytrader.libs.clients.database import ibkr

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
class SecurityBase():

    def __init__(self, *args, **kwargs):
        logger.debug10("Begin Function")
        logger.debug("Kwargs: %s", kwargs)

        if kwargs.get("ticker_symbol"):
            self.ticker_symbol = kwargs["ticker_symbol"]
        if kwargs.get("brokerclient"):
            self.brokerclient = kwargs["brokerclient"]
        if kwargs.get("process_queue"):
            self.process_queue = kwargs["process_queue"]

        if kwargs.get("bar_sizes"):
            self.bar_sizes = kwargs["bar_sizes"]
        else:
            self.bar_sizes = ["1 day"]

        ## Used to hold the contract
        self.contract = None

        ## Used to hold the bar information
        self.bars = {}

        ## Duration for contract history
        self.duration = None

        ## Used to store the exchange
        self.exchange = "SMART"

        ## Used to store the primary exchange
        self.primary_exchange = None

        ## Used to store the currency
        self.currency = "USD"

        ## Used for the database session
        self.db_session = self.__create_database_session()

        self.ibkr_etf = None

        if kwargs.get("duration"):
            self.duration = kwargs["duration"]

        logger.debug10("End Function")

    def set_contract(self):
        """!@fn set_contract

        @param exchange
        """
        logger.debug10("Begin Function")
        contract = Contract()
        contract.symbol = self.ticker_symbol
        contract.secType = self.security_type
        contract.exchange = self.exchange
        contract.currency = self.currency
        if self.primary_exchange:
            contract.primaryExchange = self.primary_exchange

        logger.debug("Contract: %s", contract)
        self.contract = contract

        logger.debug10("End Function")

        return contract

    def set_contract_info(self):
        contract = self.__query_broker_database()
        self.ibkr_etf = contract

        if contract is not None:
            self.contract_id = contract.contract_id
            self.ticker_symbol = contract.ticker_symbol
            self.security_type = contract.security_type
            self.exchange = contract.exchange
            self.currency = contract.currency
            self.primary_exchange = contract.primary_exchange
        else:
            self.update_broker_info()

    def set_bar_begin_date(self):
        logger.debug10("Begin Function")
        begin_date = self.__query_begin_date()
        logger.debug("Begin Date: %s", begin_date)
        self.begin_date = begin_date
        logger.debug10("End Function")

    def get_bars(self):
        return self.bars

    def update_info(self, source=None):
        logger.debug10("Begin Function")

        if source == "broker" or source == "ibkr":
            self.__update_broker_info()
            self.__update_broker_bar_begin_date()
        elif source == "yahoo":
            self.update_yahoo_info()
        else:
            logger.error("Source Not Selected.")

    def get_broker_info(self):
        """!
        get_broker_info
        """

        req_id = self.brokerclient.get_security_data(self.contract)
        data = self.brokerclient.get_data(req_id)
        return data

    def get_yahoo_info(self, ticker):
        yc = yahoo.YahooClient()
        yc.get_info(self.securities_type, ticker)

    def place_order(self):
        logger.debug10("Begin Function")
        order = orders.Order(order_type="market",
                             action="BUY",
                             quantity=1,
                             transmit=False,
                             brokerclient=self.brokerclient)
        logger.debug("Contract: %s", self.contract)
        logger.debug("Order:\n%s", order)
        order.place_order(self.contract)

        logger.debug10("End Function")

    def update_history(self, keep_up_to_date=False):
        logger.debug10("Begin Function")
        self.set_contract_info()
        self.set_contract()
        self.set_bar_begin_date()

        for size in self.bar_sizes:
            self.bars[size] = bars.Bars(brokerclient=self.brokerclient,
                                        contract=self.contract,
                                        keep_up_to_date=keep_up_to_date,
                                        bar_size=size,
                                        duration=self.duration,
                                        begin_date=self.begin_date)
            self.bars[size].retrieve_bar_history()
        logger.debug("End Function")

    def update_bars(self):
        bar_process = {}
        for size in self.bar_sizes:
            bar_process[size] = multiprocessing.Process(
                target=self.bars[size].update_bars, args=())
            bar_process[size].start()

        logger.debug("Bars: %s", bars)
        logger.debug("End Function")
        return None

    def calculate_ema(self, bar_size, span):
        self.bars[bar_size].calculate_ema(span)

    def calculate_sma(self, bar_size, span):
        self.bars[bar_size].calculate_sma(span)

    def __create_database_session(self):
        db = database.Database()
        db.create_engine()
        db_session = db.create_session()

        return db_session

    def __query_broker_database(self):
        logger.debug10("Begin Function")
        db = ibkr.IbkrEtfContracts()
        contract = db.query_contract(self.db_session, self.ticker_symbol)

        if len(contract) > 0:
            return contract[0]
        else:
            return None

        logger.debug10("End Function")

    def __query_begin_date(self):
        contract = self.__query_broker_database()

        db = ibkr.IbkrEtfBarHistoryBeginDate()
        begin_date = db.query_begin_date(self.db_session, self.ibkr_etf)
        logger.debug("Begin Date: %s", begin_date)
        return begin_date

    def __update_broker_bar_begin_date(self):
        logger.debug10("Begin Function")
        database = ibkr.IbkrEtfBarHistoryBeginDate()
        logger.debug10("End Function")

    def __update_broker_info(self):
        contract = self.__query_broker_database()

        # self.set_contract()
        # logger.debug("Get Security Data")

        # req_id = self.brokerclient.req_contract_details(self.contract)
        # logger.debug("Request ID: %s", req_id)
        # data = self.brokerclient.get_data(req_id)

        # contract = ibkr.IbkrEtfContracts()
        # contract.insert(db_session, data.contract.conId, data.contract.symbol,
        #                 data.contract.secType, data.contract.exchange,
        #                 data.contract.currency, data.contract.localSymbol,
        #                 data.contract.primaryExchange,
        #                 data.contract.tradingClass)

        # req_id = self.brokerclient.req_head_timestamp(
        #     self.contract, use_regular_trading_hours=0)
        # data = self.brokerclient.get_data(req_id)

        # locale_ = locale.getlocale()
        # logger.debug("Locale: %s", locale_)
        # data = data + " UTC"
        # datetime_utc = datetime.datetime.strptime(data, '%Y%m%d %H:%M:%S %Z')

        # datetime_est = datetime_utc.replace(
        #     tzinfo=datetime.timezone.utc).astimezone(tz=None)

        # logger.debug("DateTime: %s",
        #              datetime_est.strftime('%Y-%m-%d %H:%M:%S %Z%z'))

        # begin_history_datetime = ibkr.IbkrEtfBarHistoryBeginDate(
        #     ibkr_etf=contract)
        # begin_history_datetime.insert(db_session, datetime_est)

        # # self.update_ipo_date()
        # logger.debug10("End Function")
        # return None
