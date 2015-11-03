import os
import io
import json
import tarfile
import hashlib
import sys
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from . import default
from . import util
from . import uget
from .archive import Archive
from .manifest import Manifest
from .session import Session, GetRequest, PutRequest
from .base import Base
from .package_string import PackageString


class PackageNotFoundException(Exception): pass


class Index(Base):
    def __init__(self, data_path, repository_url, **kwargs):
        if not repository_url:
            raise Exception('invalid repository_url: %s' % repository_url)

        self.data_path = data_path
        self.repository_url = repository_url

        self.meta = {}
        self.urls = {}

        super(Index, self).__init__(**kwargs)

    def upload(self, path):
        from boto.s3.connection import S3Connection

        access_key_id = os.environ['AWS_ACCESS_KEY_ID']
        secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
        region = os.environ['AWS_REGION']
        bucket = os.environ['S3_BUCKET']

        os.environ['S3_USE_SIGV4'] = 'True'
        conn = S3Connection(access_key_id, secret_access_key,
            host='s3.%s.amazonaws.com' % region)
        bucket = conn.get_bucket(bucket, validate=False)

        archive = Archive(path, s=self.s)
        for key_name, f in archive.fileobjs().items():
            self.s.log('uploading %s...' % key_name)
            key = bucket.new_key(key_name)
            key.set_contents_from_file(f)

        request = PutRequest(urljoin(self.repository_url, '/reindex'))
        session = Session(self.data_path, s=self.s)
        response = session.open(request)

        res = response.getcode() == 200
        self.s.log('reindex %s' % res)
        return res

    def get_package_name(self, name):
        package_strings = []
        for key, value in self.meta.items():

            manifest = Manifest(value['package'], s=self.s)
            ps = PackageString(key)

            if manifest.is_compatible() and PackageString(name).match(ps):
                package_strings.append((ps, key))

        res = sorted(package_strings)
        if res:
            return res[-1][1]

    def update(self):
        if not self.data_path:
            raise Exception('invalid data_path: %s' % repository_url)

        # read cache
        # cached = {}
        # if os.path.exists(cache_path):
        #     for filename, ext in map(os.path.splitext, os.listdir(cache_path)):
        #         name, etag = filename.rsplit('-', 1)
        #         if ext == '.' + default.meta_extension:
        #             cached[name] = (etag, filename + ext)


        request = GetRequest(urljoin(self.repository_url, '/index'))
        session = Session(self.data_path, s=self.s)
        index = json.load(session.open(request, 'utf8'))

        meta = {}
        urls = {}

        for name, (meta_url, etag) in index.items():
            urls[name] = urljoin(self.repository_url, meta_url)

            # if name in cached:
            #     print(name, '(cached)')
            #     cached_etag, cached_filename = cached[name]

            #     # skip if cached
            #     if etag == cached_etag:
            #         meta[name] = util.json_load(os.path.join(cache_path, cached_filename))
            #         continue

            #     # remove cached file on etag mismatch
            #     os.unlink(os.path.join(cache_path, cached_filename))
            # else:
            #     print(name)

            filename = os.path.basename(meta_url)
            path = os.path.join(self.data_path, '.' + name, filename)
            util.makedirs(path)

            request = GetRequest(urls[name])
            meta[name] = json.load(session.open(request, 'utf8'))

            with io.open(path, 'wb') as f:
                f.write(util.json_dump(meta[name]))

        self.meta = meta
        self.urls = urls

    def cache(self, package_string):
        name = self.get_package_name(package_string)
        if not name:
            raise PackageNotFoundException(package_string)

        archive_url, checksum = self.meta[name]['archive']
        url = urljoin(self.urls[name], archive_url)

        filename = os.path.basename(archive_url)
        path = os.path.join(self.data_path, '.' + name, filename)

        util.makedirs(path)
        # TODO etag header is not md5 for multipart uploads
        uget.download(self.data_path, url, path, console=self.s.console,
            checksum=hashlib.md5(), checksum_header='etag', s=self.s)

        return Archive(os.path.dirname(path), s=self.s)

    def list(self, search_string=None):
        return [p for p in self.meta.keys() if search_string in p]
