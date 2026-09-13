import subprocess
from pathlib import Path

from .settings import settings

output = Path('output')

layers = sorted(output.glob('layer*.png'))

concat = output / 'concat'
lines = ['ffconcat version 1.0']

durations = settings.tempo

layers.append(layers[-1])
lines += [
    line
    for layer, duration in zip(layers, durations)
    for line in (f'file {layer.relative_to(output)}', f'duration {duration}')
]

concat.write_text('\n'.join(lines))

sminutes, sseconds = divmod(settings.audio_start, 60)
dminutes, dseconds = divmod(sum(durations), 60)

subprocess.run([
    'ffmpeg',
    '-i', settings.audio_source,
    '-ss', f'{int(sminutes)}:{sseconds}',
    '-t', f'00:{int(dminutes)}:{dseconds}',
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
