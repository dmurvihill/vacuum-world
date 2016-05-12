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
    locations = ['A', 'B']

    def __init__(self, agent_location, dirt_status):
        assert agent_location in BasicVacuumWorld.locations
        assert set(dirt_status.keys()) == set(BasicVacuumWorld.locations)
        assert all((type(status) == bool for status in dirt_status.values()))
        self._agent_location = agent_location
        self._dirt_status = dirt_status

    @property
    def observable_state(self):
        return {
            "agent_location": self._agent_location,
            "is_dirty": self._dirt_status[self._agent_location]
        }
