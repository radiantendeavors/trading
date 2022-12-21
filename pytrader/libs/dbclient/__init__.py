"""!
@package pytrader.libs.dbclient

Provides the database client

@author Geoff S. derber
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


@file __init__.py
"""
# System Libraries
import pymysql

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.utilities import config
from pytrader.libs.utilities import text

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
"""!
@var logger
The base logger.

@var colortext
Allows Color text on the console
"""
logger = logging.getLogger(__name__)
colortext = text.ConsoleText()


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class MySQLDatabase():
    """!Class MySQLDatabase

    """

    def __init__(self, *args, **kwargs):
        conf = config.Config()
        conf.read_config()

        self.host = conf.database_host
        self.user = conf.database_username
        self.password = conf.database_password

        try:
            with pymysql.connect(host=self.host,
                                 user=self.user,
                                 password=self.password) as mydb:
                print(mydb)
        except pymysql.Error as e:
            logger.error(e)

        self.mydb = mydb
        self.mycursor = self.mydb.cursor()

    def create_database(self):
        sql = "CREATE DATABASE IF NOT EXISTS " + conf.database_name
        logger.debug("Create Database SQL: ", sql)

        try:
            self.mycursor.execute(sql)
        except mysql.connector.Error as e:
            logger.error(e)

    def check_database_exists(self):
        sql = "SHOW DATABASES LIKE " + conf.database_name
        row = self.mycursor.execute(sql)
        logger.debug("Row: ", row)


# class Investments():

#     def __init__(self, *args, **kwargs):
#         self.tickers = []
#         if self.investments == "stocks":
#             stocks.init_sqlalchemy()
#         elif self.investments == "etf":
#             etfs.init_sqlalchemy()

#         return None

#     def download_list(self, *args, **kwargs):
#         headers = {
#             "User-Agent":
#             "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
#         }

#         url = "https://api.nasdaq.com/api/screener/"
#         url = url + self.investments
#         url = url + "?tableonly=true&limit=25&offset=0&download=true"
#         investments_url = requests.get(url, headers=headers, timeout=5)

#         json_data = investments_url.json()
#         table = json_data["data"]

#         if self.investments == "etf":
#             table = table["data"]

#         for table_row in table["rows"]:
#             if self.investments == "stocks":
#                 stock = stocks.StockInfo()
#                 stock.add_stock_info(ticker=table_row["symbol"])
#             elif self.investments == "etf":
#                 etf = etfs.EtfInfo()
#                 etf.add_etf_info(ticker=table_row["symbol"])

#             self.tickers.append(table_row["symbol"])

#         return self.tickers

#     def download_daily(self, *args, **kwargs):
#         midnight = int(
#             datetime.combine(datetime.today(), time.min).timestamp())

#         if "start" in kwargs:
#             start_date = kwargs["start"]
#         else:
#             start_date = midnight

#         if "period" in kwargs:
#             period = kwargs["period"]
#         else:
#             period = "1d"

#         for ticker in self.tickers:
#             ystock = YahooStock(ticker=ticker)
#             if self.investments == "stocks":
#                 security = stocks.StockDaily()
#             elif self.investments == "etf":
#                 security = etfs.EtfDaily()

#             yahoo_data = ystock.get_history(period=period, interval="1d")
#             try:
#                 if self.investments == "stocks":
#                     yahoo_data[
#                         "shares_outstanding"] = ystock.get_shares_outstanding(
#                         )
#                     security.add_stock_daily(ticker=ticker, yahoo=yahoo_data)
#                 elif self.investments == "etf":
#                     security.add_etf_daily(ticker=ticker, yahoo=yahoo_data)
#             except Exception as e:
#                 print("Error adding", ticker, ":", e)
#                 print("Yahoo Data:")
#                 print(yahoo_data)
#             if period == "max":
#                 timelib.sleep(random.randint(min_sleeptime, max_sleeptime))

#         return None

#     def get_option_chain(self, *args, **kwargs):
#         for ticker in self.tickers:
#             ystock = YahooStock(ticker=ticker)
#             ystock.get_option_chain()

#         return None

#     def get_ticker_info(self, *args, **kwargs):
#         for ticker in self.tickers:
#             ystock = YahooStock(ticker=ticker)
#             ystock.get_info()

#         return None

# class Stocks(Investments):

#     def __init__(self):
#         self.investments = "stocks"
#         super(Stocks, self).__init__()
#         return None

#     def get_ticker_list(self, *args, **kwargs):
#         tickers = []
#         investments = stocks.StockInfo()
#         self.tickers = investments.get_ticker_list()

