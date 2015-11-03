import semver

from .base import Base


class Manifest(Base):
    keys = ['name', 'version', 'description', 'model', 'dependencies',
            'languages', 'license', 'compatibility']

    def __init__(self, defaults=None, **kwargs):
        defaults = defaults or {}
        self.name = defaults.get('name')
        self.version = defaults.get('version', {})
        self.description = defaults.get('description')
        self.model = defaults.get('model')
        self.dependencies = defaults.get('dependencies')
        self.languages = defaults.get('languages')
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')

        super(Manifest, self).__init__(**kwargs)

    def package_name(self):
        return '%s-%s' % (self.name, self.version)

    def is_valid(self):
        pass

    def is_compatible(self):
        if self.s.name and self.s.version:
            compatible_version = self.compatibility.get(self.s.name)
            if not compatible_version:
                return False
            return semver.match(self.s.version, compatible_version)
        return True
