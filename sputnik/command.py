import os
import io

from . import default
from . import util
from .archive import Archive
from .pool import Pool
from .package import Package, PackageRecipe
from .index import Index
from .base import Base
from .cache import Cache


class Command(Base):
    def __init__(self, data_path=None, repository_url=None, **kwargs):
        self.data_path = data_path
        self.repository_url = repository_url

        super(Command, self).__init__(**kwargs)

    def install(self, package_name):
        if os.path.isfile(package_name):
            archive = Archive(package_name, s=self.s)
        else:
            index = Index(self.data_path, self.repository_url, s=self.s)
            index.update()

            cache = Cache(self.data_path, s=self.s)
            package = cache.get(package_name)
            archive = package.fetch()

        pool = Pool(self.data_path, s=self.s)
        path = archive.install(pool)
        return Package(path=path, s=self.s)

    def build(self, package_path=default.build_package_path):
        recipe = PackageRecipe(package_path, s=self.s)
        return recipe.build(package_path)

    def remove(self, package_string):
        pool = Pool(self.data_path, s=self.s)
        packages = pool.list(package_string)
        for package in packages:
            package.remove()

    def search(self, search_string=default.search_string):
        # TODO make it work without data dir???
        index = Index(self.data_path, self.repository_url, s=self.s)
        index.update()

        cache = Cache(self.data_path, s=self.s)
        packages = cache.list(search_string)
        util.json_print(self.s.log, [p.ident for p in packages])
        return packages

    def list(self, package_string=default.list_package_string, meta=default.list_meta):
        # TODO add cli option to list cache
        pool = Pool(self.data_path, s=self.s)
        packages = pool.list(package_string)
        keys = not meta and ('name', 'version') or ()
        util.json_print(self.s.log, [p.to_dict(keys) for p in packages])
        return packages

    def upload(self, package_path):
        index = Index(self.data_path, self.repository_url, s=self.s)
        return index.upload(package_path)

    def update(self):
        index = Index(self.data_path, self.repository_url, s=self.s)
        index.update()

    def file(self, package_string, path):
        pool = Pool(self.data_path, s=self.s)
        package = pool.get(package_string)
        file_path = package.file_path(path)
        util.json_print(self.s.log, file_path)
        return io.open(file_path, 'rb')

    def files(self, package_string):
        pool = Pool(self.data_path, s=self.s)
        package = pool.get(package_string)
        files = {f['path']: {'checksum': f['checksum'], 'size': f['size']}
                 for f in package.manifest}
        util.json_print(self.s.log, {package.ident: files})
        return files

    def purge(self, cache=False, pool=False):
        if cache or not cache and not pool:
            self.s.log('purging cache')
            Cache(self.data_path, s=self.s).purge()

        if pool or not cache and not pool:
            self.s.log('purging pool')
            Pool(self.data_path, s=self.s).purge()
