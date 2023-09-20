/**************************************************************************************************
 *
 * @package trader
 *
 * Algorithmic Trading Program
 *
 * @file trader.cpp
 *
 * This file is part of trader.
 *
 * @author G S Derber
 * @date 2022-2023
 * @copyright GNU Affero General Public License
 *
 * This program is free software; you can redistribute and/or modify it under the terms of the
 * GNU Affero General Public License v3.0 as published by the Free Software Foundation
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
 * the GNU Affero General Public License for more details.
 *
 **************************************************************************************************/
// C sytem headers


// C++ standard library headers
#include <iostream>

// 3rd Party Headers
#include "argparse/include/argparse/argparse.hpp"

// Local Headers

#include "clients/broker/ibkr/tws/ibkrclient.hpp"
#include "version/version.hpp"

/**************************************************************************************************
 *
 * main
 *
 * @param argc: Provides number of arguments.
 * @param argv: Provides the actual arguments.
 *
 * @return int: Program Exit Code
 *
 **************************************************************************************************/
int main(int argc, char** argv) {
  std::string version = TO_LITERAL(trader_VERSION_MAJOR.trader_VERSION_MINOR.trader_VERSION_PATCH);
  argparse::ArgumentParser program("trader", version);

  program.add_argument("-s", "--strategies").nargs(argparse::nargs_pattern::any).help("List of Strategies to run.");

  try {
    program.parse_args(argc, argv);
  }
  catch (const std::runtime_error& err) {
    std::cerr << err.what() << std::endl;
    std::cerr << program;
    return 1;
  }

  // Connect to TWS or IB Gateway
  TwsApiClient twsapi_client("127.0.0.1", 7497, 0);

  // Request the current time
  twsapi_client.reqCurrentTime();

  // Sleep while the message is received
  std::this_thread::sleep_for(std::chrono::seconds(1));

  // Read the message
  twsapi_client.signal.waitForSignal();
  twsapi_client.reader->processMsgs();

  // Disconnect
  twsapi_client.eDisconnect();
  return 0;
}
