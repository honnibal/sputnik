import os
import io
from hashlib import sha256
import shutil
from glob import glob

from . import util
from . import validation
from . import default
from .manifest import Manifest
from .archive import NewArchive
from .base import Base
from .package_string import PackageString


class Package(Manifest):  # installed package
    def __init__(self, path, **kwargs):
        self.path = path
        defaults = util.json_load(os.path.join(path,
            default.META_FILENAME))['package']

        super(Package, self).__init__(defaults, **kwargs)

    @classmethod
    def find(cls, package_string, data_path, s):
        packages = []

        for p in os.listdir(data_path):
            if p.startswith('.') or not os.path.isdir(os.path.join(data_path, p)):
                continue

            package = Package(os.path.join(data_path, p), s=s)

            if not package_string:
                packages.append(package)
                continue

            ps = PackageString(package_string)
            if ps.match(PackageString(name=package.name,
                                      version=package.version)):
                packages.append(package)

        return packages

    def remove(self):
        if not os.path.isdir(self.path):
            raise Exception("not installed")

        tmp = self.path + ".remove"

        # cleanup remove
        if os.path.exists(self.path):
            self.s.log('remove %s' % self.path)
            shutil.move(self.path, tmp)
            shutil.rmtree(tmp)


class PackageRecipe(Base):  # package.json recipe
    keys = ['name', 'version', 'description', 'include', 'model',
            'dependencies', 'languages', 'license', 'compatibility']

    def __init__(self, path, **kwargs):
        if not validation.is_package_path(path):
            raise Exception("%r must be a directory" % path)

        self.path = path
        package_json_path = os.path.join(path, "package.json")
        defaults = util.json_load(package_json_path)

        ps = PackageString(
            name=defaults.get('name'),
            version=defaults.get('version', {}))

        self.name = ps.name
        self.version = ps.version
        self.description = defaults.get('description')
        self.include = defaults.get('include')
        self.model = defaults.get('model')
        self.dependencies = defaults.get('dependencies')
        self.languages = defaults.get('languages')
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')

        super(PackageRecipe, self).__init__(**kwargs)

    def is_valid(self):
        if not self.include:
            raise Exception("missing include")

    def build(self, archive_path):
        with NewArchive(self, archive_path, sha256, s=self.s) as archive:
            self.s.log("build %s" % archive.path)

            for include in self.include:
                for path in glob(os.path.join(self.path, include)):
                    archive.add_file(path)
            return archive
