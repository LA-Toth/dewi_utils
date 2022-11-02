# Copyright 2017-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import re

from dewi_utils.rrdtool.config import GraphConfig, Host, Plugin


class ConfigModifier:
    def modify(self, config: GraphConfig):
        self._modify_plugins(config)

    def _modify_plugins(self, config: GraphConfig):
        for d, h, plugin_name in config.plugins:
            self._modify_plugin(config.domains[d].hosts[h].plugins[plugin_name])

    def _modify_hosts(self, config: GraphConfig):
        for d, h in config.hosts:
            self._modify_host(config.domains[d].hosts[h])

    def _modify_plugin(self, plugin: Plugin):
        pass

    def _modify_host(self, host: Host):
        pass


class IgnoreLoopbackDisks(ConfigModifier):
    def _modify_plugin(self, plugin: Plugin):
        if plugin.category != 'disk':
            return
        plugin.field_order = [x for x in plugin.field_order if not x.startswith('loop')]


class RewriteDiskstatsLabels(ConfigModifier):
    ENDINGS = ['iops', 'throughput']
    PLUGIN_NAMES = [f'diskstats_{x}' for x in ENDINGS]

    def _modify_plugin(self, plugin: Plugin):
        if plugin.category != 'disk' or plugin.name not in self.PLUGIN_NAMES:
            return

        plugin.options['graph_vlabel'] = 'IO/second' if plugin.name.endswith('iops') else 'Bytes/second'

        for f in plugin.field_order:
            field = plugin.fields[f]

            if field.name.endswith('_rdio'):
                field.options['label'] = 'Read IO ({})'.format(field.options['label'])
            elif field.name.endswith('_wrio'):
                field.options['label'] = 'Written IO ({})'.format(field.options['label'])
            elif field.name.endswith('_rdbytes'):
                field.options['label'] = 'Read bytes ({})'.format(field.options['label'])
            elif field.name.endswith('_wrbytes'):
                field.options['label'] = 'Written bytes ({})'.format(field.options['label'])


class SeparateDiskstatsPluginsPerDevice(ConfigModifier):
    ENDINGS = ['iops', 'throughput']
    PLUGIN_NAMES = [f'diskstats_{x}' for x in ENDINGS]

    def modify(self, config: GraphConfig):
        self._modify_hosts(config)

    def _modify_host(self, host: Host):
        plugin_names = list(host.plugins.keys())
        idx = -1

        while idx < len(plugin_names) - 1:
            idx += 1
            plugin = host.plugins[plugin_names[idx]]

            if plugin.category != 'disk' or plugin.name not in self.PLUGIN_NAMES:
                continue

            new_plugins = self._rewrite_plugin(plugin)

            del host.plugins[plugin_names[idx]]

            for new_plugin in new_plugins:
                host.plugins[new_plugin.name] = new_plugin

    def _rewrite_plugin(self, plugin: Plugin) -> list[Plugin]:
        result = list()

        graph_type = 'IO' if plugin.name.endswith('iops') else 'Bytes'

        for f in plugin.field_order:
            m = re.match(r'^(.+)_rd(io|bytes)$', f)
            if not m:
                continue

            device = m.group(1)
            read_name = f
            write_name = re.sub(r'^(.*_)rd(io|bytes)$', r'\1wr\2', read_name)

            new_plugin = Plugin()
            result.append(new_plugin)

            if plugin.name.endswith('_iops'):
                new_plugin.title = f'Disk IOs for /dev/{device}'
            else:
                new_plugin.title = f'Disk throughput for /dev/{device}'
            new_plugin.name = f'{plugin.name}_{device}'
            new_plugin.category = plugin.category
            new_plugin.period = plugin.period
            new_plugin.field_order = 'read write'.split()
            new_plugin.options = {
                'graph_args': plugin.options['graph_args'],
                'graph_vlabel': f'{graph_type}/second',
            }

            rfield = plugin.fields[read_name]
            rfield.name = 'read'
            rfield.options['label'] = 'Read ' + graph_type

            wfield = plugin.fields[write_name]
            wfield.name = 'write'
            wfield.options['label'] = 'Written ' + graph_type

            new_plugin.fields[rfield.name] = rfield
            new_plugin.fields[wfield.name] = wfield

        return result
