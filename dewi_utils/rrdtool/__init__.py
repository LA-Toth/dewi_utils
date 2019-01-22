# Copyright 2017 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

"""
Representing and writing Munin graphs from .rrd files.
Some parts of the code are based on Munin's lib/Munin/Master/Graph.pm

Sometimes I copied rrdtool parameters as is, as it does not worth to alter it, as it cannot be use without
those parameters.

Munin datafile is not really documented,
a good starting point: https://github.com/mvonthron/munin-influxdb/blob/master/munininfluxdb/settings.py
"""
