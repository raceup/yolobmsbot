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

# Run services to remote control BMS

# Telegram Bot
sudo service raceup_bms_telegram_bot stop
sudo service raceup_bms_telegram_bot start

# Remote BMS
# TODO sudo service raceup_bms_telegram_bot stop
# TODO sudo service raceup_bms_telegram_bot start
