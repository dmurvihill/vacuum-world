from unittest.mock import Mock

import pytest

from vacuum_world import BasicVacuumWorld


@pytest.fixture
def dirty_floor():
    return BasicVacuumWorld('A', {'A': True, 'B': True})


def test_init_with_invalid_agent_location_fails():
    with pytest.raises(AssertionError):
        BasicVacuumWorld(Mock(), {'A': Mock(), 'B': Mock()})


def test_init_with_invalid_dirt_location_fails():
    with pytest.raises(AssertionError):
        BasicVacuumWorld('A', {'A': Mock(), 'B': Mock(), Mock(): Mock()})


def test_init_with_non_boolean_dirt_status_fails():
    with pytest.raises(AssertionError):
        BasicVacuumWorld('A', {'A': Mock(), 'B': True})


def test_location_is_observable():
    for agent_location in BasicVacuumWorld.locations:
        environment = BasicVacuumWorld(agent_location,
                                       {'A': False, 'B': False})
        assert environment.observable_state['agent_location'] == agent_location


def test_same_location_dirt_is_observable():
    location_a = BasicVacuumWorld.locations[0]
    location_b = BasicVacuumWorld.locations[1]

    for agent_location in BasicVacuumWorld.locations:
        other_location = location_b if agent_location is location_a \
            else location_a
        for is_dirty in (True, False):
            starting_state = {agent_location: is_dirty, other_location: False}
            environment = BasicVacuumWorld(agent_location, starting_state)
            assert environment.observable_state['is_dirty'] == is_dirty


def test_illegal_action_fails(dirty_floor):
    with pytest.raises(AssertionError):
        dirty_floor.update('FOOBAR')


def test_suck_removes_dirt():
    for agent_location in BasicVacuumWorld.locations:
        dirt_status = {'A': True, 'B': True}
        environment = BasicVacuumWorld(agent_location, dirt_status)
        environment.update('SUCK')
        assert environment.observable_state['is_dirty'] == False


def test_suck_does_not_move(dirty_floor):
    dirty_floor.update('SUCK')
    assert dirty_floor.observable_state['agent_location'] == 'A'


def test_right_at_a_goes_to_b(dirty_floor):
    dirty_floor.update('RIGHT')
    assert dirty_floor.observable_state['agent_location'] == 'B'


def test_left_at_a_does_not_remove_dirt(dirty_floor):
    dirty_floor.update('LEFT')
    assert dirty_floor.observable_state['is_dirty'] == True


def test_left_at_a_does_not_move(dirty_floor):
    dirty_floor.update('LEFT')
    assert dirty_floor.observable_state['agent_location'] == 'A'


def test_left_at_b_goes_to_a():
    environment = BasicVacuumWorld('B', {'A': True, 'B': True})
    environment.update('LEFT')
    assert environment.observable_state['agent_location'] == 'A'
