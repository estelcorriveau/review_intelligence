import anthropic
import json

client=anthropic.Anthropic()

#Load the data we already produced in earlier steps

with open("classified.json","r") as f:
    classified=json.load(f)

with open("extracted.json", "r") as f:
    extracted=json.load(f)

#Build a compact text summary of all the data to feed the model

lines=[]
for c in classified:
    lines.append(f"Review #{c['id']}: sentiment={c['sentiment']},themes={c['themes']}")
for e in extracted:
    lines.append(f"Review #{e['id']} praises:{e['praises']}")
    lines.append(f"Review #{e['id']}complaints:{e['complaints']}")

data_blob="\n".join(lines)

#A SINGLE call: summarize everything into one marketing brief

prompt= f"""You are helping a book marketing team. Below is analyzed data from 20 reader reviews of the novel "The Salt House." 

DATA:
{data_blob}

Write a concise marketing reception brief(about 200 words) covering:
1. Overall sentiment (how many positive/mixed/negative)
2. What readers consistently praised
3. What the common criticisms were
4. Which themes resonated the most

Write in clear prose for a marketing audience. No JSON, just the brief."""

message=client.messages.create(
    model="claude-opus-4-8",
    max_tokens=600,
    messages=[{"role":"user","content":prompt}],
)

brief=message.content[0].text.strip()

#Save the brief to a text file

with open("brief.txt", "w") as f:
    f.write(brief)

print(brief)
print("\nSaved brief to brief.txt")