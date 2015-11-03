import os

from .. import Shuttle


def test_build_install_remove(command, sample_package_path, tmp_path):
    archive = command.build(sample_package_path)
    assert os.path.isfile(archive.path)

    packages = command.list()
    assert len(packages) == 0

    package = command.install(archive.path)
    assert os.path.isdir(package.path)

    packages = command.list()
    assert len(packages) == 1
    assert packages[0].package_name() == package.package_name()

    command.remove(package.name)
    assert not os.path.isdir(package.path)

    packages = command.list()
    assert len(packages) == 0
