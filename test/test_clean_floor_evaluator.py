from vacuum_world import CleanFloorEvaluator


def test_score_0_with_no_updates():
    evaluator = CleanFloorEvaluator()
    assert evaluator.score == 0


def test_score_0_with_no_clean_square():
    state = {
        "agent_location": 'A',
        "dirt_status": {'A': True, 'B': True}
    }
    evaluator = CleanFloorEvaluator()
    evaluator.update(state)
    assert evaluator.score == 0


def test_score_1_with_one_clean_square():
    state = {
        "agent_location": 'A',
        "dirt_status": {'A': False, 'B': True}
    }
    evaluator = CleanFloorEvaluator()
    evaluator.update(state)
    assert evaluator.score == 1


def test_score_2_with_two_clean_squares():
    state = {
        "agent_location": 'A',
        "dirt_status": {'A': False, 'B': False}
    }
    evaluator = CleanFloorEvaluator()
    evaluator.update(state)
    assert evaluator.score == 2


def test_score_2_with_one_clean_square_twice():
    state = {
        "agent_location": 'A',
        "dirt_status": {'A': True, 'B': False}
    }
    evaluator = CleanFloorEvaluator()
    evaluator.update(state)
    evaluator.update(state)
    assert evaluator.score == 2
