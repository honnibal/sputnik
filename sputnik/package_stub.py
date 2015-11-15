import semver

from . import util
from .base import Base


class PackageStub(Base):
    keys = ['name', 'version', 'description', 'license', 'compatibility']

    def __init__(self, defaults=None, **kwargs):
        defaults = defaults or {}
        self.name = defaults.get('name')
        self.version = defaults.get('version')
        self.description = defaults.get('description')
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')

        super(PackageStub, self).__init__(**kwargs)

    def is_valid(self, raise_exception=False):
        res = False
        if self.name and self.version:
            res = True

        if raise_exception and not res:
            raise Exception('invalid package')
        return res

    def is_compatible(self):
        if self.s.name and self.compatibility:
            compatible_version = self.compatibility.get(self.s.name)
            if not compatible_version:
                return False

            if self.s.version:
                return semver.match(self.s.version, compatible_version)

            return False
        return True

    @property
    def ident(self):
        if self.is_valid(True):
            return util.archive_filename(self.name, self.version)
