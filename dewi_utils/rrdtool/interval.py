# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import enum
import time


class GraphIntervalType(enum.Enum):
    HOUR = 1
    DAY = 2
    WEEK = 3
    MONTH = 4
    YEAR = 5
    CUSTOM = 6


class GraphInterval:
    def __init__(self,
                 interval_type: GraphIntervalType,
                 start_time: int | None = None,
                 end_time: int | None = None
                 ):
        self.interval_type = interval_type
        self.interval_name = interval_type.name.lower()
        self.interval_title = self.interval_name.capitalize()

        if self.interval_type == GraphIntervalType.CUSTOM:
            self._start_time = start_time
            self._end_time = end_time
            self.title_suffix = f'from {time.localtime(start_time)} to {time.localtime(end_time)}'
        else:
            self._start_time = self._end_time = None
            self.title_suffix = f'by {self.interval_title}'

    def range(self, end_time_maybe: int) -> tuple[int, int]:
        """
        Return start and end time as UNIX timestamps based on `end_time_maybe` as end time.

        In case of custom ranges the end_time_maybe is ignored.

        Ranges are slightly differ from day/week/month/day, it's for 400px wide graphs, 1 RRA/px.
        """
        if self.interval_type == GraphIntervalType.CUSTOM:
            return self._start_time, self._end_time
        if self.interval_type == GraphIntervalType.HOUR:
            # 4000s, 1h 6m 40s
            return end_time_maybe - 4000, end_time_maybe
        elif self.interval_type == GraphIntervalType.DAY:
            # 2000m, 33h 20m
            return end_time_maybe - 2000 * 60, end_time_maybe
        elif self.interval_type == GraphIntervalType.WEEK:
            # 12000m, 8d 13h 20m
            return end_time_maybe - 12000 * 60, end_time_maybe
        elif self.interval_type == GraphIntervalType.MONTH:
            # 48000m, 33d 8h
            return end_time_maybe - 48000 * 60, end_time_maybe
        elif self.interval_type == GraphIntervalType.YEAR:
            # 400d
            return end_time_maybe - 400 * 24 * 3600, end_time_maybe

    @classmethod
    def default_intervals(cls):
        return [
            cls(GraphIntervalType.DAY),
            cls(GraphIntervalType.WEEK),
            cls(GraphIntervalType.MONTH),
            cls(GraphIntervalType.YEAR),
        ]
