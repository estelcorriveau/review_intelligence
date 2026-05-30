import anthropic 
client = anthropic.Anthropic()
message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "Say hello and tell me one fun fact about books in two sentences."}
    ],
)
print(message.content[0].text)