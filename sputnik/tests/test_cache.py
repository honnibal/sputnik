import pytest

from .. import Sputnik
from ..cache import Cache
from ..package_stub import PackageStub
from ..package_list import CompatiblePackageNotFoundException, \
                           PackageNotFoundException


def test_update(tmp_path):
    s = Sputnik('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({'name': 'abc', 'version': '1.0.0'}, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 1
    assert cache.list()[0].ident == package.ident

    with pytest.raises(PackageNotFoundException):
        assert cache.get('abc >=1.0.1')

    assert cache.get('abc').ident == package.ident
    assert cache.get('abc ==1.0.0').ident == package.ident
    assert cache.get('abc >0.0.1').ident == package.ident

    with pytest.raises(PackageNotFoundException):
        assert cache.get('xyz')


def test_remove(tmp_path):
    s = Sputnik('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({'name': 'abc', 'version': '1.0.0'}, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 1
    assert cache.list()[0].ident == package.ident

    package = cache.get('abc')
    package.remove()

    assert len(cache.list()) == 0

    with pytest.raises(PackageNotFoundException):
        assert cache.get('abc')


def test_update_compatible(tmp_path):
    s = Sputnik('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({
        'name': 'abc',
        'version': '1.0.0',
        'compatibility': {
            'test': '>=0.9.0'
        }
    }, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 1

    with pytest.raises(PackageNotFoundException):
        assert cache.get('abc >=1.0.1')

    assert cache.get('abc').ident == package.ident
    assert cache.get('abc ==1.0.0').ident == package.ident
    assert cache.get('abc >0.0.1').ident == package.ident

    with pytest.raises(PackageNotFoundException):
        assert cache.get('xyz')


def test_update_incompatible(tmp_path):
    s = Sputnik('test', '1.0.0')
    cache = Cache(tmp_path, s=s)
    package = PackageStub({
        'name': 'abc',
        'version': '1.0.0',
        'compatibility': {
            'test': '>=2.0.0'
        }
    }, s=s)

    meta = {
        'archive': ['archive.gz', None],
        'package': package.to_dict()
    }

    assert len(cache.list()) == 0

    cache.update(meta, None)

    assert len(cache.list()) == 0

    with pytest.raises(CompatiblePackageNotFoundException):
        cache.get('abc')
        cache.get('abc >=0.0.0')

    with pytest.raises(PackageNotFoundException):
        assert cache.get('xyz')


def test_update_multiple_compatible(tmp_path):
    s = Sputnik('test', '5.0.0')
    cache = Cache(tmp_path, s=s)

    for i in range(1, 11):
        package = PackageStub({
            'name': 'abc',
            'version': '%d.0.0' % i,  # from 1.0.0 to 10.0.0
            'compatibility': {
                'test': '>=%d.0.0' % i  # from 1.0.0 to 10.0.0
            }
        }, s=s)

        meta = {
            'archive': ['archive.gz', None],
            'package': package.to_dict()
        }

        cache.update(meta, None)

    assert len(cache.list()) == 5
    assert cache.get('abc').version == '5.0.0'

    with pytest.raises(PackageNotFoundException):
        assert cache.get('xyz')


def test_update_multiple_incompatible(tmp_path):
    s = Sputnik('test', '0.0.0')
    cache = Cache(tmp_path, s=s)

    for i in range(1, 11):
        package = PackageStub({
            'name': 'abc',
            'version': '%d.0.0' % i,  # from 1.0.0 to 10.0.0
            'compatibility': {
                'test': '>=%d.0.0' % i  # from 1.0.0 to 10.0.0
            }
        }, s=s)

        meta = {
            'archive': ['archive.gz', None],
            'package': package.to_dict()
        }

        cache.update(meta, None)

    assert len(cache.list()) == 0

    with pytest.raises(CompatiblePackageNotFoundException):
        cache.get('abc')
        cache.get('abc >=0.0.0')

    with pytest.raises(PackageNotFoundException):
        assert cache.get('xyz')
