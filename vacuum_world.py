import argparse
import importlib
import logging
import sys


NUM_TRIALS = 1000
LOGGER_NAME = "vacuum_world"
LOG_LEVEL = logging.INFO

MSG_AGENT_DECISION = "t={}\tAgent Decision: {}"
MSG_AGENT_ERROR = "Agent caused the following error: {}"
MSG_AGENT_NOT_FOUND = "Could not load agent \'{}\'"
MSG_DESCRIPTION_AGENT = "Import path and class name for the agent"
MSG_DESCRIPTION_AGENT_LOCATION = "Initial location of the agent"
MSG_DESCRIPTION_DIRT_STATUS = "Initial dirt status each location. 't' for a" \
                              "dirty floor, 'f' for a clean one."
MSG_DESCRIPTION_PROGRAM = "Agent evaluator and environment simulator for " \
                          "the vacuum world described in AIMA, page 38."
MSG_BAD_BOOLEAN_STR = "Invalid boolean string: {}"
MSG_COMPLETE = "Simulation complete."
MSG_HELLO = "Vacuum World Simulator v1.0"
MSG_MODULE_NOT_LOADED = "Could not load agent module \'{}\'"
MSG_SCORE = "Agent Score: {}"

DIRTY_VALUES = ('y', 'yes', 't', 'true', 'dirty')
CLEAN_VALUES = ('n', 'no', 'f', 'false', 'clean')


class AgentError(Exception):
    def __init__(self, cause):
        self.cause = cause


