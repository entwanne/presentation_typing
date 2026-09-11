import time
import sys
import vlc
from pathlib import Path

CWD = Path('.')
record_path = CWD / 'song.tp'
lyrics_path = CWD / 'song.lr'
song_path = '/home/antoine/Music/Boby_Lapointe/Ta_Katie_t_as_quitte.mp3'

song = vlc.MediaPlayer(song_path)
seek = 36 * 1000

if sys.argv[1] == 'record':
    with record_path.open('w') as f:

        input('Tap a first time to start recording ')
        song.play()
        song.set_time(seek)
        start = time.monotonic()

        for _ in sys.stdin:
            t = time.monotonic()
            print(t - start, file=f)
            start = t

        print(time.monotonic() - start, file=f)

        song.stop()

elif sys.argv[1] == 'replay':
    import csv

    with record_path.open() as f:
        records = iter([float(line) for line in f])

    with lyrics_path.open() as f:
        reader = csv.reader(f, delimiter="|")
        syllables = [tuple(line) for line in reader]

    song.play()
    song.set_time(seek)

    for sentence in syllables:
        for i, syllable in enumerate(sentence):
            if not i:
                print()
            print(syllable, end='', flush=True)
            time.sleep(next(records))
    print()
    song.stop()
