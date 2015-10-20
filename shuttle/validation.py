import os


def is_path(path):
    return path and os.path.isdir(path)


def is_data_path(path):
    return is_path(path)


def is_package_path(path):
    return is_path(path)
