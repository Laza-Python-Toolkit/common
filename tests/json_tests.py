import pytest



xfail = pytest.mark.xfail
parametrize = pytest.mark.parametrize


from jani.common import json





class BasicTests:

    def test_basic(self):
        assert 1


