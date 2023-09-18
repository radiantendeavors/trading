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
from pytrader import DEBUG
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
        self.parser.add_broker_options()

        strategy_options = self.parser.add_argument_group("Strategy Options")
        strategy_options.add_argument(
            "-s",
            "--strategies",
            nargs="*",
            default=[],
            help="Strategies to run.  If not specified no strategies will run.")

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

    def start_process_manager(self) -> None:
        """!
        Starts the Overall Process Manager.

        @param args: The arguments received from the command line.

        @return None
        """
        process_manager = trader.ProcessManager(self.args)

        if self.args.disable_broker:
            process_manager.config_brokers()

        process_manager.run()

    def run(self) -> int:
        """!
        The main function.

        @return int:
        """
        # 'application' code
        if DEBUG:
            self.start_process_manager()
            return 0

        logger.debug8("Attempting to start client")
        try:
            self.start_process_manager()
            return 0
        # We want a catchall exception
        except Exception as msg:
            logger.critical(msg)
            return 1


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
    return pytrader.run()


# ==================================================================================================
#
#
#
# ==================================================================================================
if __name__ == "__main__":
    sys.exit(main())
