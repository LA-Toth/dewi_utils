# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import datetime
import os.path
import shlex
import subprocess

from dewi_core.config.node import Node, NodeList
from dewi_core.logger import log_info
from dewi_utils.rrdtool import config
from dewi_utils.rrdtool.interval import GraphInterval, GraphIntervalType
from ..threading import Job, JobParam, Pool


class GraphNode(Node):
    def __init__(self):
        self.short_name = ''
        self.title = ''
        self.title_suffix = ''
        self.category = ''
        self.interval_type: GraphIntervalType = None
        self.start_time: int = 0
        self.end_time: int = 0
        self.image: bytearray = None


class GraphResult(Node):
    def __init__(self):
        self.graphs: list[GraphNode] = NodeList(GraphNode)


class GraphWriter:
    """
    Writing a graph based
    """
    DEFAULT_WIDTH = 400
    DEFAULT_HEIGHT = 175

    def __init__(self,
                 munin_directory: str,
                 config: config.GraphConfig,
                 output: GraphResult,
                 last_update_date_time: datetime.datetime | None,
                 width: int | None = None,
                 height: int | None = None,
                 parallel_count: int = 1
                 ):
        self._munin_directory = munin_directory
        self._config = config
        self._output = output
        self._last_update_date_time: datetime.datetime = last_update_date_time
        self._last_update_timestamp = int(last_update_date_time.timestamp())
        self._width = width or self.DEFAULT_WIDTH
        self._height = height or self.DEFAULT_HEIGHT
        self._parallel_count = parallel_count

        if self._width < 200 or self._height < 100:
            self._width = self.DEFAULT_WIDTH
            self._height = self.DEFAULT_HEIGHT

        self._header_args = [
            'graph',
            '--font', 'TITLE:12:Sans',
            '--font', 'DEFAULT:7',
            '--font', 'LEGEND:7',

            '--color', 'BACK#F0F0F0',  # Area around the graph
            '--color', 'FRAME#F0F0F0',  # Line around legend spot
            '--color', 'CANVAS#FFFFFF',  # Graph background, max contrast
            '--color', 'FONT#666666',  # Some kind of gray
            '--color', 'AXIS#CFD6F8',  # And axis like html boxes
            '--color', 'ARROW#CFD6F8',  # And arrow, ditto.

            '--border', '0',

            '--watermark', "DEWI - dewi_utils.rrdtool",
            '--slope-mode',
            '--disable-rrdtool-tag',
            '-',
            '--width', self._width,
            '--height', self._height,
            '--imgformat', 'PNG',
        ]

        self._env_tz = self._prepare_env_tz()

    def _prepare_env_tz(self) -> str | None:
        if self._last_update_date_time is not None:
            offset = self._last_update_date_time.utcoffset()

            if offset:
                offset = offset.total_seconds()
                # Strange, but inversion is needed for rrdtool
                sign = '-' if offset > 0 else '-'
                offset = int(abs(offset)) // 60
                h, m = offset // 60, offset % 60
                log_info(f'{self.__class__.__name__}: Set TZ', tz=f'UTC{sign}{h:02d}:{m:02d}')
                return f'UTC{sign}{h:02d}:{m:02d}'

        return None

    def generate(self, intervals: list[GraphInterval]):
        log_info(f'Generating graphs in {self._parallel_count} thread(s)')
        if self._parallel_count == 1:
            job = GraphWriterJob(self._munin_directory, self._config, self._output, self._last_update_date_time,
                                 self._last_update_timestamp,
                                 self._width, self._height, self._header_args, self._env_tz)
            job.generate_all(intervals)

        else:
            pool = Pool(state=self, thread_count=self._parallel_count)
            job_params: list[JobParam] = []

            for domain, host, plugin in self._config.plugins:
                for interval in intervals:
                    job_params.append(JobParam(
                        self,
                        self._munin_directory, self._config, self._output, self._last_update_date_time,
                        self._last_update_timestamp,
                        self._width, self._height, self._header_args, self._env_tz,
                        self._config.domains[domain].hosts[host].plugins[plugin],
                        interval))

            pool.run(GraphWriterJob, job_params)


