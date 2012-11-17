class Base(object):
    def __init__(self):
        self._config_file = None

    def open(self, filename):
        self._config_file = filename
        self._open()

    def _open(self):
        raise NotImplementedError

    def write(self):
        raise NotImplementedError

    def get(self, path):
        raise NotImplementedError

    def set(self, path, value):
        raise NotImplementedError
