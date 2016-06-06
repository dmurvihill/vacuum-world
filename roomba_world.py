import random
from collections import namedtuple


MSG_WRONG_ARGV_LEN = "expected {} value(s) for {}, got '{}'"
MSG_ILLEGAL_FLOOR_STATE_CHR = "Unexpected character in floor state file: '{}'"
MSG_ILLEGAL_ACTION = "Unrecognized action: {}"
MSG_INVALID_PARAM = "Invalid parameter for '{}': '{}' ({})"
REPR_LOCATION = "{}, {} location"
STR_CLEAN = "clean"
STR_DIRTY = "dirty"
STR_EXPECTED_BOOLEAN = "expected a boolean"
STR_IMPASSABLE = "impassable"
STR_OUT_OF_BOUNDS = "out of bounds"
STR_PASSABLE = "passable"


class RoombaWorld(object):

    State = namedtuple('State', ['floor_status', 'agent_location'])
    ObservableState = namedtuple('ObservableState', ['agent_location',
                                                     'is_dirty'])
    Point = namedtuple('Point', ['x', 'y'])

    @staticmethod
    def _read_floor_status(floor_state_file):
        x = 0
        y = 0
        floor_status = {}
        for line in floor_state_file.readlines():
            for char in line.rstrip():
                if char == '.':
                    location = Location(is_dirty=False)
                elif char == '+':
                    location = Location(is_dirty=True)
                elif char == 'x':
                    location = Obstacle()
                else:
                    raise ValueError(MSG_ILLEGAL_FLOOR_STATE_CHR.format(char))
                floor_status[(x, y)] = location
                y += 1
            x += 1
            y = 0
        return floor_status

    def __init__(self, agent_location, floor_state_path):
        if len(floor_state_path) != 1:
            raise ValueError(MSG_WRONG_ARGV_LEN.format(1,
                                                       'floor_state_path',
                                                       repr(floor_state_path)))

        self._floor_status = self._initialize_floor_state(floor_state_path)
        self._agent_location = self._initialize_agent_location(agent_location)

    @property
    def state(self):
        return RoombaWorld.State(floor_status=self._floor_status,
                                 agent_location=tuple(self._agent_location))

    @property
    def observable_state(self):
        agent_location = tuple(self._agent_location)
        is_dirty = self._floor_status[self._agent_location].is_dirty
        return RoombaWorld.ObservableState(agent_location=agent_location,
                                           is_dirty=is_dirty)

    def update(self, action):
        old_loc = self._agent_location
        if action == 'UP':
            new_loc = RoombaWorld.Point(old_loc.x - 1, old_loc.y)
        elif action == 'DOWN':
            new_loc = RoombaWorld.Point(old_loc.x + 1, old_loc.y)
        elif action == 'LEFT':
            new_loc = RoombaWorld.Point(old_loc.x, old_loc.y - 1)
        elif action == 'RIGHT':
            new_loc = RoombaWorld.Point(old_loc.x, old_loc.y + 1)
        elif action == 'SUCK':
            new_loc = old_loc
            self._floor_status[(old_loc.x, old_loc.y)].is_dirty = False
        else:
            raise ValueError(MSG_ILLEGAL_ACTION.format(action))

        if new_loc in self._floor_status.keys() \
                and self._floor_status[new_loc].is_passable:
            self._agent_location = new_loc

    def _initialize_floor_state(self, floor_state_path):
        floor_state_file = open(floor_state_path[0], 'r')
        try:
            floor_status = RoombaWorld._read_floor_status(floor_state_file)
        finally:
            floor_state_file.close()
        return floor_status

    def _initialize_agent_location(self, agent_location):
        if len(agent_location) != 2:
            raise ValueError(MSG_WRONG_ARGV_LEN.format(2,
                                                       'agent_location',
                                                       repr(agent_location)))
        agent_location = RoombaWorld.Point(*(int(x) for x in agent_location))
        if agent_location not in self._floor_status.keys():
            failure_reason = STR_OUT_OF_BOUNDS
        elif not self._floor_status[agent_location].is_passable:
            failure_reason = STR_IMPASSABLE
        else:
            failure_reason = None

        if failure_reason:
            message = MSG_INVALID_PARAM.format("agent_location",
                                               agent_location,
                                               failure_reason)
            raise ValueError(message)
        return agent_location


class Location(object):

    is_dirty_str = {
        True: STR_DIRTY,
        False: STR_CLEAN
    }

    is_passable_str = {
        True: STR_PASSABLE,
        False: STR_IMPASSABLE
    }

    def __init__(self, is_dirty):
        if is_dirty not in (True, False):
            raise TypeError(MSG_INVALID_PARAM.format("is_dirty",
                                                     is_dirty,
                                                     STR_EXPECTED_BOOLEAN))
        self._is_dirty = is_dirty

    def __eq__(self, other):
        return self.is_dirty == other.is_dirty and \
               self.is_passable == other.is_passable

    def __repr__(self):
        return REPR_LOCATION.format(Location.is_dirty_str[self.is_dirty],
                                    Location.is_passable_str[self.is_passable])

    @property
    def is_dirty(self):
        return self._is_dirty

    @is_dirty.setter
    def is_dirty(self, is_dirty):
        self._is_dirty = is_dirty

    @property
    def is_passable(self):
        return True


class Obstacle(Location):

    def __init__(self):
        Location.__init__(self, is_dirty=False)

    @property
    def is_passable(self):
        return False


class CleanFloorEvaluator(object):

    def __init__(self):
        self._score = 0

    def update(self, state):
        locations = state.floor_status.values()
        self._score += len([x for x in locations if not x.is_dirty])

    @property
    def score(self):
        return self._score


class RandomReflexAgent(object):

    action = {
        0: 'UP',
        1: 'DOWN',
        2: 'LEFT',
        3: 'RIGHT'
    }

    def decide(self, state):
        if state.is_dirty:
            return 'SUCK'
        else:
            return RandomReflexAgent.action[random.randint(0, 3)]
