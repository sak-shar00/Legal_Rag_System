"""
evaluate_full.py

Milestone 4 - Complete Evaluation: Retrieval Accuracy + Faithfulness

STRATEGY TO AVOID RATE LIMITS:
Your main /ask API uses llama-3.3-70b-versatile (its own daily token quota).
This script's Faithfulness JUDGE uses a DIFFERENT model (llama-3.1-8b-instant),
which has a SEPARATE quota on Groq. This lets both metrics run today without
competing for the same token budget.

RESUMABLE: If you hit a rate limit on either model, just re-run this script -
it picks up where it left off (tracked per-query in the output file).
"""

import pandas as pd
import requests
import time
import re
import os
from dotenv import load_dotenv
from groq import Groq

# ==============================
# CONFIG
# ==============================

API_URL = "http://127.0.0.1:8000/ask"
INPUT_FILE = "golden_set_FINAL_CLEAN.xlsx"
OUTPUT_FILE = "evaluation_results_full.xlsx"

load_dotenv()
judge_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
JUDGE_MODEL = "llama-3.1-8b-instant"  # different model = separate quota from main 70B system

# ==============================
# READ GOLDEN SET
# ==============================

df = pd.read_excel(INPUT_FILE)
print("Columns Found:", df.columns.tolist())

if os.path.exists(OUTPUT_FILE):
    existing_df = pd.read_excel(OUTPUT_FILE)
    done_queries = set(existing_df[existing_df["Status"] == "Success"]["Query"].tolist())
    print(f"Resuming: {len(done_queries)} queries already done.")
    results = existing_df.to_dict("records")
else:
    done_queries = set()
    results = []

total = len(df)
remaining = df[~df["Query"].astype(str).str.strip().isin(done_queries)]
print(f"{len(remaining)} queries left.\n")


# ==============================
# RETRIEVAL MATCH CHECK
# ==============================

def check_retrieval_match(expected_doc, model_answer_text, all_sources):
    if not expected_doc or len(expected_doc.strip()) < 8 or expected_doc.strip().lower() == "nan":
        return "INVALID"
    expected_clean = expected_doc.strip().lower()

    m = re.search(r'Primary Citation\s*\n*\(Document:\s*([^,]+),', model_answer_text)
    if m and expected_clean in m.group(1).strip().lower():
        return "PRIMARY_MATCH"
    if expected_clean in model_answer_text.lower():
        return "SECONDARY_MATCH"
    for s in all_sources:
        doc_name = str(s.get("document", s.get("filename", ""))).strip().lower()
        if expected_clean in doc_name:
            return "RETRIEVED_ONLY"
    return "NOT_FOUND"


# ==============================
# FAITHFULNESS CHECK (uses the SEPARATE judge model)
# ==============================

