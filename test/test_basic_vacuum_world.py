from unittest.mock import Mock

import pytest

from vacuum_world import BasicVacuumWorld


status_mapping = {
    't': True,
    'f': False
}


@pytest.fixture
def dirty_floor():
    return BasicVacuumWorld(agent_location=['A'], dirt_status=['t', 't'])


def test_init_with_invalid_agent_location_fails():
    with pytest.raises(ValueError):
        BasicVacuumWorld(agent_location=[Mock()], dirt_status=['t', 'f'])


def test_init_with_insufficient_dirt_status_fails():
    with pytest.raises(ValueError):
        BasicVacuumWorld(agent_location=['A'], dirt_status=['t'])


def test_init_with_too_many_dirt_status_fails():
    with pytest.raises(ValueError):
        BasicVacuumWorld(agent_location=['A'], dirt_status=['t', 't', 't'])


def test_init_with_insufficient_location_fails():
    with pytest.raises(ValueError):
        BasicVacuumWorld(agent_location=[], dirt_status=['t', 't'])


def test_init_with_too_many_location_fails():
    with pytest.raises(ValueError):
        BasicVacuumWorld(agent_location=['A', 'B'], dirt_status=['t', 't'])


def test_legal_dirt_status_accepted():
    dirt_statuses = zip(BasicVacuumWorld.CLEAN_VALUES,
                        BasicVacuumWorld.DIRTY_VALUES)
    for dirt_status in dirt_statuses:
        environment = BasicVacuumWorld(agent_location=['A'],
                                       dirt_status=dirt_status)
        assert environment.state['dirt_status'] == {
            'A': False,
            'B': True
        }


def test_illegal_dirt_status_rejected():
    dirt_statuses = [('not a boolean', 'CLEAN'), ('t', 'blah')]
    for dirt_status in dirt_statuses:
        with pytest.raises(ValueError):
            BasicVacuumWorld(agent_location=['A'], dirt_status=dirt_status)


def test_state_has_agent_location():
    dirt_status = ['t', 't']
    for agent_location in BasicVacuumWorld.locations:
        environment = BasicVacuumWorld(agent_location=[agent_location],
                                       dirt_status=dirt_status)
        assert environment.state['agent_location'] == agent_location


def test_state_has_dirt_status():
    dirt_statuses = [('t', 'f'), ('f', 't'), ('f', 'f')]
    for dirt_status in dirt_statuses:
        environment = BasicVacuumWorld(agent_location=['A'],
                                       dirt_status=dirt_status)
        assert environment.state['dirt_status'] == {
            'A': status_mapping[dirt_status[0]],
            'B': status_mapping[dirt_status[1]]
        }


def test_location_is_observable():
    for agent_location in BasicVacuumWorld.locations:
        environment = BasicVacuumWorld(agent_location=[agent_location],
                                       dirt_status=['t', 'f'])
        assert environment.observable_state['agent_location'] == agent_location


def test_same_location_dirt_is_observable():
    locations = BasicVacuumWorld.locations
    for i in range(len(locations)):
        for is_dirty in ('t', 'f'):
            starting_state = ['f'] * len(locations)
            starting_state[i] = is_dirty
            environment = BasicVacuumWorld(agent_location=[locations[i]],
                                           dirt_status=starting_state)
            assert environment.observable_state['is_dirty'] == \
                status_mapping[is_dirty]


def test_illegal_action_fails(dirty_floor):
    with pytest.raises(ValueError):
        dirty_floor.update('FOOBAR')


def test_suck_removes_dirt():
    for agent_location in BasicVacuumWorld.locations:
        dirt_status = ['t', 't']
        environment = BasicVacuumWorld(agent_location=[agent_location],
                                       dirt_status=dirt_status)
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
    environment = BasicVacuumWorld(agent_location=['B'],
                                   dirt_status=['t', 't'])
    environment.update('LEFT')
    assert environment.observable_state['agent_location'] == 'A'
