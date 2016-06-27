from collections import namedtuple
from queue import Queue


Problem = namedtuple('Problem', ['initial_state', 'is_goal', 'path_cost',
                                 'legal_actions', 'next_state'])
PathNode = namedtuple('PathNode', ['state', 'parent_node', 'parent_action'])


def graph_search(problem, frontier_strategy):
    initial_state = problem.initial_state()
    explored_states = set()
    path = ()
    frontier = frontier_strategy()
    frontier.put(PathNode(initial_state, None, None))
    goal_node = None

    while not goal_node and frontier.qsize() > 0:
        expanding_node = frontier.get()
        expanding_state = expanding_node.state
        if expanding_state not in explored_states:
            explored_states.add(expanding_state)
            if problem.is_goal(expanding_state):
                goal_node = expanding_node
            else:
                for action in problem.legal_actions(expanding_state):
                    next_state = problem.next_state(expanding_state, action)
                    frontier.put(PathNode(next_state, expanding_node, action))

    result = _expand_path(goal_node) if goal_node is not None else None
    return result


def _expand_path(path_node):
    if path_node.parent_node is None:
        path = ()
    else:
        path = _expand_path(path_node.parent_node) + (path_node.parent_action,)
    return path


def first(test, lst):
    if len(lst) == 0:
        result = None
    elif test(lst[0]):
        result = lst[0]
    else:
        result = first(test, lst[1:])
    return result
