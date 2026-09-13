import time
import sys
import vlc
from pathlib import Path

from .settings import settings

song = vlc.MediaPlayer(settings.audio_source)
seek = int(settings.audio_start * 1000)

if sys.argv[1] == 'record':
    with settings.tempo_path.open('w') as f:

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

    tempo = iter(settings.tempo)

    song.play()
    song.set_time(seek)

    for verse in settings.lyrics:
        for i, syllable in enumerate(verse):
            if not i:
                print()
            print(syllable, end='', flush=True)
            time.sleep(next(tempo))
    print()
    song.stop()
    exit()

import tkinter as tk

root = tk.Tk()
records = []

all_syllables = []
for verse in settings.lyrics:
    if verse := list(verse):
        verse[-1] += '\n'
        all_syllables.extend(verse)


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
rate = 1
timer = Timer(rate)
syllables = None

def play_cmd():
    global syllables

    if song.get_time() < 0: # Song was stopped
        records.clear()
        song.play()
        song.set_time(seek)
        song.set_rate(rate)
        syllables = iter(all_syllables)
        print(next(syllables))
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

def tempo_cmd():
    t = timer.tick()
    syllable = next(syllables, None)
    if syllable is not None:
        text.tag_remove("highlight", "1.0", tk.END)
        print('Tempo', t, syllable)
        if syllable.endswith('\n'):
            text.insert(tk.END, syllable.removesuffix('\n'), "highlight")
            text.insert(tk.END, '\n')
        else:
            text.insert(tk.END, syllable, "highlight")
        records.append(t)

def save_cmd():
    with settings.tempo_path.open('w') as f:
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

text = tk.Text()
text.tag_config("highlight", background="black", foreground="white")
text.pack(expand=1, fill=tk.BOTH)

root.mainloop()
