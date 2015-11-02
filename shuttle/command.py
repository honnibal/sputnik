import os

from . import validation
from . import default
from . import util
from .archive import Archive
from .package import Package, PackageRecipe
from .index import Index
from .base import Base


class Command(Base):
    def __init__(self, data_path, repository_url, **kwargs):
        if not validation.is_data_path(data_path):
            raise Exception("%r must be a directory" % data_path)

        self.data_path = data_path
        self.repository_url = repository_url

        super(Command, self).__init__(**kwargs)

    def install(self, package_name_or_path):
        if os.path.isfile(package_name_or_path):
            archive = Archive(package_name_or_path, s=self.s)
        else:
            index = Index(self.data_path, self.repository_url, s=self.s)
            index.update()
            archive = index.cache(package_name_or_path)
        path = archive.install(self.data_path)
        return Package(path, s=self.s)

    def build(self, package_path=default.build_package_path):
        recipe = PackageRecipe(package_path, s=self.s)
        return recipe.build(package_path)

    def remove(self, package_string):
        packages = Package.find(package_string, self.data_path, s=self.s)
        for package in packages:
            package.remove()

    def search(self, search_string):
        index = Index(self.data_path, self.repository_url, s=self.s)
        index.update()
        package_names = index.list(search_string)
        util.json_print(self.s.log, package_names)
        return package_names

    def list(self, package_string=default.list_package_string, meta=default.list_meta):
        packages = Package.find(package_string, self.data_path, s=self.s)
        keys = not meta and ('name', 'version') or ()
        util.json_print(self.s.log, [p.to_dict(keys) for p in packages])
        return packages

    def upload(self, package_path):
        index = Index(self.data_path, self.repository_url, s=self.s)
        return index.upload(package_path)

    def update(self):
        index = Index(self.data_path, self.repository_url, s=self.s)
        index.update()
