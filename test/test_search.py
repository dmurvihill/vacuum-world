from collections import namedtuple
from queue import LifoQueue, Queue
from unittest.mock import Mock

import search
from search import graph_search, Problem


ProblemEdge = namedtuple('ProblemEdge', ['old', 'action', 'new'])


class TestGraphSearch(object):

    def test_returns_empty_path_if_initial_state_is_goal(self):
        problem = Mock()
        problem.is_goal.return_value = True
        assert graph_search(problem, Queue) == ()

    def test_returns_first_action_if_it_leads_to_goal(self):
        action_names = ('action1', 'action2')
        for action_name in action_names:
            edges = (ProblemEdge('start', action_name, 'goal'),)
            problem = basic_problem('start', ('goal',), edges)
            assert graph_search(problem, Queue) == (action_name,)

    def test_returns_second_action_if_it_leads_to_goal(self):
        edges = (ProblemEdge('start', 'action1', 'not_goal'),
                 ProblemEdge('start', 'action2', 'goal'))
        problem = basic_problem('start', ('goal',), edges)
        assert graph_search(problem, Queue) == ('action2',)

    def test_follows_longer_paths_to_goal(self):
        edges = (ProblemEdge('start', 'action1', 'not_goal'),
                 ProblemEdge('not_goal', 'action2', 'goal'))
        problem = basic_problem('start', ('goal',), edges)
        assert graph_search(problem, Queue) == ('action1', 'action2')

    def test_ignores_loops(self):
        edges = (ProblemEdge('start', 'action1', 'not_goal'),
                 ProblemEdge('not_goal', 'loop_action', 'start'))
        problem = basic_problem('start', ('goal',), edges)
        assert graph_search(problem, Queue) is None

    def test_expands_according_to_frontier_strategy(self):
        edges = (ProblemEdge('start', 'action2', 'goal'),
                 ProblemEdge('start', 'action1', 'not_goal'),
                 ProblemEdge('not_goal', 'action3', 'goal'))
        problem = basic_problem('start', ('goal',), edges)
        assert graph_search(problem, LifoQueue) == ('action1', 'action3')

    def test_returns_none_when_no_path_to_goal(self):
        problem = basic_problem('start', ('goal',), ())
        assert graph_search(problem, Queue) is None


class TestFirst(object):

    def test_returns_none_for_empty_list(self):
        assert search.first(lambda _: True, []) is None

    def test_returns_first_item_whose_value_is_true(self):
        lst = [{'key': 1, 'value': 2}, {'key': 2, 'value': 1}]
        assert search.first(lambda x: x['value'] == 2, lst)['key'] == 1
        assert search.first(lambda x: x['value'] == 1, lst)['key'] == 2


def basic_problem(start_state, goal_states, edges):
    def initial_state():
        return start_state

    def is_goal(state):
        return state in goal_states

    def path_cost(state, action):
        return 1

    def legal_actions(state):
        return [edge.action for edge in edges if edge.old == state]

    def next_state(state, action):
        return search.first(lambda e: e.old == state and e.action == action, edges).new

    return Problem(initial_state, is_goal, path_cost, legal_actions,
                   next_state)
