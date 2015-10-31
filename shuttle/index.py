from __future__ import print_function
import os
import io
import codecs
import json
import tarfile
import hashlib
import sys
try:
    from urllib.parse import urlparse, urljoin
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import urlopen, urlparse, Request, HTTPError
try:
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection

from . import default
from . import util
from . import uget
from .archive import Archive

from boto.s3.connection import S3Connection


class PackageNotFoundException(Exception): pass


class Index(object):
    def __init__(self, data_path, repository_url, **kwargs):
        self.data_path = data_path
        self.repository_url = repository_url

        self.meta = {}
        self.urls = {}

    def upload(self, path):
        os.environ['S3_USE_SIGV4'] = 'True'
        conn = S3Connection(
            os.environ.get('AWS_ACCESS_KEY_ID'),
            os.environ.get('AWS_SECRET_ACCESS_KEY'),
            host='s3.%s.amazonaws.com' % os.environ.get('AWS_REGION'))
        bucket = conn.get_bucket(os.environ.get('S3_BUCKET'), validate=False)

        archive = Archive(path)
        for key_name, f in archive.fileobjs().items():
            print('uploading %s...' % key_name)
            key = bucket.new_key(key_name)
            key.set_contents_from_file(f)

        o = urlparse(self.repository_url)
        conn =  HTTPConnection('%s:%d' % (o.netloc, o.port or 80))
        conn.request('PUT', '/reindex')
        response = conn.getresponse()
        print('reindex', response.status == 200)

    def is_package(self, name):
        return name in self.meta

    def update(self):
        # read cache
        # cached = {}
        # if os.path.exists(cache_path):
        #     for filename, ext in map(os.path.splitext, os.listdir(cache_path)):
        #         name, etag = filename.rsplit('-', 1)
        #         if ext == '.' + default.meta_extension:
        #             cached[name] = (etag, filename + ext)

        reader = codecs.getreader('utf8')
        index = json.load(reader(urlopen(self.repository_url)))

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

            meta[name] = json.load(reader(urlopen(urls[name])))

            with io.open(path, 'wb') as f:
                f.write(util.json_dump(meta[name]))

        self.meta = meta
        self.urls = urls

    def cache(self, name):
        if not self.is_package(name):
            raise PackageNotFoundException(name)

        archive_url, checksum = self.meta[name]['archive']
        url = urljoin(self.urls[name], archive_url)

        filename = os.path.basename(archive_url)
        path = os.path.join(self.data_path, '.' + name, filename)

        util.makedirs(path)
        # TODO etag header is not md5 for multipart uploads
        uget.download(url, path, console=sys.stdout,
            checksum=hashlib.md5(), checksum_header='etag')

        return Archive(os.path.dirname(path))
