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

        for name, value in cls.__dict__.items():
            if isinstance(value, type):
                annotations = annotationlib.get_annotations(value)
                cls.config_items.update({
                    # + handle recursively
                    # -> have a function that returns dict[name, (annotation, default)] recursively
                    f'{name}.{name2}': annotation
                    for name2, annotation in annotations.items()
                })
                cls.defaults.update({
                    f'{name}.{name2}': default
                    for name2 in annotations
                    if (default := value.__dict__.get(name2, UNSET)) is not UNSET
                })
                setattr(cls, name, property(cls._get_config_proxy(name)))

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

    @staticmethod
    def _get_config_proxy(name):
        def getter(self):
            class Proxy:
                def __getattr__(s, name2):
                    return getattr(self, f'{name}.{name2}')

            return Proxy()

        return getter

    @classmethod
    def argparse_loader(cls, parser=None, config_file=False):
        # + allow custom aliases for arguments
        if parser is None:
            parser = argparse.ArgumentParser()

        for name in cls.config_items:
            arg_name = name.replace('_', '-').replace('.', '-')
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
                doc = tomllib.load(f)

                output = {}
                # + explore recursively
                for name, value in doc.items():
                    if isinstance(value, dict):
                        for name2, value in value.items():
                            output[f'{name}.{name2}'] = value
                    else:
                        output[name] = value

                return output

        return loader

    @classmethod
    def default_setup(cls):
        return cls(cls.argparse_loader(config_file=True))

    def __init__(self, *loaders):
        # -> use a tree instead of a single list
        # or allow to appender a loader just after an existing one
        # (so that we can use defaults as a loader + env var, while config file from argparse would still be prior to defaults or env vars)
        self.blocks = [ConfigBlock(self, loader) for loader in loaders]

    def add_loader(self, loader):
        self.blocks.append(ConfigBlock(self, loader))

    def load(self):
        for name in type(self).config_items:
            getattr(self, name)


if __name__ == '__main__':
    class A(Config):
        class audio: # Make inherit from Subconfig class?
            path: str | None = None
            #duration: int


    config = A.default_setup()
    #config.load()
    print(config.audio.path)
