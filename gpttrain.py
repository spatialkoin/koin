import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer, AdamW, get_linear_schedule_with_warmup
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, texts, tokenizer, max_length):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoding = self.tokenizer(
            self.texts[idx],
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        return {
            "input_ids": encoding.input_ids.view(-1),
            "attention_mask": encoding.attention_mask.view(-1)
        }

training_texts = [
    "Karlen Works at USC in radiology department with information management.",
    "The sun is shining in the sky.",
    "The cat is sleeping on the couch.",
    "A bicycle race is taking place in the city.",
    "The book on the shelf is about history.",
    "Children are playing in the park.",
    "Raindrops are falling on the roof.",
    "The chef is preparing a delicious meal.",
    "People are enjoying a concert in the park.",
    "The river flows calmly through the valley.",
    "Stars are twinkling in the night sky."
]

tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
tokenizer.add_special_tokens({'pad_token': '<|endoftext|>'}) 
model = GPT2LMHeadModel.from_pretrained("gpt2")

train_dataset = CustomDataset(training_texts, tokenizer, max_length=256)

optimizer = AdamW(model.parameters(), lr=1e-4)
scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=100, num_training_steps=len(train_dataset))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.train()

num_epochs = 3
for epoch in range(num_epochs):
    for batch in DataLoader(train_dataset, batch_size=8, shuffle=True):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = input_ids.clone()  # Shift input_ids to create labels

        inputs = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }

        optimizer.zero_grad()
        outputs = model(**inputs)
        loss = outputs.loss
        loss.backward()
        optimizer.step()
        scheduler.step()

# Save the model and tokenizer
output_dir = "custom_gpt_model"
model.save_pretrained(output_dir)
tokenizer.save_pretrained(output_dir)
