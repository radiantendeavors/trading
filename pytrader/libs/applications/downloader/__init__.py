"""!@package pytrader.libs.applications.downloader

The main user interface for the trading program.

@author G S Derber
@date 2022-2003
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

@file pytrader/libs/applications/downloader/__init__.py
"""
# System Libraries
from datetime import date, datetime, time, timedelta
from multiprocessing import Queue
from time import sleep
from typing import Optional

# 3rd Party
from ibapi.contract import ContractDetails

# Application Libraries
from pytrader.libs.clients.broker.ibkr.webscraper import IbkrWebScraper
from pytrader.libs.clients.database.mysql.ibkr import (
    IbkrContractUniverse, IbkrIndOptHistoryBeginDate,
    IbkrIndOptInvalidContracts, IbkrIndOptNoHistory,
    IbkrStkOptHistoryBeginDate, IbkrStkOptInvalidContracts,
    IbkrStkOptNoHistory)
from pytrader.libs.contracts import (IndexContract, IndOptionContract,
                                     StkOptionContract, StockContract)
from pytrader.libs.system import logging

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The base logger.
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
# pylint: disable=R0902
class DownloadProcess():
    """!
    Managers the Data Downloading Process.
    """
    contracts = {}
    contract_universe = None
    option_contracts = []
    option_contract_symbols = []
    symbol_list = []
    loop_list = []
    next_order_id = 0
    enabled = False
    download_options = False

    def __init__(self, cmd_queue: Queue, data_queue: Queue) -> None:
        """!
        Initializes the Downloader Process

        @param cmd_queue:
        @param data_queue:

        @return None
        """
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue

    def enable_historical_downloader(self,
                                     asset_classes: list,
                                     regions: list,
                                     currencies: list,
                                     tickers: Optional[list] = None) -> None:
        """!
        Enable Downloading Historical Data.

        @param asset_classes:
        @param currencies:
        @param regions:
        @param tickers:

        @return None
        """
        self._get_contract_universe(asset_classes, regions, currencies, tickers)
        # self._clean_invalid_contracts()

        self.loop_list = [self.contract_universe[:] for _ in range(4)]

        self.enabled = True

    def enable_options(self) -> None:
        """!
        Enable downloading options.

        @return None
        """
        self.download_options = True

    def run(self) -> None:
        """!
        Runs the Download Process.

        @return None
        """
        # ==========================================================================================
        #
        # We run this in this loop like this to:
        # 1. Ensure we have get the data to process incrementally rather than waiting until
        #    everything has been requested
        # 2. Slow down the requests a bit to play nice with the broker's servers.
        #
        # ==========================================================================================
        counter = 0
        continue_loop = True

        while continue_loop:
            message = self.data_queue.get()

            if isinstance(message, dict):
                message = self._process_data(message)

            if message == "Done":
                continue_loop = False
            elif message == "Next" and self.enabled:
                counter = self._next_step(counter)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _clean_invalid_contracts(self):
        db_table = IbkrIndOptInvalidContracts()
        db_table.clean_invalid()

        db_table = IbkrIndOptHistoryBeginDate()
        db_table.clean_history()

        db_table = IbkrStkOptInvalidContracts()
        db_table.clean_invalid()

        db_table = IbkrStkOptHistoryBeginDate()
        db_table.clean_history()

    def _create_contract(self, symbol, asset_class):
        if asset_class.upper() == "STK":
            self.contracts[symbol] = StockContract(self.cmd_queue, self.data_queue, symbol)
        elif asset_class.upper() == "IND":
            self.contracts[symbol] = IndexContract(self.cmd_queue, self.data_queue, symbol)

    def _download_contract_universe(self, asset_classes: list, regions: list,
                                    currencies: list) -> None:
        """!
        Downloads the stock universe
        """
        scraper = IbkrWebScraper()
        scraper.get_exchange_listings(regions)
        scraper.get_asset_classes()
        scraper.get_asset_class_pages(asset_classes)
        scraper.get_assets()
        scraper.filter_assets(currencies)
        scraper.to_sql()

    def _gen_options_contracts(self, ticker: dict) -> None:
        logger.debug("Generating Options Contracts For: '%s'", ticker["ib_symbol"])
        symbol = ticker["ib_symbol"]

        option_params = self.contracts[symbol].get_option_parameters()
        expirations = option_params[0]
        strikes = option_params[1]
        multiplier = option_params[2]

        logger.debug9("Expirations: %s", expirations)
        logger.debug9("Strikes: %s", strikes)

        expirations.sort()
        strikes.sort()

        if expirations:
            for expiry in expirations[0:4]:
                expiry_date = datetime.strptime(expiry, "%Y%m%d")
                today = datetime.combine(date.today(), time(0, 0))
                if expiry_date >= today:
                    self._loop_option_strikes(symbol, expiry, strikes, multiplier)

    def _get_contract_details(self, ticker: dict) -> None:
        logger.debug("Getting Contract Details for '%s'", ticker["ib_symbol"])
        symbol = ticker["ib_symbol"]
        self._create_contract(symbol, ticker["asset_class"])
        self.contracts[symbol].select_columns()
        self.contracts[symbol].create_contract(ticker["exchange"], ticker["currency"])
        self.contracts[symbol].get_contract_details()

    def _get_contract_history_begin_date(self, symbol: str) -> None:
        logger.debug("Getting History Begin Date for %s", symbol)
        no_history = self.contracts[symbol].query_no_history()

        if no_history:
            logger.debug("No History Exists for Contract, Skipping")
            self.data_queue.put("Next")
        else:
            self.contracts[symbol].get_contract_history_begin_date()

    def _get_contract_option_params(self, ticker: dict) -> None:
        logger.debug("Getting Contract Option Parameters for '%s'", ticker["ib_symbol"])
        symbol = ticker["ib_symbol"]
        self.contracts[symbol].get_contract_option_parameters()

    def _get_contract_universe(self,
                               asset_classes: list,
                               regions: list,
                               currencies: list,
                               tickers: Optional[list] = None) -> None:
        db = IbkrContractUniverse()
        max_date = db.max_date()

        # Update every 30 days.
        # FIXME: Should this be more frequent?  Less frequent?
        #
        # It's a lot of data that takes a while to download.  99.999% of which does not change
        # often, but when it does change, that data is needed quickly.
        renew_data_date = date.today() - timedelta(days=30)

        logger.debug("Max Date: %s", max_date)
        logger.debug("Renew Date: %s", renew_data_date)
        if max_date and max_date > renew_data_date:
            self._query_contract_universe(tickers)
        else:
            logger.debug("Updating Contract Universe")
            self._download_contract_universe(asset_classes, regions, currencies)
            self._query_contract_universe(tickers)

    def _get_invalid_option_contracts(self, opt_contract) -> None:
        option_params = opt_contract.get_option_contract_parameters()
        expiration = option_params[0]
        strike = option_params[1]
        right = option_params[2]

        last_trading_date = datetime.strptime(expiration, "%Y%m%d").date()

        additional_criteria = {
            "last_trading_date": [last_trading_date],
            "strike": [strike],
            "opt_right": [right[0]]
        }
        db_contract = opt_contract.query_contracts(additional_criteria)

        if not db_contract:
            opt_contract.save_invalid_contract(additional_criteria)

        self.data_queue.put("Next")

    def _get_option_contract_details(self, opt_contract) -> None:
        option_params = opt_contract.get_option_contract_parameters()
        expiration = option_params[0]
        strike = option_params[1]
        right = option_params[2]

        last_trading_date = datetime.strptime(expiration, "%Y%m%d").date()

        additional_criteria = {
            "last_trading_date": [last_trading_date],
            "strike": [strike],
            "opt_right": [right[0]]
        }
        db_contract = opt_contract.query_contracts(additional_criteria)
        if db_contract:
            opt_contract.set_contract_parameters(db_contract)
            self.contracts[db_contract["local_symbol"]] = opt_contract
            self.option_contract_symbols.append(db_contract["local_symbol"])
            self.data_queue.put("Next")
        else:
            invalid_contract = opt_contract.query_invalid_contracts()
            if invalid_contract:
                logger.debug("Contract is invalid, skipping")
                self.data_queue.put("Next")
            else:
                opt_contract.req_contract_details("downloader")

    def _loop_option_strikes(self, symbol, expiry, strikes, multiplier):
        if strikes:
            for strike in strikes:
                self._loop_option_right(symbol, expiry, strike, multiplier)

    def _loop_option_right(self, symbol, expiry, strike, multiplier):
        for right in ["Call", "Put"]:
            underlying_type = self.contracts[symbol].sec_type

            if underlying_type == "STK":
                opt_contract = StkOptionContract(self.cmd_queue, self.data_queue, symbol)
            elif underlying_type == "IND":
                opt_contract = IndOptionContract(self.cmd_queue, self.data_queue, symbol)
            local_symbol = opt_contract.create_contract("SMART", "USD", expiry, right, strike,
                                                        multiplier)
            logger.debug("Local Symbol: %s", local_symbol)
            self.option_contracts.append(opt_contract)

    def _next_step(self, counter: int) -> int:
        if len(self.loop_list[0]) > 0:
            self._get_contract_details(self.loop_list[0].pop())
        elif len(self.loop_list[1]) > 0:
            self._get_contract_option_params(self.loop_list[1].pop())
        elif len(self.loop_list[2]) > 0:
            self._gen_options_contracts(self.loop_list[2].pop())
            self.data_queue.put("Next")
        elif len(list(self.option_contracts)) > 0 and counter == 0:
            self._get_option_contract_details(self.option_contracts.pop())
        elif len(self.loop_list[3]) > 0:
            counter = 1
            self._gen_options_contracts(self.loop_list[3].pop())
            logger.debug("Number of Options Contracts: %s", len(self.option_contracts))
            self.data_queue.put("Next")
        elif len(list(self.option_contracts)) > 0 and counter == 1:
            self._get_invalid_option_contracts(self.option_contracts.pop())
        elif counter == 1:
            counter = 2
            self.symbol_list = list(self.contracts.copy())
            self.data_queue.put("Next")
        elif len(self.symbol_list) > 0:
            self._get_contract_history_begin_date(self.symbol_list.pop())
        else:
            logger.debug("All Data Downloaded, shutting down")
            self.data_queue.put("Done")

        return counter

    def _process_data(self, data: dict) -> str | bool:
        logger.debug("Data: %s", data)
        if data.get("contract_details"):
            contract_details = data["contract_details"]
            self._process_contract_details(contract_details)
            return "Next"

        if data.get("contract_history_begin_date"):
            history_begin_date = data["contract_history_begin_date"]
            self._process_history_begin_date(history_begin_date)
            return "Next"

        if data.get("contract_option_parameters"):
            option_parameters = data["contract_option_parameters"]
            self._process_option_parameters(option_parameters)
            return "Next"

        if data.get("db_option_parameters"):
            return "Next"

        if data.get("next_order_id"):
            self.next_order_id = data["next_order_id"]
            return "Next"

        return False

    def _process_contract_details(self, contract_details: ContractDetails) -> None:
        logger.debug("Contract Details: %s", contract_details)
        local_symbol = contract_details.contract.localSymbol

        if contract_details.contract.secType == "OPT":
            symbol = contract_details.contract.symbol
            underlying_type = self.contracts[symbol].sec_type
            if underlying_type == "STK":
                self.contracts[local_symbol] = StkOptionContract(self.cmd_queue, self.data_queue,
                                                                 local_symbol)
            else:
                self.contracts[local_symbol] = IndOptionContract(self.cmd_queue, self.data_queue,
                                                                 local_symbol)

            self.option_contract_symbols.append(local_symbol)

        self.contracts[local_symbol].save_contract(contract_details)

    def _process_history_begin_date(self, history_begin_date: dict) -> None:
        ticker = list(history_begin_date)[0]
        self.contracts[ticker].save_history_begin_date(history_begin_date[ticker])

    def _process_option_parameters(self, option_parameters: dict) -> None:
        ticker = list(option_parameters)[0]
        self.contracts[ticker].save_option_parameters(option_parameters[ticker])

    def _query_contract_universe(self, tickers: Optional[list] = None) -> None:
        universe_db = IbkrContractUniverse()

        if tickers and len(tickers) > 0:
            criteria = {"ib_symbol": tickers}
            self.contract_universe = universe_db.select(criteria=criteria)
            logger.debug9("Contract Universe: %s", self.contract_universe)
        else:
            self.contract_universe = universe_db.select()
            logger.debug9("Contract Universe: %s", self.contract_universe)
