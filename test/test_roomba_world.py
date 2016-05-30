from unittest.mock import MagicMock, Mock

import pytest

from roomba_world import *


@pytest.fixture
def floor_file(monkeypatch):
    my_open = Mock()
    file = MagicMock()
    my_open.return_value = file
    file.readlines.return_value = ['.\n']
    file.__enter__ = Mock(return_value=file)
    file.__exit__ = Mock()
    monkeypatch.setattr("builtins.open", my_open)
    return file


class TestRoombaWorld(object):
    def test_reads_environment_from_file(self, monkeypatch):
        my_open = MagicMock()
        my_open.return_value.readlines.return_value = ['.']
        monkeypatch.setattr("builtins.open", my_open)
        RoombaWorld(agent_location=["0", "0"],
                    floor_state_path=["different/path/from/other/tests"])
        assert my_open.call_args == (("different/path/from/other/tests", 'r'),
                                     {})

    def test_expects_floor_states_with_one_argument(self, floor_file):
        with pytest.raises(ValueError):
            RoombaWorld(agent_location=["0", "0"],
                        floor_state_path=[])
        with pytest.raises(ValueError) as e:
            paths = ["path1", "path2"]
            RoombaWorld(agent_location=["0", "0"],
                        floor_state_path=paths)
            message = MSG_WRONG_ARGV_LEN.format(1,
                                                'floor_state_path',
                                                repr(paths))
            assert e.message == message
        RoombaWorld(agent_location=["0", "0"],
                    floor_state_path=["some/path"])

    def test_reads_dot_as_clean_floor(self, floor_file):
        floor_file.readlines.return_value = ['.\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.floor_status[(0, 0)] == Location(
            is_dirty=False)

    def test_reads_plus_as_dirty_floor(self, floor_file):
        floor_file.readlines.return_value = ['+\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.floor_status[(0, 0)].is_dirty is True

    def test_reads_x_as_obstacle(self, floor_file):
        floor_file.readlines.return_value = ['.x\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.floor_status[(0, 1)] == Obstacle()

    def test_rejects_other_characters_in_floor_state(self, floor_file):
        floor_file.readlines.return_value = ['.b']
        with pytest.raises(ValueError) as e:
            RoombaWorld(agent_location=["0", "0"],
                        floor_state_path=["some/path"])
            assert e.message == MSG_ILLEGAL_FLOOR_STATE_CHR.format('b')

    def test_reads_increasing_ypos_to_the_right(self, floor_file):
        floor_file.readlines.return_value = ['+.\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.floor_status == {
            (0, 0): Location(is_dirty=True),
            (0, 1): Location(is_dirty=False)
        }

    def test_reads_increasing_xpos_down(self, floor_file):
        floor_file.readlines.return_value = ['+\n', '.\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.floor_status == {
            (0, 0): Location(is_dirty=True),
            (1, 0): Location(is_dirty=False)
        }

    def test_expects_two_argument_agent_start(self, floor_file):
        RoombaWorld(agent_location=["0", "0"], floor_state_path=["some/path"])
        with pytest.raises(ValueError) as e:
            RoombaWorld(agent_location=["0"], floor_state_path=["some/path"])
            message = MSG_WRONG_ARGV_LEN.format(2,
                                                'agent_location',
                                                str(["0"]))
            assert e.message == message
        with pytest.raises(ValueError) as e:
            RoombaWorld(agent_location=["0", "0", "0"],
                        floor_state_path=["some/path"])
            message = MSG_WRONG_ARGV_LEN.format(2,
                                                'agent_location',
                                                str(["0", "0", "0"]))
            assert e.message == message

    def test_expects_agent_start_in_bounds(self, floor_file):
        floor_file.readlines.return_value = ['..\n', '..\n']
        RoombaWorld(agent_location=["0", "0"], floor_state_path=["some/path"])

        out_of_bounds_starts = [["-1", "0"], ["2", "0"], ["0", "-1"],
                                ["0", "2"]]
        for agent_start in out_of_bounds_starts:
            with pytest.raises(ValueError) as e:
                agent_start_tuple = tuple(int(x) for x in agent_start)
                RoombaWorld(agent_location=agent_start,
                            floor_state_path=["some/path"])
                message = MSG_INVALID_PARAM.format('agent_location',
                                                   agent_start_tuple,
                                                   STR_OUT_OF_BOUNDS)
                assert e.message == message

    def test_expects_passable_agent_start(self, floor_file):
        floor_file.readlines.return_value = ['.x\n']
        RoombaWorld(agent_location=["0", "0"], floor_state_path=["some/path"])

        floor_file.readlines.return_value = ['.x\n']
        with pytest.raises(ValueError) as e:
            RoombaWorld(agent_location=["0", "1"],
                        floor_state_path=["some/path"])
            message_template = MSG_INVALID_PARAM
            message = message_template.format('agent_location',
                                              (0, 1),
                                              STR_IMPASSABLE)
            assert e.message == message

    def test_starts_agent_at_requested_location(self, floor_file):
        floor_file.readlines.return_value = ['..\n', '..\n']
        for location in ((0, 0), (0, 1), (1, 0)):
            location_param = list(str(x) for x in location)
            environment = RoombaWorld(agent_location=location_param,
                                      floor_state_path=["some/path"])
            assert environment.state.agent_location == location

    def test_shows_agent_location(self, floor_file):
        floor_file.readlines.return_value = ['..\n', '..\n']
        for location in ((0, 0), (0, 1), (1, 0)):
            location_param = list(str(x) for x in location)
            environment = RoombaWorld(agent_location=location_param,
                                      floor_state_path=["some/path"])
            assert environment.observable_state.agent_location == location

    def test_shows_dirt_at_agent_location(self, floor_file):
        floor_file.readlines.return_value = ['+.\n', '.+\n']
        for (location, is_dirty) in (((0, 0), True), ((0, 1), False)):
            location_param = list(str(x) for x in location)
            environment = RoombaWorld(agent_location=location_param,
                                      floor_state_path=["some/path"])
            assert environment.observable_state.is_dirty == is_dirty

    def test_moves_agent_in_requested_direction(self, floor_file):
        floor_file.readlines.return_value = ['..\n', '..\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.agent_location == (0, 0)
        environment.update('RIGHT')
        assert environment.state.agent_location == (0, 1)
        environment.update('DOWN')
        assert environment.state.agent_location == (1, 1)
        environment.update('LEFT')
        assert environment.state.agent_location == (1, 0)
        environment.update('UP')
        assert environment.state.agent_location == (0, 0)

    def test_moves_do_not_suck(self, floor_file):
        floor_file.readlines.return_value = ['++\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        environment.update('RIGHT')
        environment.update('LEFT')
        assert all(
            (x.is_dirty for x in environment.state.floor_status.values()))

    def test_does_not_change_when_agent_moves_out_of_bounds(self, floor_file):
        floor_file.readlines.return_value = ['..\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        environment.update('RIGHT')
        assert environment.state.agent_location == (0, 1)
        environment.update('RIGHT')
        assert environment.state.agent_location == (0, 1)

    def test_does_not_change_when_agent_moves_to_obstacle(self, floor_file):
        floor_file.readlines.return_value = ['.x\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.agent_location == (0, 0)
        environment.update('RIGHT')
        assert environment.state.agent_location == (0, 0)

    def test_removes_dirt_from_suck_location(self, floor_file):
        floor_file.readlines.return_value = ['+\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        assert environment.state.floor_status[(0, 0)].is_dirty
        environment.update('SUCK')
        assert not environment.state.floor_status[(0, 0)].is_dirty

    def test_rejects_other_actions(self, floor_file):
        floor_file.readlines.return_value = ['+\n']
        environment = RoombaWorld(agent_location=["0", "0"],
                                  floor_state_path=["some/path"])
        with pytest.raises(ValueError):
            environment.update('NOPE')


class TestLocation(object):
    def test_expects_is_dirty_as_boolean(self):
        Location(is_dirty=True)
        with pytest.raises(TypeError) as e:
            Location(is_dirty="notabool")
            message_template = MSG_INVALID_PARAM
            message = message_template.format("is_dirty",
                                              "notabool",
                                              STR_EXPECTED_BOOLEAN)
            assert e.message == message

    def test_allows_accessing_is_dirty(self):
        for dirt_status in (True, False):
            location = Location(is_dirty=dirt_status)
            assert location.is_dirty == dirt_status

    def test_allows_mutating_is_dirty(self):
        location = Location(is_dirty=True)
        location.is_dirty = False
        assert not location.is_dirty

    def test_is_passable(self):
        location = Location(is_dirty=False)
        assert location.is_passable

    def test_equals_checks_is_dirty(self):
        assert Location(is_dirty=False) == Location(is_dirty=False)
        assert Location(is_dirty=True) != Location(is_dirty=False)

    def test_equals_checks_is_passable(self):
        other = namedtuple('Tmp', ['is_dirty', 'is_passable'])
        location = Location(is_dirty=True)
        assert location == other(is_dirty=True, is_passable=True)
        assert location != other(is_dirty=True, is_passable=False)

    def test_repr_is_human_readable(self):
        dirt = [(True, STR_DIRTY), (False, STR_CLEAN)]
        msg_template = REPR_LOCATION
        for (is_dirty, is_dirty_str) in dirt:
            location = Location(is_dirty=is_dirty)
            message = msg_template.format(is_dirty_str,
                                          STR_PASSABLE)
            assert repr(location) == message


class TestObstacle(object):
    def test_is_clean(self):
        obstacle = Obstacle()
        assert not obstacle.is_dirty

    def test_is_not_passable(self):
        obstacle = Obstacle()
        assert not obstacle.is_passable

    def test_equals_checks_is_dirty(self):
        other = namedtuple('Tmp', ['is_dirty', 'is_passable'])
        obstacle = Obstacle()
        assert obstacle == other(is_dirty=False, is_passable=False)
        assert obstacle != other(is_dirty=True, is_passable=False)

    def test_equals_checks_is_passable(self):
        other = namedtuple('Tmp', ['is_dirty', 'is_passable'])
        obstacle = Obstacle()
        assert obstacle == other(is_dirty=False, is_passable=False)
        assert obstacle != other(is_dirty=False, is_passable=True)

    def test_repr_includes_passability(self):
        message = REPR_LOCATION.format(STR_CLEAN,
                                       STR_IMPASSABLE)
        assert repr(Obstacle()) == message


class TestCleanFloorEvaluator(object):
    def test_scores_0_with_no_updates(self):
        evaluator = CleanFloorEvaluator()
        assert evaluator.score == 0

    def test_scores_0_with_no_clean_squares(self):
        floor_status = {
            (0, 0): Location(True)
        }
        state = RoombaWorld.State(agent_location=(0, 0),
                                  floor_status=floor_status)
        evaluator = CleanFloorEvaluator()
        evaluator.update(state)
        assert evaluator.score == 0

    def test_scores_1_with_one_clean_square(self):
        floor_status = {
            (0, 0): Location(True),
            (0, 1): Location(False)
        }
        state = RoombaWorld.State(agent_location=(0, 0),
                                  floor_status=floor_status)
        evaluator = CleanFloorEvaluator()
        evaluator.update(state)
        assert evaluator.score == 1

    def test_scores_2_with_two_clean_squares(self):
        floor_status = {
            (0, 0): Location(False),
            (0, 1): Location(False)
        }
        state = RoombaWorld.State(agent_location=(0, 0),
                                  floor_status=floor_status)
        evaluator = CleanFloorEvaluator()
        evaluator.update(state)
        assert evaluator.score == 2

    def test_adds_to_score_each_update(self):
        floor_status = {
            (0, 0): Location(True),
            (0, 1): Location(False)
        }
        state = RoombaWorld.State(agent_location=(0, 0),
                                  floor_status=floor_status)
        evaluator = CleanFloorEvaluator()
        evaluator.update(state)
        evaluator.update(state)
        assert evaluator.score == 2


class TestRandomReflexAgent(object):
    @pytest.fixture
    def canned_rand(self, monkeypatch):
        random = Mock()
        random.side_effect = [0, 2, 1, 2, 3]
        monkeypatch.setattr('random.randint', random)

    def test_sucks_with_dirt(self):
        agent = RandomReflexAgent()
        state = RoombaWorld.ObservableState(agent_location=(0, 0),
                                            is_dirty=True)
        assert agent.decide(state) == 'SUCK'

    def test_moves_randomly_with_no_dirt(self, canned_rand):
        agent = RandomReflexAgent()
        location = (2, 2)
        state = RoombaWorld.ObservableState(agent_location=location,
                                            is_dirty=False)
        assert agent.decide(state) == 'UP'
        assert agent.decide(state) == 'LEFT'
        assert agent.decide(state) == 'DOWN'
        assert agent.decide(state) == 'LEFT'
        assert agent.decide(state) == 'RIGHT'
