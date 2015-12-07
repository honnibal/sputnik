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


class InvalidPathPartsException(Exception): pass
class NotFoundException(Exception): pass
class NotIncludedException(Exception): pass


def get_path(*path_parts):
    if any([p for p in path_parts if '/' in p or '\\' in p]):
        raise InvalidPathPartsException('avoid / and \\ in path parts: %s' % path_parts)
    return os.path.join(*path_parts)


class Package(PackageStub):  # installed package
    def __init__(self, **kwargs):
        self.path = kwargs.pop('path')
        self.meta = util.json_load(os.path.join(self.path,
                                                default.META_FILENAME))

        kwargs['defaults'] = self.meta['package']
        super(Package, self).__init__(**kwargs)

    def has_file(self, *path_parts):
        path = get_path(*path_parts)
        return any([m for m in self.manifest if m['path'] == path])

    def file_path(self, *path_parts, **kwargs):
        require = kwargs.pop('require', True)
        path = get_path(*path_parts)

        if not self.has_file(*path_parts):
            if require:
                raise NotIncludedException('package does not include file: %s' % path)
            return

        res = os.path.join(self.path, path)
        if not os.path.isfile(res):
            if require:
                raise NotFoundException('file not found: %s' % res)
            return
        return res

    def dir_path(self, *path_parts, **kwargs):
        require = kwargs.pop('require', True)
        path = get_path(*path_parts)

        res = os.path.join(self.path, path)
        if not os.path.isdir(res):
            if require:
                raise NotFoundException('dir not found: %s' % res)
        return res

    def _load(self, func, *path_parts, **kwargs):
        require = kwargs.pop('require', True)
        default = kwargs.pop('default', None)

        try:
            path = self.file_path(*path_parts)
        except (NotIncludedException, NotFoundException):
            if require and not default:
                raise
            return default
        return func(io.open(path, **kwargs))

    def load_utf8(self, func, *path_parts, **kwargs):
        kwargs.update({'mode': 'r', 'encoding': 'utf8'})
        return self._load(func, *path_parts, **kwargs)

    def load(self, func, *path_parts, **kwargs):
        kwargs.update({'mode': 'rb'})
        return self._load(func, *path_parts, **kwargs)

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
        with NewArchive(self, archive_path, md5,
                        base_path=self.path, s=self.s) as archive:
            self.s.log("build %s" % archive.path)

            for include in self.include:
                for path in glob(os.path.join(self.path, include)):
                    if os.path.isfile(path):
                        archive.add_file(path)
            return archive
