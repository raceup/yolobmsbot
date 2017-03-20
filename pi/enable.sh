#!/usr/bin/env bash
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

# Enable service for bot

sudo chmod 644 /lib/systemd/system/raceup_bms_telegram_bot.service
sudo chmod +x /home/pi/Raceup/Ed/Elettronica/projects/bms/bms-telegram-bot/bot.py
sudo systemctl daemon-reload
sudo systemctl enable raceup_bms_telegram_bot.service
sudo systemctl start raceup_bms_telegram_bot.service