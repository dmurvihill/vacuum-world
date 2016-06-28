import pytest
from unittest.mock import Mock, patch

from roomba_world_search import *


@pytest.fixture
def is_legal_state(request):
    my_patch = patch('roomba_world_search.is_legal_agent_state')
    is_legal_state = my_patch.start()
    is_legal_state.return_value = (True, '')
    request.addfinalizer(lambda: my_patch.stop())
    return is_legal_state


class TestIsGoal(object):

    def test_returns_false_when_some_locations_are_unvisited(self,
                                                             is_legal_state):
        agent_state = AgentState(visited_locations={(0, 0)},
                                 all_locations={(0, 0), (0, 1)},
                                 agent_location=(0, 0))
        assert not is_goal(agent_state)

    def test_returns_true_when_all_locations_are_visited(self, is_legal_state):
        agent_state = AgentState(visited_locations={(0, 0), (0, 1)},
                                 all_locations={(0, 0), (0, 1)},
                                 agent_location=(0, 0))
        assert is_goal(agent_state)


class TestInitialState(object):

    def test_sets_agent_location_directly(self, is_legal_state):
        for agent_location in {(0, 0), (0, 1)}:
            state = initial_state(all_locations={(0, 0), (0, 1)},
                                  agent_location=agent_location)
            assert state.agent_location == agent_location

    def test_sets_all_locations_directly(self, is_legal_state):
        for all_locations in {frozenset({(0, 0), (0, 1), (1, 1)}),
                              frozenset({(0, 0), (0, 1)})}:
            state = initial_state(all_locations=all_locations,
                                  agent_location=(0, 0))
            assert state.all_locations == all_locations

    def test_converts_iterable_locations_to_set(self, is_legal_state):
        state = initial_state(all_locations=((0, 0), (0, 1)),
                              agent_location=(0, 0))
        assert isinstance(state.all_locations, set)

    def test_marks_only_agent_location_as_visited(self, is_legal_state):
        for agent_location in {(0, 0), (0, 1)}:
            state = initial_state(all_locations={(0, 0), (0, 1)},
                                  agent_location=agent_location)
            assert state.visited_locations == {agent_location}

    def test_raises_value_error_when_state_is_illegal(self, is_legal_state):
        for message in {'test_message_1', 'test_message_2'}:
            is_legal_state.return_value = (False, message)
            with pytest.raises(ValueError) as error:
                initial_state(all_locations={(0, 1), (1, 1)},
                              agent_location=(0, 0))
            assert MSG_ILLEGAL_STATE.format(message) in str(error)


class TestPathCost(object):

    def test_returns_1_for_legal_action(self):
        for action in {'RIGHT', 'LEFT'}:
            with patch('roomba_world_search.legal_actions') as legal_actions:
                legal_actions.return_value = {'RIGHT', 'LEFT'}
                agent_state = Mock()
                assert path_cost(agent_state, action) == 1

    def test_raises_value_error_when_action_is_illegal(self):
        for action in {'RIGHT', 'LEFT'}:
            with patch('roomba_world_search.legal_actions') as legal_actions:
                legal_actions.return_value = {'UP', 'DOWN'}
                agent_state = Mock()
                with pytest.raises(ValueError) as error:
                    path_cost(agent_state, action)
                assert MSG_ILLEGAL_ACTION.format(action) in str(error)
                assert legal_actions.call_count == 1
                assert legal_actions.call_args == ((agent_state,), {})


class TestLegalActions(object):

    def test_returns_direction_based_on_relative_agent_location(self):
        agent_locations = ((0, 1), (2, 1), (1, 0), (1, 2), (0, 2), (2, 0))
        target_locations = ((1, 1), (1, 1), (1, 1), (1, 1), (1, 2), (2, 1))
        directions = ('DOWN', 'UP', 'RIGHT', 'LEFT', 'DOWN', 'RIGHT')
        for (agent_location, target_location, direction) \
                in zip(agent_locations, target_locations, directions):
            state = AgentState(visited_locations={agent_location},
                               all_locations={agent_location, target_location},
                               agent_location=agent_location)
            assert direction in legal_actions(state)

    def test_returns_correct_direction_for_adjacent_location(self):
        locations = ((0, 1), (2, 1), (1, 0), (1, 2))
        directions = ('UP', 'DOWN', 'LEFT', 'RIGHT')
        for (location, direction) in zip(locations, directions):
            state = AgentState(visited_locations={(1, 1)},
                               all_locations={(1, 1), location},
                               agent_location=(1, 1))
            assert direction in legal_actions(state)

    def test_ignores_locations_not_adjacent_to_agent(self):
        agent_location = (1, 1)
        locations = {(1, 0), (1, 1), (1, 2), (1, 3)}
        state = AgentState(visited_locations={agent_location},
                           all_locations=locations,
                           agent_location=agent_location)
        assert legal_actions(state) == {'LEFT', 'RIGHT'}


