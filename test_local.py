import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# Path to your LoRA adapter
LORA_PATH = "./nordic-bank-model"
BASE_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Check files exist
print(f"Current directory: {os.getcwd()}")
print(f"Path: {LORA_PATH}")
print(f"Exists: {os.path.exists(LORA_PATH)}")

if os.path.exists(LORA_PATH):
    print("Files:", os.listdir(LORA_PATH))
else:
    print("❌ Folder not found!")
    exit()

# Load
print("\nLoading base model... (this takes 1-2 minutes)")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
tokenizer.pad_token = tokenizer.eos_token

base = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float32,
    device_map="cpu"
)

print("Loading LoRA adapter...")
model = PeftModel.from_pretrained(base, LORA_PATH)
model.eval()
print("✅ Model loaded!")

# Test
print("\n" + "="*50)
print("TESTING...")
print("="*50)

prompt = """<|system|>
You are a banking assistant for NordicPay.</s>
<|user|>
Context: NordicPay Plus costs €4.90 per month with unlimited ATM withdrawals.

Question: What is the monthly fee for Plus?</s>
<|assistant|>
"""

inputs = tokenizer(prompt, return_tensors="pt")
input_len = inputs["input_ids"].shape[1]

print("Generating response...")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=100,
        temperature=0.7,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

response = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True)
print(f"\n✅ Question: What is the monthly fee for Plus?")
print(f"✅ Response: {response}")