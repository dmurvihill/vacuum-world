NUM_TRIALS = 1000


def run_experiment(environment, agent):
    """
    Simulate an agent in the environment for 1000 steps.

    :param environment: where the agent must perform
    :param agent: agent to evaluate
    """
    for i in range(1000):
        decision = agent.decide(environment.observable_state)
        environment.update(decision)


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

        :param action: The action the agent takes. Allowed values are 'LEFT', 'RIGHT', and 'SUCK'.
        """
        if action == 'SUCK':
            self._dirt_status[self._agent_location] = False
        elif action == 'RIGHT':
            self._agent_location = 'B'
        elif action == 'LEFT':
            self._agent_location = 'A'
        else:
            assert action in [BasicVacuumWorld.actions]
