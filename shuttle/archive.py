from __future__ import print_function
import os
import io
import time
import tarfile
import shutil

from . import util
from . import default
from .manifest import Manifest
from .archive_writer import ArchiveWriter
from .archive_reader import ArchiveReader


class NewArchive(Manifest):  # package archive
    def __init__(self, recipe, path, hash_func):
        self.path = path
        self.hash_func = hash_func
        self.archive = None
        self.filename = util.archive_filename(
            recipe.name, recipe.version, suffix=True)

        Manifest.__init__(self, recipe.to_dict())

    def __enter__(self):
        archive_path = os.path.join(self.path, self.filename)
        self.archive = ArchiveWriter(archive_path)
        return self

    def __exit__(self, type, value, traceback):
        self.add_json('package', self.to_dict())
        self.archive.close()

    def add_file(self, path):
        if not os.path.isfile(path):
            raise Exception("only files")
        
        self.archive.add(path)

    def add_json(self, name, obj):
        self.archive.add_json(name, obj)


class Archive(Manifest):
    def __init__(self, path):
        self.path = path
        self.archive = ArchiveReader(path)

        defaults = self.archive.get_member('package')

        Manifest.__init__(self, defaults)

    def cleanup(self, data_path):
        tmp_install_dir = data_path + ".install"
        tmp_remove_dir = data_path + ".remove"
    
        # cleanup remove
        if os.path.exists(tmp_remove_dir):
            print("remove", tmp_remove_dir)
            shutil.rmtree(tmp_remove_dir)
    
        # cleanup install
        if os.path.exists(tmp_install_dir):
            print("install", tmp_install_dir)
            os.rename(tmp_install_dir, data_path)

    def fileobjs(self):
        return {
            '%s/meta.json' % self.package_name(): io.BytesIO(util.json_dump(self.archive.meta)),
            '%s/archive.gz' % self.package_name(): self.archive.archive,
        }

    def install(self, data_path):
        archive_name = util.archive_filename(self.name, self.version)
        dest_dir = os.path.join(data_path, archive_name)

        self.cleanup(dest_dir)
    
        tmp_install_dir = dest_dir + ".install"
        tmp_remove_dir = dest_dir + ".remove"
    
        if not util.is_enough_space(data_path, self.archive.size()):
            raise Exception("not enough space")
    
        # tmp install
        print("pending install", tmp_install_dir)
        self.archive.extract_all(tmp_install_dir)
    
        # make way
        if os.path.exists(dest_dir):
            print("pending remove", dest_dir)
            os.rename(dest_dir, tmp_remove_dir)
    
        # install
        print("install", dest_dir)
        shutil.move(tmp_install_dir, dest_dir)
    
        self.cleanup(dest_dir)
