import os

from . import util
from . import default
from .package_string import PackageString
from .package_stub import PackageStub
from .base import Base


class CompatiblePackageNotFoundException(Exception): pass
class PackageNotFoundException(Exception): pass


class PackageList(Base):

    package_class = PackageStub

    def __init__(self, path, **kwargs):
        super(PackageList, self).__init__(**kwargs)

        self.path = path
        self.data_path = kwargs.get('data_path') or path
        self.load()

    def packages(self):
        if not os.path.exists(self.path):
            os.mkdir(self.path)

        for path in os.listdir(self.path):
            if path.endswith('.tmp'):
                continue

            meta_path = os.path.join(self.path, path, default.META_FILENAME)
            if not os.path.isfile(meta_path):
                continue

            meta = util.json_load(meta_path)

            yield self.__class__.package_class(
                defaults=meta['package'],
                path=os.path.join(self.path, path),
                meta=meta,
                package_list=self,
                s=self.s)

    def load(self):
        self._packages = {}
        for package in self.packages():
            self._packages[package.ident] = package

    def get(self, package_string):
        candidates = []
        query = PackageString(package_string)

        for package in self._packages.values():
            ps = PackageString(package=package)
            if query.match(ps):
                candidates.append(ps)

        if not candidates:
            raise PackageNotFoundException

        candidates.sort(key=lambda c: (c.package.is_compatible(), c))
        package = candidates[-1].package

        if not package.is_compatible():
            raise CompatiblePackageNotFoundException(
                'running %s %s but requires %s' %
                (self.s.name, self.s.version, package.compatibility))

        return package

    def list(self, package_string=None, check_compatibility=True):
        def c(value):
            if check_compatibility:
                return value
            return True

        if not package_string:
            return [p for p in self._packages.values() if c(p.is_compatible())]

        candidates = []
        query = PackageString(package_string)

        for package in self._packages.values():
            ps = PackageString(package=package)
            if query.match(ps) and c(ps.package.is_compatible()):
                candidates.append(ps.package)

        return candidates

    def list_all(self, package_string=None):
        return self.list(package_string, check_compatibility=False)

    def purge(self):
        for package in self.list():
            package.remove()

        if not os.listdir(self.path):
            os.rmdir(self.path)
