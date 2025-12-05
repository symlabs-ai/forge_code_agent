import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.skip("BDD (tool calling and files) pending implementation")

scenarios("../../specs/bdd/10_forge_core/11_code_agent_tools_and_files.feature")

