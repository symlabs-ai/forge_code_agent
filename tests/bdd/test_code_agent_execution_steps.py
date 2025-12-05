import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip("BDD (code agent execution) pending implementation")

scenarios("../../specs/bdd/10_forge_core/10_code_agent_execution.feature")

