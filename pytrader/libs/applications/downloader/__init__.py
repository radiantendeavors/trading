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
from datetime import date, timedelta
from multiprocessing import Queue

# Application Libraries
from pytrader.libs.clients.broker.ibkr.webscraper import IbkrWebScraper
from pytrader.libs.clients.database.mysql.ibkr.contract_universe import \
    IbkrContractUniverse
from pytrader.libs.contracts import Contract
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
class DownloadProcess():
    """!
    Managers the Data Downloading Process.
    """
    contracts = {}
    contract_universe = None

    def __init__(self, cmd_queue: Queue, data_queue: Queue, tickers: list, enable_options: bool,
                 asset_classes: list, currencies: list, regions: list, export: list) -> None:
        """!
        Initializes the Downloader Process

        @param cmd_queue:
        @param data_queue:
        @param tickers:
        @param enable_options:
        @param asset_classes:
        @param currencies:
        @param regions:
        @param export:

        @return None
        """
        self.cmd_queue = cmd_queue
        self.data_queue = data_queue
        self.ticker_list = tickers
        self.enable_options = enable_options
        self.asset_classes = asset_classes
        self.currencies = currencies
        self.regions = regions
        self.export = export

    def run(self) -> None:
        """!
        Runs the Download Process.

        @return None
        """
        self._get_contract_universe()

        for item in self.contract_universe:
            self._get_contract_details(item)

        for item in self.contract_universe:
            self._get_contract_history_begin_date(item)

    def _download_contract_details(self, ticker: dict) -> None:
        symbol = ticker["ib_symbol"]
        sec_type = ticker["asset_class"]
        self.contracts[symbol] = Contract(self.cmd_queue, symbol, sec_type)
        self.contracts[symbol].create_contract(ticker["exchange"], ticker["currency"])
        self.contracts[symbol].send_contract("downloader")

    def _download_contract_universe(self):
        """!
        Downloads the stock universe
        """
        scraper = IbkrWebScraper()
        scraper.get_exchange_listings(self.regions)
        scraper.get_asset_classes()
        scraper.get_asset_class_pages(self.asset_classes)
        scraper.get_assets()
        scraper.filter_assets(self.currencies)
        scraper.to_sql()

        if "csv" in self.export:
            scraper.to_csv()

    def _get_contract_details(self, ticker: dict) -> None:
        symbol = ticker["ib_symbol"]
        self.contracts[symbol] = Contract(self.cmd_queue, symbol, ticker["asset_class"])
        self.contracts[symbol].create_contract(ticker["exchange"], ticker["currency"])
        self.contracts[symbol].get_contract_details()

    def _get_contract_history_begin_date(self, ticker: dict) -> None:
        symbol = ticker["ib_symbol"]
        self.contracts[symbol].get_contract_history_begin_date()

    def _get_contract_universe(self):
        db = IbkrContractUniverse()
        max_date = db.max_date()
        renew_data_date = date.today() - timedelta(days=7)

        logger.debug("Max Date: %s", max_date)
        logger.debug("Renew Date: %s", renew_data_date)
        if max_date and max_date > renew_data_date:
            self._query_contract_universe()
        else:
            logger.debug("Updating Contract Universe")
            self._download_contract_universe()
            self._query_contract_universe()

    def _query_contract_universe(self):
        db = IbkrContractUniverse()

        if len(self.ticker_list) > 0:
            criteria = {"ib_symbol": self.ticker_list}
            self.contract_universe = db.select(criteria=criteria)
            logger.debug("Contract Universe: %s", self.contract_universe)
        else:
            self.contract_universe = db.select()
            logger.debug("Contract Universe: %s", self.contract_universe)

    def _process_data(self, data):
        if data.get("contracts"):
            self.contracts = data["contracts"]
            logger.debug("Contracts: %s", self.contracts)
        # if data.get("option_details"):
        #     logger.debug("Processing Option Details")
        #     self._process_option_details(data["option_details"])
        # if data.get("bars"):
        #     logger.debug3("Processing Bars")
        #     self._process_bars(data["bars"])
        # if data.get("tick"):
        #     logger.debug3("Processing Tick Data")
        #     self._process_ticks(data["tick"])
