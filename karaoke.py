import subprocess
import time
from pathlib import Path

syllables = (
    ("…",),
    (),
    ("…",),

    ("Tip ", "top ", "tip ", "top"),
    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
    ("Tip ", "top ", "tip ", "top"),
    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),

    ("Tip ", "top ", "tip ", "top"),
    ("T'es ", "pa", "ré ", "t'as ", "ta", "pé"),
    ("Tout ", "plein ", "d'an", "no", "ta", "tions"),
    ("Tu ", "t'en ", "n'es ", "pas ", "pri", "vé"),

    ("Ton ", "code ", "est ", "tout ", "pim", "pé"),
    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
    ("Ton ", "code ", "é", "tait ", "pas ", "top"),
    ("Ton ", "code ", "é", "tait ", "pas ", "top"),

    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
    ("Sta", "tique", "ment ", "t'as ", "tes", "té"),
    ("Cent ", "pour ", "cent ", "d'l'A", "S", "T"),
    ("Tes ", "types ", "et ", "tes ", "pa", "quets"),

    ("T'les ", "as ", "tous ", "im", "por", "tés"),
    ("Tu ", "t'y ", "es ", "pas ", "trom", "pé"),
    ("T'as ", "plus ", "d'bugs ", "tout ", "pé", "tés"),
    ("Ton ", "code ", "est ", "tout ", "pim", "pé"),

    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
    ("T'as ", "ty", "pé ", "ton ", "Py", "thon"),
)


def present(syllables, sleep_time=0.3):
    for sentence in syllables:
        for syllable in sentence:
            time.sleep(0.3)
            print(syllable, end='', flush=True)
        time.sleep(0.3)
        print()


def iterpages(pages):
    it = iter(pages)
    previous_page = None
    next_page = next(it, None)

    while (page := next_page) is not None:
        next_page = next(it, None)
        yield previous_page, page, next_page
        previous_page = page


def itercursor(values):
    values = list(values)
    acc = []

    while values:
        acc.append(values.pop(0))
        yield acc, values


def animate(syllables):
    output = Path('output')
    output.mkdir(exist_ok=True)

    doc = [
        '<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        '<svg width="1280" height="800" xmlns="http://www.w3.org/2000/svg">',
    ]
    layers = []

    for prev_sentence, sentence, next_sentence in iterpages(syllables):
        for group1, group2 in itercursor(sentence):
            layer_id = f'layer{len(layers)+1:03}'
            layers.append(layer_id)

            doc.append(f'<g id="{layer_id}">')

            if prev_sentence:
                doc += [
                    '<text style="font-size:100px;line-height:125%;font-family:\'Radio Canada Big\'" x="20" y="100">',
                    f'<tspan style="fill:#ffff00">{"".join(prev_sentence)}</tspan>',
                    '</text>',
                ]

            doc += [
                '<text style="font-size:100px;line-height:125%;font-family:\'Radio Canada Big\'" x="20" y="300">',
                f'<tspan style="fill:#ffff00">{"".join(group1).replace(" ", " ")}</tspan>',
                f'<tspan style="fill:#0000ff">{"".join(group2).replace(" ", " ")}</tspan>',
                '</text>',
            ]

            if next_sentence:
                doc += [
                    '<text style="font-size:100px;line-height:125%;font-family:\'Radio Canada Big\'" x="20" y="500">',
                    f'<tspan style="fill:#0000ff">{"".join(next_sentence)}</tspan>',
                    '</text>',
                ]

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


#present(syllables)
animate(syllables)
