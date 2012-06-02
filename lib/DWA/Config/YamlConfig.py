# vim: sts=4 ts=8 et ai

import yaml

class YamlConfig(object):
    def __init__(self):
        self.config_file = None
        self.config = None

    def open(self, cfgfile):
        self.config_file = cfgfile
        self.config = yaml.load(file(self.config_file, 'r'))

    def write(self):
        yaml.dump(self.config, file(self.config_file, 'w'))

    def close(self):
        self.write()
        self.config_file = None
        self.config = None

    def get(self, path):
        path = path.split('/')
        i = 0;
        while i < len(path):
            if not path[i]:
                del path[i]
                i -= 1
            i += 1

        if not path:
            return None
        else:
            res = self.config
            for item in path:
                res = res[item]
            return res
