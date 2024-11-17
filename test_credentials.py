import pytest
from PyTado.interface import Tado

@pytest.fixture
def tado_instance():
    return Tado('username', 'password')