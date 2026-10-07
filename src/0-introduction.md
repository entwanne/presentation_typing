# Écrire un analyseur de types en Python
#### <div align="right">Antoine "entwanne" Rozo</div>

<div align="right"><img src="img/schtroumpf_flat_rounded.png" style="width: 5em;" /></div>

<div align="right"><img src="img/cc_by_sa.svg" style="width: 5em;" /></div>


```python skip
%load_ext ipython_reopenclass

from IPython.display import Video

def karaoke():
    return Video("img/karaoke.webm", width=800)

import pathlib, shutil
shutil.rmtree('assets', ignore_errors=True)
pathlib.Path('assets').mkdir()
pathlib.Path('test_mypy.py').unlink(missing_ok=True)

%alias mypy ./env/bin/mypy
```
