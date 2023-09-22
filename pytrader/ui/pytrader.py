"""!@package pytrader.ui.pytrader

The main user interface for the trading program.

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

@file pytrader/ui/pytrader.py

"""
# System libraries
import sys

# Application Libraries
from pytrader import CLIENT_ID
from pytrader.libs.applications import trader
# System Library Overrides
from pytrader.libs.system import argparse, logging
from pytrader.libs.utilities import config

# 3rd Party libraries

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base logger
logger = logging.getLogger(__name__)


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class PyTrader():
    """!
    The main program class.
    """
    process_manager = None

    def __init__(self) -> None:
        """!
        Initialize the main program.

        @param args: Arguments received from the command line.

        @return None
        """
        epilog_text = """
        See man pytrader for more information.\n
        \n
        Report bugs to ...
        """
        self.conf = config.Config()
        self.parser = argparse.ArgParser(description="Automated trading system", epilog=epilog_text)
        self.parser.add_version_option()
        self._add_broker_options()
        self._add_strategy_options()
        self._add_download_options()

        self.parser.add_logging_option()
        self.parser.set_defaults(debug=False, verbosity=0, loglevel='INFO')
        self.args = self.parser.parse_args()

    def config(self) -> None:
        """!
        Reads the configuration file and sets the log levels.

        @return None
        """
        self.conf.read_config()
        self.conf.set_loglevel(self.args)
        logger.debug2('Configuration set')
        logger.debug8('Configuration Settings: ' + str(self.conf))
        logger.debug9('Arguments: ' + str(self.args))

    def start(self) -> int:
        """!
        Run Program

        @return int: Program Return Code
        """
        logger.debug("Starting Process Manager")
        try:
            self._start_process_manager()
            return 0
        except KeyboardInterrupt as msg:
            logger.critical("Keyboard Interrupt Detected! Shutting Down. %s", msg)
            self._stop()
            return 130
        # We want a catchall exception
        except Exception as msg:
            logger.critical(msg)
            self._stop()
            return 1

    # ==============================================================================================
    #
    # Private Functions
    #
    # ==============================================================================================
    def _add_broker_options(self) -> None:
        """!
        Adds options related to the broker.

        @return None
        """
        broker_list = ["twsapi"]
        help_str = (f"Brokers (Default: {broker_list})\n"
                    f"If 'backtest' is chosen, all other brokers will be ignored.")
        broker = self.parser.add_argument_group("broker")
        broker.add_argument("-b",
                            "--brokers",
                            nargs="*",
                            choices=broker_list,
                            default=[broker_list[0]],
                            help=help_str)
        default_address = "127.0.0.1"
        broker.add_argument("-a",
                            "--address",
                            default=default_address,
                            help=f"The Broker Address (Default: {default_address})")
        broker.add_argument("-c",
                            "--client-id",
                            default=CLIENT_ID,
                            help=f"Broker Client Id (Default: {CLIENT_ID})")
        broker.add_argument("-p",
                            "--ports",
                            nargs="*",
                            metavar="PORT",
                            help="List of ports available to connect to.")
        help_str = "Disable Broker Initialization, NOTE: This severely limits capabilities"
        broker.add_argument("-d",
                            "--disable-broker",
                            action="store_false",
                            default=True,
                            help=help_str)

    def _add_download_options(self) -> None:
        download_options = self.parser.add_argument_group("Data Downloader Options")
        download_options.add_argument("-t",
                                      "--tickers",
                                      nargs="*",
                                      default=[],
                                      help="Tickers for downloading data.")

        download_options.add_argument("-o",
                                      "--enable-options",
                                      action="store_true",
                                      default=False,
                                      help="Enable downloading Options data.")
        download_options.add_argument(
            "-A",
            "--asset_classes",
            nargs="*",
            default=["STK", "ETF", "BOND", "BILL", "IND", "FUTGRP", "OPTGRP", "WAR"],
            choices=["STK", "ETF", "BOND", "BILL", "IND", "FUTGRP", "OPTGRP", "WAR"],
            help="Asset Classes for stock universe.")

        # Currently, the default is "USD" because that is all I have access to.
        # While other currencies should 'theoretically' work, it has not been tested.
        #
        # The same goes for other regions besides 'north_america'
        currency_choices = [
            "AUD", "CAD", "CHF", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "ILS", "INR", "JPY",
            "KRW", "MXN", "NOK", "NZD", "PLN", "SEK", "SGD", "TWD", "USD", "ZAR"
        ]
        download_options.add_argument(
            "-C",
            "--currencies",
            nargs="*",
            default=["USD"],
            choices=currency_choices,
            help="Allowed currencies for securities. (default is ['USD'])")
        download_options.add_argument(
            "-r",
            "--regions",
            nargs="*",
            default=["north_america"],
            choices=["north_america", "europe", "asia", "global"],
            help="Regions to download exchange listings for (default is ['north_america'])")

        # Not sure if this configuration is really necessary.  I doubt it'll ever export to anything
        # other than CSV.  It always exports to the database.  It may export to CSV.  CSV format is
        # helpful for debugging and working out how to manage duplicates.
        download_options.add_argument("-x",
                                      "--export",
                                      nargs="*",
                                      default=[],
                                      choices=["csv"],
                                      help="Additional options to save stock universe.")

    def _add_strategy_options(self) -> None:
        strategy_options = self.parser.add_argument_group("Strategy Options")
        strategy_options.add_argument(
            "-s",
            "--strategies",
            nargs="*",
            default=[],
            help="Strategies to run.  If not specified no strategies will run.")

    def _start_process_manager(self) -> None:
        """!
        Starts the Overall Process Manager.

        @param args: The arguments received from the command line.

        @return None
        """
        self.process_manager = trader.ProcessManager(self.args)
        self.process_manager.start(self.args.disable_broker)

    def _stop(self) -> None:
        """!
        Stops the Process Manager

        @return None
        """
        self.process_manager.stop()


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def main() -> int:
    """! The main program.

    @param args - The input from the command line.
    @return 0
    """
    pytrader = PyTrader()
    pytrader.config()
    return pytrader.start()


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == "__main__":
    sys.exit(main())
