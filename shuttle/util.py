import shutil
import json
import io
import os


def is_enough_space(path, size):
    if hasattr(shutil, "disk_usage"):  # python >= 3.3
        free = shutil.disk_usage(path).free
        return free >= size
    return True


def archive_filename(name, version, suffix=False):
    res = "%s-%s" % (name, version)
    if suffix:
        res += ".shuttle"
    return res


def archive_json(archive, path):
    f = archive.extractfile(path)
    res = json.loads(f.read().decode("ascii"))
    f.close()
    return res


def json_dump(obj):
    defaults = {'indent': 4, 'separators': (',', ': ')}
    return json.dumps(obj, **defaults)


def json_load(path):
    with io.open(path, "rb") as f:
        return json.loads(f.read().decode('ascii'))


def makedirs(path):
    path = os.path.dirname(path)
    if path and not os.path.exists(path):
        os.makedirs(path)
