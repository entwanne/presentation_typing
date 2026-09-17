from pathlib import Path

import pytest

from typy import Typy


@pytest.fixture()
def typy():
    return Typy()


@pytest.fixture()
def samples():
    cwd = Path('.').resolve()
    abs_path = (Path(__file__).parent / 'samples').resolve()
    if abs_path.is_relative_to(cwd):
        return abs_path.relative_to(cwd)
    return abs_path


@pytest.fixture()
def sample(samples, request):
    testfile_path = Path(request.node.location[0])
    sample_name = testfile_path.name.removeprefix('test_')
    return samples / sample_name
