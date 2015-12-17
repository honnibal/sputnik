import os
import json

import pytest

from .. import Sputnik
from ..package import (PackageRecipe, Package,
                       NotFoundException, NotIncludedException)
from ..archive import Archive
from ..pool import Pool


def test_build_and_check_archive(tmp_path, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive1 = recipe.build(tmp_path)

    assert os.path.isfile(archive1.path)

    archive2 = Archive(archive1.path, s=s)

    for key in Archive.keys:
        assert getattr(archive1, key) == getattr(archive2, key)


def test_archive_is_compatible(tmp_path, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = recipe.build(tmp_path)
    assert archive.is_compatible()

    s = Sputnik('test', '2.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = recipe.build(tmp_path)
    assert not archive.is_compatible()

    s = Sputnik('xxx', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = recipe.build(tmp_path)
    assert not archive.is_compatible()


def test_file_load(tmp_path, tmp_path2, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = Archive(recipe.build(tmp_path).path, s=s)
    pool = Pool(tmp_path2, s=s)
    package = Package(path=archive.install(pool), s=s)

    assert package.has_file('data', 'xyz.model')
    assert package.load_utf8(json.load, 'data', 'xyz.json') == {'test': True}
    assert package.load(lambda x:x.read(), 'data', 'xyz.json') == \
        json.dumps({'test': True}).encode('ascii')

    assert not package.has_file('data', 'model')

    assert package.load_utf8(None, 'data', 'model', default=0) == 0
    assert package.load_utf8(None, 'data', 'model', require=False) == None

    assert package.load(None, 'data', 'model', default=0) == 0
    assert package.load(None, 'data', 'model', require=False) == None


def test_file_path(tmp_path, tmp_path2, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = Archive(recipe.build(tmp_path).path, s=s)
    pool = Pool(tmp_path2, s=s)
    package = Package(path=archive.install(pool), s=s)

    assert package.has_file('data', 'xyz.model')
    assert package.file_path('data', 'xyz.model') == os.path.join(package.path, 'data', 'xyz.model')
    assert package.dir_path('data') == os.path.join(package.path, 'data')

    assert not package.has_file('data')
    assert not package.has_file('data', 'model')
    with pytest.raises(NotIncludedException):
        assert package.file_path('data', 'model')

    assert package.file_path('data', 'model', require=False) is None


def test_file_path_same_build_directory(tmp_path, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = Archive(recipe.build(sample_package_path).path, s=s)
    pool = Pool(tmp_path, s=s)
    package = Package(path=archive.install(pool), s=s)

    assert package.has_file('data', 'xyz.model')
    assert package.file_path('data', 'xyz.model') == os.path.join(package.path, 'data', 'xyz.model')
    assert package.dir_path('data') == os.path.join(package.path, 'data')

    assert not package.has_file('data')
    assert not package.has_file('data', 'model')
    with pytest.raises(NotIncludedException):
        assert package.file_path('data', 'model')


@pytest.mark.xfail
def test_new_archive_files(tmp_path, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    archive = recipe.build(tmp_path)

    assert archive.manifest
    assert {m['path'] for m in archive.manifest} == \
           {'data/xyz.model', 'data/xyz.json'}


def test_archive_files(tmp_path, sample_package_path):
    s = Sputnik('test', '1.0.0')
    recipe = PackageRecipe(sample_package_path, s=s)
    new_archive = recipe.build(tmp_path)
    archive = Archive(new_archive.path, s=s)

    assert archive.manifest
    assert {m['path'] for m in archive.manifest} == \
           {'data/xyz.model', 'data/xyz.json'}
