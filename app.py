import anthropic
import json
import streamlit as st

client = anthropic.Anthropic()

MODEL = "claude-opus-4-8"


# ---------- Helper: strip code fences from model output ----------
def clean_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1]
        text = text.rsplit("```", 1)[0]
        text = text.strip()
    return json.loads(text)


# ---------- The four pipeline steps ----------
def classify_review(review_text):
    prompt = f"""Analyze this reader review of a novel.

Review: "{review_text}"

Classify it and return ONLY a JSON object (no preamble, no code fences) with these fields:
- "sentiment": one of "positive", "mixed", or "negative"
- "themes": a list of 1-3 themes chosen from: ["plot", "characters", "pacing", "writing style", "ending", "emotional impact"]

Return nothing but the JSON object."""
    message = client.messages.create(
        model=MODEL, max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return clean_json(message.content[0].text)


def extract_from_review(review_text):
    prompt = f"""Extract key information from this reader review of a novel.

Review: "{review_text}"

Return ONLY a JSON object (no preamble, no code fences) with these fields:
- "praises": a list of specific things the reviewer praised (empty list if none)
- "complaints": a list of specific things the reviewer criticized (empty list if none)
- "pull_quotes": a list of 0-2 short, vivid verbatim phrases that would work as marketing quotes

Return nothing but the JSON object."""
    message = client.messages.create(
        model=MODEL, max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return clean_json(message.content[0].text)


def summarize(classified, extracted):
    lines = []
    for c in classified:
        lines.append(f"Review: sentiment={c['sentiment']}, themes={c['themes']}")
    for e in extracted:
        lines.append(f"praises: {e['praises']} | complaints: {e['complaints']}")
    data_blob = "\n".join(lines)
    prompt = f"""You are helping a book marketing team. Below is analyzed data from reader reviews.

DATA:
{data_blob}

Write a concise marketing reception brief (about 200 words) covering overall sentiment, consistent praise, common criticisms, and which themes resonated most. Clear prose for a marketing audience. No JSON, just the brief."""
    message = client.messages.create(
        model=MODEL, max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def generate_copy(brief, all_pull_quotes):
    quotes_blob = "\n".join(all_pull_quotes)
    prompt = f"""You are a book marketing copywriter.

Reception brief:
{brief}

Real pull-quotes from reviews:
{quotes_blob}

Return ONLY a JSON object (no preamble, no code fences) with these fields:
- "best_pull_quotes": the 3 strongest verbatim pull-quotes from the list
- "back_cover_blurb": a 2-3 sentence back-cover blurb
- "social_posts": a list of exactly 2 short social media posts (each under 280 characters)

Return nothing but the JSON object."""
    message = client.messages.create(
        model=MODEL, max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return clean_json(message.content[0].text)


# ---------- The web page ----------
st.title("📚 Reader Review Intelligence")
st.write("Paste reader reviews (one per line) and turn them into marketing intelligence.")

default_reviews = """I read this in two sittings and cried at least three times. The way the author captures grief is stunning.
Beautifully written but nothing happens. They arrive at the house, sort through boxes, and that's it for 340 pages.
The Salt House is a quiet triumph. The prose is restrained, precise, never showing off.
DNF at 40%. Everyone here is so passive and mopey. The sisters resent each other but never say anything.
What a gorgeous, devastating book. The reveal about the summer their father left reorganizes the whole story."""

reviews_text = st.text_area("Reviews (one per line):", value=default_reviews, height=200)

if st.button("Run Analysis", type="primary"):
    raw_reviews = [r.strip() for r in reviews_text.split("\n") if r.strip()]

    if not raw_reviews:
        st.warning("Please paste at least one review.")
    else:
        classified = []
        extracted = []
        all_pull_quotes = []

        progress = st.progress(0, text="Analyzing reviews...")
        for i, review in enumerate(raw_reviews):
            c = classify_review(review)
            e = extract_from_review(review)
            classified.append(c)
            extracted.append(e)
            for q in e["pull_quotes"]:
                all_pull_quotes.append(q)
            progress.progress((i + 1) / len(raw_reviews), text=f"Analyzed {i+1} of {len(raw_reviews)} reviews")

        with st.spinner("Writing the marketing brief..."):
            brief = summarize(classified, extracted)
        with st.spinner("Generating marketing copy..."):
            copy = generate_copy(brief, all_pull_quotes)

        # ---- Display results ----
        st.header("Sentiment Breakdown")
        pos = sum(1 for c in classified if c["sentiment"] == "positive")
        mix = sum(1 for c in classified if c["sentiment"] == "mixed")
        neg = sum(1 for c in classified if c["sentiment"] == "negative")
        col1, col2, col3 = st.columns(3)
        col1.metric("Positive", pos)
        col2.metric("Mixed", mix)
        col3.metric("Negative", neg)

        st.header("Marketing Brief")
        st.write(brief)

        st.header("Best Pull-Quotes")
        for q in copy["best_pull_quotes"]:
            st.markdown(f"> {q}")

        st.header("Back-Cover Blurb")
        st.info(copy["back_cover_blurb"])

        st.header("Social Posts")
        for post in copy["social_posts"]:
            st.markdown(f"- {post}")
            