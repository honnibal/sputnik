import os

from .. import Sputnik
from ..package import PackageRecipe
from ..archive import Archive


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
