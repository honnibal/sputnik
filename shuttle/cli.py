import sys
import argparse

from . import command
from . import validation
from . import default
from . import Shuttle


def data_path_type(path):
    if not validation.is_data_path(path):
        raise argparse.ArgumentTypeError("%r must be a directory")
    return path


def package_path_type(path):
    if not validation.is_package_path(path):
        raise argparse.ArgumentTypeError("%r must be a directory")
    return path


def make_command(args):
    s = Shuttle(name=args.name, version=args.version, console=sys.stdout)
    return s.make_command(args.data_path)


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
        c.build(args.package_path)

    parser.set_defaults(run=run)


def add_install_parser(subparsers):
    parser = subparsers.add_parser('install',
        help='install package from repository')
    parser.add_argument('package_name_or_path',
        help='package name or path')
    parser.add_argument('repository_url',
        default=default.install_repository_url,
        nargs='?',
        help='repository url')

    def run(args):
        c = make_command(args)
        c.install(args.package_name_or_path, args.repository_url)

    parser.set_defaults(run=run)


def add_remove_parser(subparsers):
    parser = subparsers.add_parser('remove',
        help='remove installed package')
    parser.add_argument('package_string',
        help='package string')

    def run(args):
        c = make_command(args)
        c.remove(args.package_string)

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

    def run(args):
        c = make_command(args)
        c.list(package_string=args.package_string, meta=args.meta)

    parser.set_defaults(run=run)


def add_upload_parser(subparsers):
    parser = subparsers.add_parser('upload',
        help='upload package')
    parser.add_argument('package_path',
        help='package path')
    parser.add_argument('repository_url',
        default=default.upload_repository_url,
        nargs='?',
        help='repository url')

    def run(args):
        c = make_command(args)
        c.upload(
            package_path=args.package_path,
            repository_url=args.repository_url)

    parser.set_defaults(run=run)


def add_update_parser(subparsers):
    parser = subparsers.add_parser('update',
        help='update package cache')
    parser.add_argument('repository_url',
        default=default.update_repository_url,
        nargs='?',
        help='repository url')

    def run(args):
        c = make_command(args)
        c.update(repository_url=args.repository_url)

    parser.set_defaults(run=run)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name',
        help='project name')
    parser.add_argument('--version',
        help='project version')
    parser.add_argument('--data-path',
        type=data_path_type,
        required=True,
        help='data storage path')

    subparsers = parser.add_subparsers()
    add_build_parser(subparsers)
    add_install_parser(subparsers)
    add_remove_parser(subparsers)
    add_list_parser(subparsers)
    add_upload_parser(subparsers)
    add_update_parser(subparsers)

    return parser


def run(parser):
    args = parser.parse_args(sys.argv[1:])
    if hasattr(args, 'run'):
        args.run(args)
    else:
        parser.print_usage()
