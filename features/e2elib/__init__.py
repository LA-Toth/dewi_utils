from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class PluginTestPlugin(Plugin):
    def get_description(self):
        return "A simple plugin to test plugin loader via BDD"

    def get_dependencies(self):
        return ('dewi.core.CorePlugin',)

    def load(self, c: Context):
        c.register('test_result', 42 + c['commandregistry'].get_command_count())
