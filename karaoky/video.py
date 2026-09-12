import subprocess
from pathlib import Path
output = Path('output')

layers = sorted(output.glob('layer*.png'))

concat = output / 'concat'
lines = ['ffconcat version 1.0']

with open('song.tp') as f:
    durations = (float(line) for line in f)
    lines += [
        line
        for layer, duration in zip(layers, durations)
        for line in (f'file {layer.relative_to(output)}', f'duration {duration}')
    ]

lines += [f'file {layers[-1].relative_to(output)}', 'duration 10']

concat.write_text('\n'.join(lines))

subprocess.run([
    'ffmpeg',
    '-i', '/home/antoine/Music/Boby_Lapointe/Ta_Katie_t_as_quitte.mp3',
    '-ss', '0:00:36',
    #'-t', '00:26:19',
    '-c:a', 'copy',
    output / 'audio.mp3',
])

subprocess.run([
    'ffmpeg',
    '-i', concat,
    '-i', output / 'audio.mp3',
    '-c:a', 'copy',
    '-vf', 'fps=25',
    '-c:v', 'libx264',
    '-pix_fmt', 'yuv420p',
    output / 'video.avi',
])
