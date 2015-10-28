import gzip
import io
import os
import hashlib
import json
import tarfile
import codecs

from .archive_defaults import *
from . import util


class ArchiveReader(object):
    def __init__(self, path):
        self.path = path
        self.archive = None
        self.tar = tarfile.open(self.path, 'r')

        self.meta = self.get_meta()
        self.archive = self.tar.extractfile(self.meta['archive'])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.archive.close()
        self.tar.close()

    def extract(self, member, extract_path, cb=None):
        noffset = 0
        for entry in self.meta['manifest']:
            if entry['path'] == member:
                path = entry['path']
                size = entry['size']

                self.archive.seek(noffset)

                checksum = getattr(hashlib, entry['checksum'][0])()

                with gzip.GzipFile(fileobj=self.archive) as gz:

                    filename = os.path.join(extract_path, path)
                    util.makedirs(filename)
                    with io.open(filename, 'wb') as f:

                        bytes_read = 0
                        while True:
                            chunk = gz.read(min(size - bytes_read, CHUNK_SIZE))
                            if not chunk:
                                break

                            bytes_read += len(chunk)

                            f.write(chunk)
                            checksum.update(chunk)

                            # callback for progress tracking
                            if cb:
                                cb(bytes_read)

                # checksums from bytes read and meta data should match
                if checksum.hexdigest() != entry['checksum'][1]:
                    raise Exception('checksum mismatch: %s' % path)

            noffset = entry['noffset']

    def extract_all(self, extract_path, cb=None):
        for entry in self.meta['manifest']:
            self.extract(entry['path'], extract_path, cb=cb)

        members = [m.name for m in self.index_members()]
        for member in members:
            self.tar.extract(member, extract_path)

    def get_meta(self):
        reader = codecs.getreader('utf8')
        return json.load(reader(self.tar.extractfile(META_FILENAME)))

    def get_member(self, member):
        return self.meta[member]

    def list(self):
        return [e['path'] for e in self.meta['manifest']]

    def size_compressed(self):
        return self.meta[-1]['noffset']

    def index_members(self):
        return [m for m in self.tar.getmembers() if m.name != ARCHIVE_FILENAME]

    def size(self):
        indices = [m.size for m in self.index_members()]
        files = [m['size'] for m in self.meta['manifest']]
        return sum(indices) + sum(files)
