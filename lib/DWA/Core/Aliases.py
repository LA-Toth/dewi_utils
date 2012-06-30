from DWA.Core.State import main_config
class Aliases(object):
    def __init__(self, config=None):
        if not config:
            config = main_config
        self.aliases = config.get_program_config('alias')
        if not self.aliases:
            self.aliases = dict()


    def get_alias(self, name):
        try:
            return self.aliases[name]
        except KeyError:
            return None


    def get_alias_names(self):
        return list(self.aliases.keys())
