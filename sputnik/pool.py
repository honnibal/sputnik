import os
import shutil

from .package import Package
from .package_list import PackageList


class Pool(PackageList):

    package_class = Package

    def __init__(self, path, **kwargs):
        super(Pool, self).__init__(path, **kwargs)
        self.cleanup()

    def cleanup(self):
        for filename in os.listdir(self.path):
            if filename.endswith('.tmp'):
                self.s.log('remove %s' % filename)
                shutil.rmtree(os.path.join(self.path, filename))
