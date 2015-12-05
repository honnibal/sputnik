[![Travis CI](https://travis-ci.org/henningpeters/sputnik.svg?branch=master)](https://travis-ci.org/henningpeters/sputnik)

# Sputnik: a data package manager library

Sputnik is a library for managing data packages for another library, e.g., models for a machine learning library.

It also comes with a command-line interface, run ```sputnik --help``` or ```python -m sputnik --help``` for assistance.

Sputnik is a pure Python library licensed under MIT, has minimal dependencies (only ```semver```) and is tested against ```python ==2.7``` and ```python ==3.4```.

## Installation

Sputnik is available from [PyPI](https://pypi.python.org/pypi/sputnik) via ```pip```:

```
pip install sputnik
```

## Build a package

Add a ```package.json``` file with following JSON to a directory ```sample``` and add some files in ```sample/data``` that you would like to have packaged, e.g., ```sample/data/model```. See a sample layout [here](https://github.com/henningpeters/sputnik/tree/master/sample).

```
{
  "name": "my_model",
  "include": ["data/*"],
  "version": "1.0.0"
}
```

Get a Sputnik reference:

```
from sputnik import Sputnik
sputnik = Sputnik()
```

Then build the package with following code, it should produce a new file and output its path: ```sample/my_model-1.0.0.sputnik```.

```
command = sputnik.command()
archive = command.build('sample')
print(archive.path)
```

## Install a package

Decide for a location for your installed packages, e.g., ```packages```. Then install the previously built package with following code, it should output the path of the now installed package: ```packages/my_model-1.0.0```

```
command = sputnik.command(data_path='packages')
package = command.install('sample/my_model-1.0.0.sputnik')
print(package.path)
```

## List installed packages

This should output the package strings for all installed packages, e.g., ```['my_model-1.0.0']```:

```
command = sputnik.command(data_path='packages')
packages = command.list()
print([p.ident for p in packages])
```

## Access package data

Sputnik makes it easy to access packaged data files without dealing with filesystem paths or archive file formats.

```
command.file('my_model', 'data/model')
```

returns a file object. Or in case you already hold a package object:

```
package.file_path('data/model')
```

returns a string with the path to the file.

If you want to list all file contents of a package use ```command.files('my_model')```.

## Remove package

```
command.remove('my_model')
```

## Versioning

```install```, ```list```, ```file```, ```files```, ```search``` and ```remove``` commands accept version strings that follow [semantic versioning](http://semver.org/), e.g.:

```
command.install('my_model ==1.0.0')
command.list('my_model >1.0.0')
command.file('my_model >=1.0.0')
command.files('my_model <1.0.0')
command.remove('my_model <=1.0.0')
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
command = sputnik.command(data_path='packages')

archive = command.build('my_model')
command.install(archive.path)
```

This should throw an exception as it requires version ```0.6.1``` of our library:

```
sputnik.archive.PackageNotCompatibleException:
running my_library 0.6.0 but requires {'my_library': '>=0.6.1'}
```

Upgrading our library to version ```0.6.1```:

```
sputnik = Sputnik('my_library', '0.6.1')
command = sputnik.command(data_path='packages')

archive = command.build('my_model')
command.install(archive.path)
```
