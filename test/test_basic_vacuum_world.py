from unittest.mock import Mock

import pytest

from vacuum_world import BasicVacuumWorld


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

