"""!
@package pytrader.libs.applications.broker.observers

Provides the observer classes for the broker process.

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

@file pytrader/libs/applications/broker/observers/__init__.py
"""
# This file doesn't actually do anything more than act as an intermediary, allowing the various
# observers to be further split into multiple files to keep them small, while simultaneously
# allowing a single import statement by the broker.

from pytrader.libs.clients.broker.observers.broker import BrokerOrderIdObserver
from pytrader.libs.clients.broker.observers.downloader import (
    DownloaderBarDataObserver, DownloaderContractDataObserver,
    DownloaderContractHistoryBeginObserver,
    DownloaderContractOptionParametersObserver, DownloaderMarketDataObserver,
    DownloaderOrderDataObserver, DownloaderOrderIdObserver,
    DownloaderRealTimeBarObserver)
from pytrader.libs.clients.broker.observers.main import MainOrderIdObserver
from pytrader.libs.clients.broker.observers.strategy import (
    StrategyMarketDataObserver, StrategyOrderDataObserver,
    StrategyRealTimeBarObserver)
