# pylint: disable=C0330
import sys
import argparse

from . import validation
from . import default
from . import Sputnik


def package_path_type(path):
    if not validation.is_package_path(path):
        raise argparse.ArgumentTypeError("%r must be a directory")
    return path


def make_command(args):
    s = Sputnik(name=args.name,
                version=args.version,
                console=sys.stdout)
    return s.make_command(
        data_path=args.data_path,
        repository_url=args.repository_url)


def add_build_parser(subparsers):
    parser = subparsers.add_parser('build',
        help='build package from package.json')
    parser.add_argument('package_path',
        type=package_path_type,
        default=default.build_package_path,
        nargs='?',
        help='package.json directory')

    def run(args):
        c = make_command(args)
        c.build(package_path=args.package_path)

    parser.set_defaults(run=run)


def add_install_parser(subparsers):
    parser = subparsers.add_parser('install',
        help='install package from repository or filesystem')
    parser.add_argument('package_name',
        help='package name or path')

    def run(args):
        c = make_command(args)
        c.install(package_name=args.package_name)

    parser.set_defaults(run=run)


def add_remove_parser(subparsers):
    parser = subparsers.add_parser('remove',
        help='remove installed package')
    parser.add_argument('package_string',
        help='package string')

    def run(args):
        c = make_command(args)
        c.remove(package_string=args.package_string)

    parser.set_defaults(run=run)


def add_list_parser(subparsers):
    parser = subparsers.add_parser('list',
        help='list installed packages')
    parser.add_argument('package_string',
        default=default.list_package_string,
        nargs="?",
        help='package string')
    parser.add_argument('--meta',
        default=default.list_meta,
        action='store_true',
        help='show package meta data')
    parser.add_argument('--cache',
        default=default.list_cache,
        action='store_true',
        help='list cached instead of installed packages')

    def run(args):
        c = make_command(args)
        c.list(package_string=args.package_string,
               meta=args.meta,
               cache=args.cache)

    parser.set_defaults(run=run)


def add_search_parser(subparsers):
    parser = subparsers.add_parser('search',
        help='search installable packages on repository')
    parser.add_argument('search_string',
        nargs="?",
        help='search string')

    def run(args):
        c = make_command(args)
        c.search(search_string=args.search_string)

    parser.set_defaults(run=run)


def add_upload_parser(subparsers):
    parser = subparsers.add_parser('upload',
        help='upload package')
    parser.add_argument('package_path',
        help='package path')

    def run(args):
        c = make_command(args)
        c.upload(package_path=args.package_path)

    parser.set_defaults(run=run)


def add_update_parser(subparsers):
    parser = subparsers.add_parser('update',
        help='update package cache')

    def run(args):
        c = make_command(args)
        c.update()

    parser.set_defaults(run=run)


def add_file_parser(subparsers):
    parser = subparsers.add_parser('file',
        help='displays file path')
    parser.add_argument('package_string',
        help='package string')
    parser.add_argument('path',
        help='file path')

    def run(args):
        c = make_command(args)
        c.file(package_string=args.package_string,
               path=args.path)

    parser.set_defaults(run=run)


def add_files_parser(subparsers):
    parser = subparsers.add_parser('files',
        help='displays package files')
    parser.add_argument('package_string',
        help='package string')

    def run(args):
        c = make_command(args)
        c.files(package_string=args.package_string)

    parser.set_defaults(run=run)


def add_purge_parser(subparsers):
    parser = subparsers.add_parser('purge',
        help='purges downloaded data')
    parser.add_argument('--cache',
        default=False,
        action='store_true',
        help='purge cache (cached packages)')
    parser.add_argument('--pool',
        default=False,
        action='store_true',
        help='purge pool (installed packages)')

    def run(args):
        c = make_command(args)
        c.purge(cache=args.cache,
                pool=args.pool)

    parser.set_defaults(run=run)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name',
        help='project name')
    parser.add_argument('--version',
        help='project version')
    parser.add_argument('--data-path',
        default=default.data_path,
        help='data storage path')
    parser.add_argument('--repository-url',
        default=default.repository_url,
        help='package repository path')

    subparsers = parser.add_subparsers()
    add_build_parser(subparsers)
    add_install_parser(subparsers)
    add_remove_parser(subparsers)
    add_list_parser(subparsers)
    add_search_parser(subparsers)
    add_upload_parser(subparsers)
    add_update_parser(subparsers)
    add_file_parser(subparsers)
    add_files_parser(subparsers)
    add_purge_parser(subparsers)

    return parser
