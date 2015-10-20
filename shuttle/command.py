import os

from shuttle import validation
from shuttle import default
from shuttle import util
from shuttle.archive import Archive
from shuttle.package import Package, PackageRecipe


class Command(object):
    def __init__(self, data_path):
        if not validation.is_data_path(data_path):
            raise Exception("%r must be a directory" % data_path)
        self.data_path = data_path

    def install(self, package_name, repository=default.install_repository):
        archive_path = os.path.join(repository, package_name)
        archive = Archive(archive_path)
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
        print(util.json_dump([p.to_dict(keys) for p in packages]))
