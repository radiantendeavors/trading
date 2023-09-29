"""!@package pytrader.libs.applications.downloader.basecontract

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

@file pytrader/libs/applications/downloader/basecontract.py
"""
# System Libraries
from datetime import date, datetime, time, timedelta
from multiprocessing import Queue

# 3rd Party
from ibapi.contract import ContractDetails

# Application Libraries
from pytrader.libs.contracts import (IndexContract, StkOptionContract,
                                     StockContract)
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
class BaseContractDownloader():

    def __init__(self, contract_list: list) -> None:
        self.contract_list = contract_list
