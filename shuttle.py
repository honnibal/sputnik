import sys

from shuttle import cli


if __name__ == "__main__":
    cli.run(cli.get_parser().parse_args(sys.argv[1:]))
