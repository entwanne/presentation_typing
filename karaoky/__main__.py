import argparse
import csv
import itertools
import subprocess
from pathlib import Path

CWD = Path('.')

with (CWD / 'song.lr').open() as f:
    reader = csv.reader(f, delimiter="|")
    syllables = [tuple(line) for line in reader]


def iter_window(iterable, n=None, *, before=None, after=None):
    if before is None:
        before = n
    if after is None:
        after = n

    it = iter(iterable)

    previous = []
    if after is None:
        nexts = list(it)
    else:
        nexts = list(itertools.islice(it, after + 1))

    while nexts:
        current = nexts.pop(0)
        yield current, previous, nexts

        previous.append(current)
        if before is not None:
            previous = previous[-before:]

        if after is not None:
            try:
                nexts.append(next(it))
            except StopIteration:
                pass


output = CWD / 'output'
output.mkdir(exist_ok=True)

doc = [
    '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
    '<svg width="1280" height="800" xmlns="http://www.w3.org/2000/svg">',
]
layers = []

for sentence, prev_sentences, next_sentences in iter_window(syllables, 1):
    for syllable, prev_syllables, next_syllables in iter_window(sentence):
        layer_id = f'layer{len(layers)+1:03}'
        layers.append(layer_id)

        doc.append(f'<g id="{layer_id}">')

        current_line = 100

        for prev_sentence in prev_sentences:
            doc += [
                f'<text style="font-size:100px;line-height:125%;font-family:\'Radio Canada Big\'" x="20" y="{current_line}">',
                f'<tspan style="fill:#ffff00">{"".join(prev_sentence)}</tspan>',
                '</text>',
            ]
            current_line += 200

        doc += [
            f'<text style="font-size:100px;line-height:125%;font-family:\'Radio Canada Big\'" x="20" y="{current_line}">',
            f'<tspan style="fill:#ffff00">{"".join(prev_syllables).replace(" ", " ")}</tspan>',
            f'<tspan style="fill:#ffff00">{syllable.replace(" ", " ")}</tspan>',
            f'<tspan style="fill:#0000ff">{"".join(next_syllables).replace(" ", " ")}</tspan>',
            '</text>',
        ]
        current_line += 200

        for next_sentence in next_sentences:
            doc += [
                f'<text style="font-size:100px;line-height:125%;font-family:\'Radio Canada Big\'" x="20" y="{current_line}">',
                f'<tspan style="fill:#0000ff">{"".join(next_sentence)}</tspan>',
                '</text>',
            ]
            current_line += 200

        doc.append('</g>')

doc.append('</svg>')

with (output / 'output.svg').open('w') as f:
    f.writelines(doc)

for layer_id in layers:
    subprocess.run([
        'inkscape',
        f'--export-filename={output}/{layer_id}.png',
        '-i',
        layer_id,
        '-C',
        '-j',
        output / 'output.svg',
    ])
