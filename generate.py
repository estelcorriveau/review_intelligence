import anthropic
import json

client=anthropic.Anthropic()

#Load the data from earlier steps

with open("extracted.json","r") as f:
    extracted=json.load(f)

with open("brief.txt","r") as f:
    brief=f.read()

#Gather all the pull-quotes the extractor found

all_pull_quotes=[]
for e in extracted:
    for quote in e["pull_quotes"]:
        all_pull_quotes.append(quote)

quotes_blob="\n".join(all_pull_quotes)

#A SINGLE call: generate ready-to-use marketing copy

prompt=f"""You are a book marketing copywriter for the novel "The Salt House".

Here is the reception brief:
{brief}

Here are the real pull-quotes from reader reviews:
{quotes_blob}

Generate marketing copy and return ONLY a JSON object (no preamble, no code fences) with these fields:

- "best_pull_quotes": the 3 strongest verbatim pull-quotes from the list above, chosen for marketing impact
- "back_cover_blurb": a 2-3 sentence back-cover-style blurb that captures what readers love
- "social_posts": a list of exactly 2 short social media post (each under 280 characters) promoting the book

Return nothing but the JSON object."""

message=client.messages.create(
    model="claude-opus-4-8",
    max_tokens=1000,
    messages=[{"role":"user","content":prompt}],
)

result_text=message.content[0].text.strip()

#Clean fences
if result_text.startswith("```"):
    result_text=result_text.split("\n",1)[1]
    result_text=result_text.rsplit("```",1)[0]
    result_text=result_text.strip()

copy=json.loads(result_text)

#Save the generated copy
with open("marketing_copy.json","w") as f:
    json.dump(copy, f, indent=2)

#Print it nicely
print("=== BEST PULL QUOTES ===")
for q in copy["best_pull_quotes"]:
    print(f" •{q}")

print("\n=== BACK COVER BLURB ===")
print(copy["back_cover_blurb"])
print("\n=== SOCIAL POSTS ===")
for post in copy["social_posts"]:
    print(f"  • {post}")

print("\nSaved marketing copy to marketing_copy.json")
