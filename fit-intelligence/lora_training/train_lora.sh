#!/bin/bash
# LoRA Fine-tuning Script for FIT Intelligence

# Install requirements
pip install unsloth torch transformers datasets

# Run training
python -c "
from unsloth import FastLanguageModel
import torch
from transformers import TrainingArguments
from trl import SFTTrainer
from datasets import load_dataset

# Load base model
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name='unsloth/llama-3-8b-bnb-4bit',
    max_seq_length=2048,
    dtype=None,
    load_in_4bit=True,
)

# Add LoRA adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj'],
    lora_alpha=16,
    lora_dropout=0,
    bias='none',
    use_gradient_checkpointing=True,
    random_state=3407,
)

# Load dataset
dataset = load_dataset('json', data_files='fit_queries.jsonl')

# Training arguments
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=5,
    max_steps=100,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1,
    optim='adamw_8bit',
    output_dir='./fit_lora_model',
)

# Trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset['train'],
    dataset_text_field='input',
    max_seq_length=512,
    args=training_args,
)

# Train
trainer.train()

# Save
model.save_pretrained('fit_intelligence_lora')
print('Training complete! Model saved to fit_intelligence_lora')
"

echo "Training complete! Now create Ollama model:"
echo "ollama create fit-intelligence -f Modelfile"
