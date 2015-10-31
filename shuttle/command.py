import os

from . import validation
from . import default
from . import util
from .archive import Archive
from .package import Package, PackageRecipe
from .index import Index


class Command(object):
    def __init__(self, data_path):
        if not validation.is_data_path(data_path):
            raise Exception("%r must be a directory" % data_path)
        self.data_path = data_path

    def install(self, package_name, repository_url=default.install_repository_url):
        if os.path.isfile(package_name):
            archive = Archive(package_name)
        else:
            index = Index(self.data_path, repository_url)
            index.update()
            archive = index.cache(package_name)
        return archive.install(self.data_path)

    def build(self, package_path=default.build_package_path):
        recipe = PackageRecipe(package_path)
        return recipe.build(package_path)

    def remove(self, package_string):
        packages = Package.find(package_string, self.data_path)
        for package in packages:
            package.remove()

    def list(self, package_string=default.list_package_string, meta=default.list_meta):
        packages = Package.find(package_string, self.data_path)
        keys = not meta and ('name', 'version') or ()
        util.json_print([p.to_dict(keys) for p in packages])

    def upload(self, package_path, repository_url=default.upload_repository_url):
        index = Index(self.data_path, repository_url)
        index.upload(package_path)

    def update(self, repository_url=default.update_repository_url):
        index = Index(self.data_path, repository_url)
        index.update()
