import annotationlib
import argparse
import dataclasses
import tomllib
from functools import cached_property
from pathlib import Path

UNSET = object()


class ConfigBlock:
    def __init__(self, loader):
        self.loader = loader

    @cached_property
    def content(self):
        return self.loader()

    def get(self, key):
        return self.content.get(key, UNSET)


class Config:
    def __init_subclass__(cls):
        cls.config_items = annotationlib.get_annotations(cls)
        for name in cls.config_items:
            setattr(cls, name, property(cls._get_config_item(name)))

    @staticmethod
    def _get_config_item(name):
        def getter(self):
            for block in self.blocks:
                value = block.get(name)
                if value is not UNSET:
                    return value
            return None
        return getter

    @classmethod
    def argparse_loader(cls, parser=None):
        if parser is None:
            parser = argparse.ArgumentParser()
        for name in cls.config_items:
            arg_name = name.replace('_', '-')
            parser.add_argument(f'--{arg_name}', dest=name, default=UNSET)

        def loader():
            return vars(parser.parse_args())

        return loader

    @classmethod
    def toml_loader(cls, path):
        path = Path(path)

        def loader():
            with path.open('rb') as f:
                return tomllib.load(f)

        return loader

    def __init__(self, *loaders):
        self.blocks = [ConfigBlock(loader) for loader in loaders]


class A(Config):
    audio_path: str | None = None


config = A(A.argparse_loader(), A.toml_loader('toto.toml'))
print(config.audio_path)
