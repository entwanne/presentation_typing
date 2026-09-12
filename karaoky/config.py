import argparse
from pathlib import Path

def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', '-c', type=Path)
    parser.add_argument('--lyrics', '-l', type=Path)
    parser.add_argument('--tempo', '-t', type=Path)

    return parser


if __name__ == '__main__':
    print(get_parser().parse_args())
