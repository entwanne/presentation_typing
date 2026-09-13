import annotationlib
import argparse
import dataclasses
import tomllib
from functools import cached_property
from pathlib import Path

UNSET = object()


class ConfigBlock:
    def __init__(self, config, loader):
        self.config = config
        self.loader = loader

    @cached_property
    def content(self):
        return self.loader(self.config)

    def get(self, key):
        return self.content.get(key, UNSET)


class Config:
    def __init_subclass__(cls):
        cls.config_items = annotationlib.get_annotations(cls)
        cls.defaults = {
            name: default
            for name in cls.config_items
            if (default := cls.__dict__.get(name, UNSET)) is not UNSET
        }
        for name in cls.config_items:
            setattr(cls, name, property(cls._get_config_item(name)))

    @staticmethod
    def _get_config_item(name):
        def getter(self):
            for block in self.blocks:
                value = block.get(name)
                if value is not UNSET:
                    return value
            value = self.defaults.get(name, UNSET)
            if value is not UNSET:
                return value
            raise AttributeError
        return getter

    @classmethod
    def argparse_loader(cls, parser=None, config_file=False):
        if parser is None:
            parser = argparse.ArgumentParser()

        for name in cls.config_items:
            arg_name = name.replace('_', '-')
            parser.add_argument(f'--{arg_name}', dest=name, default=UNSET)

        if config_file:
            parser.add_argument('--config', '-c')

        def loader(self):
            values = vars(parser.parse_args())
            if config_file and (config_path := values.pop('config')):
                self.add_loader(cls.toml_loader(config_path))
            return values

        return loader

    @classmethod
    def toml_loader(cls, path):
        path = Path(path)

        def loader(self):
            with path.open('rb') as f:
                return tomllib.load(f)

        return loader

    @classmethod
    def default_setup(cls):
        return cls(cls.argparse_loader(config_file=True))

    def __init__(self, *loaders):
        self.blocks = [ConfigBlock(self, loader) for loader in loaders]

    def add_loader(self, loader):
        self.blocks.append(ConfigBlock(self, loader))

    def load(self):
        for name in type(self).config_items:
            getattr(self, name)


class A(Config):
    audio_path: str | None = None


config = A.default_setup()
#config.load()
print(config.audio_path)
