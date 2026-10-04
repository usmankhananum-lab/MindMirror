"""
MindMirror — Main Streamlit App
Owner: Member 4 (Streamlit / UI)

VISUAL REDESIGN on top of the working app. All pipeline logic (student
agent calls, evaluator calls, memory save/load, session flow) is unchanged.

Run with:
    streamlit run app.py
"""

import html
import streamlit as st

from modules.student_agent import generate_student_question, validate_round_count
from modules.evaluator import evaluate_session
from services.memory import save_session, load_sessions


st.set_page_config(page_title="MindMirror", page_icon="🧠", layout="centered")

MIN_ROUNDS, MAX_ROUNDS = 3, 5
WEAK_SCORE_THRESHOLD = 6  # scores below this are marked "weak" per FR-11

LEVEL_OPTIONS = ["Complete Beginner", "High School Student", "College Student"]

# =======================================================================
# DESIGN SYSTEM — "Reflection" palette: violet + teal, warm neutral paper
# =======================================================================
# Primary accent    #7C3AED  (violet-600)
# Secondary accent  #06B6D4  (cyan-500)
# Page background   #F7F5FC  (soft lavender-white)
# Card background   #FFFFFF
# Border            #E7E2F5
# Main text         #211C33
# Muted text        #6B6680
# Success/Strength  #10B981 / bg #DCFCE9
# Warning/Gap       #F59E0B / bg #FEF3D9
# Info/Revise       #3B82F6 / bg #E0ECFF
# Weak banner       #EF4444 / bg #FEE2E2

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

:root {
    --mm-primary: #7C3AED;
    --mm-primary-dark: #6D28D9;
    --mm-secondary: #06B6D4;
    --mm-bg: #F7F5FC;
    --mm-card: #FFFFFF;
    --mm-border: #E7E2F5;
    --mm-text: #211C33;
    --mm-muted: #6B6680;
    --mm-success: #10B981;
    --mm-success-bg: #DCFCE9;
    --mm-warning: #F59E0B;
    --mm-warning-bg: #FEF3D9;
    --mm-info: #3B82F6;
    --mm-info-bg: #E0ECFF;
    --mm-weak: #EF4444;
    --mm-weak-bg: #FEE2E2;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
    color: var(--mm-text);
}
h1, h2, h3, .mm-heading-font {
    font-family: 'Poppins', 'Inter', sans-serif !important;
}

.stApp {
    background: linear-gradient(180deg, #F7F5FC 0%, #F3EFFC 100%);
}

@keyframes mmFadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes mmShimmer {
    0%   { background-position: -200px 0; }
    100% { background-position: 200px 0; }
}
@keyframes mmFloat {
    0%, 100% { transform: translateY(0); }
    50%      { transform: translateY(-4px); }
}

.mm-fade-in { animation: mmFadeUp 0.45s ease both; }

/* ---- Hero header ---- */
.mm-hero {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 6px 0 2px 0;
}
.mm-hero-icon {
    font-size: 42px;
    line-height: 1;
    animation: mmFloat 3.5s ease-in-out infinite;
}
.mm-hero-title {
    font-family: 'Poppins', sans-serif;
    font-size: 32px;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin: 0;
    background: linear-gradient(90deg, var(--mm-primary-dark), var(--mm-secondary));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.mm-hero-subtitle {
    font-size: 14.5px;
    color: var(--mm-muted);
    margin-top: 2px;
    font-weight: 500;
}
.mm-hero-divider {
    height: 1px;
    background: linear-gradient(90deg, var(--mm-border), transparent);
    margin: 16px 0 26px 0;
    border: none;
}

.mm-section-title {
    font-family: 'Poppins', sans-serif;
    font-size: 19px;
    font-weight: 700;
    color: var(--mm-text);
    margin: 2px 0 12px 0;
}
.mm-eyebrow {
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--mm-primary);
    margin-bottom: 2px;
}

/* ---- Form card ---- */
div[data-testid="stForm"] {
    background: var(--mm-card);
    border: 1px solid var(--mm-border);
    border-radius: 18px;
    padding: 30px 30px 18px 30px;
    box-shadow: 0 1px 3px rgba(124, 58, 237, 0.05), 0 10px 30px rgba(124, 58, 237, 0.06);
    transition: box-shadow 0.2s ease;
}
div[data-testid="stForm"]:hover {
    box-shadow: 0 1px 3px rgba(124, 58, 237, 0.07), 0 14px 36px rgba(124, 58, 237, 0.1);
}

/* ---- Inputs ---- */
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div, .stTextArea textarea {
    border-radius: 12px !important;
    border: 1.5px solid var(--mm-border) !important;
    background-color: #FBFAFE !important;
    font-size: 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--mm-primary) !important;
    box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.14) !important;
}
.stTextInput label, .stSelectbox label, .stTextArea label {
    font-weight: 600 !important;
    font-size: 13.5px !important;
    color: var(--mm-text) !important;
}

