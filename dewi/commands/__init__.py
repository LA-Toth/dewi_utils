# Copyright (c) 2015 Laszlo Attila Toth
# Distributed under the terms of the GNU General Public License v3

import collections

from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class CommandsPlugin(Plugin):
    def get_description(self) -> str:
        return "Commnands of DEWI"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi.core.CorePlugin',
            'dewi.commands.collect_images.ImageCollectorPlugin',
            'dewi.commands.deduplicate_images.ImageDeduplicatorPlugin',
            'dewi.commands.edit.edit.EditPlugin',
            'dewi.commands.filesync.FileSyncPlugin',
            'dewi.commands.select_images.ImageSelectorPlugin',
            'dewi.commands.split_zorp_log.SplitZorpLogPlugin',
            'dewi.commands.ssh_ubuntu_windows.SshToUbuntuOnWindowsPlugin',
        }

    def load(self, c: Context):
        pass
