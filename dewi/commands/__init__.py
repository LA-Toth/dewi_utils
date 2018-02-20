# Copyright 2015-2018 Laszlo Attila Toth
# Distributed under the terms of the GNU Lesser General Public License v3

import collections

from dewi.core.context import Context
from dewi.loader.plugin import Plugin


class ImageHandlerCommandsPlugin(Plugin):
    def get_description(self):
        return "Commands to collect / sort / copy / delete images (photos)"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi.commands.collect_images.ImageCollectorPlugin',
            'dewi.commands.deduplicate_images.ImageDeduplicatorPlugin',
            'dewi.commands.safe_delete_images.SafeEraserPlugin',
            'dewi.commands.select_images.ImageSelectorPlugin',
        }

    def load(self, c: Context):
        pass


class CommandsPlugin(Plugin):
    def get_description(self) -> str:
        return "Commnands of DEWI"

    def get_dependencies(self) -> collections.Iterable:
        return {
            'dewi.commands.ImageHandlerCommandsPlugin',
            'dewi.commands.edit.edit.EditPlugin',
            'dewi.commands.filesync.FileSyncPlugin',
            'dewi.commands.license.LicensePlugin',
            'dewi.commands.lithurgical.LithurgicalPlugin',
            'dewi.commands.split_zorp_log.SplitZorpLogPlugin',
            'dewi.commands.ssh_ubuntu_windows.SshToUbuntuOnWindowsPlugin',
        }

    def load(self, c: Context):
        pass
