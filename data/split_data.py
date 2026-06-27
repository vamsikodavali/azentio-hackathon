import os

root_dir = "/Users/vamsi/Workstation/azentio/data"
folders = ["loan_summary", "recommendation", "risk_assessment"]
train_consolidated = []
val_consolidated = []

for folder in folders:
    train_path = os.path.join(root_dir, folder, f"{folder}_train.jsonl")
    val_path = os.path.join(root_dir, folder, f"{folder}_val.jsonl")
    with open(train_path, "r") as f:
        train_consolidated.extend(f.readlines())
    with open(val_path, "r") as f:
        val_consolidated.extend(f.readlines())

with open("consolidated_train.jsonl", "w") as f:
    f.writelines(train_consolidated)
with open("consolidated_val.jsonl", "w") as f:
    f.writelines(val_consolidated)

    
    