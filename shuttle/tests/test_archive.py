import os
import tarfile
import hashlib
import io

import pytest

from ..archive_writer import ArchiveWriter
from ..archive_reader import ArchiveReader
from ..archive_defaults import *


def path_content(path, base_path=None):
    if base_path is None:
        base_path = path
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            yield os.path.relpath(file_path, base_path)


def test_create_and_check(tmp_path, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    with ArchiveWriter(archive_path, base_path=sample_package_path) as f:
        f.add_path(sample_package_path)

    assert os.path.exists(archive_path)

    tar = tarfile.open(archive_path, 'r')

    assert set(tar.getnames()) == set([ARCHIVE_FILENAME, META_FILENAME])


def test_create_and_read(tmp_path, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    with ArchiveWriter(archive_path, base_path=sample_package_path) as f:
        f.add_path(sample_package_path)

    assert os.path.exists(archive_path)

    with ArchiveReader(archive_path) as f:
        assert set(f.list()) == set(path_content(sample_package_path))


def test_create_and_checksum(tmp_path, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    with ArchiveWriter(archive_path,
                       base_path=sample_package_path,
                       hash_func=hashlib.md5) as f:
        f.add_path(sample_package_path)

    assert os.path.exists(archive_path)

    with ArchiveReader(archive_path) as archive:
        for entry in archive.meta['manifest']:
            with io.open(os.path.join(sample_package_path, entry['path']), 'rb') as f:
                assert entry['checksum'][0] == hashlib.md5().name
                assert entry['checksum'][1] == hashlib.md5(f.read()).hexdigest()


def test_create_and_extract(tmp_path, tmp_path2, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    with ArchiveWriter(archive_path, base_path=sample_package_path) as f:
        f.add_path(sample_package_path)

    assert os.path.exists(archive_path)

    with ArchiveReader(archive_path) as archive:
        archive.extract_all(tmp_path2)

    for root, _, filenames in os.walk(sample_package_path):
        for filename in filenames:
            path = os.path.relpath(os.path.join(root, filename), sample_package_path)
            package_path = os.path.join(sample_package_path, path)
            extract_path = os.path.join(tmp_path2, path)

            assert os.stat(package_path).st_size == os.stat(extract_path).st_size

            assert hashlib.sha256(io.open(package_path, 'rb').read()).hexdigest() == \
                   hashlib.sha256(io.open(extract_path, 'rb').read()).hexdigest()


def test_create_with_index(tmp_path, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    with ArchiveWriter(archive_path, base_path=sample_package_path) as f:
        f.add_path(os.path.join(sample_package_path, 'data'))

    assert os.path.exists(archive_path)

    tar = tarfile.open(archive_path, 'r')

    assert set(tar.getnames()) == set([ARCHIVE_FILENAME, META_FILENAME])

    with ArchiveReader(archive_path) as f:
        content = path_content(os.path.join(sample_package_path, 'data'),
                               base_path=sample_package_path)
        assert set(f.list()) == set(content)


def test_create_without_base_path(tmp_path, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    os.chdir(sample_package_path)

    with ArchiveWriter(archive_path) as f:
        f.add_path('data')

    assert os.path.exists(archive_path)

    tar = tarfile.open(archive_path, 'r')

    assert set(tar.getnames()) == set([ARCHIVE_FILENAME, META_FILENAME])

    with ArchiveReader(archive_path) as f:
        content = path_content(os.path.join(sample_package_path, 'data'),
                               base_path=sample_package_path)
        assert set(f.list()) == set(content)


def test_create_abspath_without_base_path(tmp_path, sample_package_path):
    archive_path = os.path.join(tmp_path, 'test.shuttle')

    with ArchiveWriter(archive_path) as f:
        with pytest.raises(Exception):
           f.add_path(sample_package_path)
