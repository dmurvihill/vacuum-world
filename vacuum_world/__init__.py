NUM_TRIALS = 1000


def run_experiment(environment, agent):
    """
    Simulate an agent in the environment for 1000 steps.

    :param environment: where the agent must perform
    :param agent: agent to evaluate
    """
    for i in range(1000):
        percept = environment.trigger_sensors()
        decision = agent.decide(percept)
        environment.update(decision)
