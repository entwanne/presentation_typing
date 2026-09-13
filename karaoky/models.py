import csv
import dataclasses


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

    def __iter__(self):
        return iter(self.verses)


class Tempo(tuple[float, ...]):
    @classmethod
    def from_file(cls, file):
        return cls(float(line) for line in file)
