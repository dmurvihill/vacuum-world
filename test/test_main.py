import sys
from unittest.mock import Mock, PropertyMock

import pytest

import vacuum_world
from vacuum_world import MSG_AGENT_DECISION, MSG_COMPLETE, MSG_HELLO, MSG_SCORE

DEFAULT_ARGS = ['vacuum_world.py']


@pytest.fixture
def default_args(monkeypatch):
    monkeypatch.setattr('sys.argv', DEFAULT_ARGS)


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


def test_run_experiment_handles_agent_exceptions(logger):
    agent = Mock()
    agent.decide.side_effect = Exception

    with pytest.raises(vacuum_world.AgentError):
        vacuum_world.run_experiment(Mock(), agent, Mock())


def test_run_experiment_handles_bad_inputs_to_environment(logger):
    environment = Mock()
    environment.update.side_effect = ValueError

    with pytest.raises(vacuum_world.AgentError):
        vacuum_world.run_experiment(environment, Mock(), Mock())


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
    log_lines = [MSG_AGENT_DECISION.format(t, repr(decisions[t - 1]))
                 for t in range(1, 1001)]
    agent.decide.side_effect = decisions

    vacuum_world.run_experiment(Mock(), agent, Mock())
    _assert_call_args(log_lines, logger.info.call_args_list)


def test_main_log_level(logger, default_args):
    vacuum_world.main()
    assert logger.setLevel.call_count == 2
    assert logger.setLevel.call_args[0][0] == vacuum_world.LOG_LEVEL


def test_main_prints_welcome_header(logger, default_args):
    vacuum_world.main()
    messages = [call[0][0] for call in logger.info.call_args_list]
    assert MSG_HELLO in messages


def test_main_runs_experiment(monkeypatch, default_args):
    run_experiment = Mock()
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
    vacuum_world.main()
    assert run_experiment.call_count == 1


def test_main_sets_handler(monkeypatch, default_args):
    run_experiment = Mock()
    stream_handler_class = Mock()
    logger = Mock()
    monkeypatch.setattr('logging.getLogger', lambda: logger)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
    monkeypatch.setattr('logging.StreamHandler', stream_handler_class)

    vacuum_world.main()

    messages = [args[0][0] for args in logger.info.call_args_list]
    assert stream_handler_class.call_args[1]["stream"] == sys.stdout
    assert vacuum_world.MSG_HELLO in messages


def test_main_reports_score(monkeypatch, logger, default_args):
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


def test_main_with_bad_dirt_status_fails(monkeypatch, logger):
    run_experiment = Mock()
    argv = ['vacuum_world.py', '--dirt-status', 't', 'foo']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    with pytest.raises(SystemExit):
        vacuum_world.main()

    assert not run_experiment.called


def test_main_with_incomplete_dirt_status_fails(monkeypatch, logger):
    run_experiment = Mock()
    argv = ['vacuum_world.py', '--dirt-status', 't']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    with pytest.raises(SystemExit):
        vacuum_world.main()

    assert not run_experiment.called


def test_main_sets_dirt(monkeypatch, logger):
    dirt_args_list = [('f', 'f'),
                      ('t', 'f'),
                      ('f', 't')] + list(
        zip(vacuum_world.DIRTY_VALUES,
            vacuum_world.CLEAN_VALUES))
    dirt_status_list = [{'A': False, 'B': False},
                        {'A': True, 'B': False},
                        {'A': False, 'B': True}] + \
                       [{'A': True, 'B': False}] * len(
                           vacuum_world.DIRTY_VALUES)

    for dirt_args, dirt_status in zip(dirt_args_list, dirt_status_list):
        environment = Mock()
        evaluator = Mock()
        environment.locations = ['A', 'B']
        argv = ['vacuum_world.py', '--dirt-status'] + list(dirt_args)
        monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
        monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
        monkeypatch.setattr('sys.argv', argv)

        vacuum_world.main()

        assert environment.call_args[0][1] == dirt_status


