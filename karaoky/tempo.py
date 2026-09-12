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
    exit()

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
    exit()

import tkinter as tk

root = tk.Tk()
records = []

import csv
with lyrics_path.open() as f:
    reader = csv.reader(f, delimiter="|")
    syllables = [syllable for line in reader for syllable in line]

class Timer:
    def __init__(self, rate=1):
        self.reset()
        self.rate = rate

    def start(self):
        self.last_tick = time.monotonic()

    def pause(self):
        self.previous += self._tick()

    def reset(self):
        self.last_tick = None
        self.previous = 0

    def _tick(self):
        current = time.monotonic()
        elapsed = current - self.last_tick
        self.last_tick = current
        return elapsed

    def tick(self):
        elapsed = self._tick() + self.previous
        self.previous = 0
        return elapsed * self.rate

rate = 0.4
timer = Timer(rate)
sit = None

def play_cmd():
    global sit

    if song.get_time() < 0: # Song was stopped
        records.clear()
        song.play()
        song.set_time(seek)
        song.set_rate(rate)
        sit = iter(syllables)
        print(next(sit))
    else:
        song.play()
    timer.start()

    play_button.configure(state='disabled')
    pause_button.configure(state='normal')
    stop_button.configure(state='normal')
    tempo_button.configure(state='normal')

def pause_cmd():
    song.pause()
    timer.pause()

    play_button.configure(state='normal')
    pause_button.configure(state='disabled')
    stop_button.configure(state='normal')
    tempo_button.configure(state='disabled')

def stop_cmd():
    song.stop()
    timer.reset()

    play_button.configure(state='normal')
    pause_button.configure(state='disabled')
    stop_button.configure(state='disabled')
    tempo_button.configure(state='disabled')

#x = 50
#y = 50
#texts = []

def tempo_cmd():
    global x, y
    t = timer.tick()
    syllable = next(sit, None)
    if syllable is not None:
        print('Tempo', t, syllable)
        #for tid in texts:
        #    canvas.delete(tid)
        #texts.clear()
        #texts.append(canvas.create_text((x, y), text=syllable, fill="#0000ff", font=("Arial", 30)))
        #x += 50
        #if x > 300:
        #    x = 50
        #    y += 50
        text.insert(tk.END, syllable)
        text.tag_add("start", "1.8", "1.13") # (y=1, x=8, y2=1, x2=13)
        text.tag_config("start", background="black", foreground="red")
        records.append(t)

def save_cmd():
    with record_path.open('w') as f:
        for record in records:
            print(record, file=f)

play_button = tk.Button(root, text='Play', command=play_cmd)
play_button.pack()

pause_button = tk.Button(root, text='Pause', state='disabled', command=pause_cmd)
pause_button.pack()

stop_button = tk.Button(root, text='Stop', state='disabled', command=stop_cmd)
stop_button.pack()

tempo_button = tk.Button(root, text='Tempo', state='disabled', command=tempo_cmd)
tempo_button.pack()

save_button = tk.Button(root, text='Save', command=save_cmd)
save_button.pack()

#canvas = tk.Canvas()
#canvas.create_text((50, 50), text="toto", fill="#0000ff", font=("Arial", 30))
#canvas.pack()
text = tk.Text()
text.pack(expand=1, fill=tk.BOTH)

root.mainloop()
