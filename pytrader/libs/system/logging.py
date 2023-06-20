"""!@package pytrader.libs.system.logging

Provides additional functionality to the logging library from
Python.

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

@file pytrader/libs/system/logging.py
"""

# ==================================================================================================
#
# Libraries
#
#
# ==================================================================================================
# System Libraries
import logging
import copy
from logging import *

# 3rd Party Libraries

# Application Libraries
from pytrader.libs.utilities import text

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================
DEBUG2 = 9
DEBUG3 = 8
DEBUG4 = 7
DEBUG5 = 6
DEBUG6 = 5
DEBUG7 = 4
DEBUG8 = 3
DEBUG9 = 2
DEBUG10 = 1

INFO1 = 21
INFO2 = 22
INFO3 = 23
INFO4 = 24
INFO5 = 25
INFO6 = 26
INFO7 = 27
INFO8 = 28
INFO9 = 29

VINFO1 = 19
VINFO2 = 18
VINFO3 = 17
VINFO4 = 16
VINFO5 = 15
VINFO6 = 14
VINFO7 = 13
VINFO8 = 12
VINFO9 = 11

logging.addLevelName(9, "DEBUG2")
logging.addLevelName(8, "DEBUG3")
logging.addLevelName(7, "DEBUG4")
logging.addLevelName(6, "DEBUG5")
logging.addLevelName(5, "DEBUG6")
logging.addLevelName(4, "DEBUG7")
logging.addLevelName(3, "DEBUG8")
logging.addLevelName(2, "DEBUG9")
logging.addLevelName(1, "DEBUG10")

logging.addLevelName(19, "VINFO1")
logging.addLevelName(18, "VINFO2")
logging.addLevelName(17, "VINFO3")
logging.addLevelName(16, "VINFO4")
logging.addLevelName(15, "VINFO5")
logging.addLevelName(14, "VINFO6")
logging.addLevelName(13, "VINFO7")
logging.addLevelName(12, "VINFO8")
logging.addLevelName(11, "VINFO9")

logging.addLevelName(21, "INFO1")
logging.addLevelName(22, "INFO2")
logging.addLevelName(23, "INFO3")
logging.addLevelName(24, "INFO4")
logging.addLevelName(25, "INFO5")
logging.addLevelName(26, "INFO6")
logging.addLevelName(27, "INFO7")
logging.addLevelName(28, "INFO8")
logging.addLevelName(29, "INFO9")

colortext = text.ConsoleText()

# ==================================================================================================
#
# Classes
#
# LocalLogger
# ConsoleLvlFormatter
# ColorizingStreamHandler
#
# ==================================================================================================


