class TwsBars():

    def __init__(self):
        ## Bar Duration
        self.duration = ""

    def retrieve_bar_history(self, contract: contract.Contract, bar_size: str):
        """!
        Retrieves Bar History from TWS
        """
        logger.debug("Begin Function 'Retrieve Bar History'")
        bar_list = []
        if len(bar_list) == 0:
            if self.bar_size == "rtb":
                logger.error("Invalid Bar Size for History: %s", self.bar_size)
            else:
                logger.debug("Duration: %s", self.duration)
                self._set_duration()
                logger.debug("Duration: %s", self.duration)
                logger.debug("Retrieving %s Bar History for %s", self.bar_size,
                             self.contract.localSymbol)

                if self.brokerclient:
                    self._retreive_broker_bar_history()
                else:
                    raise NotImplementedError

        logger.debug("End Function")

    def request_real_time_bars(self, contract: contract.Contract):
        """!
        Requests real time bar information from TWS
        """
        req_id = self.brokerclient.req_real_time_bars(self.queue, contract)
        self.data_req_id[req_id] = contract.localSymbol

    def set_bar_sizes(self, bar_sizes: list):
        """!
        Sets bar sizes

        @param bar_sizes: Bar sizes to use

        @return None
        """
        self.bar_sizes = list(set(self.bar_sizes, bar_sizes))

    def _send_bars(self, data):
        """!
        Sends bar data to the strategies.
        """
        req_id = data["req_id"]
        ticker = self.data_tickers[req_id]
        bar_info = data["bar"]
        bar_type = bar_info["type"]
        bar = bar_info["bar"]
        message = {
            bar_type: {
                self.contract.localSymbol: {
                    self.bar_size: bars
                }
            }
        }
        self.data_queue.put(message)

    def _set_duration(self, bar_size):
        """!
        Defines bar duration.
        """
        logger.debug("Begin Function")
        if self.duration is None:
            logger.debug("Setting Duration for Bar Size: %s", bar_size)
            if bar_size == "1 month":
                self.duration = "2 Y"
            elif bar_size == "1 week":
                self.duration = "1 Y"
            elif bar_size == "1 day":
                self.duration = "1 Y"
            elif bar_size == "1 hour":
                self.duration = "7 W"
            elif bar_size == "30 mins":
                self.duration = "4 W"
            elif bar_size == "15 mins":
                self.duration = "10 D"
            elif bar_size == "5 mins":
                self.duration = "4 D"
            elif bar_size == "1 min":
                self.duration = "2 D"
            logger.debug("Duration Set to %s", self.duration)
        logger.debug("End Function")

    def _retreive_broker_bar_history(self):
        logger.debug("Begin Function")

        logger.debug("Duration: %s", self.duration)
        if self.duration == "all":
            logger.debug("Getting all history")
        else:
            req_id = self.brokerclient.req_historical_data(
                self.contract, self.bar_size, duration_str=self.duration)

        bar_list = self.brokerclient.get_data(req_id)

        # self.brokerclient.cancel_historical_data(req_id)
        logger.debug("Bar List: %s", bar_list)

        for bar in bar_list:
            logger.debug("Bar: %s", bar)
            bar_date = bar.date
            bar_open = bar.open
            bar_high = bar.high
            bar_low = bar.low
            bar_close = bar.close
            bar_volume = float(bar.volume)
            #bar_wap = bar.wap
            bar_count = bar.barCount

            self.bar_list.append([
                bar_date, bar_open, bar_high, bar_low, bar_close, bar_volume,
                bar_count
            ])

        self.send_bars("bars", self.bar_list)

        logger.debug("End Function")

    def _request_bar_history(self):
        for local_symbol in self.contracts.keys():
            for size in self.bars[local_symbol].keys():
                # TODO: Check if this should be an 'and'
                if size != "rtb" and size in self.bars[local_symbol].keys():
                    self.bars[local_symbol][size].retrieve_bar_history()

    def _request_real_time_bars(self):
        for local_symbol in self.contracts.keys():
            logger.debug("Bar Tickers: %s", self.bars.keys())

            if local_symbol not in self.bars.keys():
                self.bars[local_symbol] = {}

            if "rtb" not in self.bars[local_symbol].keys():
                logger.debug("Requesting Real Time Bars for Ticker: %s",
                             local_symbol)
                self.bars[local_symbol]["rtb"] = bars.BrokerBars(
                    contract=self.contracts[local_symbol],
                    bar_size="rtb",
                    brokerclient=self.brokerclient,
                    data_queue=self.data_queue)
                self.bars[local_symbol]["rtb"].request_real_time_bars()

                self.rtb_thread[local_symbol] = threading.Thread(
                    target=self.bars[local_symbol]["rtb"].run, daemon=True)
                self.rtb_thread[local_symbol].start()

    def _send_real_time_bar(self, data):
        """!
        Sends real time bar data to the strategies.
        """
        req_id = data["req_id"]
        ticker = self.data_tickers[req_id]
        bar = data["bar"]
        message = {"real_time_bar": {ticker: bar}}
        self.data_queue.put(message)