#         if len(tickers) > 0:
#             return self.tickers
#         else:
#             return self.download_list()

# class Etfs(Investments):

#     def __init__(self):
#         self.investments = "etf"
#         super(Etfs, self).__init__()
#         return None

#     def get_ticker_list(self, *args, **kwargs):
#         tickers = []
#         investments = etfs.EtfInfo()
#         self.tickers = investments.get_ticker_list()

#         if len(tickers) > 0:
#             return self.tickers
#         else:
#             return self.download_list()

# class YahooStock():

#     def __init__(self, *args, **kwargs):
#         self.ticker = kwargs["ticker"]
#         self.stock = yfinance.Ticker(self.ticker)
#         return None

#     def get_info(self, *args, **kwargs):
#         print(self.stock.info)

#         # info = {
#         #     'zip': '95051',
#         #     'sector': 'Healthcare',
#         #     'fullTimeEmployees': 16400,
#         #     'longBusinessSummary':
#         #     "Agilent Technologies, Inc. provides application focused solutions to the life sciences, diagnostics, and applied chemical markets worldwide. The Life Sciences and Applied Markets segment offers liquid and gas chromatography systems and components; liquid and gas chromatography mass spectrometry systems; inductively coupled plasma mass and optical emission spectrometry instruments; atomic absorption instruments; microwave plasma-atomic emission spectrometry instruments; raman spectroscopy; cell analysis plate based assays; flow cytometer; real-time cell analyzer; cell imaging systems; microplate readers; laboratory software, information management, and analytics; laboratory automation and robotic systems; dissolution testing; vacuum pumps; and measurement technologies. The Diagnostics and Genomics segment provides arrays for DNA mutation detection, genotyping, gene copy number determination, identification of gene rearrangements, DNA methylation profiling, and gene expression profiling, as well as sequencing target enrichment, genetic data management, and interpretation support software; and equipment to produce synthesized oligonucleotide. It also offers immunohistochemistry, in situ hybridization, and hematoxylin and eosin staining and special staining; instruments, consumables, and software for quality control analysis of nucleic acid samples; and reagents for use in turbidimetry and flow cytometry, as well as develops pharmacodiagnostics. The Agilent CrossLab segment provides GC and LC columns, sample preparation products, custom chemistries, and laboratory instrument supplies; and startup, operational, training, compliance support, software as a service, asset management, and consultation services. The company markets its products through direct sales, distributors, resellers, manufacturer's representatives, and electronic commerce. It has collaboration agreement with SGS AXYS. The company was incorporated in 1999 and is headquartered in Santa Clara, California.",
#         #     'city': 'Santa Clara',
#         #     'phone': '800 227 9770',
#         #     'state': 'CA',
#         #     'country': 'United States',
#         #     'companyOfficers': [],
#         #     'website': 'http://www.agilent.com',
#         #     'maxAge': 1,
#         #     'address1': '5301 Stevens Creek Boulevard',
#         #     'fax': '866 497 1134',
#         #     'industry': 'Diagnostics & Research',
#         #     'ebitdaMargins': 0.28688,
#         #     'profitMargins': 0.16118999,
#         #     'grossMargins': 0.53647,
#         #     'operatingCashflow': 1420999936,
#         #     'revenueGrowth': 0.258,
#         #     'operatingMargins': 0.23592,
#         #     'ebitda': 1762000000,
#         #     'targetLowPrice': 158,
#         #     'recommendationKey': 'buy',
#         #     'grossProfits': 2837000000,
#         #     'freeCashflow': 1179250048,
#         #     'targetMedianPrice': 170,
#         #     'currentPrice': 160,
#         #     'earningsGrowth': 0.344,
#         #     'currentRatio': 2.107,
#         #     'returnOnAssets': 0.0904,
#         #     'numberOfAnalystOpinions': 17,
#         #     'targetMeanPrice': 173.35,
#         #     'debtToEquity': 57.784,
#         #     'returnOnEquity': 0.19945998,
#         #     'targetHighPrice': 195,
#         #     'totalCash': 1428000000,
#         #     'totalDebt': 2857999872,
#         #     'totalRevenue': 6142000128,
#         #     'totalCashPerShare': 4.713,
#         #     'financialCurrency': 'USD',
#         #     'revenuePerShare': 20.072,
#         #     'quickRatio': 1.479,
#         #     'recommendationMean': 2,
#         #     'exchange': 'NYQ',
#         #     'shortName': 'Agilent Technologies, Inc.',
#         #     'longName': 'Agilent Technologies, Inc.',
#         #     'exchangeTimezoneName': 'America/New_York',
#         #     'exchangeTimezoneShortName': 'EDT',
#         #     'isEsgPopulated': True,
#         #     'gmtOffSetMilliseconds': '-14400000',
#         #     'underlyingSymbol': None,
#         #     'quoteType': 'EQUITY',
#         #     'symbol': 'A',
#         #     'underlyingExchangeSymbol': None,
#         #     'headSymbol': None,
#         #     'messageBoardId': 'finmb_154924',
#         #     'uuid': '7fc56270-e7a7-3fa8-9a59-35b72eacbe29',
#         #     'market': 'us_market',
#         #     'annualHoldingsTurnover': None,
#         #     'enterpriseToRevenue': 8.647,
#         #     'beta3Year': None,
#         #     'enterpriseToEbitda': 30.143,
#         #     '52WeekChange': None,
#         #     'morningStarRiskRating': None,
#         #     'forwardEps': 4.36,
#         #     'revenueQuarterlyGrowth': None,
#         #     'sharesOutstanding': 304697984,
#         #     'fundInceptionDate': None,
#         #     'annualReportExpenseRatio': None,
#         #     'totalAssets': None,
#         #     'bookValue': 15.756,
#         #     'sharesShort': 3890515,
#         #     'sharesPercentSharesOut': 0.0128,
#         #     'fundFamily': None,
#         #     'lastFiscalYearEnd': 1604102400,
#         #     'heldPercentInstitutions': 0.90196997,
#         #     'netIncomeToCommon': 990000000,
#         #     'trailingEps': 2.597,
#         #     'lastDividendValue': None,
#         #     'SandP52WeekChange': None,
#         #     'priceToBook': 10.154861,
#         #     'heldPercentInsiders': 0.00265,
#         #     'nextFiscalYearEnd': 1667174400,
#         #     'yield': None,
#         #     'mostRecentQuarter': 1627689600,
#         #     'shortRatio': 2.23,
#         #     'sharesShortPreviousMonthDate': 1626307200,
#         #     'floatShares': 302060700,
#         #     'beta': 0.993006,
#         #     'enterpriseValue': 53112709120,
#         #     'priceHint': 2,
#         #     'threeYearAverageReturn': None,
#         #     'lastSplitDate': 1414972800,
#         #     'lastSplitFactor': '1398:1000',
#         #     'legalType': None,
#         #     'morningStarOverallRating': None,
#         #     'earningsQuarterlyGrowth': 0.327,
#         #     'priceToSalesTrailing12Months': 7.937427,
#         #     'dateShortInterest': 1628812800,
#         #     'pegRatio': 0.77,
#         #     'ytdReturn': None,
#         #     'forwardPE': 36.697247,
#         #     'lastCapGain': None,
#         #     'shortPercentOfFloat': 0.0128999995,
#         #     'sharesShortPriorMonth': 2571122,
#         #     'category': None,
#         #     'fiveYearAverageReturn': None,
#         #     'previousClose': 159.9,
#         #     'regularMarketOpen': 161.39,
#         #     'twoHundredDayAverage': 146.62312,
#         #     'trailingAnnualDividendYield': 0.0045903693,
#         #     'payoutRatio': 0.2374,
#         #     'volume24Hr': None,
#         #     'regularMarketDayHigh': 161.805,
#         #     'navPrice': None,
#         #     'averageDailyVolume10Day': 1471057,
#         #     'regularMarketPreviousClose': 159.9,
#         #     'fiftyDayAverage': 170.32942,
#         #     'trailingAnnualDividendRate': 0.734,
#         #     'open': 161.39,
#         #     'averageVolume10days': 1471057,
#         #     'expireDate': None,
#         #     'algorithm': None,
#         #     'dividendRate': 0.78,
#         #     'exDividendDate': 1625184000,
#         #     'circulatingSupply': None,
#         #     'startDate': None,
#         #     'regularMarketDayLow': 159.83,
#         #     'currency': 'USD',
#         #     'trailingPE': 61.60955,
#         #     'regularMarketVolume': 1205816,
#         #     'lastMarket': None,
#         #     'maxSupply': None,
#         #     'openInterest': None,
#         #     'marketCap': 48751677440,
#         #     'volumeAllCurrencies': None,
#         #     'strikePrice': None,
#         #     'averageVolume': 1642534,
#         #     'dayLow': 159.83,
#         #     'ask': 160.08,
#         #     'askSize': 1100,
#         #     'volume': 1205816,
#         #     'fiftyTwoWeekHigh': 179.57,
#         #     'fromCurrency': None,
#         #     'fiveYearAvgDividendYield': 0.81,
#         #     'fiftyTwoWeekLow': 99.81,
#         #     'bid': 159.93,
#         #     'tradeable': False,
#         #     'dividendYield': 0.0045,
#         #     'bidSize': 1000,
#         #     'dayHigh': 161.805,
#         #     'regularMarketPrice': 160,
#         #     'logo_url': 'https://logo.clearbit.com/agilent.com'
#         #}
#         return None

