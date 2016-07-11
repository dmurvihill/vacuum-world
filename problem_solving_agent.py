class ClassicalProblemSolvingAgent(object):

    def __init__(self, solver, completion_decision, failure_decision):
        self._solver = solver
        self._path = None
        self._completion_decision = completion_decision
        self._failure_decision = failure_decision

    def decide(self, percept):
        if self._path is None:
            path = self._solver()
            if path is None:
                return self._failure_decision
            else:
                self._path = iter(path)

        try:
            decision = next(self._path)
        except StopIteration:
            decision = self._completion_decision

        return decision
