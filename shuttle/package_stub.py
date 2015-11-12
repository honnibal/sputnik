import semver

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

    def package_name(self):
        return '%s-%s' % (self.name, self.version)

    def is_valid(self):
        pass

    def is_compatible(self):
        if self.s.name:
            compatible_version = self.compatibility.get(self.s.name)
            if not compatible_version:
                return False

            if self.s.version:
                return semver.match(self.s.version, compatible_version)

            return False
        return True

    @property
    def ident(self):
        return '%s-%s' % (self.name, self.version)
