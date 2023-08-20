import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load the trained model and tokenizer
model_path = "custom_gpt_model"
tokenizer = GPT2Tokenizer.from_pretrained(model_path)
model = GPT2LMHeadModel.from_pretrained(model_path)

# Set the device for inference
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

print("Bot: Hello! I'm your chatbot. You can start the conversation by typing a message. Type 'exit' to end the conversation.")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Bot: Goodbye!")
        break

    # Encode the user input and generate a response
    input_ids = tokenizer.encode(user_input, return_tensors="pt").to(device)

    # Create an attention mask to avoid attending to padding tokens
    attention_mask = torch.ones(input_ids.shape, device=device)

    with torch.no_grad():
        output = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=100,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            pad_token_id=tokenizer.eos_token_id
        )

    # Decode the generated response
    bot_response = tokenizer.decode(output[0], skip_special_tokens=True)
    print("Bot:", bot_response)
