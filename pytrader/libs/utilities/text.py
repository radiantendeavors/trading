"""!@package pytrader.libs.utilities.text

Provides console text formatting capabilities.

@author G S Derber
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

@file pytrader/libs/utilities/text.py
"""

# ==================================================================================================
#
# Libraries
#
#
# ==================================================================================================
# Standard Libraries

# 3rd Party Libraries

# Application Libraries
# Application System Overrides

# ==================================================================================================
#
# Global Variables
#
# ==================================================================================================


# ==================================================================================================
#
# Classes
#
# ==================================================================================================
class ConsoleText():
    """!
    Provides formatting for console text
    """
    __escape = "\x1b["
    __attributes = {
        "none": 0,
        "bold": 1,
        "unk_a": 2,
        "unk_b": 3,
        "underline": 4,
        "blink": 5,
        "unk_c": 6,
        "reverse": 7
    }
    __fgcolors = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "fuchsia": 35,
        "magenta": 35,
        "turquoise": 36,
        "cyan": 36,
        "white": 37
    }
    __bgcolors = {
        "black": 40,
        "red": 41,
        "green": 42,
        "yellow": 43,
        "blue": 44,
        "fuchsia": 45,
        "magenta": 45,
        "turquoise": 46,
        "cyan": 46,
        "white": 47
    }

    def colorize(self,
                 text: str,
                 attribute: str = "none",
                 fgcolor: str = "white",
                 bgcolor: str = "black") -> str:
        """!
        Adds color to the text.

        @param text:
        @param attribute:
        @param fgcolor:
        @param bgcolor:

        @return textstring
        """
        if attribute in self.__attributes:
            begincolor = self.__escape + str(self.__attributes[attribute])
        else:
            begincolor = self.__escape + str(self.__attributes['none'])

        if fgcolor in self.__fgcolors:
            begincolor = begincolor + ";" + str(self.__fgcolors[fgcolor])
        else:
            begincolor = begincolor + ";" + str(self.__fgcolors['white'])

        if bgcolor in self.__bgcolors:
            begincolor = begincolor + ";" + str(self.__bgcolors[bgcolor]) + "m"
        else:
            begincolor = begincolor + ";" + str(self.__bgcolors['black']) + "m"

        resetcolor = self.__escape + str(self.__attributes['none']) + ";" + str(
            self.__fgcolors['white']) + ";" + str(self.__bgcolors['black']) + "m"

        textstring = begincolor + text + resetcolor
        return textstring
