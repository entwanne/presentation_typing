import argparse
import csv
import dataclasses
import tomllib
from functools import cached_property
from pathlib import Path

class Verse(tuple[str, ...]):
    pass

@dataclasses.dataclass
class Lyrics:
    verses: tuple[Verse, ...]

    @classmethod
    def from_file(cls, file, separator='|'):
        reader = csv.reader(file, delimiter=separator)
        return cls(verses=tuple(Verse(row) for row in reader))

    @property
    def syllables(self):
        for verse in self.verses:
            yield from verse


class Tempo(tuple[float, ...]):
    @classmethod
    def from_file(cls, file):
        return cls(float(line) for line in file)


@dataclasses.dataclass
class InnerConfig:
    audio_path: Path | None
    audio_start: int | None
    lyrics_path: Path | None
    lyrics_separator: str | None
    tempo_path: Path | None


@dataclasses.dataclass
class Config:
    config_path: Path | None
    inner_config: InnerConfig

    @cached_property
    def config_file(self) -> InnerConfig:
        if self.config_path is None:
            return None

        path = Path(self.config_path)
        with path.open('rb') as f:
             doc = tomllib.load(f)

        return InnerConfig(
            audio_path=doc.get('audio', {}).get('source'),
            audio_start=doc.get('audio', {}).get('start'),
            lyrics_path=doc.get('lyrics', {}).get('path'),
            lyrics_separator=doc.get('lyrics', {}).get('separator'),
            tempo_path=doc.get('tempo', {}).get('path'),
        )

    @cached_property
    def lyrics_path(self):
        if self.inner_config.lyrics_path is not None:
            return Path(self.inner_config.lyrics_path)
        elif self.config_file is not None:
            return Path(self.config_file.lyrics_path)
        return None

    @cached_property
    def lyrics_separator(self):
        if self.inner_config.lyrics_separator is not None:
            return self.inner_config.lyrics_separator
        elif self.config_file is not None and self.config_file.lyrics_separator is not None:
            return self.config_file.lyrics_separator
        return '|'

    @cached_property
    def lyrics(self):
        with self.lyrics_path.open() as f:
            return Lyrics.from_file(f)

    @cached_property
    def tempo_path(self):
        if self.inner_config.tempo_path is not None:
            return Path(self.inner_config.tempo_path)
        elif self.config_file is not None:
            return Path(self.config_file.tempo_path)
        return None

    @cached_property
    def tempo(self):
        with self.tempo_path.open() as f:
            return Tempo.from_file(f)


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--config', '-c', type=Path)
    parser.add_argument('--lyrics', '-l', type=Path)
    parser.add_argument('--lyrics_separator')
    parser.add_argument('--tempo', '-t', type=Path)

    return parser


def map_args(args):
    return Config(
        config_path=args.config,
        inner_config=InnerConfig(
            audio_path=None,
            audio_start=None,
            lyrics_path=args.lyrics,
            lyrics_separator=args.lyrics_separator,
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
    print(config.lyrics)
    print(config.tempo)
