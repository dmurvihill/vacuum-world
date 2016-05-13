import logging


NUM_TRIALS = 1000
LOGGER_NAME = "vacuum_world"
LOG_LEVEL = logging.INFO
MSG_AGENT_DECISION = "Agent_decision: {}"


def run_experiment(environment,
                   agent,
                   evaluator,
                   handler=logging.NullHandler()):
    """
    Simulate an agent in the environment for 1000 steps.

    :param environment: where the agent must perform
    :param agent: agent to evaluate
    :param evaluator: object that scores the agent against the
      performance measure
    :param handler: log handler to report environment changes to
    """
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(LOG_LEVEL)
    logger.addHandler(handler)

    for i in range(1000):
        decision = agent.decide(environment.observable_state)
        logger.info(MSG_AGENT_DECISION.format(repr(decision)))
        environment.update(decision)
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
            assert False


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
