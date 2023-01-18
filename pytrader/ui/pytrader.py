"""!@package pytrader.ui.pytrader

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

@file ui/pytrader.py

"""
# System libraries
import multiprocessing
import random
import sys
import time

# 3rd Party libraries

# System Library Overrides
from pytrader.libs.system import argparse
from pytrader.libs.system import logging

# Application Libraries
from pytrader import DEBUG
from pytrader.libs.clients import broker
from pytrader.libs import utilities
from pytrader.libs.utilities import config
from pytrader import strategies

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
## The Base logger
logger = logging.getLogger(__name__)

## Client ID Used for the Interactive Brokers API
client_id = 1

## The python formatted location of the strategies
import_path = "pytrader.strategies."


# ==================================================================================================
#
# Functions
#
# ==================================================================================================
def fix_bar_size_format(bar_sizes):
    """!
    Converts the input format from args.bar_sizes to the format required by Interactive Brokers

    @param bar_sizes - The bar sizes requested using the command line arguments.

    @return fixed_bar_sizes - A list of bar sizes in the format required by Interactive Brokers
    """
    bar_size_map = {
        "1secs": "1 secs",
        "5secs": "5 secs",
        "10secs": "10 secs",
        "15secs": "15 secs",
        "30secs": "30 secs",
        "1min": "1 min",
        "2mins": "2 mins",
        "3mins": "3 mins",
        "5mins": "5 mins",
        "10mins": "10 mins",
        "15mins": "15 mins",
        "20mins": "20 mins",
        "30mins": "30 mins",
        "1hour": "1 hour",
        "2hours": "2 hours",
        "3hours": "3 hours",
        "4hours": "4 hours",
        "8hours": "8 hours",
        "1day": "1 day",
        "1week": "1 week",
        "1month": "1 month"
    }
    fixed_bar_sizes = []
    for item in bar_sizes:
        fixed_bar_sizes.append(bar_size_map[item])

    return fixed_bar_sizes


def broker_address(args, conf):
    """!
    Returns the address to be used by the broker.

    @param args - Provides the arguments from the command line
    @param conf - Provides the configuration information from config files.

    @return address - The brokeclient's address
    """
    if args.address:
        return args.address
    else:
        return conf.brokerclient_address


def broker_port(args, conf):
    """!
    Returns the port to be used by the broker.

    @param args - Provides the arguments from the command line
    @param conf - Provides the configuration information from config files.

    @return port - The brokeclient's port
    """
    if args.port:
        return args.port
    else:
        return conf.brokerclient_port


def process_arguments(args, conf):
    """!
    Processes the arguments received from the command line.

    @param args - Provides the arguments from the command line.
    @param conf - Provides the configuration from config files.

    @return None
    """
    # Create the client and connect to TWS or IB Gateway
    logger.debug10("Begin Function")

    address = broker_address(args, conf)
    port = broker_port(args, conf)

    strategy_list = args.strategies

    if args.bar_sizes:
        bar_sizes = fix_bar_size_format(args.bar_sizes)
    else:
        bar_sizes = None

    logger.debug("Bar Sizes: %s", bar_sizes)

    if args.securities:
        securities = args.securities
    else:
        securities = None

    processed_args = (address, port, strategy_list, bar_sizes, securities)
    logger.debug10("End Function")
    return processed_args


# generate work
def producer(queue):
    print('Producer: Running', flush=True)
    # generate work
    for i in range(10):
        # generate a value
        value = random.random()
        # block
        time.sleep(value)
        # add to the queue
        queue.put(value)
    # all done
    queue.put(None)
    print('Producer: Done', flush=True)


# consume work
def consumer(queue):
    print('Consumer: Running', flush=True)
    # consume work
    while True:
        # get a unit of work
        item = queue.get()
        # check for stop
        if item is None:
            break
        # report
        print(f'>got {item}', flush=True)
    # all done
    print('Consumer: Done', flush=True)