class TestNextState(object):

    @pytest.fixture
    def starting_states(self):
        all_locations = {(i, j) for i in range(4) for j in range(4)}
        return (AgentState(visited_locations={agent_location},
                           all_locations=all_locations,
                           agent_location=agent_location)
                for agent_location in ((1, 1), (2, 2)))

    def test_right_increments_ypos(self, starting_states):
        for state in starting_states:
            (xpos, ypos) = state.agent_location
            assert self._is_agent_in_correct_square_after_move(
                state, 'RIGHT', (xpos, ypos + 1))

    def test_left_decrements_ypos(self, starting_states):
        for state in starting_states:
            (xpos, ypos) = state.agent_location
            assert self._is_agent_in_correct_square_after_move(
                state, 'LEFT', (xpos, ypos - 1))

    def test_up_decrements_xpos(self, starting_states):
        for state in starting_states:
            (xpos, ypos) = state.agent_location
            assert self._is_agent_in_correct_square_after_move(
                state, 'UP', (xpos - 1, ypos))

    def test_down_increments_xpos(self, starting_states):
        for state in starting_states:
            (xpos, ypos) = state.agent_location
            assert self._is_agent_in_correct_square_after_move(
                state, 'DOWN', (xpos + 1, ypos))

    def test_movement_preserves_visited_locations(self, starting_states):
        for old_state in starting_states:
            (xpos, ypos) = old_state.agent_location
            new_state = next_state(old_state, 'RIGHT')
            assert new_state.visited_locations.issuperset(
                old_state.visited_locations)

    def test_movement_preserves_all_locations(self, starting_states):
        state = next(iter(starting_states))
        assert next_state(state, 'RIGHT').all_locations == state.all_locations

    def test_movement_marks_new_location_visited(self, starting_states):
        for state in starting_states:
            (xpos, ypos) = state.agent_location
            new_state = next_state(state, 'RIGHT')
            assert (xpos, ypos + 1) in new_state.visited_locations

    def test_raises_value_error_on_non_movement_action(self, starting_states):
        state = next(iter(starting_states))
        with pytest.raises(ValueError) as error:
            next_state(state, 'NOPE')
        assert MSG_ILLEGAL_ACTION.format('NOPE') in str(error)

    def _is_agent_in_correct_square_after_move(
            self, state, action, new_location):
        return next_state(state, action).agent_location == new_location


class TestIsLegalAgentState(object):

    def test_fails_when_agent_is_outside_world(self):
        state = AgentState(visited_locations={(0, 0)},
                           all_locations={(0, 0)},
                           agent_location=(0, 1))
        (is_legal, message) = is_legal_agent_state(state)
        assert not is_legal
        assert message == MSG_AGENT_OUT_OF_BOUNDS

    def test_fails_when_visited_locations_do_not_exist(self):
        state = AgentState(visited_locations={(0, 0), (0, 2)},
                           all_locations={(0, 0), (0, 1)},
                           agent_location=(0, 1))
        (is_legal, message) = is_legal_agent_state(state)
        assert not is_legal
        assert message == MSG_VISITED_ILLEGAL_LOCATION.format((0, 2))

    def test_responds_with_true_and_empty_string_when_state_is_legal(self):
        state = AgentState(visited_locations={(0, 0)},
                           all_locations={(0, 0), (0, 1)},
                           agent_location=(0, 1))
        (is_legal, message) = is_legal_agent_state(state)
        assert is_legal
        assert message == ''
