# Copyright 2016-2022 Laszlo Attila Toth
# Distributed under the terms of the Apache License, Version 2.0

import collections.abc
import sys

import jinja2


class TemplateRenderer:
    def __init__(self, base_path: str | list[str]):
        loader = jinja2.FileSystemLoader(base_path or sys.path)
        environment = jinja2.Environment(loader=loader)
        self._environment = environment

    def render(self, template_file_path: str, template_variables: collections.abc.Mapping) -> str:
        template = self._environment.get_template(template_file_path)

        return template.render(**template_variables)
