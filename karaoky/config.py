import argparse
import csv
import dataclasses
import tomllib
from functools import cached_property
from pathlib import Path

from .lib.config import Config as BaseConfig

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


class Config(BaseConfig):
    class audio:
        path: Path | None = None
        start: int = 0

    class lyrics:
        path: Path | None = None
        separator: str = '|'

    class tempo:
        path: Path | None = None


@dataclasses.dataclass
class Settings:
    config: Config

    @cached_property
    def lyrics(self):
        with open(self.config.lyrics.path) as f:
            return Lyrics.from_file(f, separator=self.config.lyrics.separator)

    @cached_property
    def tempo(self):
        with open(self.config.tempo.path) as f:
            return Tempo.from_file(f)


if __name__ == '__main__':
    settings = Settings(config=Config.default_setup())
    print(settings)
    print(settings.lyrics)
    print(settings.tempo)
