from unittest.mock import Mock, PropertyMock

import vacuum_world
from vacuum_world import MSG_AGENT_DECISION


def test_run_experiment_loops_1000_times(monkeypatch):
    agent = Mock()
    environment = Mock()
    evaluator = Mock()
    logger = Mock()
    monkeypatch.setattr('logging.getLogger', lambda _: logger)

    vacuum_world.run_experiment(environment, agent, evaluator)

    assert agent.decide.call_count == 1000
    assert environment.update.call_count == 1000
    assert evaluator.update.call_count == 1000
    assert logger.info.call_count == 1000


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


def test_logger_name(monkeypatch):
    logger = Mock()

    def get_logger(name):
        assert name == vacuum_world.LOGGER_NAME
        return logger

    monkeypatch.setattr('logging.getLogger', get_logger)
    vacuum_world.run_experiment(Mock(), Mock(), Mock())
    assert logger.info.call_count == 1000


def test_log_level(monkeypatch):
    logger = Mock()
    monkeypatch.setattr('logging.getLogger', lambda _: logger)

    vacuum_world.run_experiment(Mock(), Mock(), Mock())
    assert logger.setLevel.call_count == 1
    assert logger.setLevel.call_args == ((vacuum_world.LOG_LEVEL,), {})


def test_agent_decisions_logged(monkeypatch):
    agent = Mock()
    logger = Mock()
    decisions = [Mock() for _ in range(1000)]
    log_lines = [MSG_AGENT_DECISION.format(repr(d)) for d in decisions]
    agent.decide.side_effect = decisions
    monkeypatch.setattr('logging.getLogger', lambda _: logger)

    vacuum_world.run_experiment(Mock(), agent, Mock())
    _assert_call_args(log_lines, logger.info.call_args_list)


def test_experiment_logs_to_handler():
    handler = Mock()
    handler.level = vacuum_world.LOG_LEVEL
    vacuum_world.run_experiment(Mock(), Mock(), Mock(), handler=handler)
    assert handler.handle.call_count == 1000


def _assert_call_args(values, call_args_list):
    """
    Assert that each value is the sole argument to its counterpart in
    the call args list
    """
    assert len(values) == len(call_args_list)
    for value, args in zip(values, call_args_list):
        assert args == ((value,), {})