/* ---- Buttons ---- */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
    background: linear-gradient(135deg, var(--mm-primary) 0%, var(--mm-secondary) 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 14.5px !important;
    box-shadow: 0 3px 10px rgba(124, 58, 237, 0.25) !important;
    transition: transform 0.12s ease, box-shadow 0.12s ease !important;
}
.stButton button:hover, .stFormSubmitButton button:hover, .stDownloadButton button:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 6px 18px rgba(124, 58, 237, 0.35) !important;
    color: #FFFFFF !important;
}
.stButton button:active, .stFormSubmitButton button:active {
    transform: translateY(0) scale(0.99);
}

/* ---- Progress bar ---- */
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, var(--mm-primary), var(--mm-secondary)) !important;
    background-size: 200px 100%;
    animation: mmShimmer 1.8s linear infinite;
    border-radius: 999px;
}
div[data-testid="stProgress"] {
    background: #EDE9FA;
    border-radius: 999px;
}

/* ---- Chat bubbles (Q&A) ---- */
div[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    border: 1px solid var(--mm-border) !important;
    box-shadow: 0 1px 2px rgba(124, 58, 237, 0.04);
    animation: mmFadeUp 0.35s ease both;
}

/* ---- Metric (Clarity Score) ---- */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #FFFFFF 0%, #F3EFFC 100%);
    border: 1px solid var(--mm-border);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(124, 58, 237, 0.05);
}
div[data-testid="stMetricValue"] {
    color: var(--mm-primary) !important;
    font-family: 'Poppins', sans-serif !important;
    font-weight: 800 !important;
}
div[data-testid="stMetricLabel"] {
    color: var(--mm-muted) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 11.5px !important;
    letter-spacing: 0.06em;
}

/* ---- Alerts ---- */
div[data-testid="stAlertContainer"] {
    border-radius: 14px !important;
    font-size: 14px !important;
    animation: mmFadeUp 0.3s ease both;
}

/* ---- Expanders (history) ---- */
div[data-testid="stExpander"] {
    border: 1px solid var(--mm-border) !important;
    border-radius: 14px !important;
    background: var(--mm-card) !important;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(124, 58, 237, 0.03);
}
div[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 14.5px !important;
    padding: 12px 16px !important;
}

/* ---- Report pill cards ---- */
.mm-report-card {
    background: var(--mm-card);
    border: 1px solid var(--mm-border);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 14px;
    box-shadow: 0 1px 3px rgba(124, 58, 237, 0.05);
}
.mm-report-card-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 15px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.mm-report-item {
    display: flex;
    gap: 10px;
    padding: 7px 0;
    font-size: 14px;
    line-height: 1.5;
    border-bottom: 1px solid #F3F0FA;
}
.mm-report-item:last-child { border-bottom: none; }
.mm-dot {
    flex-shrink: 0;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    margin-top: 7px;
}
.mm-dot-success { background: var(--mm-success); }
.mm-dot-warning { background: var(--mm-warning); }
.mm-dot-info { background: var(--mm-info); }

.mm-weak-banner {
    background: var(--mm-weak-bg);
    color: #991B1B;
    border: 1px solid #FCA5A5;
    border-radius: 14px;
    padding: 14px 18px;
    font-size: 14px;
    font-weight: 600;
    margin: 6px 0 18px 0;
    animation: mmFadeUp 0.3s ease both;
}

/* ---- History row score badges ---- */
.mm-score-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-left: 6px;
}
.mm-score-strong { background: var(--mm-success-bg); color: var(--mm-success); }
.mm-score-weak { background: var(--mm-weak-bg); color: var(--mm-weak); }

