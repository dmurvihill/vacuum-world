from vacuum_world import SuckyAgent


def test_decision():
    agent = SuckyAgent()
    assert agent.decide({"agent_location": 'A', "is_dirty": False}) == 'SUCK'
