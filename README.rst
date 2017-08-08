DEWI: A developer tool and framework
====================================

Name
----
DEWI: Old Welsh form of David

The name is chosen because of the similarity to DWA, which was the project's
original name, which stands for Developer's Work Area.


Purpose
-------

As the name implies the original purpose was to add tools - commands - helping
product development.

Now it is my toolchain written in Python, and it can be used for several different
tasks, such as edit files or sync file source to a remote location, manage photos
or images, and finally it is a framework of other unpublished codes.


Installation
------------

It can be installed from source::

        python3 setup.py

Or from pip::

        pip install dewi


Usage as a command-line tool
----------------------------

Common usage
~~~~~~~~~~~~

To print its help::

        dewi -h

An example: I want to open ~/.ssh/known_hosts at line 123, and it's
listed on the console as ~/.ssh/known_hosts:123. After copy-paste::

        dewi edit ~/.ssh/known_hosts:123

And it starts `vim` with arguments `~/.ssh/known_hosts +123`


Run commands from specific plugin(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is an example plugin in file ``dewi/commands/sample.py``, and a command.
This command doesn't do too much, simply exits with exit status `42`::

        dewi -p dewi.commands.sample.SamplePlugin sample


Usage as a plugin framework
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A minimal example can be found in the ``samples/as_framework`` directory,
the application is named as Steven.

Assuming that it's already created, it can be the aforementioned way::

        dewi -p example.my.custom.Plugin mycustom-command
        dewi -p steven.StevenPlugin xssh ....

The exact plugin can be hidden if there is a main entry point or script:

.. code-block:: python

    #!/usr/bin/env python3
    from dewi.core.application import MainApplication
    from dewi.loader.loader import PluginLoader


    def main():
        args = ['-p', 'steven.StevenPlugin'] + sys.argv[1:]

        loader = PluginLoader()
        app = MainApplication(loader, 'steven')
        app.run(args)


    if __name__ == '__main__':
        main()


Usage as a regular Python library
---------------------------------

Some parts of DEWI can be used as regular Python library, without the Plugin
boilerplate. A simple example is creating a somewhat typesafe (config) tree:

.. code-block:: python

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


    # ....
    sc = SampleConfig()
    sc.get_main_node().hw.mem_size = 1024  # OK
    sc.set('root.hw.mem_size', 1024)       # OK
    sc.set('root.hw.memsize', 1024)        # NOT OK, typo

    # but...
    c = Config()
    c.set('root.hw.mem_size', 1024)  # OK
    c.set('root.hw.memsize', 1024)   # OK, but typo

As you can see, DEWI can be used as library, and it can contain slightly different
solutions of the same problem.


Current features
----------------

* Plugin and command frameworks
* A configuration tree which is a smart dict, ``Config``, in ``dewi.config.config``
* A typesafe tree node for config tree, ``Node``, in ``dewi.config.node``
* Processing files from a directory subtree by modules in ``dewi.module_framework.module``
* Message / Messages classes for module framework in ``dewi.module_framework.messages``
* Log event processing module base based on the module framework in ``dewi.logparser.loghandler``
* Log file processing class, ``LogHandlerModule`` also in ``dewi.logparser.loghandler``
* Realtime sync framework in ``dewi.realtime_sync`` with ``filesync`` command
* Commands for collecting and sorting images (photos)
* Modules for
   * Kayako REST API in ``dewi.utils.kayako_rest``
   * network card vendor lookup in ``dewi.utils.network``
   * Converting XML to a dict in ``dewi.utils.xml``
   * Looking up of executable binaries in ``dewi.utils.process``
   * enhancing dicts in ``dewi.utils.dictionaries``
   * Events in a lithurgical year (Hungarian Lutheran) in ``dewi.utils.lithurgical``