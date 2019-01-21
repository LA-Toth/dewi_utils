DEWI Utils: small utilities
====================================

Name
----
DEWI: Old Welsh form of David

The name is chosen because of the similarity to DWA, which was the project's
original name, which stands for Developer's Work Area.


Purpose
-------

Several smaller Python modules can be created to
help other codes, a bunch of them is added to this repository.
These can be either used by DEWI's command module, dewi_commands_,
or by applications based on the dewi_core.

.. _dewi_commands: https://github.com/LA-Toth/dewi_commands
.. _dewi_core: https://github.com/LA-Toth/dewi_core


Installation
------------

It can be installed from source::

        python3 setup.py

Or from pip::

        pip install dewi_utils


Modules
-------

* Unpack archives - currently only .zip files - in ``dewi_utils.archives``
* Kayako REST API in ``dewi_utils.kayako_rest``
* network card vendor lookup in ``dewi_utils.network``
* Converting XML to a dict in ``dewi_utils.xml``
* Looking up of executable binaries in ``dewi_utils.process``
* enhancing dicts in ``dewi_utils.dictionaries``
* Events in a lithurgical year (Hungarian Lutheran) in ``dewi_utils.lithurgical``
* Write a dict into an output file or stdout in ``dewi_utils.yaml``