def run_experiment(environment, agent, evaluator):
    """
    Simulate an agent in the environment for 1000 steps.

    Decisions are logged to the 'vacuum_world' logger.

    :param environment: where the agent must perform
    :param agent: agent to evaluate
    :param evaluator: object that scores the agent against the
      performance measure
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(LOG_LEVEL)

    for t in range(1, 1001):
        try:
            decision = agent.decide(environment.observable_state)
        except Exception as e:
            raise AgentError(e)
        logger.info(MSG_AGENT_DECISION.format(t, repr(decision)))
        try:
            environment.update(decision)
        except ValueError as e:
            raise AgentError(e)
        evaluator.update(environment.state)


class BasicVacuumWorld(object):
    """
    Basic vacuum world specified on page 38 and depicted in Figure 2.2.

    There are two locations, A and B, and one agent. Either or both
    locations may contain dirt. The agent perceives its current location
    and whether there is dirt there.

    The agent may move left, move right, or suck up the dirt in its
    current location. Sucking cleans the current square and clean
    squares stay clean.
    """
    locations = ['A', 'B']
    actions = ['LEFT', 'RIGHT', 'SUCK']

    def __init__(self, agent_location, dirt_status):
        """
        Initialize a new environment.

        :param agent_location: Starting location of the agent.
        :param dirt_status: A dictionary mapping from each location in
          the environment to a boolean value indicating whether there is
          dirt in that location.
        """
        assert agent_location in BasicVacuumWorld.locations
        assert set(dirt_status.keys()) == set(BasicVacuumWorld.locations)
        assert all((type(status) == bool for status in dirt_status.values()))
        self._agent_location = agent_location
        self._dirt_status = dirt_status

    @property
    def state(self):
        """
        All information, observable or not, about the state of the
        environment.

        A dictionary with two keys:
          - agent_location gives the agent's present location
          - dirt_status is a dictionary with a key for each location,
            and a boolean indicating whether there is dirt in that
            location.
        """
        return {
            "agent_location": self._agent_location,
            "dirt_status": self._dirt_status
        }

    @property
    def observable_state(self):
        """
        All information the agent's sensors can observe.

        A dictionary with two keys:
          - agent_location gives the agent's present location.
          - is_dirty is True if there is dirt in the agent's present
              location.
        """
        return {
            "agent_location": self._agent_location,
            "is_dirty": self._dirt_status[self._agent_location]
        }

    def update(self, action):
        """
        Update the environment with the results of an action taken by
        the agent's actuators.

        :param action: The action the agent takes. Allowed values are
          'LEFT', 'RIGHT', and 'SUCK'.
        """
        if action == 'SUCK':
            self._dirt_status[self._agent_location] = False
        elif action == 'RIGHT':
            self._agent_location = 'B'
        elif action == 'LEFT':
            self._agent_location = 'A'
        else:
            raise ValueError(action)


class CleanFloorEvaluator(object):
    """
    Evaluator that scores Vacuum World environments highly for having
    clean floors.
    """
    def __init__(self):
        self._score = 0

    def update(self, state):
        """
        Award one point for each location that is clear of dirt.

        :param state: Environment state dictionary that has a
          "dirt_status" key, which maps to a dictionary of
          location -> has_dirt.
        """
        self._score += list(state["dirt_status"].values()).count(False)

    @property
    def score(self):
        """
        Sum of the total number of time steps each location has been
        clear of dirt.
        """
        return self._score


class SuckyAgent(object):
    """
    Vacuum World agent that only chooses the SUCK action.
    """
    def decide(self, _):
        """
        Suck up the dirt, if there is any.

        :param _: for compliance with the agent interface; not used.
        """
        return 'SUCK'


def main():
    # Set up logging
    logger = logging.getLogger()
    handler = logging.StreamHandler(stream=sys.stdout)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    # Parse arguments
    arg_parser = argparse.ArgumentParser(description=MSG_DESCRIPTION_PROGRAM)
    arg_parser.add_argument('--agent', type=str, required=False,
                            default='SuckyAgent', metavar='AGENT_CLASS',
                            help=MSG_DESCRIPTION_AGENT)
    arg_parser.add_argument('--dirt-status', type=_strtobool, nargs=2,
                            required=False, default=[True, True],
                            metavar=('LOC_A_STATUS', 'LOC_B_STATUS'),
                            help=MSG_DESCRIPTION_DIRT_STATUS)
    arg_parser.add_argument('--agent-location', type=str, required=False,
                            default='A', choices=BasicVacuumWorld.locations,
                            help=MSG_DESCRIPTION_AGENT_LOCATION)
    args = arg_parser.parse_args()

    logger.info(MSG_HELLO)

    try:
        agent_class = _load_agent(args.agent)
    except ImportError as e:
        logger.error(MSG_MODULE_NOT_LOADED.format(e.name))
        return 1
    except _ClassNotFoundError:
        logger.error(MSG_AGENT_NOT_FOUND.format(args.agent))
        return 1

    dirt_status_tuples = zip(BasicVacuumWorld.locations, args.dirt_status)
    dirt_status = {location: status for location, status in dirt_status_tuples}
    evaluator = CleanFloorEvaluator()

    try:
        run_experiment(BasicVacuumWorld(args.agent_location, dirt_status),
                       agent_class(),
                       evaluator)

        logger.info(MSG_COMPLETE)
    except AgentError as e:
        logger.error(MSG_AGENT_ERROR.format(repr(e.cause)))

    score = evaluator.score
    logger.info(MSG_SCORE.format(score))


def _strtobool(string):
    string = string.lower()
    if string in DIRTY_VALUES:
        value = True
    elif string in CLEAN_VALUES:
        value = False
    else:
        message = MSG_BAD_BOOLEAN_STR.format(string)
        raise argparse.ArgumentTypeError(message)
    return value


def _load_agent(agent_path):
    agent_path_segments = agent_path.split('.')
    agent_module_name = '.'.join(agent_path_segments[:-1])
    agent_class_name = agent_path_segments[-1]
    if agent_module_name != '':
        agent_module = importlib.import_module(agent_module_name)
        try:
            agent_class = getattr(agent_module, agent_class_name)
        except AttributeError:
            raise _ClassNotFoundError
    else:
        try:
            agent_class = globals()[agent_class_name]
        except KeyError:
            raise _ClassNotFoundError
    return agent_class


class _ClassNotFoundError(Exception):
    pass


if __name__ == '__main__':
    main()
