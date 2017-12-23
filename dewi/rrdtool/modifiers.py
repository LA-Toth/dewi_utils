# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

from dewi.rrdtool.config import GraphConfig, Plugin


class ConfigModifier:
    def modify(self, config: GraphConfig):
        for d, h, plugin_name in config.plugins:
            self.modify_plugin(config.domains[d].hosts[h].plugins[plugin_name])

    def modify_plugin(self, plugin: Plugin):
        pass


class IgnoreLoopbackDisks(ConfigModifier):
    def modify_plugin(self, plugin: Plugin):
        if plugin.category != 'disk':
            return
        plugin.field_order = [x for x in plugin.field_order if not x.startswith('loop')]
