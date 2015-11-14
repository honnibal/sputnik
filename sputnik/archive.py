import os
import io
import shutil

from . import util
from . import default
from .package import Pool
from .package_stub import PackageStub
from .archive_writer import ArchiveWriter
from .archive_reader import ArchiveReader


class PackageNotCompatibleException(Exception): pass


class Archive(PackageStub):
    def __init__(self, path, **kwargs):
        self.path = path
        self.archive = ArchiveReader(path)

        defaults = self.archive.get_member('package')

        super(Archive, self).__init__(defaults, **kwargs)

    def cleanup(self, data_path):
        tmp_install_dir = data_path + ".install"
        tmp_remove_dir = data_path + ".remove"

        # cleanup remove
        if os.path.exists(tmp_remove_dir):
            self.s.log('remove %s' % tmp_remove_dir)
            shutil.rmtree(tmp_remove_dir)

        # cleanup install
        if os.path.exists(tmp_install_dir):
            self.s.log('install %s' % tmp_install_dir)
            os.rename(tmp_install_dir, data_path)

    def fileobjs(self):
        return {
            os.path.join(self.ident, default.META_FILENAME):
                io.BytesIO(util.json_dump(self.archive.meta)),
            os.path.join(self.ident, default.ARCHIVE_FILENAME):
                self.archive.archive
        }

    def install(self, data_path):
        if not self.is_compatible():
            raise PackageNotCompatibleException(
                'running %s %s but requires %s' %
                (self.s.name, self.s.version, self.compatibility))

        # remove installed versions of same package
        pool = Pool(data_path, s=self.s)
        for p in pool.list_all(self.name):
            p.remove()

        archive_name = util.archive_filename(self.name, self.version)
        dest_dir = os.path.join(data_path, archive_name)

        self.cleanup(dest_dir)

        tmp_install_dir = dest_dir + ".install"
        tmp_remove_dir = dest_dir + ".remove"

        if not util.is_enough_space(data_path, self.archive.size()):
            raise Exception("not enough space")

        # tmp install
        self.s.log('pending install %s' % os.path.basename(tmp_install_dir))
        self.archive.extract_all(tmp_install_dir)

        # make way
        if os.path.exists(dest_dir):
            self.s.log('pending remove %s' % dest_dir)
            os.rename(dest_dir, tmp_remove_dir)

        # install
        self.s.log('install %s' % dest_dir)
        shutil.move(tmp_install_dir, dest_dir)

        self.cleanup(dest_dir)
        return dest_dir
