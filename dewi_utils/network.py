# Copyright 2016-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import os
import re
from urllib.request import urlopen

import yaml


class NetworkCardVendors:
    URL = 'http://standards-oui.ieee.org/oui/oui.txt'
    UNKNOWN_VENDOR = 'UNKNOWN Vendor'

    def __init__(self, file_name: str, prefix_to_vendor_map: dict | None = None,
                 *,
                 enable_debug: bool = False,
                 debug_prefix: str | None = None,
                 without_network: bool | None = None):
        self._file_name_base = file_name
        self._vendor_map = prefix_to_vendor_map or dict()
        self._loaded = False
        self._without_network = without_network or False

        if self._file_name_base.endswith('.yml'):
            self._file_name_base = self._file_name_base[:-4]

        self._file_name = self._file_name_base + '.yml'
        self._original_file = self._file_name_base + '.txt'

        self._enable_debug = enable_debug
        self._debug_prefix = debug_prefix + ' ' if debug_prefix else ''

    def get_vendor(self, mac_or_prefix: str):
        prefix = mac_or_prefix.replace('-', '').replace(':', '')[:6].upper()

        try:
            return self._vendor_map[prefix]
        except KeyError:
            if not self._loaded:
                self._update_vendor_map()
            return self._vendor_map.get(prefix, self.UNKNOWN_VENDOR)

    def _update_vendor_map(self):
        if self._without_network:
            self._loaded = True
            return

        if not os.path.exists(self._file_name):
            macs = self._update_file_cache()
        else:
            self._print_debug("Loading Network Card Vendor Cache")

            with open(self._file_name) as f:
                macs = yaml.load(f)

        self._vendor_map.update(macs)
        self._loaded = True

    def _update_file_cache(self):
        self._print_debug("Updating Network Card Vendor Cache")
        if not os.path.exists(self._original_file):
            self._fetch_original_file()
        self._print_debug("Regenerating Network Card Vendor Cache")

        macs = dict()
        with open(self._original_file, encoding='UTF-8', errors='surrogateescape') as src:
            for line in src:
                if '(base 16)' in line:
                    m = re.match('^([A-F0-9]+)\s+\(base 16\)\s+(.*)$', line)
                    if m:
                        macs[m.group(1)] = m.group(2)
            with open(self._file_name, 'w') as dst:
                yaml.dump(macs, dst, indent=4, default_flow_style=False)
        self._print_debug("Network Card Vendor Cache is regenerated")

        return macs

    def _fetch_original_file(self):
        with urlopen(self.URL) as response:
            with open(self._file_name_base + '.txt', 'wb') as f:
                f.write(response.read())

    def _print_debug(self, msg: str):
        if self._enable_debug:
            print(self._debug_prefix + msg)
