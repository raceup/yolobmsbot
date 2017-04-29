# !/usr/bin/python3
# coding: utf_8

# Copyright 2017 RaceUp ED
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
from datetime import datetime
from math import ceil

from telegram.ext import Updater, CommandHandler

from yolobmsbot import logs
from yolobmsbot.batterypack import BatteryPack, BatteryCellValue
from yolobmsbot.google import gsheets

# bot settings
SCRIPT_DIRECTORY = os.path.dirname(__file__)  # path to directory of python script running
CLIENT_TOKEN_FILE = os.path.join(SCRIPT_DIRECTORY, "yolobmsbot", ".user_credentials", "telegram", "bot_token")  # path to token file
BOT_TOKEN = open(CLIENT_TOKEN_FILE, "r").read().strip()
UPDATE_INTERVAL_MINUTES = 30  # minutes between 2 consecutive values updates
QUERY_WAIT_MESSAGE = "Please let me compute the query ... it may take a few moments"

# chat settings
KEYBOARD_CELLS = [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12], [13, 14, 15], [16, 17, 18]]

# bms settings
NUMBER_OF_SEGMENTS = 8
NUMBER_OF_CELLS_PER_SEGMENT = [17, 18, 18, 18, 18, 18, 18, 17]  # first and last segment have 1 less cell


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


class BatteryPackUpdater(object):
    """ Fetches new values of battery pack and updates """

    def __init__(self, b_pack, update_interval):
        """
        :param b_pack: BatteryPack
            Battery to update
        :param update_interval: int
            Number of minutes between two consecutive values updates
        """

        object.__init__(self)

        self.battery_pack = b_pack  # battery
        self.update_interval = update_interval
        self.last_update = datetime.fromtimestamp(0)  # first january 1970

    def _is_update_needed(self):
        """
        :return: bool
            True if need to update cells values because timer timeout
        """

        time_now = datetime.now()
        minutes_since_last_update = time_now - self.last_update
        minutes_since_last_update = minutes_since_last_update.total_seconds() / 60.0
        return minutes_since_last_update >= self.update_interval

    def update_values(self):
        """
        :return: void
            Updates all values in battery pack
        """

        if self._is_update_needed():  # check timer timeout
            print("Updating values")
            self.last_update = datetime.now()  # update last time of update
            last_row = None
            for s in range(len(self.battery_pack.segments)):
                last_values_of_cells_in_segment, last_update_time, last_row = gsheets.get_last_cells_values(
                    s,
                    row=last_row
                )  # get last values

                for c in range(len(self.battery_pack.segments[s].cells)):
                    new_voltage_value = last_values_of_cells_in_segment[c]
                    new_temp_value = 0.0
                    self.battery_pack.segments[s].cells[c].update_values(new_temp_value, new_voltage_value)  # update
                    print("Updated (cell, segment) (" + str(c) + ", " + str(s) + "): voltage", str(new_voltage_value))
            print("Done updating values")