def start_brokerclient_process(brokerclient, queue, address, port, client_id):
    brokerclient.connect(address, port, client_id)
    brokerclient.set_process_queue(queue)

    #broker_process = multiprocessing.Process(target=brokerclient.run, args=())
    broker_process = multiprocessing.Process(target=broker.run_loop,
                                             args=(brokerclient, ))

    #producer_ = multiprocessing.Process(target=producer, args=(queue, ))
    #producer_.start()
    broker_process.start()
    next_order_id = brokerclient.get_next_order_id()
    logger.debug("Received next order id: %s", next_order_id)
    return broker_process


def start_strategy_process(strategy, brokerclient, queue, securities_list,
                           bar_sizes):

    strategy_process = multiprocessing.Process(target=consumer, args=(queue, ))
    strategy_process.start()

    return strategy_process
    # strategy(brokerclient,
    #          securities_list=securities_list,
    #          bar_sizes=bar_sizes)


def run_processes(processed_args):
    address = processed_args[0]
    port = processed_args[1]
    strategy_list = processed_args[2]
    bar_sizes = processed_args[3]
    securities = processed_args[4]

    queue = multiprocessing.Queue()
    brokerclient = broker.brokerclient("ibkr")

    strategy_process = start_strategy_process("A", brokerclient, queue,
                                              securities, bar_sizes)
    # strategy_processes = {}
    # for i in strategy_list:
    #     strategy = utilities.get_plugin_function(program=i,
    #                                              cmd='run',
    #                                              import_path=import_path)
    #     strategy_processes[i] = start_strategy_process(strategy, brokerclient,
    #                                                    queue, securities_list,
    #                                                    bar_sizes)

    broker_process = start_brokerclient_process(brokerclient, queue, address,
                                                port, client_id)

    broker_process.join()
    strategy_process.join()
    #brokerclient.disconnect()

    logger.debug10("End Function")
    return None


def init(args):
    """! Initializates the program.

    @param args
    Provides the arguments from the command line.

    @return 0
    """
    logger.debug("Entered real main")

    epilog_text = """
    See man pytrader for more information.\n
    \n
    Report bugs to ...
    """

    parser = argparse.ArgParser(description="Automated trading system",
                                epilog=epilog_text)

    parser.add_version_option()
    parser.add_ibapi_connection_options()
    parser.add_logging_option()

    parser.add_argument("-b",
                        "--bar-sizes",
                        choices=[
                            "1secs", "5secs", "10secs", "15secs", "30secs",
                            "1min", "2mins", "3mins", "5mins", "10mins",
                            "15mins", "20mins", "30mins", "1hour", "2hours",
                            "3hours", "4hours", "8hours", "1day", "1week",
                            "1month"
                        ],
                        nargs="+",
                        help="Bar Size")
    parser.add_argument("-s",
                        "--strategies",
                        nargs="+",
                        required=True,
                        help="One or more strategies to run.")
    parser.add_argument("-S",
                        "--securities",
                        nargs="?",
                        help="""
        Optionally one or more securities to use for strategy.  If not
        set, the strategies default securities list will be used.
        """)

    parser.set_defaults(debug=False, verbosity=0, loglevel='INFO')

    args = parser.parse_args()

    conf = config.Config()
    conf.read_config()
    conf.set_loglevel(args)

    logger.debug2('Configuration set')
    logger.debug3('Configuration Settings: ' + str(conf))
    logger.debug4('Arguments: ' + str(args))

    # 'application' code
    if DEBUG is False:
        logger.debug("Attempting to start client")
        try:
            processed_args = process_arguments(args, conf)
            run_processes(processed_args)
        except Exception as msg:
            parser.print_help()
            logger.error('No command was given')
            logger.critical(msg)
    else:
        logger.debug("Starting Client")
        processed_args = process_arguments(args, conf)
        run_processes(processed_args)

    logger.debug("End real main")
    return 0


def main(args=None):
    """! The main program.

    @param args - The input from the command line.
    @return 0
    """
    logger.debug("Begin Application")

    if DEBUG is False:
        try:
            init(args)
        except Exception as msg:
            logger.critical(msg)
    else:
        init(args)

    logger.debug("End Application")
    return 0


if __name__ == "__main__":
    sys.exit(main())
