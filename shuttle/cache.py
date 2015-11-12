import os
import shutil
import hashlib
import io
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from . import uget
from . import util
from . import default
from .package_stub import PackageStub
from .package_string import PackageString
from .archive import Archive
from .base import Base


class PackageNotCompatibleException(Exception): pass


class CachedPackage(PackageStub):
    keys = PackageStub.keys + ['path']

    def __init__(self, meta, **kwargs):
        super(CachedPackage, self).__init__(meta['package'], **kwargs)

        self.data_path = kwargs.pop('data_path')
        self.meta = meta
        self.path = os.path.join(self.data_path,
                                 default.CACHE_DIRNAME, self.ident)

        assert os.path.isfile(os.path.join(self.path, default.META_FILENAME))

    @property
    def manifest(self):
        return self.meta['manifest']

    def fetch(self):
        path, checksum, url = self.meta['archive'][:3]

        full_path = os.path.join(self.path, path)

        util.makedirs(full_path)
        uget.download(self.data_path, url, full_path,
                      console=self.s.console,
                      checksum=hashlib.md5(),
                      checksum_header=util.s3_header('md5'),
                      s=self.s)

        # TODO: use checksum

        return Archive(self.path, s=self.s)

    def remove(self):
        if not os.path.isdir(self.path):
            raise Exception("not installed")

        tmp = self.path + ".remove"

        # cleanup remove
        if os.path.exists(self.path):
            self.s.log('remove %s' % self.path)
            shutil.move(self.path, tmp)
            shutil.rmtree(tmp)


class Cache(Base):
    def __init__(self, data_path, **kwargs):
        super(Cache, self).__init__(**kwargs)

        self.data_path = data_path
        self.load()

    def packages(self):
        cache_path = os.path.join(self.data_path, default.CACHE_DIRNAME)

        if not os.path.exists(cache_path):
            os.mkdir(cache_path)

        for path in os.listdir(cache_path):

            meta_path = os.path.join(cache_path, path, default.META_FILENAME)
            if not os.path.isfile(meta_path):
                continue

            meta = util.json_load(meta_path)
            yield CachedPackage(meta, data_path=self.data_path, s=self.s)

    def load(self):
        self._packages = {}
        for package in self.packages():
            self._packages[package.ident] = package

    def get(self, package_string):
        candidates = []
        query = PackageString(package_string)

        for package in self.list():
            ps = PackageString(package=package)

            if query.match(ps):
                if not package.is_compatible():
                    raise PackageNotCompatibleException(
                        'running %s %s but requires %s' %
                        (self.s.name, self.s.version, package.compatibility))

                candidates.append(ps)

        if candidates:
            return sorted(candidates)[-1].package

    def list(self):
        return self._packages.values()

    def update(self, meta, url):
        assert len(meta['archive']) == 2

        package = PackageStub(meta['package'], s=self.s)

        meta['archive'].append(urljoin(url, meta['archive'][0]))

        path = os.path.join(self.data_path, default.CACHE_DIRNAME,
                            package.ident, default.META_FILENAME)

        util.makedirs(path)
        with io.open(path, 'wb') as f:
            f.write(util.json_dump(meta))

        # TODO optimize for calling update in a loop
        self.load()
