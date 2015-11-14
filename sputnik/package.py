import io
import os
from hashlib import md5
import shutil
from glob import glob

from . import util
from . import validation
from . import default
from .base import Base
from .new_archive import NewArchive
from .package_string import PackageString
from .package_stub import PackageStub
from .package_list import PackageList


class Package(PackageStub):  # installed package
    def __init__(self, **kwargs):
        self.path = kwargs.pop('path')
        self.meta = util.json_load(os.path.join(self.path,
                                                default.META_FILENAME))

        kwargs['defaults'] = self.meta['package']
        super(Package, self).__init__(**kwargs)

    def has_file(self, path):
        return any([m for m in self.manifest if m['path'] == path])

    def file_path(self, path):
        if not self.has_file(path):
            raise Exception('package does not include file: %s' % path)

        file_path = os.path.join(self.path, path)
        if not os.path.isfile(file_path):
            raise Exception('file not found: %s' % path)

        return file_path

    @property
    def manifest(self):
        return self.meta['manifest']

    def remove(self):
        if not os.path.isdir(self.path):
            raise Exception("not installed")

        tmp = self.path + ".remove"

        # cleanup remove
        if os.path.exists(self.path):
            self.s.log('pending remove %s' % self.path)
            shutil.move(self.path, tmp)
            self.s.log('remove %s' % self.path)
            shutil.rmtree(tmp)


class PackageRecipe(Base):  # package.json recipe
    keys = ['name', 'version', 'description', 'include',
            'license', 'compatibility']

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
        self.license = defaults.get('license')
        self.compatibility = defaults.get('compatibility')

        super(PackageRecipe, self).__init__(**kwargs)

    def is_valid(self):
        if not self.include:
            raise Exception("missing include")

    def build(self, archive_path):
        with NewArchive(self, archive_path, md5, s=self.s) as archive:
            self.s.log("build %s" % archive.path)

            for include in self.include:
                for path in glob(os.path.join(self.path, include)):
                    if os.path.isfile(path):
                        archive.add_file(path)
            return archive


class Pool(PackageList):

    package_class = Package
