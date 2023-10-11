"""!
@package pytrader.libs.clients.broker.ibkr.tws.errors

Provides the client for Interactive Brokers TWSAPI.

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

@file pytrader/libs/clients/broker/ibkr/tws/errors.py

Provides the client for Interactive Brokers TWSAPI.

This is the only file to not use snake_case for functions or variables.  This is to match TWSAPI
abstract function names, and their variables.
"""
import datetime
import time

from ibapi.client import EClient
from ibapi.wrapper import EWrapper

from pytrader.libs.clients.broker.baseclient import BaseBroker
from pytrader.libs.system import logging
from pytrader.libs.utilities.exceptions import BrokerNotAvailable

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## Instance of Logging class
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class TwsErrors(EWrapper, EClient, BaseBroker):
    """!
    Class for handling Errors received by TWSAPI.

    Error Code Definitions are available at:
    https://interactivebrokers.github.io/tws-api/message_codes.html
    """
    __critical_codes = [1300]
    __error_codes = [
        100, 102, 103, 104, 105, 106, 107, 109, 110, 111, 113, 116, 117, 118, 119, 120, 121, 122,
        123, 124, 125, 126, 129, 131, 132, 162, 200, 320, 321, 502, 503, 504, 1101, 2100, 2101,
        2102, 2103, 2168, 2169, 10038, 10147
    ]
    __warning_codes = [101, 501, 1100, 2105, 2107, 2108, 2109, 2110, 2137]
    __info_codes = [1102]
    __debug_codes = [2104, 2106, 2158]
    request_commands = {}

    def __init__(self) -> None:
        """!
        Initialize the IbkrClient class

        @return None
        """
        EWrapper.__init__(self)
        EClient.__init__(self, self)
        BaseBroker.__init__(self)

    def add_command(self, req_id: int, command: str) -> None:
        """!
        Adds a command for tracking.

        @param req_id:
        @param command:

        @return None
        """
        self.request_commands[req_id] = command

    def process_error_code(self, req_id: int, error_code: int, error_string: str,
                           advanced_order_rejection: str) -> None:
        """!
        Processes Error messages received from TWSAPI.

        @param req_id:
        @param error_code:
        @param error_string:
        @param advanced_order_rejection:

        @return None
        """
        if error_code in self.__critical_codes:
            self._process_critical_code(req_id, error_code, error_string, advanced_order_rejection)
        elif error_code in self.__error_codes:
            self._process_error_code(req_id, error_code, error_string, advanced_order_rejection)
        elif error_code in self.__warning_codes:
            self._process_warning_code(req_id, error_code, error_string, advanced_order_rejection)
        elif error_code in self.__info_codes:
            self._process_info_code(req_id, error_code, error_string, advanced_order_rejection)
        elif error_code in self.__debug_codes:
            self._process_debug_code(req_id, error_code, error_string, advanced_order_rejection)
        else:
            logger.error("Error Code Level has not been identified")
            self._process_error_code(req_id, error_code, error_string, advanced_order_rejection)

    def remove_command(self, req_id: int) -> None:
        """!
        Removes a command from the tracker.

        @param req_id:

        @return None
        """
        self.request_commands.pop(req_id, None)

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _process_critical_code(self, req_id: int, error_code, error_string,
                               advanced_order_rejection):
        if advanced_order_rejection:
            logger.critical("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                            error_code, error_string, advanced_order_rejection)
        else:
            logger.critical("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_error_code(self, req_id: int, error_code, error_string, advanced_order_rejection):
        if advanced_order_rejection:
            logger.error("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                         error_code, error_string, advanced_order_rejection)
        else:
            logger.error("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

        match error_code:
            case 162:
                self._process_code_162(req_id, error_string)
            case 200:
                self._process_code_200(req_id, error_string)
            case 103 | 10147:
                msg = {"order_status": {req_id: {"status": "TWS_CLOSED"}}}
                logger.debug("Message: %s", msg)
            case 502:
                raise BrokerNotAvailable(error_string)
            case _:
                pass

    def _process_warning_code(self, req_id: int, error_code, error_string,
                              advanced_order_rejection):
        if advanced_order_rejection:
            logger.warning("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                           error_code, error_string, advanced_order_rejection)
        else:
            logger.warning("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_info_code(self, req_id: int, error_code, error_string, advanced_order_rejection):
        if advanced_order_rejection:
            logger.info("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                        error_code, error_string, advanced_order_rejection)
        else:
            logger.info("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_debug_code(self, req_id: int, error_code, error_string, advanced_order_rejection):
        if advanced_order_rejection:
            logger.debug("ReqID# %s, Code: %s (%s), Advanced Order Rejection: %s", req_id,
                         error_code, error_string, advanced_order_rejection)
        else:
            logger.debug("ReqID# %s, Code: %s (%s)", req_id, error_code, error_string)

    def _process_code_162(self, req_id: int, error_string: str) -> None:
        """!
        Error Code 162: Historical market data Service error message.

        @param req_id:
        @param error_string:

        @return None
        """
        match self.request_commands[req_id]:
            case "history_begin":
                self._process_code_162_history_begin(req_id, error_string)
            case _:
                logger.error("Historical Market Data Service Error for Command '%s' not configured",
                             self.request_commands[req_id])

    def _process_code_200(self, req_id: int, error_string: str) -> None:
        """!
        Error Code 200:

        Means either:
        - No security definition has been found for the request.
        - The contract description specified for <Symbol> is ambiguous

        @param req_id:
        @param error_string:

        @return None
        """
        if self.request_commands[req_id] == "contract_details":
            self.remove_command(req_id)

            if error_string == "No security definition has been found for the request":
                self.contract_subjects.set_contract_details(req_id, "NonExistant")
            else:
                self.contract_subjects.set_contract_details(req_id, "Error")

        logger.debug9("Error String: %s", error_string)

    def _process_code_162_history_begin(self, req_id: int, error_string: str) -> None:
        self.remove_command(req_id)
        match error_string:
            case "Historical Market Data Service error message:No head time stamp":
                self.cancelHeadTimeStamp(req_id)
                self.contract_history_begin_subjects.set_history_begin_date(req_id, "NoHistory")
            case "Historical Market Data Service error message:Request Timed Out":
                self.cancelHeadTimeStamp(req_id)
                self.contract_history_begin_subjects.set_history_begin_date(req_id, "NoHistory")
            case _:
                self.cancelHeadTimeStamp(req_id)
                self.contract_history_begin_subjects.set_history_begin_date(req_id, "Error")
                now = datetime.datetime.today()
                logger.debug("Paused for 10 min at %s", now)
                time.sleep(600)
