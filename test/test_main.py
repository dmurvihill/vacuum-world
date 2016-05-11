import random

from unittest.mock import Mock

import vacuum_world


def test_run_experiment_loops_1000_times():
    agent = Mock()
    environment = Mock()

    vacuum_world.run_experiment(environment=environment, agent=agent)

    assert agent.decide.call_count == 1000
    assert environment.update.call_count == 1000


def test_agent_affects_and_perceives_environment():
    agent = Mock()
    environment = Mock()

    _assert_argument_passing(_close_over_experiment(environment, agent),
                             agent.decide,
                             environment.update)


def test_agent_perceives_true_environment():
    agent = Mock()
    environment = Mock()

    _assert_argument_passing(_close_over_experiment(environment, agent),
                             environment.trigger_sensors,
                             agent.decide)


def _close_over_experiment(environment, agent):
    return lambda: vacuum_world.run_experiment(environment=environment,
                                               agent=agent)


def _assert_argument_passing(experiment, function_a, function_b):
    """
    Assert that output from function A is always passed as input to function B.
    """
    possible_outputs = ['out1', 'out2', 'out3']
    outputs_from_a = []

    def a(*_):
        output = random.choice(possible_outputs)
        outputs_from_a.append(output)
        return output

    function_a.side_effect = a

    experiment()

    assert len(outputs_from_a) == function_b.call_count
    for a_out, b_in in zip(outputs_from_a, function_b.call_args_list):
        assert b_in == ((a_out,), {})
