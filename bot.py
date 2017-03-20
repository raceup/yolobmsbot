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

from yolobmsbot.google import gsheets

# bot settings
SCRIPT_DIRECTORY = os.path.dirname(__file__)  # path to directory of python script running
CLIENT_TOKEN_FILE = os.path.join(SCRIPT_DIRECTORY, "yolobmsbot", ".user_credentials", "telegram", "bot_token")  # path to token file

# bms settings
NUMBER_OF_SEGMENTS = 8
NUMBER_OF_CELLS_PER_SEGMENT = [17, 18, 18, 18, 18, 18, 18, 17]  # first and last segment have 1 less cell

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

    def __init__(self):
        object.__init__(self)

        self.updater = Updater(get_bot_token())
        self.dp = self.updater.dispatcher  # get the dispatcher to register handlers
        self.dp.add_error_handler(self.error)  # log errors
        self.setup_commands()  # setup commands

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
        self.dp.add_handler(CommandHandler("segment", self.get_segment_average_value))
        self.dp.add_handler(CommandHandler("cell", self.get_cell_value))

    @staticmethod
    def start(bot, update):
        message = "Hello {}! I'm here to provide you with information about the RaceUp Bms" \
            .format(update.message.from_user.first_name)
        update.message.reply_text(message)

    @staticmethod
    def error(bot, update, error):
        """
        :param bot: bot
            Bot to use
        :param update: updater
            Updater of bot chat
        :param error: string
            Exception string
        :return: void
            Logs exception
        """

        logging.error('Update "%s" caused error "%s"' % (update, error))

    @staticmethod
    def get_segment_average_value(bot, update):
        """
        :param bot: bot
            Bot to use
        :param update: updater
            Updater of bot chat
        :return: void
            Prompt user then returns value to screen
        """

        # TODO: set keyboard with segment to choose
        message_text = str(update.message.text)  # get text of user message
        args = message_text.split(" ")

        if len(args) < 2:
            message = "Sorry " + update.message.from_user.first_name + " but you have to specify a segment (in [1, 8])!\ne.g \"/segment 1\""
        else:
            wait_message = "Please, let me compute the query..."
            update.message.reply_text(wait_message)

            segment = int(args[-1])  # parse segment
            if segment not in range(1, NUMBER_OF_SEGMENTS + 1):
                message = "Sorry " + update.message.from_user.first_name + " but the segment " + str(
                    segment) + " does not exists!"
                message += "\nPossible segments are from 1 to " + str(NUMBER_OF_SEGMENTS)
            else:
                value, time = gsheets.get_last_segment_value(segment - 1)
                time_date = time.split(" ")[0]
                time_hours = time.split(" ")[1]

                print("\tGetting value of average of segment", segment, "for", update.message.from_user.first_name)
                print("\tValue updated in", str(time_date), "at", str(time_hours))

                message = "Latest value of segment " + str(segment) + " is " + "{0:.2f}".format(float(value)) + " mV" +\
                          " as of " + str(time_date) + " at " + str(time_hours) + ".\n"
        update.message.reply_text(message)  # send message

    @staticmethod
    def get_cell_value(bot, update):
        """
        :param bot: bot
            Bot to use
        :param update: updater
            Updater of bot chat
        :return: void
            Prompt user then returns value to screen
        """

        # TODO: set keyboard with segment to choose, set keyboard with cell to choose
        message_text = str(update.message.text)  # get text of user message
        args = message_text.split(" ")

        if len(args) < 3:
            message = "Sorry " + update.message.from_user.first_name + " but you have to specify the cell and the segment (in [1, 17(18)] x [1, 8])!\ne.g \"/cell 1 2\""
        else:
            wait_message = "Please, let me compute the query..."
            update.message.reply_text(wait_message)

            cell = int(args[-2])  # read cell
            segment = int(args[-1])  # parse segment

            if segment not in range(1, NUMBER_OF_SEGMENTS + 1) or cell not in range(1, NUMBER_OF_CELLS_PER_SEGMENT[segment - 1] + 1):
                message = "Sorry " + update.message.from_user.first_name + " but the cell " + str(cell) + " does not exists in the segment " + str(segment)

                if segment not in range(1, NUMBER_OF_SEGMENTS + 1):
                    message += "\nPossible segments are from 1 to " + str(NUMBER_OF_SEGMENTS)
                else:  # segment is right
                    if cell not in range(NUMBER_OF_CELLS_PER_SEGMENT[segment - 1]):
                        message += "\nPossible cells in segment " + str(segment) + " are from 1 to " + str(NUMBER_OF_CELLS_PER_SEGMENT[segment - 1])
            else:
                value, time = gsheets.get_last_cell_value(cell - 1, segment - 1)
                time_date = time.split(" ")[0]
                time_hours = time.split(" ")[1]

                print("\tGetting value of cell", cell, "in segment", segment, "for",
                      update.message.from_user.first_name)
                print("\tValue updated in", str(time_date), "at", str(time_hours))

                message = "Latest value of cell " + str(cell) + " in segment " + str(segment) + " is " + "{0:.2f}".format(float(value)) + " mV" +\
                          " as of " + str(time_date) + " at " + str(time_hours) + ".\n"
        update.message.reply_text(message)  # send message

if __name__ == '__main__':
    bot = YoloBmsBot()
    bot.run()
