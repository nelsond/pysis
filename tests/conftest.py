import sys
import os
import pytest
import shutil

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, '..'))

@pytest.yield_fixture(autouse=True)
def setup_tmp_directory():
    tmp_path = os.path.join(here, 'tmp')
    os.makedirs(tmp_path)

    yield

    shutil.rmtree(tmp_path)

@pytest.fixture
def tmp_path():
    return os.path.join(here, 'tmp')

@pytest.fixture
def fixtures_path():
    return os.path.join(here, 'fixtures')
