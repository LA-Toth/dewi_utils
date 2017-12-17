# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import datetime
import os
import os.path
import typing

import dewi.utils.yaml as _yaml
from dewi.rrdtool.interval import GraphInterval
from dewi.rrdtool.loader import GraphLoader
from dewi.rrdtool.writer import GraphResult, GraphWriter


class RrdTool:
    """
    Core module that loads a Munin datafile and generates the graphs using 'rrdtool graph'.

    By default the graphs are generated using a specific end time,
    the start time is determined by the specified list of intervals.

    Default set of intervals is year/month/week/day, but with wider ranges, see GraphInterval type.
    The width and height of the graphs can also be specified.
    """
    def __init__(self,
                 munin_directory: str,
                 end_time: typing.Optional[datetime.datetime],
                 *,
                 intervals: typing.Optional[typing.List[GraphInterval]] = None,
                 width: typing.Optional[int] = None,
                 height: typing.Optional[int] = None
                 ):
        self._munin_directory = munin_directory
        self._end_time: datetime.datetime = end_time
        self._intervals = intervals or GraphInterval.default_intervals()
        self._width = width or 800
        self._height = height or 300
        self._graphs = GraphResult()

    def run(self):
        loader = GraphLoader(os.path.join(self._munin_directory, 'datafile'))
        loader.load()
        config = loader.config

        g = GraphWriter(self._munin_directory, config, self._graphs, self._end_time, self._width, self._height)
        g.generate(self._intervals)

    @property
    def graph_result(self) -> GraphResult:
        return self._graphs

    def save_to_yaml(self, filename: str):
        _yaml.save_to_yaml(self._graphs, filename)

    def save_to_directory(self, directory: str, create: bool = False):
        if create:
            os.makedirs(directory, exist_ok=True)

        for graph in self._graphs.graphs:
            filename = os.path.join(directory,
                                    f'{graph.category}-{graph.short_name}-{graph.interval_type.lower()}.png')

            with open(filename, 'wb') as f:
                f.write(graph.image)
