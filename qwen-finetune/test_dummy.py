from transformers import AutoTokenizer
from transformers import AutoModelForCausalLM
from peft import PeftModel
import torch

base = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-0.5B-Instruct",
    torch_dtype=torch.float16,
)

model = PeftModel.from_pretrained(base, "output")

tokenizer = AutoTokenizer.from_pretrained("output")

messages = [
    {"role":"user","content":"Given borrower profile and loan details, generate a natural language loan summary. \n Age: 35 \n Income: ₹60,000 \n Loan Amount: ₹5,00,000 \n Bureau Score: 785 \nCurrent DPD: 0"}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
)

inputs = tokenizer(text, return_tensors="pt")

outputs = model.generate(
    **inputs,
    max_new_tokens=100
)

print(tokenizer.decode(outputs[0]))