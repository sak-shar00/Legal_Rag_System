# TODO - Improve Retrieval Accuracy (Milestone 4)

- [x] Step 1: Update `python/llm_answer.py` hybrid_retrieve() to keep **best chunk per document (filename)** before returning chunks.

- [x] Step 2: Re-run evaluation via `python python/evaluation/evaluate.py` and record Retrieval Accuracy.

- [ ] Step 3: If needed, apply scoring/ranking tuning (normalization change or rank-based merging) in retrieval.
- [ ] Step 4 (optional): Update `python/evaluation/evaluate.py` to also compute Top-3 retrieval accuracy.
- [ ] Step 5: Iterate until Retrieval Accuracy is in the 80-90% target range.
