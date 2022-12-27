/**************************************************************************************************
 *
 * @file trader.cpp
 *
 * This file is part of trader.
 *
 * @author G Derber
 * @version HEAD
 * @date 2022
 * @author G Derber <gd.github@radiantendeavors.com>
 *
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

// TWS API Specific Headers

// Local Headers
#include "version/version.hpp"
#include "brokerclient/brokerclient.hpp"

/**************************************************************************************************
 *
 * main
 *
 * @param argc Provides number of arguments.
 * @param argv Provides the actual arguments.
 *
 **************************************************************************************************/
int main(int argc, char** argv) {

  // Connect to TWS / IB Gateway
  BrokerClient broker_client("127.0.0.1", 7497, 0);

  // Request the current time
  broker_client.reqCurrentTime();

  // Sleep while the message is received
  std::this_thread::sleep_for(std::chrono::seconds(1));

  // Read the message
  broker_client.signal.waitForSignal();
  broker_client.reader -> processMsgs();

  // Disconnect
  broker_client.eDisconnect();

  return 0;
}
