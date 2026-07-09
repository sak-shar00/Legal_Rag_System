import numpy as np


def normalize_scores(scores):
    """
    Min-Max Normalize scores between 0 and 1
    """

    scores = np.array(scores, dtype=float)

    if len(scores) == 0:
        return scores

    min_score = scores.min()
    max_score = scores.max()

    if max_score == min_score:
        return np.ones(len(scores))

    return (scores - min_score) / (max_score - min_score)


def hybrid_score(vector_score, bm25_score,
                 vector_weight,
                 bm25_weight):
    """
    Final Hybrid Score
    """

    return (
        vector_weight * vector_score
        +
        bm25_weight * bm25_score
    )


def sort_results(results):
    """
    Sort by Hybrid Score
    """

    return sorted(
        results,
        key=lambda x: x["hybrid_score"],
        reverse=True
    )


def remove_duplicates(results):
    """
    Remove duplicate chunks
    """

    seen = set()

    final = []

    for item in results:

        if item["chunk_id"] not in seen:

            seen.add(item["chunk_id"])

            final.append(item)

    return final