def first_correct_rank(results, file, heading):
    """Return the 1-based rank of the first correct result, or None."""

    for i, r in enumerate(results, start=1):
        if r["file"] == file and r["heading"] == heading:
            return i

    return None


def hit_at_k(ranks, k):
    """Fraction of questions with the correct result in the top k."""

    if not ranks:
        return 0.0

    return sum(
        1 for r in ranks
        if r is not None and r <= k
    ) / len(ranks)


def mrr(ranks):
    """Calculate Mean Reciprocal Rank."""

    if not ranks:
        return 0.0

    return sum(
        1 / r if r is not None else 0.0
        for r in ranks
    ) / len(ranks)