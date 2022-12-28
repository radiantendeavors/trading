"""!
@package pytrader.libs.clients.mysql.index_info

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


@file pytrader/libs/clients/mysql/etf_info.py
"""
# System Libraries
import pymysql
from datetime import date, time

# 3rd Party Libraries

# Application Libraries
# System Library Overrides
from pytrader.libs.system import logging

# Other Application Libraries
from pytrader.libs.clients import mysql

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


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class IndexBarDailyRaw(mysql.MySQLDatabase):

    def __init__(self):
        self.table_name = "index_bar_daily_raw"
        super().__init__()

    def select(self, select_clause=None, where_clause=None):
        logger.debug("Begin Function")
        if select_clause:
            sql = """
            SELECT""" + select_clause + "\n"
        else:
            sql = """
            SELECT *
            """

        sql += "FROM `index_bar_daily_raw`\n"
        logger.debug("SQL: %s", sql)

        if where_clause:
            sql += "WHERE " + where_clause

        logger.debug("SQL: %s", sql)
        cursor = self.mycursor
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            # logger.debug("Result: %s", result)
            return result
        except pymysql.Error as e:
            logger.error("Select Error: %s", e)
            return None

    def insert(self, ticker, date_time, p_open, p_high, p_low, p_close,
               p_adjusted_close, volume, data_source, date_downloaded):
        logger.debug("Begin Function")

        today = date.today()

        where = "`ticker`='" + ticker + "' AND `date`='" + str(date_time) + "'"
        item = self.select(where_clause=where)
        logger.debug("Item: %s", item[0])

        logger.debug("Today is: %s", today)
        logger.debug("Date time is: %s", str(date_time).split(" ")[0])

        if str(date_time).split(" ")[0] == str(today):
            if item[0]["data_source"] == data_source:

                sql = """
                UPDATE `index_bar_daily_raw`
                SET `open`=%s, `high`=%s, `low`=%s, `close`=%s, `adjusted_close`=%s, `volume`=%s
                WHERE `ticker`=%s AND `date`=%s AND `data_source`=%s
                """

                logger.debug("SQL: %s", sql)
                cursor = self.mycursor
                try:
                    cursor.execute(
                        sql, (p_open, p_high, p_low, p_close, p_adjusted_close,
                              volume, ticker, date_time, data_source))
                except pymysql.Error as e:
                    logger.error("Insert Error: %s", e)

                self.mydb.commit()

        if item:
            logger.debug("Item: %s", item)
        else:
            logger.debug("Empty Item")

            sql = """
            INSERT INTO `index_bar_daily_raw`
            (`ticker`, `date`, `open`, `high`, `low`, `close`, `adjusted_close`, `volume`, `data_source`, `date_downloaded`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor = self.mycursor
            try:
                cursor.execute(
                    sql,
                    (ticker, date, p_open, p_high, p_low, p_close,
                     p_adjusted_close, volume, data_source, date_downloaded))
            except pymysql.Error as e:
                logger.error("Insert Error: %s", e)

            self.mydb.commit()

        logger.debug("End Function")
        return None
