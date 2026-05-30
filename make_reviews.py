import anthropic 
import json
client = anthropic.Anthropic()
prompt="""Generate 20 realistic reader reviews for a fictional literary novel called "The Salt House" —
a family drama about three sisters reuniting at their late mother's coastal home.

Make them varied and realistic — some glowing, some mixed, some negative. Vary the length, writing style, and what each reviewer cares about.
(Plot, character, pacing, writing style, the ending, emotional impact).

Focus on a JSON array of objects, each with two fields: 
- an "id" : a number from 1 to 20
- "text" : the review text

Return nothing but the JSON array. No preamble, no explanation."""

message = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=4000,
    messages=[
        {"role": "user", "content": prompt}
    ],
)
reviews_text=message.content[0].text
#Clean Up: strip markdown code fences if the model added them
reviews_text=reviews_text.strip()
if reviews_text.startswith("```"):
    reviews_text=reviews_text.split("\n",1)[1] #drop the first line (``` json)
    reviews_text=reviews_text.rsplit("```",1)[0] #drop the closing ```
reviews_text=reviews_text.strip()

with open("reviews.json", "w") as f:
    f.write(reviews_text)
print("Done! Here's what was generated:\n")
print(reviews_text)

