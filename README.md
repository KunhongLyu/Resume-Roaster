# 🔥 Resume Roaster

**An LLM-powered tool that scores your resume against a job description, points out the gaps, and roasts you (constructively) for the things you missed.**

Built with Streamlit and the Gemini API. Upload a PDF, paste a JD, get a numeric match score, a witty roast, and three concrete improvement suggestions in about ten seconds.

🌐 **[Try it live](https://resume-roaster-kunhonglyu.streamlit.app/)** &nbsp;·&nbsp; Built by [Kunhong Lyu](https://github.com/KunhongLyu)

---

## What it does

1. **Match Score** — a 0–100 score for how well your resume fits the job
2. **Matched & Missing Keywords** — the skills the JD asks for, sorted by what's in your resume and what isn't
3. **The Roast** — a 3–5 sentence playful critique that calls out your biggest gap
4. **Suggested Improvements** — three specific, actionable changes you can make today

---

## Why I built this

I was applying to a lot of internships and got tired of manually checking each resume version against each job description. So I built the tool I wished existed — one that gives me honest, fast feedback and is mildly funny about it.

The roast tone is intentional. Plain "your resume is missing X" feedback is easy to ignore; a playful jab is harder to forget, and it makes iterating on your resume something you actually want to do.

---

## Tech stack

- **Frontend & app:** Streamlit
- **LLM:** Google Gemini API (`gemini-2.5-flash`)
- **PDF parsing:** pypdf
- **Language:** Python 3.10+

---

## Production lessons: shipping a public LLM app responsibly

Putting an LLM-backed app on the public internet means **every visitor's button click costs me money**. Before going live I added two safeguards that I think matter more than the model code itself:

**1. Hard budget cap on the API key.** I set a Google Cloud billing limit and disabled auto-refill, so the worst case is the app stops working when the budget is hit — not a surprise charge on my card.

**2. Per-session rate limiting in the app.** I added Streamlit session-state checks that prevent any single user from spamming the API: a minimum cooldown between requests and a daily cap per session. This won't stop a determined attacker, but it raises the cost of casual abuse and keeps the experience usable for real users.

These aren't model improvements — they're product decisions. I think internships at AI companies are partly about understanding that LLM features only become products when you treat reliability, cost, and abuse as first-class problems.

---

## Run it locally

```bash
git clone https://github.com/KunhongLyu/resume-roaster.git
cd resume-roaster
pip install -r requirements.txt
echo "GEMINI_API_KEY=your_key_here" > .env
streamlit run app.py
```

Get a Gemini API key for free at [aistudio.google.com](https://aistudio.google.com).

---

## License

MIT — fork it, roast your friends' resumes, use the code however you like.
