import re

import semver


class PackageString(object):
    def __init__(self, string=None, name=None, version=None, package=None):
        if string:
            res = re.split(r'[\s-]', string, 1)
            if len(res) > 1:
                self.name, self.version = res
            elif len(res) > 0:
                self.name, self.version = res[0], None
        elif name:
            self.name = name
            self.version = version
        elif package:
            self.name = package.name
            self.version = package.version
            self.package = package
        else:
            raise Exception('invalid package string: %s' % string)

    def check_name(self, other):
        if self.name != other.name:
            raise Exception('name mismatch: %s != %s' % (self.name, other.name))

    def __gt__(self, other):
        self.check_name(other)
        return semver.compare(self.version, other.version) > 0

    def __lt__(self, other):
        self.check_name(other)
        return semver.compare(self.version, other.version) < 0

    def __eq__(self, other):
        self.check_name(other)
        return semver.compare(self.version, other.version) == 0

    def __ne__(self, other):
        return not self.__eq__(other)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)

    def __str__(self):
        return '%s %s' % (self.name, self.version)

    def match(self, other):
        return self.name == other.name and \
            (not self.version or semver.match(other.version, self.version))
