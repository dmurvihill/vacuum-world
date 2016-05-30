import sys
from unittest.mock import Mock, PropertyMock

import pytest

import vacuum_world
from vacuum_world import MSG_AGENT_DECISION, MSG_COMPLETE, MSG_HELLO, MSG_SCORE

get_logger = None


@pytest.fixture
def default_args(monkeypatch):
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', Mock())
    monkeypatch.setattr('vacuum_world.run_experiment', Mock())
    monkeypatch.setattr('sys.argv', ['vacuum_world.py'])


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

    with pytest.raises(vacuum_world.ExperimentError) as e:
        vacuum_world.run_experiment(Mock(), agent, Mock())
        assert e.component == 'agent'


def test_run_experiment_handles_bad_inputs_to_environment(logger):
    environment = Mock()
    environment.update.side_effect = ValueError

    with pytest.raises(vacuum_world.ExperimentError) as e:
        vacuum_world.run_experiment(environment, Mock(), Mock())
        assert e.component == 'agent'


def test_run_experiment_handles_environment_exceptions(logger):
    environment = Mock()
    environment.update.side_effect = Exception

    with pytest.raises(vacuum_world.ExperimentError) as e:
        vacuum_world.run_experiment(environment, Mock(), Mock())
        assert e.component == 'environment'


def test_run_experiment_handles_bad_inputs_to_agent(logger):
    agent = Mock()
    agent.decide.side_effect = ValueError

    with pytest.raises(vacuum_world.ExperimentError) as e:
        vacuum_world.run_experiment(Mock(), agent, Mock())
        assert e.component == 'environment'


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
    assert logger.setLevel.call_count == 1
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


def test_main_passes_env_prefixes_to_environment_init(monkeypatch):
    args_list = [['a', 'b'],
                 ['a'],
                 []]
    parameter_names = ['name1', 'name2']

    for parameter_name in parameter_names:
        for args in args_list:
            environment = Mock()
            evaluator = Mock()
            full_param_option = "--env-{}".format(parameter_name)
            argv = ['vacuum_world.py', full_param_option] + list(args)
            monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
            monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
            monkeypatch.setattr('sys.argv', argv)

            vacuum_world.main()

            assert environment.call_args[1][parameter_name] == args


def test_main_accepts_with_empty_env_args(monkeypatch):
    argv = ['vacuum_world.py', '--env-arg']
    environment = Mock()
    evaluator = Mock()
    monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
    monkeypatch.setattr('sys.argv', argv)

    vacuum_world.main()

    assert environment.call_args[1] == {'arg': []}


def test_main_accepts_with_multiple_env_args(monkeypatch):
    argv = ['vacuum_world.py', '--env-a', 'a-val', '--env-b', 'b-val']
    environment = Mock()
    evaluator = Mock()
    monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
    monkeypatch.setattr('sys.argv', argv)

    vacuum_world.main()

    assert environment.call_args[1] == {'a': ['a-val'], 'b': ['b-val']}


def test_main_rejects_non_env_custom_arg(monkeypatch):
    argv = ['vacuum_world.py', 'foobar']
    environment = Mock()
    evaluator = Mock()
    monkeypatch.setattr('vacuum_world.CleanFloorEvaluator', evaluator)
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
    monkeypatch.setattr('sys.argv', argv)

    with pytest.raises(SystemExit):
        vacuum_world.main()

    assert not environment.called


def test_main_handles_bad_env_args(monkeypatch, logger):
    argv = ['vacuum_world.py', '--env-a', 'a-val']
    environment = Mock()
    run_experiment = Mock()
    environment.side_effect = ValueError(['a-val'])
    monkeypatch.setattr('vacuum_world.BasicVacuumWorld', environment)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
    monkeypatch.setattr('sys.argv', argv)

    vacuum_world.main()

    messages = [call[0][0] for call in logger.error.call_args_list]
    assert vacuum_world.MSG_ENVIRONMENT_INIT_ERROR.format(repr(['a-val'])) in messages
    assert not run_experiment.called


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
            setattr(module, 'MyAgent', my_agent_class)
            vacuum_world.main()

            assert run_experiment.call_args[0][1] == \
                my_agent_class.return_value
        finally:
            del sys.modules[module_name]


def test_main_loads_environment(monkeypatch, logger):
    module_names = ['my_package', 'foo.bar']
    for module_name in module_names:
        module = Mock()
        my_environment_class = Mock()
        run_experiment = Mock()
        module.getattr.return_value = my_environment_class
        argv = ['vacuum_world.py',
                '--environment',
                '{}.MyEnvironment'.format(module_name)]
        monkeypatch.setattr('sys.argv', argv)
        monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
        sys.modules[module_name] = module

        try:
            setattr(module, 'MyEnvironment', my_environment_class)
            vacuum_world.main()

            assert run_experiment.call_args[0][0] == \
                my_environment_class.return_value
        finally:
            del sys.modules[module_name]


def test_load_nonexistent_agent(monkeypatch, logger):
    old_getattr = getattr
    my_package = Mock()

    def raise_attribute_error_on_foobar(*args):
        if args[0] == my_package and args[1] == 'FooBar':
            raise AttributeError()
        else:
            return old_getattr(*args)

    run_experiment = Mock()
    argv = ['vacuum_world.py', '--agent', 'my_package.FooBar']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)
    monkeypatch.setattr('builtins.getattr', raise_attribute_error_on_foobar)
    sys.modules['my_package'] = my_package

    try:
        with pytest.raises(SystemExit):
            vacuum_world.main()

        error_message = vacuum_world.MSG_CLASS_NOT_FOUND.format("agent", "my_package.FooBar")
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

    with pytest.raises(SystemExit):
        vacuum_world.main()

    error_message = vacuum_world.MSG_CLASS_NOT_FOUND.format("agent", "FooBar")
    messages = [call[0][0] for call in logger.error.call_args_list]
    assert not run_experiment.called
    assert error_message in messages


def test_load_nonexistent_agent_module(monkeypatch, logger):
    run_experiment = Mock()
    argv = ['vacuum_world.py', '--agent', 'foo.bar.FooBar']
    monkeypatch.setattr('sys.argv', argv)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    with pytest.raises(SystemExit):
        vacuum_world.main()

    error_message = vacuum_world.MSG_MODULE_NOT_LOADED.format("foo")
    messages = [call[0][0] for call in logger.error.call_args_list]
    assert not run_experiment.called
    assert error_message in messages


def test_main_catches_agent_exceptions(monkeypatch, default_args, logger):
    error = ValueError('blah')
    run_experiment = Mock()
    run_experiment.side_effect = vacuum_world.ExperimentError('agent', error)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    vacuum_world.main()

    error_message = vacuum_world.MSG_EXPERIMENT_ERROR.format('agent',
                                                             repr(error))
    messages = [call[0][0] for call in logger.error.call_args_list]
    assert error_message in messages


def test_main_catches_environment_exceptions(monkeypatch, default_args, logger):
    error = ValueError('blergh')
    run_experiment = Mock()
    run_experiment.side_effect = vacuum_world.ExperimentError('environment',
                                                              error)
    monkeypatch.setattr('vacuum_world.run_experiment', run_experiment)

    vacuum_world.main()

    error_message = vacuum_world.MSG_EXPERIMENT_ERROR.format('environment',
                                                             repr(error))
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
