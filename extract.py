import anthropic 
import json

client=anthropic.Anthropic()

#Load the original reviews
with open("reviews.json","r") as f:
    reviews=json.load(f)

#A FUNCTION: extract the specific useful bits from one review 
def extract_from_review(review_text):
    prompt=f"""Extract key information from this reader review of a novel.

Review: "{review_text}"

    Return ONLY a JSON object (no preamble, no code fences) with these fields:
    - "praises": a list of specific things the reviewer praised (empty list if none)
    - "complaints": a list of specific things the reviewer criticized (empty list if none)
    - "pull_quotes": a list of 0-2 short, vivid phrases (verbatim from the review) that would work as marketing quotes

    Return nothing but the JSON object."""

    message=client.messages.create(
            model="claude-opus-4-8",
            max_tokens=500,
            messages=[{"role":"user","content":prompt}],
        )
    result_text=message.content[0].text.strip()
        #Clean fences
    if result_text.startswith("```"):
        result_text=result_text.split("\n",1)[1]
        result_text=result_text.rsplit("```",1)[0]
        result_text=result_text.strip()
    return json.loads(result_text)

#A LOOP: extract from every review and collect results
results=[]
for review in reviews:
    extraction=extract_from_review(review["text"])
    extraction["id"]=review["id"]
    results.append(extraction)
    print(f"Review #{review['id']}:{len(extraction['praises'])} praises, {len(extraction['complaints'])} complaints,{len(extraction['pull_quotes'])} pull-quotes")

#Save for next steps
with open("extracted.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nSaved extractions to extracted.json")