# ==================================================================================================
#
# Class LocalLogger
#
# Calls the read function based on the file format.
#
# Inputs
# ------
#    @param:
#
# Returns
# -------
#    @return: None
#
# Raises
# ------
#    ...
#
# ==================================================================================================
class LocalLogger(Logger):
    #-------------------------------------------------------------------
    #
    # Function debug2
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug2(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(9):
            self._log(9, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug3
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug3(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(8):
            self._log(8, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug4
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug4(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(7):
            self._log(7, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug5
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug5(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(6):
            self._log(6, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug6
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug6(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(5):
            self._log(5, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug7
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug7(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(4):
            self._log(4, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug8
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug8(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(3):
            self._log(3, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug9
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug9(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(2):
            self._log(2, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function debug10
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def debug10(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(1):
            self._log(1, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo1
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo1(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(19):
            self._log(19, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo2
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo2(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(18):
            self._log(18, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo3
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo3(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(17):
            self._log(17, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo4
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo4(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(16):
            self._log(16, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo5
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo5(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(15):
            self._log(15, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo6
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo6(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(14):
            self._log(14, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo7
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo7(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(13):
            self._log(13, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo8
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo8(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(12):
            self._log(12, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function vinfo9
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def vinfo9(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(11):
            self._log(11, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info1
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info1(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(21):
            self._log(21, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info2
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info2(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(22):
            self._log(22, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info3
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info3(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(23):
            self._log(23, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info4
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info4(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(24):
            self._log(24, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info5
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info5(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(25):
            self._log(25, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info6
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info6(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(26):
            self._log(26, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info7
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info7(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(27):
            self._log(27, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info8
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info8(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(28):
            self._log(28, message, args, **kws)

    #-------------------------------------------------------------------
    #
    # Function info9
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: message - The error message to print.
    #    @param: *args
    #    @param: **kwargs
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def info9(self, message, *args, **kws):
        # Yes, logger takes its '*args' as 'args'.
        if self.isEnabledFor(29):
            self._log(29, message, args, **kws)


#-----------------------------------------------------------------------
#
# Class ConsoleLvlFormatter
#
# Adds further functionality for the console to change the
# format based on the logging lewel
#
# Inputs
# ------
#    @param: self
#    @param: message - The error message to print.
#    @param: *args
#    @param: **kwargs
#
# Returns
# -------
#    @return: None
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
class ConsoleLvlFormatter(Formatter):

    def __init__(self, fmt="%(levelno)s: %(message)s"):
        Formatter.__init__(self, fmt)
        self.dbg_fmt = "%(levelname)-8s: %(name)s:%(funcName)s:%(lineno)d - %(message)s"
        self.info_fmt = "%(message)s"
        self.warn_fmt = "%(levelname)-8s: %(message)s"
        self.err_fmt = "%(levelname)-8s: %(message)s"
        self.crit_fmt = "%(levelname)-8s: %(message)s"

    #-------------------------------------------------------------------
    #
    # Function format
    #
    # ...
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: record - The error message to print.
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def format(self, record):

        # Save the original format configured by the user
        # when the logger formatter was instantiated
        format_orig = self._style._fmt

        # Replace the original format with one customized by logging level
        if record.levelno <= DEBUG:
            self._style._fmt = self.dbg_fmt

        elif record.levelno >= INFO and record.levelno < WARNING:
            self._style._fmt = self.info_fmt

        elif record.levelno == WARNING:
            self._style._fmt = self.warn_fmt

        elif record.levelno == ERROR:
            self._style._fmt = self.err_fmt

        elif record.levelno == CRITICAL:
            self._style._fmt = self.crit_fmt

        # Call the original formatter class to do the grunt work
        result = Formatter.format(self, record)

        # Restore the original format configured by the user
        self._style._fmt = format_orig

        return result


#-----------------------------------------------------------------------
#
# Class ColorizingStreamHandler
#
# Calls the read function based on the file format.
#
# Inputs
# ------
#    @param: self
#    @param: *args
#    @param: **kwargs
#
# Returns
# -------
#    @return: None
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
class ColorizingStreamHandler(logging.StreamHandler, text.ConsoleText):

    def __init__(self, *args, **kwargs):
        self._colors = {
            DEBUG10: "green",
            DEBUG9: "green",
            DEBUG8: "green",
            DEBUG7: "green",
            DEBUG6: "green",
            DEBUG5: "green",
            DEBUG4: "green",
            DEBUG3: "green",
            DEBUG2: "green",
            DEBUG: "green",
            VINFO1: "white",
            VINFO2: "white",
            VINFO3: "white",
            VINFO4: "white",
            VINFO5: "white",
            VINFO6: "white",
            VINFO7: "white",
            VINFO8: "white",
            VINFO9: "white",
            INFO: "white",
            INFO1: "white",
            INFO2: "white",
            INFO3: "white",
            INFO4: "white",
            INFO5: "white",
            INFO6: "white",
            INFO7: "white",
            INFO8: "white",
            INFO9: "white",
            WARNING: "yellow",
            ERROR: "red",
            CRITICAL: "magenta"
        }
        super(ColorizingStreamHandler, self).__init__(*args, **kwargs)
        return None

    #-------------------------------------------------------------------
    #
    # Function is_tty
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #
    # Returns
    # -------
    #    @return: isatty
    #    @return: isatty()
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    #-------------------------------------------------------------------
    #
    # Function emit
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: record - The error message to print.
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def emit(self, record):
        try:
            message = self.format(record)
            stream = self.stream
            if not self.is_tty:
                stream.write(message)
            else:
                message = colortext.colorize(message, "none", self._colors[record.levelno], "black")
                stream.write(message)

            stream.write(getattr(self, 'terminator', '\n'))
            self.flush()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            self.handleError(record)

    #-------------------------------------------------------------------
    #
    # Function setLevelColor
    #
    # Calls the read function based on the file format.
    #
    # Inputs
    # ------
    #    @param: self
    #    @param: logging_level - The error message to print.
    #    @param: escaped_ansi_code
    #
    # Returns
    # -------
    #    @return: None
    #
    # Raises
    # ------
    #    ...
    #
    #-------------------------------------------------------------------
    def setLevelColor(self, logging_level, escaped_ansi_code):
        self._colors[logging_level] = escaped_ansi_code


local_manager = copy.copy(Logger.manager)
local_manager.loggerClass = LocalLogger

#-----------------------------------------------------------------------
#
# Functions
#
# getLogger
# verifydebuglevels
#
#-----------------------------------------------------------------------


#-----------------------------------------------------------------------
#
# Function getLogger
#
# Calls the read function based on the file format.
#
# Inputs
# ------
#    @param: self
#    @param: message - The error message to print.
#    @param: *args
#    @param: **kwargs
#
# Returns
# -------
#    @return: None
#
# Raises
# ------
#    ...
#
#-----------------------------------------------------------------------
def getLogger(name=None):  # noqa
    if name:
        return local_manager.getLogger(name)
    else:
        return Logger.root
