from dewi.config.config import Config
from dewi.config.node import Node


class Hardware(Node):
    def __init__(self):
        self.hw_type: str = ''
        self.mem_size: int = None
        self.mem_free: int = None
        self.mem_mapped: int = None


class MainNode(Node):
    def __init__(self):
        # Handling as str, but None is used as unset
        self.version: str = None
        self.hw = Hardware()
        # ... further fields

    def __repr__(self) -> str:
        return str(self.__dict__)


class SampleConfig(Config):
    def __init__(self):
        super().__init__()
        self.set('root', MainNode())

    def get_main_node(self) -> MainNode:
        return self.get('root')
