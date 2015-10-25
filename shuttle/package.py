import os
import io
from hashlib import sha256
from glob import glob
import shutil

from . import util
from . import validation
from . import default
from .manifest import Manifest
from .archive import NewArchive
from .base import Base


class Package(Manifest):  # installed package
    def __init__(self, path):
        self.path = path
        defaults = util.json_load(os.path.join(path,
            default.meta_manifest_path))

        Manifest.__init__(self, defaults)

    @classmethod
    def find(cls, package_string, data_path):
        package_glob = os.path.join(data_path, package_string)
        return [Package(p) for p in glob(package_glob)]

    def remove(self):
        if not os.path.isdir(self.path):
            raise Exception("not installed")

        tmp = self.path + ".remove"

        # cleanup remove
        if os.path.exists(self.path):
            print("remove", self.path)
            shutil.move(self.path, tmp)
            shutil.rmtree(tmp)


class PackageRecipe(Base):  # package.json recipe
    keys = ['name', 'version', 'description', 'include', 'model',
            'dependencies', 'languages', 'license', 'compatibility']

    def __init__(self, path):
        if not validation.is_package_path(path):
            raise Exception("%r must be a directory" % path)

        self.path = path
        package_json_path = os.path.join(path, "package.json")
        defaults = util.json_load(package_json_path)

        self.name = defaults.get('name')
        self.version = defaults.get('version', {})
        self.description = defaults.get('description')
        self.include = defaults.get('include')
        self.model = defaults.get('model')
        self.dependencies = defaults.get('dependencies')
        self.languages = defaults.get('languages')
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')

    def is_valid(self):
        if not self.include:
            raise Exception("missing include")

    def build(self, archive_path):
        with NewArchive(self, archive_path, sha256) as archive:
            print("build", archive.filename)
            for include in self.include:
                for path in glob(include):
                    archive.add_file(path)
            return archive
