from unittest.mock import Mock, PropertyMock

import vacuum_world


def test_run_experiment_loops_1000_times():
    agent = Mock()
    environment = Mock()
    evaluator = Mock()

    vacuum_world.run_experiment(environment, agent, evaluator)

    assert agent.decide.call_count == 1000
    assert environment.update.call_count == 1000
    assert evaluator.update.call_count == 1000


def test_agent_affects_and_perceives_environment():
    agent = Mock()
    environment = Mock()
    decisions = [Mock() for _ in range(1000)]
    agent.decide.side_effect = decisions

    vacuum_world.run_experiment(environment, agent, Mock())
    _assert_call_args(decisions, environment.update.call_args_list)


def test_agent_perceives_true_environment():
    agent = Mock()
    environment = Mock()
    states = [Mock() for _ in range(1000)]
    Mock.observable_state = PropertyMock(side_effect=states)

    try:
        vacuum_world.run_experiment(environment, agent, Mock())
        _assert_call_args(states, agent.decide.call_args_list)
    finally:
        del Mock.observable_state


def test_evaluator_sees_full_environment_state():
    environment = Mock()
    evaluator = Mock()
    states = [Mock() for _ in range(1000)]
    Mock.state = PropertyMock(side_effect=states)

    try:
        vacuum_world.run_experiment(environment, Mock(), evaluator)
        _assert_call_args(states, evaluator.update.call_args_list)
    finally:
        del Mock.state


def _assert_call_args(values, call_args_list):
    """
    Assert that each value is the sole argument to its counterpart in
    the call args list
    """
    assert len(values) == len(call_args_list)
    for value, args in zip(values, call_args_list):
        assert args == ((value,), {})
