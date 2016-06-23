from collections import namedtuple
from queue import Queue

SearchNode = namedtuple('SearchNode', ('state', 'parent', 'parent_action'))


class MissionaryCannibalProblem(object):

    def initial_state(self):
        return 3, 3, 1

    def is_goal(self, state):
        return state == (0, 0, 0)

    def legal_actions(self, state):
        sign = -1 if state[2] == 1 else 1
        actions = set()
        for move_counts in {(0, 2, 1), (0, 1, 1), (1, 1, 1), (1, 0, 1), (2, 0, 1)}:
            action = tuple(sign * ct for ct in move_counts)
            new_state = self.next_state(state, action)
            if self.is_legal_state(new_state):
                actions.add(action)
        return actions

    def is_legal_state(self, state):
        if not all(0 <= ct <= 3 for ct in state[:2]):
            return False
        left_side_counts = state[:2]
        right_side_counts = tuple((3 - ct for ct in state[:2]))
        for (num_miss, num_can) in (left_side_counts, right_side_counts):
            if num_can > num_miss > 0:
                return False
        return True

    def next_state(self, state, action):
        return tuple((sc + ac for (sc, ac) in zip(state, action)))

    def path_cost(self, state, action):
        return 1


class MissionaryCannibalEnvironment(object):

    def __init__(self):
        self._problem = MissionaryCannibalProblem()
        self._state = self._problem.initial_state()

    @property
    def state(self):
        return self._state

    @property
    def observable_state(self):
        return self._state

    def update(self, action):
        self._state = self._problem.next_state(self._state, action)


class GraphSearchAgent(object):

    def __init__(self):
        self._path = None
        self._problem = MissionaryCannibalProblem()

    def decide(self, state):
        if self._path is None:
            self._path = graph_search(self._problem, Queue())
        elif len(self._path) == 0:
            return 0, 0, 0
        action = self._path[0]
        self._path = self._path[1:]
        return action


class MissionaryCannibalEvaluator(object):

    def __init__(self):
        self._num_steps = 0
        self._is_goal = False
        self._problem = MissionaryCannibalProblem()

    @property
    def score(self):
        return self._num_steps if self._is_goal else 0

    def update(self, state):
        self._is_goal = self._problem.is_goal(state)
        if not self._is_goal:
            self._num_steps += 1


def graph_search(problem, frontier):
    explored = set()
    frontier.put(SearchNode(problem.initial_state(), None, None))
    solution_node = None

    while solution_node is None:
        expanding_node = frontier.get()
        expanding_state = expanding_node.state
        if expanding_state not in explored:
            explored.add(expanding_node)
            if problem.is_goal(expanding_state):
                solution_node = expanding_node
            else:
                for action in problem.legal_actions(expanding_state):
                    next_state = problem.next_state(expanding_state, action)
                    search_node = SearchNode(next_state,
                                             expanding_node,
                                             action)
                    frontier.put(search_node)

    actions = expand_path(solution_node)
    return actions


def expand_path(search_node):
    if search_node.parent_action is None:
        solution_path = tuple()
    else:
        parent_path = expand_path(search_node.parent)
        solution_path = parent_path + (search_node.parent_action,)
    return solution_path

