# Reader Review Intelligence

Hi everyone. This is an LLM pipeline that turns raw reader reviews into marketing intelligence. Paste in a batch of book reviews and it classifies sentiment, extracts the specific praise/complaints/quotable lines, summarizes overall reception into a brief, and generates ready-to-use marketing copy, all through a simple web app. I built this as a focused project to explore applied LLM workflows for a publishing-marketing use case. That’s my industry, after all!

---

## The Problem
A book's marketing team can have hundreds of reader reviews and no fast way to know what readers actually love, what falls flat, and which exact phrases would make good marketing copy. Reading them all by hand doesn't scale and skimming a few misses the patterns.
This tool does that analysis in seconds and hands marketing back something usable: a reception brief, the strongest pull-quotes (verbatim from real readers), a back-cover blurb angle, and drafted social posts. Ta-da!

---

## What it does
The app runs a four-stage LLM pipeline:
- **Classify:** Tags each review by sentiment (positive / mixed / negative) and theme (plot, characters, pacing, writing style, ending, emotional impact).
- **Extract:** It then pulls out the specific praises, complaints, and short verbatim phrases that would work as marketing quotes.
- **Summarize:** It synthesizes all the analyzed data into a ~200-word marketing brief.
- **Generate:** Finally, it produces the 3 strongest pull-quotes, a back-cover blurb, and two social media posts.
The front-end (Streamlit) lets a non-technical user paste reviews, click a button, and read the results laid out on a page. No code required. ☺️

---

## How it works
Each stage is a separate, self-contained step that saves its output to a file, which the next stage reads:
reviews  →  classify  →  extract  →  summarize  →  generate  →  marketing copy
Every stage is an LLM API call with a carefully written prompt that constrains the output to a specific structured format (JSON), with a cleanup step that strips stray formatting so the data is reliable for the next stage. The app version (app.py) runs the whole pipeline live on whatever reviews the user pastes in.

---

## Results
I evaluated the classifier against a personally hand-labeled golden standard: I read 20 sample reviews and labeled each one's sentiment myself, then compared the classifier's output to my labels.

- **Accuracy:** 18/20 = 90% agreement with my own labels
- **Speed:** ~1.4 seconds per review
- **Cost:** ~$0.002 per review for the classification step (Claude Opus 4.8)

I will admit the two disagreements were both on genuinely ambiguous reviews. For example, a glowing review that docks one star for a minor subplot, and a review that loved the book until an ending the reader hated. On every clear-cut review, the classifier agreed with me. This suggests the model is reasoning about sentiment rather than keyword-matching, and that accuracy here is partly bounded by how subjective the "correct" label even is. But then again, that’s publishing in a nutshell. 

---

## Limitations & What I'd Do Next
This is V1! So here are my honest gaps:

**It is admittedly a small evaluation set.** 20 hand-labeled reviews is enough to sanity-check, but not enough to trust in production. A real deployment needs a larger, multi-rater gold set.

**It’s all synthetic data.** The sample reviews were AI-generated for one fictional book. I’d like to test on real review data across multiple titles.

**There’s one tricky little edge case.** A short, purely enthusiastic review ("Stunning. Simply stunning.") classified correctly as positive but the extractor returned no "praises" because the praise was too holistic to extract as a specific item. The praise was overwhelming but it was simply not specific enough. Worth fixing in the future.

**The cost/model tradeoff has not fully tuned.** Everything runs on the premium model. Womp womp. The classify and extract steps are simpler and would likely run well on a cheaper, faster model, so I could reserve the premium model for the generation step where quality matters most.

**My code could be refactored.** The shared pipeline functions are currently duplicated between the standalone scripts and the app; they should live in one shared module. It’s a work in progress!

---

## How to run it
You'll need an Anthropic API key.

```bash
pip install anthropic streamlit
export ANTHROPIC_API_KEY="your-key-here"
streamlit run app.py
```

Then open the local URL Streamlit prints. Paste reviews (one per line) and click Run Analysis.
To regenerate the sample data and run the pipeline as standalone scripts:

```bash
python make_reviews.py   # generates sample reviews
python classify.py       # sentiment + themes
python extract.py        # praises, complaints, pull-quotes
python summarize.py      # marketing brief
python generate.py       # marketing copy
python evaluate.py       # accuracy / speed / cost
```

---

## Built with:
Python · Anthropic Claude API · Streamlit · GitHub Codespaces

---

Thanks all!



# review_intelligence
