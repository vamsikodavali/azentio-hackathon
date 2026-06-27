import torch

from datasets import load_dataset

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
)

from peft import (
    LoraConfig,
    get_peft_model,
)

from trl import SFTTrainer

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"


tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

tokenizer.pad_token = tokenizer.eos_token


model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
)



lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=[
        "q_proj",
        "k_proj",
        "v_proj",
        "o_proj",
    ],
)


# dataset = load_dataset(
#     "json",
#     data_files="train.jsonl",
# )["train"]


dataset = load_dataset(
    "json",
    data_files={
        "train": "consolidated_train.jsonl",
        "validation": "consolidated_val.jsonl",
    },
)

train_dataset = dataset["train"]
valid_dataset = dataset["validation"]


def formatting_func(example):
    return tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False,
        add_generation_prompt=False,
    )



training_args = TrainingArguments(
    output_dir="output",
    num_train_epochs=3,
    per_device_train_batch_size=1,
    per_device_eval_batch_size=1,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_strategy="steps",
    logging_steps=10,
    learning_rate=2e-4,
    report_to="none",
)



trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    eval_dataset=valid_dataset,
    args=training_args,
    peft_config=lora_config,
    formatting_func=formatting_func,
)

trainer.train()
trainer.save_model("azentio-ckpt")
tokenizer.save_pretrained("azentio-ckpt")