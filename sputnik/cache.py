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
from .package_list import PackageList
from .package_stub import PackageStub
from .archive import Archive


class CachedPackage(PackageStub):
    keys = PackageStub.keys + ['path']

    def __init__(self, **kwargs):
        meta = kwargs.pop('meta')
        cache = kwargs.pop('package_list')

        kwargs['defaults'] = meta['package']

        super(CachedPackage, self).__init__(**kwargs)

        self.data_path = cache.data_path
        self.meta = meta
        self.cache = cache
        self.path = os.path.join(cache.path, self.ident)

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
            self.s.log('pending remove %s' % self.path)
            shutil.move(self.path, tmp)
            self.s.log('remove %s' % self.path)
            shutil.rmtree(tmp)

        self.cache.load()


class Cache(PackageList):

    package_class = CachedPackage

    def __init__(self, data_path, **kwargs):
        cache_path = os.path.join(data_path, default.CACHE_DIRNAME)
        kwargs['data_path'] = data_path

        super(Cache, self).__init__(cache_path, **kwargs)

    def update(self, meta, url):
        assert len(meta['archive']) == 2
        meta = dict(meta)

        package = PackageStub(meta['package'], s=self.s)

        meta['archive'].append(urljoin(url, meta['archive'][0]))

        path = os.path.join(self.path, package.ident,
                            default.META_FILENAME)

        util.makedirs(path)
        with io.open(path, 'wb') as f:
            f.write(util.json_dump(meta))

        # TODO optimize for calling update in a loop
        self.load()
