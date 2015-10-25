import io
import os
import json
import tempfile

import pytest


@pytest.fixture
def tmp_path():
    return tempfile.mkdtemp()


@pytest.fixture
def tmp_path2():
    return tmp_path()


@pytest.fixture(scope='module')
def sample_package_path():
    path = tempfile.mkdtemp()
    with io.open(os.path.join(path, 'package.json'), 'wb') as f:
        json.dump({
            "name": "test",
            "description": "test package",
            "model": "test",
            "dependencies": [],
            "include": ["data/*"],
            "languages": ["en"],
            "version": "1.0.0",
            "license": "public domain",
            "compatibility": {}
        }, f)
    data_path = os.path.join(path, 'data')
    os.mkdir(data_path)
    with io.open(os.path.join(data_path, 'model1'), 'wb') as f:
        for i in range(1):
            f.write(str(i) * 1024)
    with io.open(os.path.join(data_path, 'model2'), 'wb') as f:
        for i in range(1):
            f.write(str(i) * 1024)
    return path
