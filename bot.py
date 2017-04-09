# !/usr/bin/python3
# coding: utf_8

# Copyright 2016 RaceUp ED
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import logging
import os
from math import ceil

from telegram.ext import Updater, CommandHandler

from yolobmsbot.batterypack import BatteryPack
from yolobmsbot.google import gsheets

# bot settings
SCRIPT_DIRECTORY = os.path.dirname(__file__)  # path to directory of python script running
CLIENT_TOKEN_FILE = os.path.join(SCRIPT_DIRECTORY, "yolobmsbot", ".user_credentials", "telegram", "bot_token")  # path to token file

# chat settings
KEYBOARD_CELLS = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18]]


def get_bot_token():
    """
    :return: void
        Authenticate bot
    """

    client_token = open(CLIENT_TOKEN_FILE, "r").read()
    client_token = client_token.strip()
    return client_token


def get_keyboard(items, max_columns):
    """
    :param items: []
        List of items to setup keyboard with
    :param max_columns: int
        Max columns per row
    :return: [] of []
        List of list: each row contains at most 3 items
    """

    matrix = []
    number_of_rows = ceil(len(items) / max_columns)
    for r in range(number_of_rows):
        row = []
        for c in range(max_columns):  # loop through columns
            try:
                row.append(str(items[r * max_columns + c]))
            except:
                pass
        matrix.append(row)
    return matrix


class YoloBmsBot(object):
    """ Remote Bms Raceup bot """

    def __init__(self, b_pack):
        """
        :param b_pack: BatteryPack
            Battery to organize
        """

        object.__init__(self)

        self.updater = Updater(get_bot_token())  # telegram settings
        self.dp = self.updater.dispatcher  # get the dispatcher to register handlers
        self.dp.add_error_handler(self.error)  # log errors
        self.setup_commands()  # setup commands
        self.battery_pack = b_pack  # battery pack

    def run(self):
        """
        :return: void
            run bot
        """

        self.updater.start_polling()
        self.updater.idle()  # run the bot until the user presses Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT

    def setup_commands(self):
        """
        :return: void
            Setup bot commmands
        """

        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("segment", self.reply_segment_command))
        self.dp.add_handler(CommandHandler("cell", self.reply_cell_command))

    def start(self, update):
        message = "Hello {}! I'm here to provide you with information about the RaceUp Bms" \
            .format(update.message.from_user.first_name)
        update.message.reply_text(message)

    def error(self, update, error):
        """
        :param update: updater
            Updater of bot chat
        :param error: string
            Exception string
        :return: void
            Logs exception
        """

        logging.error('Update "%s" caused error "%s"' % (update, error))

    def reply_segment_command(self, update):
        """
        :param update: updater
            Updater of bot chat
        :return: void
            Prompt user then returns value to screen
        """

        message_text = str(update.message.text)  # get text of user message
        update.message.reply_text("Please, let me compute the query...")
        args = message_text.split(" ")
        if len(args) < 2:  # reply all segments
            for s in range(len(self.battery_pack.segments)):
                msg = self.get_segment_value(s)
                update.message.reply_text(msg)
        else:

            s = int(args[-1])  # parse segment
            msg = self.get_segment_value(s)
            update.message.reply_text(msg)

    def get_segment_value(self, segment):
        """
        :param segment: int
            Segment to get average of
        :return: float
            Average of segment
        """

        if self.battery_pack.is_cell_in_bounds(0, segment):
            value, time = gsheets.get_last_segment_value(segment - 1)
            time_date = time.split(" ")[0]
            time_hours = time.split(" ")[1]
            return value
            # TODO update bms pack return self.battery_pack.segments.get_average(BatteryCellValue.voltage)
        else:
            raise ValueError("Invalid segment " + str(segment))

    def get_segment_value_msg(self, segment):
        """
        :param segment: int
            Segment of cell
        :return: str
            Message with cell value
        """

        try:
            value = self.get_segment_value(segment)
            return "Latest average value of segment " + str(segment) + " is " + "{0:.2f}".format(float(value)) + " mV"
        except Exception as e:
            return "Invalid segment " + str(segment)

    def reply_cell_command(self, update):
        """
        :param update: updater
            Updater of bot chat
        :return: void
            Prompt user then returns value to screen
        """

        message_text = str(update.message.text)  # get text of user message
        update.message.reply_text("Please, let me compute the query...")
        args = message_text.split(" ")
        if len(args) < 3:  # reply all cells
            for s in range(len(self.battery_pack.segments)):
                for c in range(len(self.battery_pack.segments[s].cells)):
                    msg = self.get_cell_value_msg(c, s)
                    update.message.reply_text(msg)
        else:
            c = int(args[-2])  # read cell
            s = int(args[-1])  # parse segment
            msg = self.get_cell_value_msg(c, s)
            update.message.reply_text(msg)

    def get_cell_value(self, cell, segment):
        """
        :param cell: int
            Cell to get value of
        :param segment: int
            Segment of cell
        :return: float
            Cell voltage
        """

        if self.battery_pack.is_cell_in_bounds():
            value, time = gsheets.get_last_cell_value(cell - 1, segment - 1)
            time_date = time.split(" ")[0]
            time_hours = time.split(" ")[1]
            return value
            # TODO update bms pack self.battery_pack.segments[segment].cells[cell].get(BatteryCellValue.voltage)
        else:
            raise ValueError("Invalid cell " + str(cell) + " in segment " + str(segment))

    def get_cell_value_msg(self, cell, segment):
        """
        :param cell: int
            Cell to get value of
        :param segment: int
            Segment of cell
        :return: str
            Message with cell value
        """

        try:
            value = self.get_cell_value(cell, segment)
            return "Latest value of cell " + str(cell) + " in segment " + str(segment) + " is " + "{0:.2f}".format(
                float(value)) + " mV"
        except Exception as e:
            return "Invalid cell " + str(cell) + " in segment " + str(segment)

if __name__ == '__main__':
    battery_pack = BatteryPack([18, 18, 18, 18, 18, 18])
    bot = YoloBmsBot(battery_pack)
    bot.run()
