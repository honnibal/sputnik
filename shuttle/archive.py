import os
import io
import time
import tarfile
import shutil

from shuttle import util
from shuttle import default
from shuttle.manifest import Manifest


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
        self.archive = tarfile.open(archive_path, "w:gz")
        return self

    def __exit__(self, type, value, traceback):
        self.size = sum([x for _, _, x in self.files.values()])
        self.add_bytes(default.meta_manifest_path, self.to_json().encode('ascii'))
        self.archive.close()

    def add_file_base(self, info, f):
        info.type = tarfile.REGTYPE
        info.mode = 0o644
        info.uid = info.gid = 1000
        self.archive.addfile(info, f)

    def add_file(self, path, f):
        if not os.path.isfile(path):
            raise Exception("only files")
        
        stat = os.fstat(f.fileno())

        with io.open(path, "rb") as x:
            m = self.hash_func()
            m.update(x.read())
            self.files[path] = (
                m.name,  # file path
                m.hexdigest(),  # checksum
                stat.st_size)  # file size

        info = tarfile.TarInfo(path)
        info.size = stat.st_size
        info.mtime = stat.st_mtime
        self.add_file_base(info, f)

    def add_bytes(self, path, byte_string):
        f = io.BytesIO(byte_string)
        info = tarfile.TarInfo(path)
        info.size = len(byte_string)
        info.mtime = time.time()
        self.add_file_base(info, f)


class Archive(Manifest):
    def __init__(self, path):
        self.path = path
        with tarfile.open(path, "r:gz") as archive:
            defaults = util.archive_json(archive, default.meta_manifest_path)

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

    def install(self, data_path):
        archive_name = util.archive_filename(self.name, self.version)
        dest_dir = os.path.join(data_path, archive_name)
    
        self.cleanup(dest_dir)
    
        tmp_install_dir = dest_dir + ".install"
        tmp_remove_dir = dest_dir + ".remove"
    
        if not util.is_enough_space(data_path, self.size):
            raise Exception("not enough space")
    
        # tmp install
        with tarfile.open(self.path, "r:gz") as archive:
            print("pending install", tmp_install_dir)
            archive.extractall(tmp_install_dir)
    
        # make way
        if os.path.exists(dest_dir):
            print("pending remove", dest_dir)
            os.rename(dest_dir, tmp_remove_dir)
    
        # install
        print("install", dest_dir)
        shutil.move(tmp_install_dir, dest_dir)
    
        self.cleanup(dest_dir)
