import argparse
import dataclasses
import tomllib
from functools import cached_property
from pathlib import Path

@dataclasses.dataclass
class InnerConfig:
    audio_path: Path | None
    audio_start: int | None
    lyrics_path: Path | None
    tempo_path: Path | None

@dataclasses.dataclass
class Config:
    config_path: Path | None
    inner_config: InnerConfig

    @cached_property
    def config_file(self) -> InnerConfig:
        if self.config_path is None:
            return None

        path = self.config_path
        if not isinstance(path, Path):
            path = Path(path)
        with path.open('rb') as f:
             doc = tomllib.load(f)

        return InnerConfig(
            audio_path=doc.get('audio', {}).get('source'),
            audio_start=doc.get('audio', {}).get('start'),
            lyrics_path=doc.get('lyrics', {}).get('path'),
            tempo_path=doc.get('tempo', {}).get('path'),
        )

    @cached_property
    def lyrics_path(self):
        if self.inner_config.lyrics_path is not None:
            return self.inner_config.lyrics_path
        elif self.config_file is not None:
            return self.config_file.lyrics_path
        return None

    @cached_property
    def lyrics(self):
        pass

'''
def load_config_file(path: str | Path):
    try:
        if not isinstance(path, Path):
            path = Path(path)
        with path.open('rb') as f:
            doc = tomllib.load(f)
    except Exception as e:
        print(e)
        raise ValueError(f'Invalid config file {path}') from e

    return doc
'''

def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', '-c', type=Path)
    parser.add_argument('--lyrics', '-l', type=Path)
    parser.add_argument('--tempo', '-t', type=Path)

    return parser


def map_args(args):
    return Config(
        config_path=args.config,
        inner_config=InnerConfig(
            audio_path=None,
            audio_start=None,
            lyrics_path=args.lyrics,
            tempo_path=args.tempo
        ),
    )


def parse_args(parser=None, input_args=None):
    if parser is None:
        parser = get_parser()
    return map_args(parser.parse_args(input_args))


if __name__ == '__main__':
    config = parse_args()
    print(config)
    print(config.lyrics_path)
