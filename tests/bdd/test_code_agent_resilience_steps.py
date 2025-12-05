import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip("BDD (code agent resilience) pending implementation")

scenarios("../../specs/bdd/50_observabilidade/50_code_agent_resilience.feature")

