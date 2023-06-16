"""!@package pytrader.libs.utilities.text

Provides console text formatting capabilities.

@author G S Derber
@version HEAD
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

    def __init__(self):
        self.escape = "\x1b["

        self.attributes = {
            "none": 0,
            "bold": 1,
            "unk_a": 2,
            "unk_b": 3,
            "underline": 4,
            "blink": 5,
            "unk_c": 6,
            "reverse": 7
        }

        self.fgcolors = {
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

        self.bgcolors = {
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
                 text,
                 attribute="none",
                 fgcolor="white",
                 bgcolor="black"):
        if attribute in self.attributes:
            begincolor = self.escape + str(self.attributes[attribute])
        else:
            begincolor = self.escape + str(self.attributes['none'])

        if fgcolor in self.fgcolors:
            begincolor = begincolor + ";" + str(self.fgcolors[fgcolor])
        else:
            begincolor = begincolor + ";" + str(self.fgcolors['white'])

        if bgcolor in self.bgcolors:
            begincolor = begincolor + ";" + str(self.bgcolors[bgcolor]) + "m"
        else:
            begincolor = begincolor + ";" + str(self.bgcolors['black']) + "m"

        resetcolor = self.escape + str(self.attributes['none']) + ";" + str(
            self.fgcolors['white']) + ";" + str(self.bgcolors['black']) + "m"

        textstring = begincolor + text + resetcolor
        return textstring