def test_main_has_default_dirt_status(monkeypatch, logger):
    environment = Mock()
    evaluator = Mock()
    environment.locations = ['A', 'B']

    monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
    monkeypatch.setattr('sys.argv', ['vacuum_world.py'])

    vacuum_world.main()

    assert environment.call_args[0][1] == {'A': True, 'B': True}


def test_main_sets_agent_location(monkeypatch, logger):
    locations = ['A', 'B']
    environment = Mock()
    evaluator = Mock()
    environment.locations = locations

    for location in locations:
        argv = ['vacuum_world.py', '--agent-location', location]

        monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
        monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
        monkeypatch.setattr('sys.argv', argv)

        vacuum_world.main()
        assert environment.call_args[0][0] == location


def test_main_catches_invalid_agent_location(monkeypatch, logger):
    locations = ['A', 'B']
    environment = Mock()
    evaluator = Mock()
    environment.locations = locations

    argv = ['vacuum_world.py', '--agent-location', 'C']

    monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
    monkeypatch.setattr('sys.argv', argv)

    with pytest.raises(SystemExit):
        vacuum_world.main()


def test_main_loads_agent(monkeypatch, logger):
    module_names = ['my_package', 'foo.bar']
    for module_name in module_names:
        module = Mock()
        my_agent_class = Mock()
        run_experiment = Mock()
        module.getattr.return_value = my_agent_class
        argv = ['vacuum_world.py', '--agent', '{}.MyAgent'.format(module_name)]
        monkeypatch.setattr('sys.argv', argv)
        monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
        sys.modules[module_name] = module

        try:
            vacuum_world.main()

            assert module.getattr.call_args == (('MyAgent',), {})
            assert run_experiment.call_args[0][1] == \
                   my_agent_class.return_value
        finally:
            del sys.modules[module_name]


def test_load_nonexistent_agent(monkeypatch, logger):
    my_package = Mock()
    run_experiment = Mock()
    my_package.getattr.side_effect = AttributeError
    argv = ['vacuum_world.py', '--agent', 'my_package.FooBar']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
    sys.modules['my_package'] = my_package

    try:
        vacuum_world.main()

        error_message = vacuum_world.MSG_AGENT_NOT_FOUND.format("my_package.FooBar")
        messages = [call[0][0] for call in logger.error.call_args_list]
        assert not run_experiment.called
        assert error_message in messages
    finally:
        del sys.modules['my_package']


def test_load_nonexistent_agent_from_same_module(monkeypatch, logger):
    run_experiment = Mock()
    argv = ['vacuum_world.py', '--agent', 'FooBar']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    vacuum_world.main()

    error_message = vacuum_world.MSG_AGENT_NOT_FOUND.format("FooBar")
    messages = [call[0][0] for call in logger.error.call_args_list]
    assert not run_experiment.called
    assert error_message in messages


def test_load_nonexistent_agent_module(monkeypatch, logger):
    run_experiment = Mock()
    argv = ['vacuum_world.py', '--agent', 'foo.bar.FooBar']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    vacuum_world.main()

    error_message = vacuum_world.MSG_MODULE_NOT_LOADED.format("foo")
    messages = [call[0][0] for call in logger.error.call_args_list]
    assert not run_experiment.called
    assert error_message in messages


def test_main_catches_experiment_exceptions(monkeypatch, default_args, logger):
    error = ValueError('blah')
    run_experiment = Mock()
    run_experiment.side_effect = vacuum_world.AgentError(error)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    vacuum_world.main()

    error_message = vacuum_world.MSG_AGENT_ERROR.format(repr(error))
    messages = [call[0][0] for call in logger.error.call_args_list]
    assert error_message in messages


def _assert_call_args(values, call_args_list):
    """
    Assert that each value is the sole argument to its counterpart in
    the call args list
    """
    assert len(values) == len(call_args_list)
    for value, args in zip(values, call_args_list):
        assert args == ((value,), {})
