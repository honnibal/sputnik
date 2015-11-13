import os
import sys
import platform

import semver

from .command import Command


class Sputnik(object):
    def __init__(self, name=None, version=None, console=None):
        self.name = name
        if version:
            semver.parse(version)  # raises ValueError when invalid
        self.version = version
        self.console = console

    def make_command(self, *args, **kwargs):
        kwargs['s'] = self
        return Command(*args, **kwargs)

    def user_agent(self):
        uname = platform.uname()
        user_agent_vars = [
            ('Sputnik', '1.0.0'),
            (self.name, self.version),
            (platform.python_implementation(), platform.python_version()),
            (platform.uname()[0], uname[2]),
            ('64bits', sys.maxsize > 2**32)]

        return ' '.join(['%s/%s' % (k, v) for k, v in user_agent_vars if k])

    def log(self, message):
        if self.console:
            self.console.write(message + '\n')
