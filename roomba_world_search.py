from collections import namedtuple

AgentState = namedtuple('AgentState',
                        ['visited_locations',
                         'all_locations',
                         'agent_location'])

MSG_AGENT_OUT_OF_BOUNDS = 'agent out of bounds'
MSG_ILLEGAL_ACTION = 'Illegal action \'{}\''
MSG_ILLEGAL_STATE = 'Illegal state: {}'
MSG_VISITED_ILLEGAL_LOCATION = 'location \'{}\' does not exist but was visited.'


def is_goal(agent_state):
    return agent_state.visited_locations == agent_state.all_locations


def initial_state(all_locations, agent_location):
    initial_state = AgentState(visited_locations={agent_location},
                               all_locations=set(all_locations),
                               agent_location=agent_location)
    (is_legal_state, validation_message) = is_legal_agent_state(initial_state)
    if not is_legal_state:
        raise ValueError(MSG_ILLEGAL_STATE.format(validation_message))
    return initial_state


def path_cost(agent_state, action):
    if action in legal_actions(agent_state):
        return 1
    else:
        raise ValueError(MSG_ILLEGAL_ACTION.format(action))


def legal_actions(agent_state):
    agent_xpos = agent_state.agent_location[0]
    agent_ypos = agent_state.agent_location[1]
    action_mapping = {
        'UP': (agent_xpos - 1, agent_ypos),
        'DOWN': (agent_xpos + 1, agent_ypos),
        'LEFT': (agent_xpos, agent_ypos - 1),
        'RIGHT': (agent_xpos, agent_ypos + 1)
    }
    return {direction for direction in action_mapping
            if action_mapping[direction] in agent_state.all_locations}


def next_state(agent_state, action):
    (xpos, ypos) = agent_state.agent_location
    if action == 'RIGHT':
        new_location = (xpos, ypos + 1)
    elif action == 'LEFT':
        new_location = (xpos, ypos - 1)
    elif action == 'UP':
        new_location = (xpos - 1, ypos)
    elif action == 'DOWN':
        new_location = (xpos + 1, ypos)
    else:
        raise ValueError(MSG_ILLEGAL_ACTION.format(action))
    visited_locations = agent_state.visited_locations.union({new_location})
    return AgentState(visited_locations=visited_locations,
                      all_locations=agent_state.all_locations,
                      agent_location=new_location)


def is_legal_agent_state(agent_state):
    if agent_state.agent_location not in agent_state.all_locations:
        is_valid = False
        message = MSG_AGENT_OUT_OF_BOUNDS
    elif len(agent_state.visited_locations - agent_state.all_locations) > 0:
        bad_locs = agent_state.visited_locations - agent_state.all_locations
        illegal_location = next(iter(bad_locs))
        is_valid = False
        message = MSG_VISITED_ILLEGAL_LOCATION.format(illegal_location)
    else:
        is_valid = True
        message = ''
    return is_valid, message