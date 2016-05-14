import pytest

from reflex_agent import ReflexAgent

@pytest.fixture
def agent():
    return ReflexAgent()


def test_suck_when_floor_is_dirty(agent):
    percept = {
        "agent_location": 'A',
        "is_dirty": True
    }
    assert agent.decide(percept) == 'SUCK'


def test_move_when_floor_is_clean(agent):
    percept = {
        "agent_location": 'A',
        "is_dirty": False
    }
    assert agent.decide(percept) == 'RIGHT'
    percept["agent_location"] = 'B'
    assert agent.decide(percept) == 'LEFT'


def test_exception_when_missing_agent_location(agent):
    percept = {"is_dirty": True}
    with pytest.raises(ValueError):
        agent.decide(percept)


def test_exception_when_missing_dirt_status(agent):
    percept = {"agent_location": 'A'}
    with pytest.raises(ValueError):
        agent.decide(percept)


def test_exception_with_non_boolean_dirt_status(agent):
    percept = {
        "agent_location": 'A',
        "is_dirty": 'False'
    }
    with pytest.raises(ValueError):
        agent.decide(percept)


def test_exception_with_illegal_agent_location(agent):
    percept = {
        "agent_location": 'C',
        "is_dirty": False
    }
    with pytest.raises(ValueError):
        agent.decide(percept)

