[![Travis CI](https://travis-ci.org/henningpeters/sputnik.svg?branch=master)](https://travis-ci.org/henningpeters/sputnik)

# Sputnik: a data package manager library

Sputnik is a library for managing data packages for another library, e.g., models for a machine learning library.

It also comes with a command-line interface.

## Build a package

Add a ```package.json``` file with following JSON to a directory ```test``` and add some files in ```test/data``` that you would like to have packaged, e.g., ```test/data/model```.

```
{
  "name": "test",
  "include": ["data/*"],
  "version": "1.0.0"
}
```

Get a Sputnik reference:

```
from sputnik import Sputnik
sputnik = Sputnik()
```

Then build the package with following code, it should produce a new file and output its path: ```test/test-1.0.0.sputnik```.

```
command = sputnik.make_command()
archive = command.build('test')
print(archive.path)
```

## Install a package

Decide for a location for your installed packages, e.g., ```packages```. Then install the previously built package with following code, it should output the path of the now installed package: ```repository/test-1.0.0```

```
command = sputnik.make_command(data_path='packages')
package = command.install('test/test-1.0.0.sputnik')
print(package.path)
```

## List installed packages

This should output the package strings for all installed packages, e.g., ```['test-1.0.0']```:

```
command = sputnik.make_command(data_path='packages')
packages = command.list()
print([p.ident for p in packages])
```

## Access package data

Sputnik makes it easy to access packaged data files without dealing with filesystem paths or archive file formats.

```
model = command.file('test', 'data/model')
```

or in case you already hold a package object:

```
model = package.file_path('data/model')
```

## Remove package

```
command.remove('test')
```

## Versioning

```install```, ```list```, ```file```, ```files```, ```search``` and ```remove``` commands accept version strings that follow [semantic versioning](http://semver.org/), e.g.:

```
command.install('test ==1.0.0')
command.list('test >1.0.0')
command.file('test >=1.0.0')
command.files('test <1.0.0')
command.remove('test <=1.0.0')
```

## Compatibility

Sputnik ensures compatibility with the host library using [semantic versioning](http://semver.org/). Let's see an example where this is useful:

my_model/package.json:
```
{
  "name": "my_model",
  "description": "this model is awesome",
  "include": ["data/*"],
  "version": "2.0.0",
  "license": "public domain",
  "compatibility": {
    "my_library": ">=0.6.1"
  }
}
```

This means that this package has version ```2.0.0``` and requires version ```0.6.1``` of ```my_library```, to be installed/used.

Let's get another Sputnik reference - now passing our library name and version to it - and build/install the package:

```
sputnik = Sputnik('my_library', '0.6.0')
command = sputnik.make_command(data_path='packages')

archive = command.build('my_model')
command.install(archive.path)
```

This should throw an exception as it requires version ```0.6.1``` of our library:

```
PackageNotCompatibleException: running my_library 0.6.0 but requires {'my_library': '>=0.6.1'}
```

Upgrading our library to version ```0.6.1```:

```
sputnik = Sputnik('my_library', '0.6.1')
command = sputnik.make_command(data_path='packages')

archive = command.build('my_model')
command.install(archive.path)
```