class GraphWriterJob(Job):
    # Greens Blues   Oranges Dk yel  Dk blu  Purple  lime    Reds    Gray
    COLORS = \
        """00CC00 0066B3 FF8000 FFCC00 330099 990099 CCFF00 FF0000 808080
        008F00 00487D B35A00 B38F00     6B006B 8FB300 B30000 BEBEBE
        80FF80 80C9FF FFC080 FFE680 AA80FF EE00CC FF8080
        666600 FFBFFF 00FFCC CC6699 999900""".split()

    def __init__(self,
                 munin_directory: str,
                 config: config.GraphConfig,
                 output: GraphResult,
                 last_update_date_time: datetime.datetime,
                 last_update_timestamp: int,
                 width: int,
                 height: int,
                 header_args: list[str],
                 env_tz: str | None,
                 plugin: config.Plugin | None = None,
                 interval: GraphInterval | None = None,
                 ):
        self._munin_directory = munin_directory
        self._config = config
        self._output = output
        self._last_update_date_time: datetime.datetime = last_update_date_time
        self._last_update_timestamp = last_update_timestamp
        self._width = width
        self._height = height
        self._header_args = header_args
        self._env_tz = env_tz

        self._plugin = plugin
        self._interval = interval

        self._env = self._prepare_env()

    def _prepare_env(self):
        env = dict(os.environ)
        env['LANG'] = 'en_US.UTF-8'
        env['LC_LANG'] = 'en_US.UTF-8'

        if self._env_tz:
            env['TZ'] = self._env_tz

        return env

    def generate_all(self, intervals: list[GraphInterval]):
        for domain, host, plugin in self._config.plugins:
            for interval in intervals:
                result = self._generate_graph_of_interval(self._config.domains[domain].hosts[host].plugins[plugin],
                                                          interval)
                self._output.graphs.append(result)

    def _generate_graph_of_interval(self, plugin: config.Plugin,
                                    interval: GraphInterval) -> GraphNode:
        result = GraphNode()
        result.interval_type = interval.interval_name
        result.title = plugin.title
        result.title_suffix = interval.title_suffix
        result.short_name = plugin.name
        result.category = plugin.category

        args = list(self._header_args)

        start_time, end_time = interval.range(self._last_update_timestamp)
        args += [
            '--start', start_time,
            '--end', end_time,
            '--title', f'{result.title} - {result.title_suffix}'
        ]

        result.start_time, result.end_time = start_time, end_time

        printf_format = None

        for opt_name in plugin.options:
            opt_value = plugin.options[opt_name].replace('${graph_period}', plugin.period)

            if opt_name == 'graph_args':
                args += shlex.split(opt_value)
            elif opt_name == 'graph_printf':
                printf_format = opt_value
            elif opt_name == 'graph_vlabel':
                args += ['--vertical-label', opt_value]
            elif opt_name == 'graph_scale' and opt_value.lower() == 'no':
                args += ['--units-exponent', '0']

        if printf_format is None:
            printf_format = '%7.2lf%s'

        label_max = self._get_max_label_length(plugin)
        args += [
            'COMMENT:' + ' ' * label_max,
            'COMMENT: Cur\\:',
            'COMMENT:Min\\:',
            'COMMENT:Avg\\:',
            'COMMENT:Max\\:  \\j',
        ]

        field_names = plugin.field_order if len(plugin.field_order) else plugin.fields.keys()

        field_number = -1
        for field_name in field_names:
            field_number += 1
            field = plugin.fields[field_name]

            for i in ['g:AVERAGE', 'i:MIN', 'a:MAX', 'c:LAST']:
                short_name, long_name = i.split(':')
                filename = os.path.join(self._munin_directory, field.filename)
                args.append(
                    f'DEF:{short_name}{field.name}={filename}:42:{long_name}'
                )

            color = self.COLORS[field_number % len(self.COLORS)]
            label = field.options['label'].replace(':', '\\:') if 'label' in field.options else ''
            args.append(
                f"{field.options['draw']}:g{field.name}#{color}:{label}"
            )

            for i in ['c:LAST', 'g:AVERAGE', 'i:MIN', ]:
                short_name, long_name = i.split(':')
                args.append(
                    f"GPRINT:{short_name}{field.name}:{long_name}:{printf_format}"
                )
            args.append(
                f"GPRINT:a{field.name}:MAX:{printf_format}\\j"
            )

        last_updated = str(self._last_update_date_time).replace(':', '\\:')
        args.append(
            f"COMMENT:Last update\\: {last_updated}\\r"
        )

        result.image = subprocess.check_output(['rrdtool'] + [str(x) for x in args], env=self._env)

        return result

    def _get_max_label_length(self, plugin: config.Plugin):
        result = 0

        for name in plugin.fields:
            field = plugin.fields[name]

            if 'label' in field.options:
                s = len(field.options['label'])
                if s > result:
                    result = s
        return result

    def generate_single(self):
        self._output.graphs.append(
            self._generate_graph_of_interval(self._plugin, self._interval)
        )

    def _run(self):
        self.generate_single()
