import gzip
import io
import os
import hashlib
import json
import tarfile
import time
import tempfile

from .archive_defaults import *


class ArchiveWriter(object):
    def __init__(self, path, base_path=None):
        self.base_path = base_path
        self.path = path
        self.meta = []
        self.tmp_path = tempfile.mkdtemp()
        self.tmp_archive_path = os.path.join(self.tmp_path, ARCHIVE_FILENAME)
        self.archive = io.open(self.tmp_archive_path, 'wb')
        self.index_data = {}

    def __del__(self):
        self.archive.close()
        import shutil
        shutil.rmtree(self.tmp_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        defaults = {'indent': 4, 'separators': (',', ': ')}
        meta_json = json.dumps(self.meta, **defaults)
        mtime = time.time()

        with tarfile.open(self.path, 'w') as tar:
            with io.open(self.tmp_archive_path, 'rb') as f:
                info = tarfile.TarInfo(ARCHIVE_FILENAME)
                info.size = os.stat(self.tmp_archive_path).st_size
                info.mtime = os.stat(self.tmp_archive_path).st_mtime
                info.type = tarfile.REGTYPE
                info.mode = 0o644
                info.uid = info.gid = 1000
                tar.addfile(info, f)

            for filename, data in self.index_data.items():
                with io.BytesIO(data) as f:
                    info = tarfile.TarInfo(filename)
                    info.size = len(data)
                    info.mtime = mtime
                    info.type = tarfile.REGTYPE
                    info.mode = 0o644
                    info.uid = info.gid = 1000
                    tar.addfile(info, f)

            data = meta_json.encode(JSON_ENCODING)
            with io.BytesIO(data) as f:
                info = tarfile.TarInfo(META_FILENAME)
                info.size = len(data)
                info.mtime = mtime
                info.type = tarfile.REGTYPE
                info.mode = 0o644
                info.uid = info.gid = 1000
                tar.addfile(info, f)

    def add_index(self, path):
        self.add_bytes(path, io.open(path).read().encode('utf8'))

    def add_bytes(self, path, byte_string):
        path = os.path.relpath(path, self.base_path or '')
        self.index_data[path] = byte_string

    def add(self, path, cb=None):
        if self.base_path is None and os.path.isabs(path):
            raise Exception('cannot handle absolute paths without base_path: %s' % path)

        checksum = hashlib.sha256()

        with gzip.GzipFile(fileobj=self.archive,
                           compresslevel=COMPRESSLEVEL) as gz:
            with io.open(path, 'rb') as f:
                bytes_read = 0

                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break

                    bytes_read += len(chunk)

                    gz.write(chunk)
                    checksum.update(chunk)

                    # callback for progress tracking
                    if cb:
                        cb(bytes_read)

            gz.flush()

        self.meta.append({
            'path': os.path.relpath(path, self.base_path or ''),
            'noffset': self.archive.tell(),
            'size': os.stat(path).st_size,
            'checksum': checksum.hexdigest(),
        })

    def add_path(self, path, cb=None):
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                self.add(file_path, cb=cb)
