# Copyright 2017-2021 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import os.path
import re

from dewi_core.logger import log_info
from dewi_utils.rrdtool.config import GraphConfig


class GraphLoader:
    def __init__(self, data_file_path: str):
        self._data_file_path = data_file_path

        self.config = GraphConfig()

    def load(self):
        log_info('Loading Munin datafile', path=self._data_file_path)
        self._load_file()
        self._postprocess()

    def _load_file(self):
        with open(self._data_file_path) as f:
            for line in f:
                line = line.rstrip('\r\n').rstrip('\n')
                m = re.match(r'^(.+?);(.+?):(.+?)\.(.+?) (.+)$', line)
                if m:
                    self._read_entry(m.group(1), m.group(2), m.group(3), m.group(4), m.group(5))

    def _read_entry(self, domain: str, host: str, name: str, key: str, value: str):
        if key == 'graph_order':
            # Let's make it unique
            self.config.domains[domain].hosts[host].plugins[name].field_order = self._uniq(value.split())
        elif key == 'graph_title':
            self.config.domains[domain].hosts[host].plugins[name].title = value
        elif key == 'graph_period':
            self.config.domains[domain].hosts[host].plugins[name].period = value
        elif key == 'graph_category':
            self.config.domains[domain].hosts[host].plugins[name].category = value
        elif key.startswith('graph_'):
            if key == 'graph_args':
                value = value.rstrip(';')
            self.config.domains[domain].hosts[host].plugins[name].options[key] = value
        else:
            field, key = key.split('.', 1)
            self.config.domains[domain].hosts[host].plugins[name].fields[field].options[key] = value

    def _uniq(self, l: list) -> list:
        used = set()
        return [x for x in l if x not in used and (used.add(x) or True)]

    def _postprocess(self):
        for domain, host, plugin in self.config.plugins:
            self.config.domains[domain].hosts[host].plugins[plugin].name = plugin
            if self.config.domains[domain].hosts[host].plugins[plugin].period is None:
                self.config.domains[domain].hosts[host].plugins[plugin].period = 'seconds'

        for domain in self.config.domains:
            self.config.domains[domain].name = domain
            for host in self.config.domains[domain]:
                self.config.domains[domain].hosts[host].name = host

        for domain, host, plugin, field_ in self.config.fields:
            field = self.config.domains[domain].hosts[host].plugins[plugin].fields[field_]
            field.name = field_

            if 'type' not in field.options:
                field.options['type'] = 'GAUGE'
            type_suffix = field.options['type'].lower()[0]
            field.filename = os.path.join(domain, f'{host}-{plugin.replace(".", "-")}-{field.name}-{type_suffix}.rrd')
            if 'draw' not in field.options:
                field.options['draw'] = 'LINE1'

        return
