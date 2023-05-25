"""!
@package pytrader.libs.applications.broker.ibkrtws

The main user interface for the trading program.

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

@file pytrader/libs/applications/broker/contracts/ibkrtws.py
"""


class TWSContracts():

    def set_contracts(self, contracts: dict):
        logger.debug("Set Contracts: Begin Function")
        self.tickers = list(set(self.tickers, contracts.keys()))

        for ticker, contract_ in contracts.items():
            req_id = self.brokerclient.req_contract_details(contract_)
            self.data_tickers[req_id] = ticker

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _add_contract(self, data):
        """!
        Adds a contract to the contract dictionary.
        """
        req_id = data["req_id"]
        ticker = self.data_tickers[req_id]
        contract_ = data["contract_details"].contract
        self.contracts[ticker](contract_)

    def _create_contract(self,
                         ticker,
                         sec_type: str = "STK",
                         exchange: str = "SMART",
                         currency: str = "USD",
                         strike: float = 0.0,
                         right: str = ""):
        """!
        Creates a contract
        """
        contract_ = contract.Contract()
        contract_.symbol = ticker
        contract_.secType = "STK"
        contract_.exchange = "SMART"
        contract_.currency = "USD"

        if strike > 0.0:
            contract_.strike = strike

        if right != "":
            contract_.right = right
        self.contracts[ticker] = self._set_contract_details(contract_)

    def _create_contracts(self, tickers):
        """!
        Takes a list of tickers, and creates contracts for them.

        @param tickers: The list of tickers

        @return None
        """
        logger.debug("Begin Function")
        for item in tickers:
            if not self.contracts.get(item):
                logger.debug("Creating contract for %s", item)
                self._create_contract(item)
            self.bars[item] = {}
        logger.debug("End Function")

    def _request_option_details(self):
        for ticker, contract_ in self.contracts.items():
            req_id = self.brokerclient.req_sec_def_opt_params(contract_)
            option_details = self.brokerclient.get_data(req_id)

            message = {
                "option_details": {
                    "ticker": ticker,
                    "details": option_details
                }
            }
            logger.debug("Option Details: %s", message)
            self.data_queue.put(message)
