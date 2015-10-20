from .base import Base


class Manifest(Base):
    keys = ['name', 'version', 'description', 'model', 'dependencies',
            'languages', 'license', 'compatibility', 'files', 'size']

    def __init__(self, defaults=None):
        defaults = defaults or {}
        self.name = defaults.get('name')
        self.version = defaults.get('version', {})
        self.description = defaults.get('description')
        self.model = defaults.get('model')
        self.dependencies = defaults.get('dependencies')
        self.languages = defaults.get('languages')
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')
        self.files = defaults.get('files', {})
        self.size = defaults.get('size')

    def is_valid(self):
        if not self.size or self.size <= 0:
            raise Exception('invalid size %s' % str(self.size))
