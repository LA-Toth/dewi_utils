DEWI: A developer tool and framework
====================================

Name
----
DEWI: Old Welsh form of David

This name is similar to DWA, which was the project's original name,
and it's stands for Developer's Work Are.


Purpose
-------

When somebody develops products for years, he has several smaller or larger
scripts which helps his development, and may have several aliases in bash,
or in his favorite shell. But these scripts can be in the same place, tested,
and so on. This is one target of DEWI, give several commands to help
the repetitive tasks.

DEWI's other target is that it can also be used a framework, it's highly
extensible, via its plugin framework, see below some example.


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


Usage as a framework
~~~~~~~~~~~~~~~~~~~~

The basic assumption is that somebody wants to use his own Python script
to start everything and use custom plugins. This can be partially done as::

        dewi -p example.my.custom.Plugin mycustom-command

But this can be hidden competely, using name e.g. `myprog`, based on
``dewi.__main__``:

.. code-block:: python

   #!/usr/bin/env python3

   import sys
   from dewi.core.application import MainApplication
   from dewi.loader.loader import PluginLoader


   def main():
       args = ['-p', 'example.my.custom.Plugin'] + sys.argv[1:]

       loader = PluginLoader()
       app = MainApplication(loader, 'myprog')
       app.run(args)

   if __name__ == '__main__':
       main()


If you need more details:

* check ``dewi.commands.edit.edit``: how to write a command with arguments
* check ``dewi.commands.sample``: how to write a custom plugin and register
  a command into it. Note that each plugin should depend on
  ``dewi.core.CorePlugin``.
