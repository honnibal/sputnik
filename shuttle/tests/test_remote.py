import os

import pytest


@pytest.mark.remote
def test_install_package(command):
    packages = command.list()
    assert len(packages) == 0

    package = command.install('test')
    assert os.path.isdir(package.path)

    packages = command.list()
    assert len(packages) == 1
    assert packages[0].ident == package.ident


@pytest.mark.remote
def test_upgrade_package(command):
    packages = command.list()
    assert len(packages) == 0

    package1 = command.install('test ==1.0.0')
    assert os.path.isdir(package1.path)

    package2 = command.install('test ==2.0.0')
    assert os.path.isdir(package2.path)

    packages = command.list()
    assert len(packages) == 2
    assert set([p.ident for p in packages]) == \
           set([package1.ident, package2.ident])


@pytest.mark.remote
def test_upload_package(command, sample_package_path):
    archive = command.build(sample_package_path)
    assert os.path.isfile(archive.path)

    res = command.upload(archive.path)
    assert res


@pytest.mark.remote
def test_search_packages(command):
    assert command.search()
