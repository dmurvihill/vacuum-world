from unittest.mock import Mock

from problem_solving_agent import ClassicalProblemSolvingAgent


class TestDecide(object):

    def test_makes_completion_decision_for_empty_solution(self):
        solver = Mock(return_value=())
        for completion_decision in {'party', 'celebrate'}:
            agent = ClassicalProblemSolvingAgent(solver, completion_decision,
                                                 'rage')
            assert agent.decide(Mock()) == completion_decision

    def test_makes_failure_decision_for_no_solution(self):
        solver = Mock(return_value=None)
        for failure_decision in {'rage', 'cry'}:
            agent = ClassicalProblemSolvingAgent(solver, 'party',
                                                 failure_decision)
            assert agent.decide(Mock()) == failure_decision

    def test_follows_solution_path(self):
        for solution_path in {('action1', 'action2'), ('action2', 'action1')}:
            solver = Mock(return_value=solution_path)
            agent = ClassicalProblemSolvingAgent(solver, 'party', 'rage')
            assert agent.decide(Mock()) == solution_path[0]
            assert agent.decide(Mock()) == solution_path[1]
            assert agent.decide(Mock()) == 'party'