class YoloBmsBot(object):
    """ Remote Bms Raceup bot """

    def __init__(self):
        object.__init__(self)

        self.updater = Updater(BOT_TOKEN)  # telegram settings
        self.dp = self.updater.dispatcher  # get the dispatcher to register handlers
        self.dp.add_error_handler(self.error)  # log errors
        self.setup_commands()  # setup commands

    def run(self):
        """
        :return: void
            run bot
        """

        self.updater.start_polling()
        self.updater.idle()  # run the bot until SIGINT, SIGTERM or SIGABRT

    def setup_commands(self):
        """
        :return: void
            Setup bot commmands
        """

        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("segment", self.reply_segment_command))
        self.dp.add_handler(CommandHandler("cell", self.reply_cell_command))

    @staticmethod
    def start(bot, update):
        """
        :param bot: bot
            Bot to use
        :param update: updater
            Updater of bot chat
        :return: void
            Welcomes user
        """

        logs.log_users(
            update.message.from_user.id,
            update.message.from_user.first_name,
            update.message.from_user.last_name,
            update.message.from_user.username
        )  # log

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
    def reply_segment_command(bot, update):
        """
        :param bot: bot
            Bot to use
        :param update: updater
            Updater of bot chat
        :return: void
            Prompt user then returns value to screen
        """

        user_name = update.message.from_user.first_name + update.message.from_user.last_name + " (" + update.message.from_user.username + ")"
        logs.log_user_action(update.message.from_user.id, str(update.message.text))  # log
        message_text = str(update.message.text)  # get text of user message
        print(user_name, "has asked", message_text)
        update.message.reply_text(QUERY_WAIT_MESSAGE)
        values_updater.update_values()  # update values

        args = message_text.split(" ")
        if len(args) < 2:  # reply all segments
            print("Answering all segments")
            update.message.reply_text("Going to fetch values of all segments .. be ready for spam")
            msg_counter = 0
            for s in range(len(battery_pack.segments)):
                try:
                    msg = YoloBmsBot.get_segment_value_msg(s)
                    update.message.reply_text(msg)
                    msg_counter += 1
                except Exception as e:
                    print("Cannot get value of segment " + str(s))
                    print(str(e))
                    update.message.reply_text("Ooops cannot get value of segment " + str(s))
            update.message.reply_text("Done replying " + str(msg_counter) + " values")
        else:
            s = int(args[-1]) - 1  # parse segment
            print("Answering segment", s)
            msg = YoloBmsBot.get_segment_value_msg(s)
            update.message.reply_text(msg)

    @staticmethod
    def get_segment_value(segment):
        """
        :param segment: int
            Segment to get average of
        :return: float
            Average of segment
        """

        if battery_pack.is_cell_in_bounds(0, segment):
            value = battery_pack.segments[segment].get_average(BatteryCellValue.voltage)
            return value
        else:
            raise ValueError("Invalid segment " + str(segment))

    @staticmethod
    def get_segment_value_msg(segment):
        """
        :param segment: int
            Segment of cell
        :return: str
            Message with cell value
        """

        try:
            value = YoloBmsBot.get_segment_value(segment)
            time_update = values_updater.last_update
            time_date, time_hours = str(time_update.date()), str(time_update.time())

            return "Latest average value of segment " + str(int(segment) + 1) + " is " + "{0:.2f}".format(
                float(value)) + " mV as of " + str(time_date) + " at " + str(time_hours)
        except Exception as e:
            print("Cannot answer segment", segment)
            print(str(e))
            import traceback
            traceback.print_exc()
            return "Invalid segment " + str(segment + 1)

    @staticmethod
    def reply_cell_command(bot, update):
        """
        :param bot: bot
            Bot to use
        :param update: updater
            Updater of bot chat
        :return: void
            Prompt user then returns value to screen
        """

        user_name = update.message.from_user.first_name + update.message.from_user.last_name + " (" + update.message.from_user.username + ")"
        logs.log_user_action(str(user_name), str(update.message.text))  # log
        message_text = str(update.message.text)  # get text of user message
        print(user_name, "has asked", message_text)
        update.message.reply_text(QUERY_WAIT_MESSAGE)
        values_updater.update_values()  # update values

        args = message_text.split(" ")
        if len(args) < 3:  # reply all cells
            print("Answering all cells")
            update.message.reply_text("Going to fetch values of all cells .. be ready for spam")
            msg_counter = 0
            for s in range(len(battery_pack.segments)):
                for c in range(len(battery_pack.segments[s].cells)):
                    try:
                        msg = YoloBmsBot.get_cell_value_msg(c, s)
                        update.message.reply_text(msg)
                        msg_counter += 1
                    except Exception as e:
                        print("Cannot get value of cell " + str(c) + " in segment " + str(s))
                        print(str(e))
                        update.message.reply_text("Ooops cannot get value of cell " + str(c) + " in segment " + str(s))
            update.message.reply_text("Done replying " + str(msg_counter) + " values")
        else:
            c = int(args[-2]) - 1  # read cell
            s = int(args[-1]) - 1  # parse segment
            print("Answering cell", c, "in segment", s)
            msg = YoloBmsBot.get_cell_value_msg(c, s)
            update.message.reply_text(msg)

    @staticmethod
    def get_cell_value(cell, segment):
        """
        :param cell: int
            Cell to get value of
        :param segment: int
            Segment of cell
        :return: float
            Cell voltage
        """

        if battery_pack.is_cell_in_bounds(cell, segment):
            value = battery_pack.segments[segment].cells[cell].get(BatteryCellValue.voltage)
            return value
        else:
            raise ValueError("Invalid cell " + str(cell) + " in segment " + str(segment))

    @staticmethod
    def get_cell_value_msg(cell, segment):
        """
        :param cell: int
            Cell to get value of
        :param segment: int
            Segment of cell
        :return: str
            Message with cell value
        """

        try:
            value = YoloBmsBot.get_cell_value(cell, segment)
            time_update = values_updater.last_update
            time_date, time_hours = str(time_update.date()), str(time_update.time())

            return "Latest value of cell " + str(cell + 1) + " in segment " + str(
                segment + 1) + " is " + "{0:.2f}".format(
                float(value)) + " mV as of " + time_date + " at " + time_hours
        except Exception as e:
            print("Cannot answer cell", cell, "in segment", segment)
            print(str(e))
            return "Invalid cell " + str(cell + 1) + " in segment " + str(segment + 1)

if __name__ == '__main__':
    logs.setup_log_files()
    battery_pack = BatteryPack([18, 18, 18, 18, 18, 18])
    values_updater = BatteryPackUpdater(battery_pack, UPDATE_INTERVAL_MINUTES)  # module to update cells values
    values_updater.update_values()

    bot = YoloBmsBot()
    bot.run()
