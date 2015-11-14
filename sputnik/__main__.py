import sys

from . import cli


def main():
    parser = cli.get_parser()

    args = parser.parse_args(sys.argv[1:])
    if hasattr(args, 'run'):
        args.run(args)
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
