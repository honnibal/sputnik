import os
import sys
import platform

from .command import Command


class Shuttle(object):
    def __init__(self, name, version, console=None):
        self.name = name
        self.version = version
        self.console = console

    def make_command(self, *args, **kwargs):
        kwargs['s'] = self
        return Command(*args, **kwargs)

    def user_agent(self):
        uname = platform.uname()
        user_agent_vars = [
            ('Shuttle', '1.0'),
            (self.name, self.version),
            (platform.python_implementation(), platform.python_version()),
            (platform.uname()[0], uname[2]),
            ('64bits', sys.maxsize > 2**32)]

        return ' '.join(['%s/%s' % (k, v) for k, v in user_agent_vars])

    def log(self, message):
        if self.console:
            self.console.write(message + '\n')
