from collections import OrderedDict

from . import util


class Base(object):
    def __init__(self, **kwargs):
        self.s = kwargs.pop('s')
        super(Base, self).__init__()

    def to_json(self, keys=None):
        return util.json_dump(self.to_dict(keys))

    def to_dict(self, keys=None):
        keys = keys or []
        if hasattr(self, 'is_valid'):
            self.is_valid()
        return OrderedDict([
            (k, getattr(self, k))
            for k in self.keys
            if not keys or k in keys])
