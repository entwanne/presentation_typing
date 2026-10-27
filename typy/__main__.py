import argparse

from . import Typy


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    return parser


def main(parser: argparse.ArgumentParser | None = None, input_args: tuple[str, ...] | None = None) -> None:
    if parser is None:
        parser = get_parser()
    args = parser.parse_args(input_args)

    typy = Typy()
    typy.run_path(*args.files)
    typy.print_errors()


if __name__ == '__main__':
    main()