#     def get_history(self, *args, **kwargs):
#         if "period" in kwargs:
#             period = kwargs["period"]
#         else:
#             period = "1d"

#         if "interval" in kwargs:
#             interval = kwargs["interval"]
#         elif period == "1d":
#             interval = "1m"
#         else:
#             interval = "1d"

#         history_data = self.stock.history(period=period,
#                                           interval=interval,
#                                           prepost=True)

#         # download_data = self.stock.download(period=period,
#         #                                    interval=interval,
#         #                                    prepost=True)

#         return history_data

#     def get_option_chain(self, *args, **kwargs):
#         expiry_dates = self.stock.options

#         for item in expiry_dates:
#             option_chain = self.stock.option_chain(item)
#             print(option_chain)
#         return None

#     def get_shares_outstanding(self, *args, **kwargs):
#         return self.stock.info["sharesOutstanding"]

#     def print_history(self, *args, **kwargs):
#         if "period" in kwargs:
#             period = kwargs["period"]
#         else:
#             period = "1d"

#         for item in self.stock.download(period=period):
#             print(item)

#         return None

# # class RedditStock():
# #     def __init__(self, *args, **kwargs):
# #         self.ticker = kwargs["ticker"]
# #         config = investing.lib.util.config.InvestingConfig()
# #         config.read_config()
# #         self.user_agent = conf.get_reddit_user_agent()
# #         self.client_id = conf.get_reddit_client_id()
# #         self.client_secret = conf.get_reddit_client_secret()
# #         self.username = conf.get_reddit_username()
# #         self.password = conf.get_reddit_password()
# #         self.subreddits = conf.get_reddit_subreddits()

