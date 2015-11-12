import os
import json
import hashlib
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from . import util
from .archive import Archive
from .session import Session, GetRequest, PutRequest
from .base import Base
from .cache import Cache
from .package_stub import PackageStub


class PackageNotFoundException(Exception): pass


class Index(Base):
    def __init__(self, data_path, repository_url, **kwargs):
        if not repository_url:
            raise Exception('invalid repository_url: %s' % repository_url)

        self.data_path = data_path
        self.repository_url = repository_url

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
            self.s.log('preparing upload for %s' % key_name)
            headers = {
                util.s3_header('md5'): hashlib.md5(f.read()).hexdigest()
            }
            f.seek(os.SEEK_SET, 0)

            self.s.log('uploading %s...' % key_name)
            key = bucket.new_key(key_name)
            key.set_contents_from_file(f, headers=headers)

        request = PutRequest(urljoin(self.repository_url, '/reindex'))
        session = Session(self.data_path, s=self.s)
        response = session.open(request)

        res = response.getcode() == 200
        self.s.log('reindex %s' % res)
        return res

    def update(self):
        request = GetRequest(urljoin(self.repository_url, '/index'))
        session = Session(self.data_path, s=self.s)
        cache = Cache(self.data_path, s=self.s)

        index = json.load(session.open(request, 'utf8'))

        for name, (meta_url, etag) in index.items():
            url = urljoin(self.repository_url, meta_url)
            request = GetRequest(url)
            response = session.open(request, 'utf8')
            meta = json.load(response)

            package = PackageStub(meta['package'], s=self.s)
            assert name == package.package_name()

            cache.update(meta, url=url)