.mm-footer {
    text-align: center;
    color: var(--mm-muted);
    font-size: 12.5px;
    margin-top: 44px;
    padding-top: 16px;
    border-top: 1px solid var(--mm-border);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def report_card(title: str, icon: str, items: list[str], dot_class: str) -> str:
    rows = "".join(
        f"<div class='mm-report-item'><span class='mm-dot {dot_class}'></span>"
        f"<span>{html.escape(str(item))}</span></div>"
        for item in items
    )
    return (
        f"<div class='mm-report-card mm-fade-in'>"
        f"<div class='mm-report-card-title'>{icon} {html.escape(title)}</div>"
        f"{rows}"
        f"</div>"
    )


# =======================================================================
# HEADER
# =======================================================================
st.markdown(
    """
    <div class="mm-hero mm-fade-in">
        <div class="mm-hero-icon">🧠</div>
        <div>
            <p class="mm-hero-title">MindMirror</p>
            <p class="mm-hero-subtitle">You only know it if you can teach it.</p>
        </div>
    </div>
    <hr class="mm-hero-divider" />
    """,
    unsafe_allow_html=True,
)


# =======================================================================
# Session state setup (UNCHANGED LOGIC)
# =======================================================================
defaults = {
    "phase": "intake",
    "topic": "",
    "level": "",
    "explanation": "",
    "max_rounds": MIN_ROUNDS,
    "current_round": 1,
    "history": [],
    "qa_pairs": [],
    "current_question": None,
    "qa_error": None,
}
for key, value in defaults.items():
    st.session_state.setdefault(key, value)


def reset_to_intake(prefill_topic: str = "", prefill_level: str = ""):
    st.session_state["phase"] = "intake"
    st.session_state["topic"] = prefill_topic
    st.session_state["level"] = prefill_level
    st.session_state["explanation"] = ""
    st.session_state["current_round"] = 1
    st.session_state["history"] = []
    st.session_state["qa_pairs"] = []
    st.session_state["current_question"] = None
    st.session_state["qa_error"] = None


def ask_next_question():
    """Calls the REAL student agent, with friendly error handling (FR-13)."""
    try:
        question = generate_student_question(
            st.session_state["topic"],
            st.session_state["level"],
            st.session_state["explanation"],
            st.session_state["history"] or None,
        )
        st.session_state["current_question"] = question
        st.session_state["qa_error"] = None
    except Exception as e:
        st.session_state["current_question"] = None
        st.session_state["qa_error"] = str(e)


# =======================================================================
# Screen 1 — Topic + Level + Explanation intake (UNCHANGED LOGIC)
# =======================================================================
if st.session_state["phase"] == "intake":
    with st.form("topic_form"):
        st.markdown("<p class='mm-eyebrow'>Step 1</p>", unsafe_allow_html=True)
        st.markdown("<p class='mm-section-title'>📝 Teach Me Something</p>", unsafe_allow_html=True)

        topic = st.text_input("What topic do you want to teach?", value=st.session_state["topic"])
        level = st.selectbox(
            "Explain it like I'm a...",
            LEVEL_OPTIONS,
            index=LEVEL_OPTIONS.index(st.session_state["level"]) if st.session_state["level"] in LEVEL_OPTIONS else 0,
        )
        explanation = st.text_area("Now explain it in your own words:", height=200)
        rounds = st.selectbox("Number of question rounds", [3, 4, 5], index=0)

        submitted = st.form_submit_button("Start Teaching")

    if submitted:
        if not topic.strip() or not explanation.strip():
            st.warning("Please enter a topic and an explanation before continuing.")
            st.stop()

        st.session_state["topic"] = topic.strip()
        st.session_state["level"] = level
        st.session_state["explanation"] = explanation.strip()
        st.session_state["max_rounds"] = validate_round_count(rounds)
        st.session_state["current_round"] = 1
        st.session_state["history"] = []
        st.session_state["qa_pairs"] = []

        with st.spinner("The Confused Student is thinking of a question..."):
            ask_next_question()

        st.session_state["phase"] = "qa"
        st.rerun()

# =======================================================================
# Screen 2 — Q&A loop with round counter (UNCHANGED LOGIC)
# =======================================================================
elif st.session_state["phase"] == "qa":
    st.markdown(
        f"<p class='mm-section-title mm-fade-in'>🎓 Teaching: {html.escape(st.session_state['topic'])}</p>",
        unsafe_allow_html=True,
    )
    st.caption(f"Round {st.session_state['current_round']} of {st.session_state['max_rounds']}")
    st.progress(st.session_state["current_round"] / st.session_state["max_rounds"])
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    for i, pair in enumerate(st.session_state["qa_pairs"], start=1):
        with st.chat_message("assistant"):
            st.write(pair["question"])
        with st.chat_message("user"):
            st.write(pair["answer"])

    if st.session_state["qa_error"]:
        st.error(f"The Confused Student couldn't respond: {st.session_state['qa_error']}")
        if st.button("Retry question"):
            with st.spinner("Trying again..."):
                ask_next_question()
            st.rerun()

    elif st.session_state["current_question"]:
        with st.chat_message("assistant"):
            st.write(st.session_state["current_question"])

        with st.form(f"answer_form_{st.session_state['current_round']}"):
            answer = st.text_area("Your answer:", height=120)
            answer_submitted = st.form_submit_button("Submit Answer")

        if answer_submitted:
            if not answer.strip():
                st.warning("Please write an answer before submitting.")
                st.stop()

            question = st.session_state["current_question"]
            st.session_state["qa_pairs"].append({"question": question, "answer": answer.strip()})
            st.session_state["history"].append({"role": "assistant", "content": question})
            st.session_state["history"].append({"role": "user", "content": answer.strip()})

            if st.session_state["current_round"] >= st.session_state["max_rounds"]:
                st.session_state["phase"] = "report"
            else:
                st.session_state["current_round"] += 1
                with st.spinner("The Confused Student is thinking of the next question..."):
                    ask_next_question()
            st.rerun()

# =======================================================================
# Screen 3 — Evaluation report (UNCHANGED LOGIC, redesigned presentation)
# =======================================================================
elif st.session_state["phase"] == "report":
    st.markdown(
        f"<p class='mm-section-title mm-fade-in'>📊 Evaluation Report: "
        f"{html.escape(st.session_state['topic'])}</p>",
        unsafe_allow_html=True,
    )

    with st.spinner("Evaluating your explanation..."):
        result = evaluate_session(st.session_state["topic"], st.session_state["qa_pairs"])

    score = result["clarity_score"]
    st.metric("Clarity Score", f"{score} / 10")
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    st.markdown(report_card("Strengths", "✅", result["strengths"], "mm-dot-success"), unsafe_allow_html=True)
    st.markdown(report_card("Gaps", "⚠️", result["gaps"], "mm-dot-warning"), unsafe_allow_html=True)
    st.markdown(report_card("Concepts to Revise", "📘", result["revision_concepts"], "mm-dot-info"), unsafe_allow_html=True)

    is_weak = score < WEAK_SCORE_THRESHOLD
    if is_weak:
        st.markdown(
            "<div class='mm-weak-banner'>⚠️ This topic is marked as <b>weak</b> — consider practicing it again.</div>",
            unsafe_allow_html=True,
        )

    # Save to memory.json — guard so a rerun of this screen doesn't duplicate the entry
    save_key = f"saved_{st.session_state['topic']}_{st.session_state['current_round']}"
    if not st.session_state.get(save_key):
        save_session({
            "topic": st.session_state["topic"],
            "level": st.session_state["level"],
            "clarity_score": score,
        })
        st.session_state[save_key] = True

    report_text = (
        f"MindMirror Report — {st.session_state['topic']}\n"
        f"Level: {st.session_state['level']}\n"
        f"Clarity Score: {score}/10\n\n"
        f"Strengths:\n" + "\n".join(f"- {s}" for s in result["strengths"]) + "\n\n"
        f"Gaps:\n" + "\n".join(f"- {g}" for g in result["gaps"]) + "\n\n"
        f"Concepts to Revise:\n" + "\n".join(f"- {c}" for c in result["revision_concepts"])
    )
    st.download_button("⬇️ Download Report", report_text, file_name="mindmirror_report.txt")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔁 Practice This Topic Again"):
            reset_to_intake(prefill_topic=st.session_state["topic"], prefill_level=st.session_state["level"])
            st.rerun()
    with col2:
        if st.button("➕ Teach a New Topic"):
            reset_to_intake()
            st.rerun()

    # ---------------- History ----------------
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p class='mm-section-title'>📚 Session History</p>", unsafe_allow_html=True)
    sessions = load_sessions()
    if not sessions:
        st.caption("No past sessions yet.")
    else:
        for s in reversed(sessions):
            badge_cls = "mm-score-weak" if s["weak"] else "mm-score-strong"
            weak_tag = " 🔴" if s["weak"] else ""
            label = (
                f"{s['topic']}{weak_tag}  —  {s['date']}"
            )
            with st.expander(label):
                st.markdown(
                    f"<span class='mm-score-badge {badge_cls}'>{s['score']}/10</span>",
                    unsafe_allow_html=True,
                )
                st.write(f"**Level:** {s['level']}")
                if st.button(f"Practice '{s['topic']}' again", key=f"practice_{s['topic']}_{s['date']}"):
                    reset_to_intake(prefill_topic=s["topic"], prefill_level=s["level"])
                    st.rerun()

# ---------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------
st.markdown(
    "<div class='mm-footer'>🧠 MindMirror — You only know it if you can teach it.</div>",
    unsafe_allow_html=True,
)
