import pytest


@pytest.fixture
def context():
  """Shared dict-like context for BDD steps."""
  return {}

