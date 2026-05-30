import anthropic
import json

client = anthropic.Anthropic ()

#Load the reviews generated in Step 0

with open("reviews.json", "r") as f:
    reviews = json.load(f)
    
#A FUNCTION: a reusable recipe. We define it once, then call it for each review.

def classify_review(review_text):
    prompt = f"""Analyze this reader review of a novel.

Review: "{review_text}"

Classify it and return ONLY a JSON object (no preamble, no code fences) with these fields:

- "sentiment": one of "positive", "mixed", or "negative"
- "themes" : a list of 1-3 themes the review focuses on, chosen from:
    ["plot", "characters", "pacing", "writing style", "ending", "emotional impact"]

Return nothing but the JSON object."""
        
    message = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=300,
        messages=[{"role": "user","content": prompt}],
        )
    result_text=message.content[0].text.strip()
        
        #Clean fences
    if result_text.startswith("```"):
        result_text=result_text.split("\n",1)[1]
        result_text=result_text.rsplit("```",1)[0]
        result_text=result_text.strip()

        #Turn the JSON text into real Python data we can use

    return json.loads(result_text)

#A LOOP: run the recipe once for every review in the list
results=[]
for review in reviews:
    classification=classify_review(review["text"])
    classification["id"]=review["id"]
    classification["text"]=review["text"]
    results.append(classification)
    print(f"Review #{review['id']}:{classification['sentiment']}|themes: {classification['themes']}")
#Save all classifications to a file for the next steps
with open("classified.json", "w") as f:
    json.dump(results,f,indent=2)
print("\nSaved classifications to classified.json")
