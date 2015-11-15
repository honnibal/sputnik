import os
import shutil

from .package import Package
from .package_list import PackageList


class Pool(PackageList):

    package_class = Package

    def cleanup(self):
        for filename in os.listdir(self.path):
            if filename.endswith('.remove'):
                self.s.log('remove %s' % filename)
                shutil.rmtree(os.path.join(self.path, filename))

        for filename in os.listdir(self.path):
            if filename.endswith('.install'):
                self.s.log('install %s' % filename)
                new_filename = filename.rsplit('.', 1)[0]
                os.rename(os.path.join(self.path, filename),
                          os.path.join(self.path, new_filename))
