"""
Resume Roaster — LLM-powered resume vs job description analyzer.
"""

import json
import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from pypdf import PdfReader

# ─── Setup ─────────────────────────────────────────────────────
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY", "")

if not GEMINI_KEY:
    st.error("Missing GEMINI_API_KEY. Add it to your .env or Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_KEY)

st.set_page_config(
    page_title="Resume Roaster",
    page_icon="🔥",
    layout="centered",
)


# ─── Helpers ───────────────────────────────────────────────────
def extract_pdf_text(uploaded_file) -> str:
    """Read a PDF file and return concatenated text."""
    reader = PdfReader(uploaded_file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def load_prompt(name: str) -> str:
    return Path("prompts") / f"{name}.txt"


def call_gemini(prompt: str, model_name: str = "gemini-2.5-flash") -> str:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text.strip()


def score_resume(resume_text: str, jd_text: str) -> dict:
    template = (Path("prompts") / "score.txt").read_text(encoding="utf-8")
    prompt = template.format(resume_text=resume_text, job_description=jd_text)
    
    # Debug: confirm prompt is not empty
    # st.write(f"Debug: scoring prompt length = {len(prompt)} chars")
    
    raw = call_gemini(prompt)

    # Strip code fences if present
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:].strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])
        raise

def roast_resume(resume_text: str, jd_text: str) -> str:
    template = (Path("prompts") / "roast.txt").read_text(encoding="utf-8")
    prompt = template.format(resume_text=resume_text, job_description=jd_text)
    return call_gemini(prompt)


# ─── UI ────────────────────────────────────────────────────────
st.title("🔥 Resume Roaster")
st.write(
    "Upload your resume, paste the job description, "
    "and get a real (and slightly roasted) assessment of how well you match."
)

col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

with col2:
    st.subheader("💼 Job Description")
    jd_text = st.text_area("Paste it here", height=220, placeholder="Paste the full job description...")

go = st.button("🔥 Roast My Resume", type="primary", use_container_width=True)
resume_text = ""  # default value to avoid NameError
if go:
    # Debug both inputs
    # st.write(f"Debug: jd_text length = {len(jd_text)}, first 100 chars: {jd_text[:100]!r}")

    if not pdf_file or not jd_text.strip():
        st.warning("Please upload a resume AND paste a job description.")
        st.stop()

    with st.spinner("Reading your resume..."):
        try:
            resume_text = extract_pdf_text(pdf_file)
        except Exception as e:
            st.error(f"Couldn't read PDF: {e}")
            st.stop()

    # Debug: show what we actually extracted
    if len(resume_text) < 100:
        st.error(
            "⚠️ Couldn't extract meaningful text from this PDF. "
            "This usually means the PDF is image-based (scanned) or uses non-standard text encoding. "
            f"\n\nExtracted {len(resume_text)} characters: `{resume_text[:200] or '(nothing)'}`"
        )
        st.info(
            "💡 **Fix:** Re-export your resume as a text-based PDF from Word, Google Docs, "
            "LaTeX, or any text editor. Avoid scanned or screenshot-based PDFs."
        )
        st.stop()

    # Optional: show extracted text in a collapsible debug section
    # with st.expander("🔍 Debug: extracted resume text"):
        # st.code(resume_text[:1500] + ("..." if len(resume_text) > 1500 else ""))

    # Score and roast in parallel-ish (sequential, but both fast)
    with st.spinner("Scoring the match..."):
        try:
            score_data = score_resume(resume_text, jd_text)
        except Exception as e:
            st.error(f"Scoring failed: {e}")
            st.stop()

    with st.spinner("Writing the roast..."):
        try:
            roast = roast_resume(resume_text, jd_text)
        except Exception as e:
            st.error(f"Roast failed: {e}")
            roast = "(The roast got too spicy and disappeared.)"

    # ─── Results ────────────────────────────────────────────────
    st.divider()
    
    # Success notification with balloons for visual feedback
    st.success("✅ Analysis complete! Scroll down to see your results.")
    st.balloons()  # Fun visual flourish to signal completion

    # Anchor for auto-scroll
    st.markdown('<div id="results"></div>', unsafe_allow_html=True)
    st.markdown(
        """
        <script>
            window.location.hash = "results";
        </script>
        """,
        unsafe_allow_html=True,
    )

    score = score_data.get("match_score", 0)
    st.subheader("📊 Match Score")
    st.metric(label="Out of 100", value=f"{score}")
    st.progress(min(max(score, 0), 100) / 100)

    if score >= 80:
        st.success("Strong match. Apply with confidence.")
    elif score >= 60:
        st.info("Decent match. Some tuning will help.")
    elif score >= 40:
        st.warning("Partial match. Significant gaps to close.")
    else:
        st.error("Weak match. Consider a different angle or different role.")

    st.subheader("🔥 The Roast")
    st.markdown(f"> {roast}")

    col_match, col_miss = st.columns(2)
    with col_match:
        st.subheader("✅ Matched Keywords")
        for kw in score_data.get("matched_keywords", []):
            st.markdown(f"- {kw}")
    with col_miss:
        st.subheader("❌ Missing Keywords")
        for kw in score_data.get("missing_keywords", []):
            st.markdown(f"- {kw}")

    st.subheader("💡 Suggested Improvements")
    for i, s in enumerate(score_data.get("suggestions", []), 1):
        st.markdown(f"**{i}.** {s}")

st.divider()
st.caption("Built by Kunhong Lyu · Powered by Gemini API · github.com/KunhongLyu")