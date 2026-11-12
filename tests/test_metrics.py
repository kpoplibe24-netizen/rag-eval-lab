from metrics import first_correct_rank, hit_at_k, mrr


def fake_results():
    return [
        {"file": "a.md", "heading": "A"},
        {"file": "b.md", "heading": "B"},
        {"file": "c.md", "heading": "C"},
    ]


def test_rank_found():
    assert first_correct_rank(fake_results(), "b.md", "B") == 2


def test_rank_missing():
    assert first_correct_rank(fake_results(), "z.md", "Z") is None


def test_hit_at_k():
    ranks = [1, 3, None, 2]

    assert hit_at_k(ranks, 1) == 0.25
    assert hit_at_k(ranks, 3) == 0.75


def test_mrr():
    ranks = [1, 2, None]

    assert abs(mrr(ranks) - 0.5) < 1e-9