def check_faithfulness(question, ground_truth, system_answer):
    if not ground_truth or not system_answer or ground_truth.strip().lower() == "nan":
        return "SKIPPED", "Missing ground truth or system answer"

    prompt = f"""You are an evaluation judge. Compare a SYSTEM ANSWER against a GROUND TRUTH
answer for the same legal question. Judge only on factual accuracy and whether the
system answer contradicts or fabricates information not supported by the ground truth.

QUESTION: {question}

GROUND TRUTH ANSWER: {ground_truth}

SYSTEM ANSWER: {system_answer}

Respond with EXACTLY one word on the first line: FAITHFUL, PARTIALLY_FAITHFUL, or UNFAITHFUL.
Then on the next line, give a one-sentence reason.
"""
    try:
        response = judge_client.chat.completions.create(
            model=JUDGE_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        text = response.choices[0].message.content.strip()
        lines = text.split("\n")
        verdict = lines[0].strip().upper()
        reason = lines[1].strip() if len(lines) > 1 else ""
        return verdict, reason
    except Exception as e:
        return "JUDGE_ERROR", str(e)


# ==============================
# MAIN LOOP
# ==============================

for idx, row in remaining.iterrows():
    query = str(row["Query"]).strip()
    ground_truth = str(row["Ground Truth Answer"])
    expected_source = str(row["Best Source Document"]).strip()
    confidence = str(row["Confidence"])

    position = list(df["Query"]).index(row["Query"]) + 1
    print(f"[{position}/{total}] {query}")

    predicted_source = ""
    model_answer = ""
    status = "Success"
    sources = []

    try:
        response = requests.post(API_URL, json={"question": query}, timeout=120)
        data = response.json()

        if data.get("success"):
            model_answer = data.get("answer", "")
            sources = data.get("sources", [])
            if sources:
                predicted_source = sources[0].get("document", "")
        else:
            status = "API Returned Failure"
            model_answer = data.get("answer", "")

    except Exception as e:
        status = "Exception"
        model_answer = str(e)
        if "429" in str(e) or "rate limit" in str(e).lower():
            print("\n⚠️  Main API rate limit hit. Saving progress and stopping.")
            break

    retrieval_verdict = check_retrieval_match(expected_source, model_answer, sources)
    retrieval_match = retrieval_verdict in ("PRIMARY_MATCH", "SECONDARY_MATCH")

    # Only run faithfulness check if we got a real answer
    if status == "Success":
        faithfulness_verdict, faithfulness_reason = check_faithfulness(query, ground_truth, model_answer)
        if faithfulness_verdict == "JUDGE_ERROR" and ("429" in faithfulness_reason or "rate limit" in faithfulness_reason.lower()):
            print("\n⚠️  Judge model rate limit hit. Saving progress and stopping.")
            faithfulness_verdict, faithfulness_reason = "NOT_JUDGED_YET", "Judge rate limited - will retry on next run"
            results.append({
                "Query": query, "Ground Truth Answer": ground_truth, "Expected Source": expected_source,
                "Predicted Source": predicted_source, "Confidence": confidence,
                "Retrieval Match": "YES" if retrieval_match else "NO", "Match Detail": retrieval_verdict,
                "Faithfulness": faithfulness_verdict, "Faithfulness Reason": faithfulness_reason,
                "Status": status, "Model Answer": model_answer
            })
            pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
            break
    else:
        faithfulness_verdict, faithfulness_reason = "SKIPPED", "API call failed"

    results.append({
        "Query": query,
        "Ground Truth Answer": ground_truth,
        "Expected Source": expected_source,
        "Predicted Source": predicted_source,
        "Confidence": confidence,
        "Retrieval Match": "YES" if retrieval_match else "NO",
        "Match Detail": retrieval_verdict,
        "Faithfulness": faithfulness_verdict,
        "Faithfulness Reason": faithfulness_reason,
        "Status": status,
        "Model Answer": model_answer
    })

    pd.DataFrame(results).to_excel(OUTPUT_FILE, index=False)
    time.sleep(1)

# ==============================
# SUMMARY
# ==============================

result_df = pd.DataFrame(results)
evaluated = result_df[result_df["Status"] == "Success"]

primary = (evaluated["Match Detail"] == "PRIMARY_MATCH").sum()
secondary = (evaluated["Match Detail"] == "SECONDARY_MATCH").sum()
invalid = (evaluated["Match Detail"] == "INVALID").sum()
valid_total = len(evaluated) - invalid
retrieval_accuracy = ((primary + secondary) / valid_total * 100) if valid_total else 0

faith_counts = evaluated["Faithfulness"].value_counts()
faith_total = faith_counts.get("FAITHFUL", 0) + faith_counts.get("PARTIALLY_FAITHFUL", 0) + faith_counts.get("UNFAITHFUL", 0)
faithful_pct = (faith_counts.get("FAITHFUL", 0) / faith_total * 100) if faith_total else 0

print("\n" + "=" * 60)
print("EVALUATION PROGRESS")
print("=" * 60)
print(f"Evaluated so far: {len(evaluated)}/{total}")
print(f"\nRETRIEVAL ACCURACY: {retrieval_accuracy:.1f}%  ({primary + secondary}/{valid_total} valid queries)")
print(f"\nFAITHFULNESS (of {faith_total} judged):")
print(f"  Faithful:            {faith_counts.get('FAITHFUL', 0)}")
print(f"  Partially Faithful:  {faith_counts.get('PARTIALLY_FAITHFUL', 0)}")
print(f"  Unfaithful:          {faith_counts.get('UNFAITHFUL', 0)}")
print(f"  Faithful Rate: {faithful_pct:.1f}%")
print(f"\nSaved to {OUTPUT_FILE}")
if len(evaluated) < total:
    print("\n👉 Re-run this script to continue.")