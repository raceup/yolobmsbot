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


import os
import telegram
from telegram.ext import Updater, CommandHandler

from yolobmsbot.google import gsheets

SCRIPT_DIRECTORY = os.path.dirname(__file__)  # path to directory of python script running
CLIENT_TOKEN_FILE = os.path.join(SCRIPT_DIRECTORY, "yolobmsbot", ".user_credentials", "telegram", "bot_token")  # path to token file
NUMBER_OF_SEGMENTS = 8
NUMBER_OF_CELLS_PER_SEGMENT = [17, 18, 18, 18, 18, 18, 18, 17]  # first and last segment have 1 less cell


def get_bot_token():
    """
    :return: void
        Authenticate bot
    """

    CLIENT_TOKEN = open(CLIENT_TOKEN_FILE, "r").read()
    CLIENT_TOKEN = CLIENT_TOKEN.strip()
    return CLIENT_TOKEN


class YoloBmsBot(object):
    """ Remote Bms Raceup bot """

    def __init__(self):
        object.__init__(self)

        self.updater = Updater(get_bot_token())
        self.setup_commands()  # setup commands

    def run(self):
        """
        :return: void
            run bot
        """

        self.updater.start_polling()
        self.updater.idle()

    def setup_commands(self):
        """
        :return: void
            Setup bot commmands
        """

        self.updater.dispatcher.add_handler(CommandHandler("start", self.start))
        self.updater.dispatcher.add_handler(CommandHandler("help", self.start))
        self.updater.dispatcher.add_handler(CommandHandler("segment", self.get_current_segment_average_value))
        self.updater.dispatcher.add_handler(CommandHandler("cell", self.get_current_cell_value))

    @staticmethod
    def help(bot, update):
        message = "Receive updates about the Raceup remote bms." \
                  "Go to the official page https://sites.google.com/view/raceupbms for more information."\
            .format(update.message.from_user.first_name)
        update.message.reply_text(message)

    @staticmethod
    def start(bot, update):
        message = "Hello {}! I'm here to provide you with information about the RaceUp Bms" \
            .format(update.message.from_user.first_name)
        update.message.reply_text(message)

    @staticmethod
    def get_current_segment_average_value(bot, update):
        # TODO: set keyboard with segment to choose
        message_text = str(update.message.text)  # get text of user message
        segment = int(message_text.split(" ")[-1])  # parse segment

        if segment not in range(NUMBER_OF_SEGMENTS):
            message = "Sorry " + update.message.from_user.first_name + " but the segment " + str(segment) + " does not exists!"
            message += "\nPossible segments are from 1 to " + str(NUMBER_OF_SEGMENTS)
        else:
            value, time = gsheets.get_last_segment_value(segment - 1)
            message = "Latest value of segment " + str(segment) + " is " + str(value) + " as of " + str(time) + ".\n" + str(message_text)
        update.message.reply_text(message)  # send message

    @staticmethod
    def get_current_cell_value(bot, update):
        # TODO: set keyboard with segment to choose
        # TODO: set keyboard with cell to choose

        message_text = str(update.message.text)  # get text of user message
        cell = int(message_text.split(" ")[-2])  # read cell
        segment = int(message_text.split(" ")[-1])  # parse segment

        if segment not in range(NUMBER_OF_SEGMENTS) or cell not in range(NUMBER_OF_CELLS_PER_SEGMENT[segment - 1]):
            message = "Sorry " + update.message.from_user.first_name + " but the cell " + str(cell) + " does not exists in the segment " + str(segment)

            if segment not in range(NUMBER_OF_SEGMENTS):
                message += "\nPossible segments are from 1 to " + str(NUMBER_OF_SEGMENTS)
            else:  # segment is right
                if cell not in range(NUMBER_OF_CELLS_PER_SEGMENT[segment - 1]):
                    message += "\nPossible cells in segment " + str(segment) + " are from 1 to " + str(NUMBER_OF_CELLS_PER_SEGMENT[segment - 1])
        else:
            value, time = gsheets.get_last_cell_value(cell - 1, segment - 1)
            message = "Latest value of cell " + str(cell) + " in segment " + str(segment) + " is " + str(value) + " as of " + str(time) + ".\n" + str(message_text)

        update.message.reply_text(message)  # send message


if __name__ == '__main__':
    bot = YoloBmsBot()
    bot.run()
