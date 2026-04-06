import os
import re
import torch
from openai import OpenAI
from app.config import (
    OPENAI_API_KEY, GROK_API_KEY, BASE_MODEL_ID,
    LORA_ADAPTER_PATH, MAX_TOKENS, TEMPERATURE, SYSTEM_PROMPT
)


class ModelManager:
    def __init__(self):
        self.local_model = None
        self.local_tokenizer = None
        self.local_device = None
        self.local_loaded = False

        # API clients
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.groq_client = None
        
        # Try Groq (free API)
        groq_key = os.getenv("GROQ_API_KEY", "")
        if groq_key:
            self.groq_client = OpenAI(
                api_key=groq_key,
                base_url="https://api.groq.com/openai/v1"
            )

    def load_local_model(self):
        if self.local_loaded:
            return

        from transformers import AutoModelForCausalLM, AutoTokenizer
        from peft import PeftModel

        print(f"Loading local model: {BASE_MODEL_ID}...")
        
        self.local_device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.local_device}")
        
        self.local_tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID)
        if self.local_tokenizer.pad_token is None:
            self.local_tokenizer.pad_token = self.local_tokenizer.eos_token

        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_ID,
            torch_dtype=torch.float32,
            device_map="cpu",
            trust_remote_code=True
        )

        adapter_config_path = os.path.join(LORA_ADAPTER_PATH, "adapter_config.json")
        
        if os.path.exists(adapter_config_path):
            print(f"✅ Loading LoRA adapter...")
            self.local_model = PeftModel.from_pretrained(base, LORA_ADAPTER_PATH)
        else:
            self.local_model = base

        self.local_model.eval()
        self.local_loaded = True
        print("✅ Local model ready!")

    def _is_greeting(self, question: str) -> bool:
        """Check if the question is just a greeting"""
        greetings = [
            "hi", "hello", "hey", "hola", "greetings",
            "good morning", "good afternoon", "good evening",
            "howdy", "what's up", "sup", "yo"
        ]
        clean = question.lower().strip().rstrip("!?.،")
        return clean in greetings

    def _handle_greeting(self) -> str:
        """Return a friendly greeting response"""
        return """Hello! 👋 Welcome to NordicPay Banking Assistant.

I'm here to help you with:
- Account information (Basic, Plus, Premium)
- Card services (PIN, freeze, activate)
- Loans and interest rates
- Security and data privacy
- General banking questions

How can I assist you today?"""

    def generate(self, model_id: str, question: str, context: str) -> dict:
        """Generate response with reasoning steps"""
        
        reasoning_steps = []
        
        # Step 1: Analyze question
        reasoning_steps.append({
            "step": 1,
            "action": "Analyzing question",
            "detail": f"Received: '{question}'"
        })
        
        # Step 2: Check if greeting
        if self._is_greeting(question):
            reasoning_steps.append({
                "step": 2,
                "action": "Detected greeting",
                "detail": "Responding with welcome message"
            })
            return {
                "answer": self._handle_greeting(),
                "reasoning": reasoning_steps,
                "used_context": False
            }
        
        # Step 3: Check context relevance
        reasoning_steps.append({
            "step": 2,
            "action": "Retrieving context",
            "detail": f"Found {len(context)} characters of relevant information"
        })
        
        # Step 4: Select model
        reasoning_steps.append({
            "step": 3,
            "action": "Selecting model",
            "detail": f"Using {model_id}"
        })
        
        # Step 5: Generate
        reasoning_steps.append({
            "step": 4,
            "action": "Generating response",
            "detail": "Processing with LLM..."
        })
        
        # Route to correct model
        if model_id == "openai":
            answer = self._generate_openai(question, context)
        elif model_id == "groq":
            answer = self._generate_groq(question, context)
        elif model_id == "local-lora":
            answer = self._generate_local(question, context)
        else:
            raise ValueError(f"Unknown model: {model_id}")
        
        reasoning_steps.append({
            "step": 5,
            "action": "Response complete",
            "detail": f"Generated {len(answer)} characters"
        })
        
        return {
            "answer": answer,
            "reasoning": reasoning_steps,
            "used_context": True
        }

    def _generate_openai(self, question: str, context: str) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI API key not configured")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip()

    def _generate_groq(self, question: str, context: str) -> str:
        if not self.groq_client:
            raise ValueError("Groq API key not configured. Get free key at https://console.groq.com/")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]

        response = self.groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
        return response.choices[0].message.content.strip()

    def _generate_local(self, question: str, context: str) -> str:
        if not self.local_loaded:
            self.load_local_model()

        ctx = context if context else "No relevant information found."
        
        prompt = f"""<|system|>
{SYSTEM_PROMPT}</s>
<|user|>
Context: {ctx}

Question: {question}</s>
<|assistant|>
"""
        
        inputs = self.local_tokenizer(prompt, return_tensors="pt")
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = self.local_model.generate(
                **inputs,
                max_new_tokens=150,
                temperature=max(TEMPERATURE, 0.1),
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.local_tokenizer.eos_token_id
            )

        response = self.local_tokenizer.decode(
            outputs[0][input_len:], 
            skip_special_tokens=True
        )
        
        response = response.strip()

        # Clean up response if it contains multiple sentences or ends with a special token
        if "</s>" in response:
            response = response.split("</s>")[0].strip()
        
        # Stop if model starts generating new questions
        if "\n\nQuestion:" in response:
            response = response.split("\n\nQuestion:")[0].strip()
        
        if "\nQuestion:" in response:
            response = response.split("\nQuestion:")[0].strip()
        
        
        return response