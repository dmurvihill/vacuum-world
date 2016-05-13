from unittest.mock import Mock, PropertyMock

import pytest

import vacuum_world
from vacuum_world import MSG_AGENT_DECISION, MSG_COMPLETE, MSG_HELLO, MSG_SCORE


@pytest.fixture
def logger(monkeypatch):
    logger = Mock()
    monkeypatch.setattr('logging.getLogger', lambda *_: logger)
    return logger


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


def test_log_level(logger):
    vacuum_world.run_experiment(Mock(), Mock(), Mock())
    assert logger.setLevel.call_count == 1
    assert logger.setLevel.call_args == ((vacuum_world.LOG_LEVEL,), {})


def test_agent_decisions_logged(logger):
    agent = Mock()
    decisions = [Mock() for _ in range(1000)]
    log_lines = [MSG_AGENT_DECISION.format(repr(d)) for d in decisions]
    agent.decide.side_effect = decisions

    vacuum_world.run_experiment(Mock(), agent, Mock())
    _assert_call_args(log_lines, logger.info.call_args_list)


def test_experiment_logs_to_handler():
    handler = Mock()
    handler.level = vacuum_world.LOG_LEVEL
    vacuum_world.run_experiment(Mock(), Mock(), Mock(), handler=handler)
    assert handler.handle.call_count == 1000


def test_main_log_level(logger):
    vacuum_world.main()
    assert logger.setLevel.call_count == 2
    assert logger.setLevel.call_args[0][0] == vacuum_world.LOG_LEVEL


def test_main_prints_welcome_header(logger):
    vacuum_world.main()
    messages = [call[0][0] for call in logger.info.call_args_list]
    assert MSG_HELLO in messages


def test_main_runs_experiment(monkeypatch):
    run_experiment = Mock()
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
    vacuum_world.main()
    assert run_experiment.call_count == 1


def test_main_reports_score(monkeypatch, logger):
    for score in (0, 1, 10):
        evaluator = Mock()
        Mock.score = PropertyMock(return_value=score)
        monkeypatch.setattr('vacuum_world.CleanFloorEvaluator',
                            lambda: evaluator)
        vacuum_world.main()

        score_report = MSG_SCORE.format(score)
        messages = [call[0][0] for call in logger.info.call_args_list]
        assert MSG_COMPLETE in messages
        assert score_report in messages


def _assert_call_args(values, call_args_list):
    """
    Assert that each value is the sole argument to its counterpart in
    the call args list
    """
    assert len(values) == len(call_args_list)
    for value, args in zip(values, call_args_list):
        assert args == ((value,), {})
