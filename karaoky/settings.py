import argparse
import dataclasses
import tomllib
from functools import cached_property
from pathlib import Path

from .models import Lyrics, Tempo


def _load_path(path, rel_to=None):
    if path is None:
        return None

    path = Path(path)
    path = path.expanduser()

    if rel_to and not path.is_absolute():
        path = rel_to / path

    return path


def load_config(path):
    path = Path(path)
    with path.open('rb') as f:
        doc = tomllib.load(f)

    directory = path.parent
    config = {
        'audio_source': None,
        'audio_start': 0,
        'lyrics_path': None,
        'lyrics_separator': '|',
        'tempo_path': None,
    }

    if audio := doc.get('audio'):
        config['audio_source'] = _load_path(audio.get('source'), directory)
        if start := audio.get('start'):
            s = 0
            for c in map(float, start.split(':')):
                s = s * 60 + c
            config['audio_start'] = s

    if lyrics := doc.get('lyrics'):
        config['lyrics_path'] = _load_path(lyrics.get('path'), directory)

    if tempo := doc.get('tempo'):
        config['tempo_path'] = _load_path(tempo.get('path'), directory)

    return config


@dataclasses.dataclass
class Settings:
    _config: dict

    @property
    def audio_source(self):
        return self._config['audio_source']

    @property
    def audio_start(self):
        return self._config['audio_start']

    @property
    def lyrics_path(self):
        return self._config['lyrics_path']

    @property
    def tempo_path(self):
        return self._config['tempo_path']

    @cached_property
    def lyrics(self):
        if not self.lyrics_path:
            raise ValueError('No lyrics.path set in config')
        with self.lyrics_path.open() as f:
            return Lyrics.from_file(f, separator=self._config['lyrics_separator'])

    @cached_property
    def tempo(self):
        if not self.tempo_path:
            raise ValueError('No tempo.path set in config')
        with self.tempo_path.open() as f:
            return Tempo.from_file(f)


def get_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser()

    parser.add_argument('args', nargs='*')
    parser.add_argument('--config', '-c', type=load_config)

    return parser


def __getattr__(name):
    if name == 'settings':
        parser = get_parser()
        config = parser.parse_args().config
        return Settings(_config=config)


if __name__ == '__main__':
    settings = __getattr__('settings')
    print(settings)
    print(settings.lyrics)
    print(settings.tempo)
    for syllable, duration in zip(settings.lyrics.syllables, settings.tempo):
        print(syllable, duration)
