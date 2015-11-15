import os
import io

from . import util
from . import default
from .package_stub import PackageStub
from .archive_reader import ArchiveReader


class PackageNotCompatibleException(Exception): pass
class NotEnoughSpaceException(Exception): pass


class Archive(PackageStub):
    def __init__(self, path, **kwargs):
        self.path = path
        self.archive = ArchiveReader(path)

        defaults = self.archive.get_member('package')

        super(Archive, self).__init__(defaults, **kwargs)

    def fileobjs(self):
        return {
            os.path.join(self.ident, default.META_FILENAME):
                io.BytesIO(util.json_dump(self.archive.meta)),
            os.path.join(self.ident, default.ARCHIVE_FILENAME):
                self.archive.archive
        }

    def install(self, pool):
        if not self.is_compatible():
            raise PackageNotCompatibleException(
                'running %s %s but requires %s' %
                (self.s.name, self.s.version, self.compatibility))

        if not util.is_enough_space(pool.path, self.archive.size()):
            raise NotEnoughSpaceException('requires %0.2f MB' %
                                          (self.archive.size() / 1024 / 1024))

        # remove installed versions of same package
        for p in pool.list_all(self.name):
            p.remove()

        archive_name = util.archive_filename(self.name, self.version)
        path = os.path.join(pool.path, archive_name)

        self.s.log('install %s' % os.path.basename(path))
        self.archive.extract_all(path + '.tmp')
        os.rename(path + '.tmp', path)

        return path