# #         #reddit =

# #     def get_reddit_sentiment(self, *args, **kwargs):
# #         reddit = praw.Reddit(user_agent=self.user_agent,
# #                              client_id=self.client_id,
# #                              client_secret=self.client_secret,
# #                              username=self.username,
# #                              password=self.password)

# # def submissions_pushshift_praw(subreddit,
# #                                start=None,
# #                                end=None,
# #                                limit=100,
# #                                extra_query=""):
# #     """
# #     A simple function that returns a list of PRAW submission objects during a particular period from a defined sub.
# #     This function serves as a replacement for the now deprecated PRAW `submissions()` method.

# #     :param subreddit: A subreddit name to fetch submissions from.
# #     :param start: A Unix time integer. Posts fetched will be AFTER this time. (default: None)
# #     :param end: A Unix time integer. Posts fetched will be BEFORE this time. (default: None)
# #     :param limit: There needs to be a defined limit of results (default: 100), or Pushshift will return only 25.
# #     :param extra_query: A query string is optional. If an extra_query string is not supplied,
# #                         the function will just grab everything from the defined time period. (default: empty string)

# #     Submissions are yielded newest first.

# #     For more information on PRAW, see: https://github.com/praw-dev/praw
# #     For more information on Pushshift, see: https://github.com/pushshift/api
# #     """
# #     matching_praw_submissions = []

# #     # Default time values if none are defined (credit to u/bboe's PRAW `submissions()` for this section)
# #     utc_offset = 28800
# #     now = int(time.time())
# #     start = max(int(start) + utc_offset if start else 0, 0)
# #     end = min(int(end) if end else now, now) + utc_offset

# #     # Format our search link properly.
# #     search_link = (
# #         'https://api.pushshift.io/reddit/submission/search/'
# #         '?subreddit={}&after={}&before={}&sort_type=score&sort=asc&limit={}&q={}'
# #     )
# #     search_link = search_link.format(subreddit, start, end, limit, extra_query)

# #     # Get the data from Pushshift as JSON.
# #     retrieved_data = requests.get(search_link)
# #     returned_submissions = retrieved_data.json()['data']

# #     # Iterate over the returned submissions to convert them to PRAW submission objects.
# #     for submission in returned_submissions:

# #         # Take the ID, fetch the PRAW submission object, and append to our list
# #         praw_submission = reddit.submission(id=submission['id'])
# #         matching_praw_submissions.append(praw_submission)

# #     # Return all PRAW submissions that were obtained.
# #     return matching_praw_submissions
