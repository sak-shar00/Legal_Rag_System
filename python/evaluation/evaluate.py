import pandas as pd
import requests
import time

# ==============================
# CONFIG
# ==============================

API_URL = "http://127.0.0.1:8000/ask"

INPUT_FILE = "golden_set_reviewed.xlsx"
OUTPUT_FILE = "evaluation_results.xlsx"

# ==============================
# READ GOLDEN SET
# ==============================

df = pd.read_excel(INPUT_FILE)

print("\nColumns Found:")
print(df.columns.tolist())

results = []

correct = 0
total = len(df)

print(f"\nEvaluating {total} queries...\n")

# ==============================
# LOOP
# ==============================

for idx, row in df.iterrows():

    query = str(row["Query"]).strip()
    expected_answer = str(row["Ground Truth Answer"])
    expected_source = str(row["Best Source Document"]).strip()
    expected_page = str(row["Page Number"])
    confidence = str(row["Confidence"])

    print(f"[{idx+1}/{total}] {query}")

    predicted_source = ""
    predicted_page = ""
    model_answer = ""
    status = "Success"

    try:

        response = requests.post(
            API_URL,
            json={"question": query},
            timeout=120
        )

        data = response.json()

        if data.get("success"):

            model_answer = data.get("answer", "")

            sources = data.get("sources", [])

            if len(sources) > 0:

                predicted_source = sources[0].get("document", "")

                predicted_page = (
                    f"{sources[0].get('page_start','')}-"
                    f"{sources[0].get('page_end','')}"
                )

        else:

            status = "API Returned Failure"

            model_answer = data.get("answer", "")

    except Exception as e:

        status = "Exception"

        model_answer = str(e)

    retrieval_match = (
        predicted_source.lower().strip()
        ==
        expected_source.lower().strip()
    )

    if retrieval_match:
        correct += 1

    results.append({

        "Query": query,

        "Ground Truth Answer": expected_answer,

        "Expected Source": expected_source,

        "Predicted Source": predicted_source,

        "Expected Page": expected_page,

        "Predicted Page": predicted_page,

        "Confidence": confidence,

        "Retrieval Match": "YES" if retrieval_match else "NO",

        "Status": status,

        "Model Answer": model_answer

    })

    time.sleep(1)

# ==============================
# SAVE
# ==============================

result_df = pd.DataFrame(results)

result_df.to_excel(OUTPUT_FILE, index=False)

accuracy = (correct / total) * 100

print("\n========================================")
print("Evaluation Completed")
print("========================================")
print(f"Total Queries      : {total}")
print(f"Correct Retrievals : {correct}")
print(f"Retrieval Accuracy : {accuracy:.2f}%")
print(f"\nResults saved as {OUTPUT_FILE}")