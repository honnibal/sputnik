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

        self.archive = self.tar.extractfile(ARCHIVE_FILENAME)
        self.meta = self.get_index_json(META_FILENAME)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.archive.close()
        self.tar.close()

    def extract(self, member, extract_path, cb=None):
        noffset = 0
        for entry in self.meta:
            if entry['path'] == member:
                path = entry['path']
                size = entry['size']

                self.archive.seek(noffset)

                checksum = hashlib.sha256()

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
                assert checksum.hexdigest() == entry['checksum']

            noffset = entry['noffset']

    def extract_all(self, extract_path, cb=None):
        for entry in self.meta:
            self.extract(entry['path'], extract_path, cb=cb)

        members = [m.name for m in self.index_members()]
        for member in members:
            self.tar.extract(member, extract_path)

    def get_index_json(self, member):
        reader = codecs.getreader(JSON_ENCODING)
        return json.load(reader(self.tar.extractfile(member)))

    def list(self):
        return [e['path'] for e in self.meta]

    def size_compressed(self):
        return self.meta[-1]['noffset']

    def index_members(self):
        return [m for m in self.tar.getmembers() if m.name != ARCHIVE_FILENAME]

    def size(self):
        indices = [m.size for m in self.index_members()]
        files = [m['size'] for m in self.meta]
        return sum(indices) + sum(files)
