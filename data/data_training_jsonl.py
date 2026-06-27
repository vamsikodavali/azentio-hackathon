import json
from sklearn.model_selection import train_test_split


SYSTEM_PROMPT = """
You are an expert financial analyst.

Your task is to analyze the customer's financial profile and answer the user's request.

Always perform a complete financial analysis before producing the final answer.

The financial analysis should consider:
Step 1: Understand the customer's loan profile
Step 2: Calculate financial metrics
Step 3: Interpret each metric
Step 4: Find the Positive observations
Step 5: Find the Risk observations
Step 6: Then get the overall conclusion of the financial assessment as per the user query

Return the response as a JSON object with the following structure:

{
    "reasoning": {...},
    "answer": {...}
}
""".strip()


with open("all_data.json", "r") as f:
    dataset = json.load(f)
    loan_summary = []
    risk_assessment = []
    recommendation = []
    for ind, data in enumerate(dataset):
        if ind%3==0:
            loan_summary.append(data)
        elif ind%3==1:
            risk_assessment.append(data)
        else:
            recommendation.append(data)


datasets = [loan_summary, risk_assessment, recommendation]
for dataset_type, ds in zip( ["loan_summary", "risk_assessment", "recommendation"], datasets):
    train_val, test = train_test_split(ds, test_size=0.10, random_state=42)
    train, val = train_test_split(train_val, test_size=0.1111, random_state=42)


    for split, data in zip(["train", "val", "test"], [train, val, test]):

        with open(f"{dataset_type}_{split}.jsonl", "w") as f:

            for sample in data:

                user_message = (
                    f"{SYSTEM_PROMPT}\n\n"
                    f"Customer Profile:\n"
                    f"{json.dumps(sample['input'], indent=4)}\n\n"
                    f"User Query:\n"
                    f"{sample['instruction']}"
                )

                assistant_message = json.dumps(
                    sample["output"],
                    indent=4
                )

                chat = {
                    "messages": [
                        {
                            "role": "user",
                            "content": user_message
                        },
                        {
                            "role": "assistant",
                            "content": assistant_message
                        }
                    ]
                }

                f.write(json.dumps(chat) + "\n")

print("Finished!")