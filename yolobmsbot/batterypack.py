# !/usr/bin/python
# coding: utf_8

# Copyright 2016-2017 RaceUP ED
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


from enum import Enum


class BatteryCellValue(Enum):
    """
    List of possible values of a battery cell
    """

    temperature = 0
    voltage = 1


class BatteryCell(object):
    """
    Model for a battery cell with reading of voltage/temperature
    """

    def __init__(self):
        object.__init__(self)

        self.temperature = 0.0  # initial values
        self.voltage = 0.0

    def get(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: float
            Temperature or voltage (depending on key) value of cell
        """

        if key == BatteryCellValue.temperature:
            return self.temperature
        elif key == BatteryCellValue.voltage:
            return self.voltage
        else:
            raise ValueError(str(key) + " is not a recognised key for a BatteryCell value")

    def update_values(self, temperature, voltage):
        """
        :param temperature: float
            New temperature of cell
        :param voltage: float
            New voltage of cell
        :return: void
            Updates values
        """

        self.temperature = temperature
        self.voltage = voltage

    def is_abnormal(self):
        """
        :return: bool
            True iff cell voltage is abnormal
        """

        has_abnormal_voltage = self.voltage < 3500 or self.voltage > 4200
        has_abnormal_temperature = self.temperature > 60
        return has_abnormal_voltage or has_abnormal_temperature


class BatterySegment(object):
    """
    Model for a battery segment with cells
    """

    def __init__(self, number_of_cells):
        """
        :param number_of_cells: int
            Number of cells in segment
        """

        object.__init__(self)

        self.cells = [BatteryCell() for _ in range(number_of_cells)]  # create list of cells

    def get(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: list of float
            List of temperature or voltage (depending on key) value of cells
        """

        return [cell.get(key) for cell in self.cells]

    def get_total(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: float
            Sum of all cells' values
        """

        s = 0
        for c in self.cells:
            try:
                s += float(c.get(key))
            except:
                s += 0.0
        return s  # sum all values

    def get_average(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: float
            Average of all cells' values
        """

        return self.get_total(key) / len(self.cells)  # get sum then divide


class BatteryPack(object):
    """
    Model for battery pack with segments and cells
    """

    def __init__(self, number_of_cells_per_segment):
        """
        :param number_of_cells_per_segment: list
            Each elements in the list is the number of the cells for each segment in battery pack
        """

        object.__init__(self)

        self.segments = [BatterySegment(num_of_cells) for num_of_cells in
                         number_of_cells_per_segment]  # list of segments
        self.number_of_cells_per_segment = number_of_cells_per_segment

    def get_total(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: float
            Sum of all segments' values
        """

        return sum([segment.get_total(key) for segment in self.segments])  # sum all values

    def get_average(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: float
            Average of all segments' values
        """

        return self.get_total(key) / len(self.segments)  # get sum then divide

    def get_averages(self, key):
        """
        :param key: BatteryCellValue
            Type of value you want to query
        :return: float
            Averages of all segments' values
        """

        return [segment.get_average(key) for segment in self.segments]

    def get_list_of_abnormal_cells(self):
        """
        :return: list of dicts
            each dict is of type {"cell", "segment", "voltage", "temperature"} and it's in list only if the cells is abnormal
        """

        list_of_abnormal_cells = []  # output
        for segment in range(len(self.segments)):  # loop through all segments
            for cell in range(len(self.segments[segment].cells)):  # loop through all cells
                if segment <= 5 and self.segments[segment].cells:
                    cell.is_abnormal()  # TODO segments > 5 are not considered for now
                    list_of_abnormal_cells.append(
                        {
                            "cell": cell,
                            "segment": segment,
                            "voltage": self.segments[segment].cells[cell].voltage,
                            "temperature": self.segments[segment].cells[cell].temperature
                        }
                    )  # add new cell

        return list_of_abnormal_cells

    def get_current_voltages(self):
        """
        :return: [] of []
            Matrix of voltages, each row is a segment, each column is the voltage of a cell
        """

        values = []
        for segment in self.segments:
            segment_values = segment.get(BatteryCellValue.voltage)
            values.append(segment_values)
        return values

    def is_cell_in_bounds(self, cell, segment):
        """
        :param cell: int
            Cell to get value of
        :param segment: int
            Segment of cell
        :return: bool
            True iff cell position is valid
        """

        segment_in_range = segment in range(0, len(self.segments))
        cell_in_range = cell in range(0, len(self.segments[segment].cells))
        return segment_in_range and cell_in_range
