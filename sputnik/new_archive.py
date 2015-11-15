import os

from . import util
from .package_stub import PackageStub
from .archive_writer import ArchiveWriter


class NewArchive(PackageStub):  # package archive
    def __init__(self, recipe, path, hash_func, **kwargs):
        self.hash_func = hash_func
        self.archive = None
        filename = util.archive_filename(
            recipe.name, recipe.version, suffix=True)
        self.path = os.path.join(path, filename)
        self.base_path = kwargs.pop('base_path', path)

        super(NewArchive, self).__init__(recipe.to_dict(), **kwargs)

    def __enter__(self):
        self.archive = ArchiveWriter(self.path, base_path=self.base_path)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.add_json('package', self.to_dict())
        self.archive.close()

    def add_file(self, path):
        if not os.path.isfile(path):
            raise Exception("only files")

        self.archive.add(path)

    def add_json(self, name, obj):
        self.archive.add_json(name, obj)
