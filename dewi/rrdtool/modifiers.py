# Copyright 2017-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi.rrdtool.config import GraphConfig, Host, Plugin


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
    def modify_plugin(self, plugin: Plugin):
        if plugin.category != 'disk':
            return
        plugin.field_order = [x for x in plugin.field_order if not x.startswith('loop')]
