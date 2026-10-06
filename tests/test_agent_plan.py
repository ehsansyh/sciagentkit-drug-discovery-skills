from sciagentkit.agents import molecule_analyst_plan


def test_reference_agent_plan_has_manifest_step():
    plan = molecule_analyst_plan()
    assert any(step["tool"] == "write_manifest" for step in plan)
    assert len(plan) >= 8
