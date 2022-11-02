# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import datetime
import os
import os.path
import subprocess

import dewi_core.utils.yaml as _yaml
from dewi_utils.rrdtool.config import GraphConfig
from dewi_utils.rrdtool.interval import GraphInterval
from dewi_utils.rrdtool.loader import GraphLoader
from dewi_utils.rrdtool.modifiers import ConfigModifier
from dewi_utils.rrdtool.writer import GraphResult, GraphWriter


class RrdTool:
    """
    Core module that loads a Munin datafile and generates the graphs using 'rrdtool graph'.

    By default the graphs are generated using a specific end time,
    the start time is determined by the specified list of intervals.

    Default set of intervals is year/month/week/day, but with wider ranges, see GraphInterval type.
    The width and height of the graphs can also be specified.

    The loaded config may be post-modified for more usable and readable graphs by the `modifiers` parameter.
    """

    def __init__(self,
                 munin_directory: str,
                 end_time: datetime.datetime | None,
                 *,
                 reference_datetime: datetime.datetime | None = None,
                 modifiers: list[ConfigModifier] | None = None,
                 intervals: list[GraphInterval] | None = None,
                 width: int | None = None,
                 height: int | None = None,
                 parallel_run_count: int = 1,
                 ):
        self._munin_directory = munin_directory
        self._end_time: datetime.datetime = end_time
        self._reference_datetime: datetime.datetime = reference_datetime
        self._modifiers = modifiers
        self._intervals = intervals or GraphInterval.default_intervals()
        self._width = width or 800
        self._height = height or 300
        self._graphs = GraphResult()
        self._parallel_count = parallel_run_count

    def run(self):
        loader = GraphLoader(os.path.join(self._munin_directory, 'datafile'))
        loader.load()
        config = loader.config

        self._modify_config(config)

        if not self._end_time:
            self._calculate_end_time(config)

        g = GraphWriter(self._munin_directory, config, self._graphs, self._end_time, self._width, self._height,
                        self._parallel_count)
        g.generate(self._intervals)

    def _modify_config(self, config: GraphConfig):
        if self._modifiers is not None:
            for modifier in self._modifiers:
                modifier.modify(config)

    def _calculate_end_time(self, config: GraphConfig):
        filename = self._get_an_rrd_file_name(config)
        result = subprocess.check_output(['rrdtool', 'info', filename]).decode('UTF-8').splitlines(keepends=False)
        for line in result:
            if line.startswith('last_update = '):
                tz = self._reference_datetime.tzinfo if self._reference_datetime else None
                self._end_time = datetime.datetime.fromtimestamp(int(line.replace('last_update = ', '')), tz=tz)

    def _get_an_rrd_file_name(self, config: GraphConfig) -> str:
        d = config.domains[next(iter(config.domains))]
        h = d.hosts[next(iter(d.hosts))]
        p = h.plugins[next(iter(h.plugins))]
        f = p.fields[p.field_order[0]]
        return os.path.join(self._munin_directory, f.filename)

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
