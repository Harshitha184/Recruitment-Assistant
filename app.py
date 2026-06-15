'''import streamlit as st
import os, re
import pandas as pd
from name_extractor import extract_candidate_name
from matcher import calculate_match_score
from utils import get_status
from resume_parser import extract_resume_text
from email_generator import generate_email
from email_sender import send_email
from database import save_candidates, save_email, get_all_candidates, get_all_emails, clear_db
from report_generator import generate_screening_report
from email_extractor import extract_candidate_email
from matcher import model
from qdrant_db import save_embedding, get_all_vectors
from skill_extractor import extract_jd_skills, extract_resume_skills, compute_skill_match
from langfuse import Langfuse
from pipeline import recruitment_pipeline
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL")
)
print("Langfuse initialized successfully")
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)
st.set_page_config(page_title="HR Recruitment Assistant", page_icon="💼", layout="wide")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700&family=DM+Mono&display=swap');
html,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:#0f0f13;color:#e8e8f0}
[data-testid="stSidebar"]{background:#1c1c2e!important;border-right:2px solid #4f46e5}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p{color:#e2e8f0!important;font-weight:600}
[data-testid="stSidebar"] h2{color:#a78bfa!important;font-size:.75rem!important;letter-spacing:.12em;text-transform:uppercase}
[data-testid="stSidebar"] .stTextInput>div>div>input,
[data-testid="stSidebar"] .stTextArea>div>div>textarea{background:#252538!important;border:1px solid #4f46e5!important;border-radius:8px!important;color:#f1f5f9!important}
[data-testid="stSidebar"] .stTextInput>label,
[data-testid="stSidebar"] .stTextArea>label{color:#c4b5fd!important;font-weight:600!important;font-size:.85rem!important}
.hero{
    background:linear-gradient(135deg,#1e1b4b,#312e81,#1e1b4b);
    border:1px solid #4338ca;
    border-radius:16px;
    padding:3rem;
    margin-bottom:2rem;
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    text-align:center;
}
.hero h1{
    font-size:3rem;
    font-weight:700;
    color:#f5f3ff;
    margin:0;
}
.hero p{
    color:#a5b4fc;
    font-size:1rem;
    margin-top:10px;
}
.lbl{font-size:.72rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#818cf8;margin-bottom:.75rem}
[data-testid="stFileUploader"]{
    background:#0f0f13 !important;
    border:2px dashed #6d28d9 !important;
    border-radius:12px;
    padding:1rem;
}
section[data-testid="stFileUploaderDropzone"]{
    background:#0f0f13 !important;
}
section[data-testid="stFileUploaderDropzone"] button{
    background:#161622 !important;
    color:white !important;
    border:1px solid #6d28d9 !important;
}
section[data-testid="stFileUploaderDropzone"] small{
    color:#c4b5fd !important;
}
.stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:1.5rem}
.stat{background:#1a1a24;border:1px solid #2a2a3a;border-radius:12px;padding:1.25rem;text-align:center}
.stat-v{font-size:2rem;font-weight:700;color:#a78bfa;font-family:'DM Mono',monospace}
.stat-l{font-size:.72rem;color:#94a3b8;text-transform:uppercase;letter-spacing:.08em;margin-top:.3rem}
.pill-match{display:inline-block;background:rgba(16,185,129,.15);color:#34d399;border:1px solid rgba(52,211,153,.3);border-radius:20px;padding:2px 9px;font-size:.72rem;font-weight:600;margin:2px}
.pill-miss{display:inline-block;background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(248,113,113,.25);border-radius:20px;padding:2px 9px;font-size:.72rem;font-weight:600;margin:2px}
.email-box{background:#13131d;border:1px solid #3730a3;border-left:3px solid #6366f1;border-radius:10px;padding:1.5rem;font-family:'DM Mono',monospace;font-size:.82rem;color:#c7d2fe;white-space:pre-wrap;line-height:1.7;margin-top:1rem}
.stCheckbox label {
    color: white !important;
    font-weight: 500 !important;
}
div[data-testid="stCheckbox"] label p {
    color: white !important;
    font-size: 15px !important;
}
.stButton>button{background:linear-gradient(135deg,#4f46e5,#7c3aed)!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important}
.stDownloadButton>button{background:#1a1a24!important;color:#a78bfa!important;border:1px solid #4f46e5!important;border-radius:8px!important}
hr{border-color:#2a2a38!important}
button[data-baseweb="tab"] {
    color: white !important;
    font-weight: 600 !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #ffffff !important;
}
[data-testid="stMetricLabel"] {
    color: white !important;
    font-weight: 600 !important;
}
[data-testid="stMetricValue"] {
    color: white !important;
    font-weight: 700 !important;
}
h1, h2, h3, h4, h5, h6 {
    color: white !important;
}
.stMarkdown,
.stMarkdown p,
.stText,
label {
    color: white !important;
}
</style>""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>💼 AI Recruitment Assistant</h1>
    <p>AI-powered resume screening, ranking and email generation</p>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.image(
        "Eidiko_logo.png",
        width=500
    )
    st.markdown("---")
    jd = st.text_area("📋 Job Description", height=260, placeholder="Paste JD here…")
tab1, tab2, tab3= st.tabs(["🔍 Screen Resumes", "🗄️ Candidate Database", "📋 Screening Report"])

with tab1:
    st.markdown('<div class="lbl">📂 Upload Resumes</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader("Drop PDF / DOCX resumes", type=["pdf","docx","txt"], accept_multiple_files=True, label_visibility="collapsed")
    if uploaded_files:
        os.makedirs("resumes", exist_ok=True)
        for f in uploaded_files:
            with open(os.path.join("resumes", f.name), "wb") as out:
                out.write(f.getbuffer())
        st.success(f"✅ {len(uploaded_files)} resume(s) uploaded")
        with st.expander("👁 Preview resume text"):
            for ufile in uploaded_files:
                st.markdown("**" + ufile.name + "**")
                resume_text = extract_resume_text(
                    os.path.join("resumes", ufile.name)
                )
                resume_embedding = model.encode(
                    resume_text
                ).tolist()
                st.write("Embedding length:", len(resume_embedding))
                print("Embedding generated:", len(resume_embedding))
                print(resume_embedding[:5])
                st.text_area(
                    "",
                    resume_text,
                    height=500
                )
        st.markdown("---")
        if st.button("🔍 Analyse Candidates", use_container_width=True):
            if not jd.strip():
                st.warning("⚠️ Add a Job Description in the sidebar first.")
                st.stop()
            with st.spinner("🤖 Extracting skills from Job Description…"):
                jd_skills = extract_jd_skills(jd)
            results, bar = [], st.progress(0, text="Analysing…")
            for i, f in enumerate(uploaded_files):
                result = recruitment_pipeline(
                    os.path.join("resumes", f.name),
                    jd
                )

                text = result["text"]
                score = result["score"]
                resume_skills = result["resume_skills"]

                matched = result["matched"]
                missing = result["missing"]

                candidate_name = result["candidate_name"]

                candidate_email = result["candidate_email"]
                resume_embedding = model.encode(
                    text
                ).tolist()
                save_embedding(
                    candidate_id=i + 1,
                    candidate_name=candidate_name,
                    candidate_email=candidate_email,
                    score=score,
                    embedding=resume_embedding
                )
                matched, missing = compute_skill_match(resume_skills, jd_skills)
                results.append({
                    "Candidate":      candidate_name,
                    "Email": candidate_email,
                    "File":           f.name,
                    "Score":          score,
                    "Status":         get_status(score),
                    "Matched Skills": ", ".join(sorted(matched)) or "—",
                    "Missing Skills": ", ".join(sorted(missing)) or "—",
                    "Embedding": resume_embedding
                })
                print("Embedding in results:", "Embedding" in results[-1])
                bar.progress((i+1)/len(uploaded_files), text=f"Processing {f.name}…")

            bar.empty()
            df = pd.DataFrame(results).sort_values("Score", ascending=False)
            df["Rank"] = range(1, len(df)+1)
            df = df[["Rank","Candidate","Email","File","Score","Status","Matched Skills","Missing Skills"]]
            st.session_state["df"]       = df
            st.session_state["analysed"] = True
            # Save to DB
            save_candidates(results)
    if st.session_state.get("analysed"):
        df  = st.session_state["df"]
        sim = len(df[df["Status"]=="Similar"])

        st.markdown(f"""<div class="stat-grid">
            <div class="stat"><div class="stat-v">{len(df)}</div><div class="stat-l">Total</div></div>
            <div class="stat"><div class="stat-v" style="color:#34d399">{sim}</div><div class="stat-l">Shortlisted</div></div>
            <div class="stat"><div class="stat-v" style="color:#f87171">{len(df)-sim}</div><div class="stat-l">Not Matching</div></div>
            <div class="stat"><div class="stat-v">{round(df["Score"].mean())}%</div><div class="stat-l">Avg Score</div></div>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div class="lbl">📊 Candidate Rankings</div>', unsafe_allow_html=True)

        for _, row in df.iterrows():
            c1, c2, c3, c4 = st.columns([.4, 2, 1.2, 2])
            c1.markdown(f"**#{row['Rank']}**")
            sc = "#34d399" if row["Status"]=="Similar" else "#f87171"
            c2.markdown(f"**{row['Candidate']}**<br><small style='color:#94a3b8'>{row['File']}</small>", unsafe_allow_html=True)
            c3.markdown(f"<span style='color:{sc};font-weight:700'>{row['Score']}%</span><br><span style='color:{sc};font-size:.8rem'>{row['Status']}</span>", unsafe_allow_html=True)
            mp = "".join(f'<span class="pill-match">✓ {s}</span>' for s in row["Matched Skills"].split(", ") if s!="—")
            xp = "".join(f'<span class="pill-miss">✗ {s}</span>'  for s in row["Missing Skills"].split(", ")  if s!="—")
            c4.markdown((mp or "<span style='color:#6b7280;font-size:.8rem'>no skill matches</span>") + " " + xp, unsafe_allow_html=True)
            st.markdown("<hr style='margin:4px 0;border-color:#1e1e2e'>", unsafe_allow_html=True)

        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(), "candidate_ranking.csv", "text/csv")
        st.markdown("---")
        st.markdown(
            '<div class="lbl">👩‍💼 HR Final Decision</div>',
            unsafe_allow_html=True
        )
        final_selection = {}
        for idx, row in df.iterrows():
            default_value = row["Status"] == "Similar"
            email = row["Email"] if row["Email"] else "Not Mentioned"
            final_selection[row["Candidate"]] = st.checkbox(
                f"{row['Candidate']} | {email} | {row['Score']}%",
                value=default_value,
                key=f"candidate_{idx}"
            )
        st.session_state["final_selection"] = final_selection
        selected_candidates = []
        rejected_candidates = []
        for _, row in df.iterrows():
            if final_selection[row["Candidate"]]:
                selected_candidates.append(row["Candidate"])
            else:
                rejected_candidates.append(row["Candidate"])
        col1, col2 = st.columns(2)
        with col1:
            st.success(
                f"✅ Final Shortlisted ({len(selected_candidates)})"
            )
            for candidate in selected_candidates:
                st.write(candidate)
        with col2:
            st.error(
                f"❌ Final Rejected ({len(rejected_candidates)})"
            )
            for candidate in rejected_candidates:
                st.write(candidate)
        if st.button(
            "🚀 Send Emails To All Candidates",
            use_container_width=True
        ):
            sent_count = 0
            for _, row in df.iterrows():
                candidate_name = row["Candidate"]
                candidate_email = row["Email"]
                if not candidate_email:
                    continue
                selected = final_selection[candidate_name]
                email_body = generate_email(
                    candidate_name,
                    "Similar" if selected else "Rejected"
                )
                success = send_email(
                    candidate_email,
                    "Application Update",
                    email_body
                )
                if success:
                    save_email(
                        candidate_name,candidate_email,
                        "Similar" if selected else "Rejected",
                        email_body
                    )
                    sent_count += 1
            st.success(
                f"✅ {sent_count} emails sent successfully."
            )
        st.markdown("---")
        st.markdown('<div class="lbl">✉️ Email Generator</div>', unsafe_allow_html=True)

        c1, c2 = st.columns([3,1])
        selected = c1.selectbox("Select Candidate", df["Candidate"].tolist(), label_visibility="collapsed")
        row      = df[df["Candidate"]==selected].iloc[0]
        sc       = "#34d399" if row["Status"]=="Similar" else "#f87171"
        st.markdown(f"**{selected}** &nbsp;|&nbsp; Score: `{row['Score']}%` &nbsp; <span style='color:{sc}'>{'✓ Shortlisted' if row['Status']=='Similar' else '✗ Not Matching'}</span>", unsafe_allow_html=True)
        if c2.button("Generate Email", use_container_width=True):
            with st.spinner("Generating email..."):
                st.session_state["email"] = generate_email(
                    selected,
                    row["Status"]
                )
                st.session_state["email_for"] = selected
                st.session_state["email_mode"] = "view"
                st.success("Email generated successfully!")

        if st.session_state.get("email") and st.session_state.get("email_for") == selected:
            email = st.session_state["email"]
            mode  = st.session_state.get("email_mode", "view")

            if mode == "view":
                st.markdown(f'<div class="email-box">{email}</div>', unsafe_allow_html=True)
            else:
                email = st.text_area("✏️ Edit Email", value=email, height=320, key="email_edit_area")
                st.session_state["email"] = email
        if st.session_state.get("email") and st.session_state.get("email_for") == selected:
            candidate_email = st.text_input(
                "Candidate Email Address",
                value=row["Email"]
            )
            edited_email = st.text_area(
                "Email Preview",
                value=st.session_state["email"],
                height=400
            )
            col1, col2 = st.columns(2)
            modify_clicked = col1.button(
                "✏️ Save Changes"
            )
            send_clicked = col2.button(
                "📧 Send Email"
            )
            if modify_clicked:
                st.session_state["email"] = edited_email
                st.success(
                    "Email updated successfully."
                )
            if send_clicked:
                if not candidate_email:
                    st.error(
                        "Please enter candidate email address."
                    )
                else:
                    success = send_email(
                        candidate_email,
                        "Application Update",
                        edited_email
                    )
                    if success:
                        st.success(
                            f"Email sent successfully to {candidate_email}"
                        )
                    else:
                        st.error(
                            "Failed to send email."
                        ) 
with tab2:
    st.markdown('<div class="lbl">🗄️ Candidate Database</div>', unsafe_allow_html=True)

    candidates = get_all_candidates()
    if candidates:
        cdf = pd.DataFrame(candidates, columns=[
            "Name","Email","File","Score","Status","Matched Skills","Missing Skills","Screened At"
        ])
        st.dataframe(cdf, use_container_width=True, hide_index=True)
        st.download_button("⬇️ Export Candidates DB", cdf.to_csv(index=False).encode(), "candidates_db.csv", "text/csv")
    else:
        st.info("No candidates in the database yet. Run a screening first.")

    st.markdown("---")
    st.markdown('<div class="lbl">📧 Sent Emails Log</div>', unsafe_allow_html=True)
    emails = get_all_emails()
    if emails:
        edf = pd.DataFrame(emails, columns=["Candidate","Email","Status","Email Body","Sent At"])
        for _, erow in edf.iterrows():
            with st.expander(f"📩 {erow['Candidate']} — {erow['Sent At']}"):
                st.markdown(f'<div class="email-box">{erow["Email Body"]}</div>', unsafe_allow_html=True)
    else:
        st.info("No emails logged yet.")

    st.markdown("---")
    if st.button("🗑️ Clear Database", type="secondary"):
        clear_db()
        st.success("Database cleared.")
        st.rerun()
with tab3:
    st.markdown('<div class="lbl">📋 Screening Report</div>', unsafe_allow_html=True)

    if st.session_state.get("analysed"):
        df     = st.session_state["df"]
        report = generate_screening_report(df, jd)
        st.text_area("Report Preview", report, height=500, label_visibility="collapsed")
        st.download_button("⬇️ Download Report (.txt)", report.encode(), "screening_report.txt", "text/plain")
    else:
       st.info("Run a screening in the **Screen Resumes** tab to generate a report.")

# with tab4:
#     st.markdown('<div class="lbl">🧠 Vector Database — Qdrant Embeddings</div>', unsafe_allow_html=True)
#     try:
#         points = get_all_vectors()
#     except Exception as e:
#         st.error(f"Could not connect to Qdrant: {e}")
#         points = []
#     m1, m2, m3 = st.columns(3)
#     m1.metric("📦 Total Embeddings Stored", len(points))
#     m2.metric("📐 Vector Dimension",        384)
#     m3.metric("🗄️ Database",               "Qdrant")
#     st.markdown("---")
#     if not points:
#         st.info("No embeddings found in Qdrant.")
#     else:
#         st.markdown('<div class="lbl">📊 Stored Candidates</div>', unsafe_allow_html=True)
#         rows = []
#         for p in points:
#             payload = p.payload or {}
#             rows.append({
#                 "Candidate":    payload.get("name",  "—"),
#                 "Email":        payload.get("email", "—"),
#                 "Score":        payload.get("score", "—"),
#                 "Vector Stored": "✅",
#             })
#         vdf = pd.DataFrame(rows)
#         st.dataframe(vdf, use_container_width=True, hide_index=True)
#         st.markdown("---")
#         st.markdown('<div class="lbl">🔬 Embedding Preview</div>', unsafe_allow_html=True)
#         for p in points:
#             payload   = p.payload or {}
#             name      = payload.get("name",  "Unknown")
#             email     = payload.get("email", "—")
#             score     = payload.get("score", "—")
#             vector    = list(p.vector) if p.vector is not None else []
#             dim       = len(vector)
#             preview   = [round(v, 3) for v in vector[:20]]
#             with st.expander(f"🧬 {name}"):
#                 ci1, ci2 = st.columns(2)
#                 ci1.markdown(f"**Candidate:** {name}")
#                 ci1.markdown(f"**Email:** {email}")
#                 ci2.markdown(f"**Score:** {score}%")
#                 ci2.markdown(f"**Embedding Dimension:** {dim}")
#                 st.markdown("**First 20 values:**")
#                 st.markdown(
#                     f'<div class="email-box">{preview}</div>',
#                     unsafe_allow_html=True
#                 )
'''
import streamlit as st
import os, re
import pandas as pd
from name_extractor import extract_candidate_name
from matcher import calculate_match_score
from utils import get_status
from resume_parser import extract_resume_text
from email_generator import generate_email
from email_sender import send_email
from database import save_candidates, save_email, get_all_candidates, get_all_emails, clear_db
from report_generator import generate_screening_report
from email_extractor import extract_candidate_email
from matcher import model
from qdrant_db import save_embedding, get_all_vectors
from skill_extractor import extract_jd_skills, extract_resume_skills, compute_skill_match
from langfuse import Langfuse
from pipeline import recruitment_pipeline

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_BASE_URL")
)
print("Langfuse initialized successfully")

from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Recruitment Assistant — Eidiko",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────────────────
# MASTER CSS  — Warm Earthy Enterprise Theme
# Palette: sage greens #B7C1B0 / #AFC6BE, warm tan #D7B37C, cream #F8F6F2,
#          navy text #232B4D, gold accent #D4A64A
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ═══════════════════════════════════════════════════════════════
   FONTS & RESET
═══════════════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', 'Poppins', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ═══════════════════════════════════════════════════════════════
   APP SHELL — warm cream background
═══════════════════════════════════════════════════════════════ */
.stApp {
    background: #EEF2EE !important;
    color: #232B4D !important;
    min-height: 100vh;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1400px !important;
}

/* ═══════════════════════════════════════════════════════════════
   SIDEBAR — deep navy
═══════════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #232B4D 0%, #1a2040 100%) !important;
    border-right: 1px solid rgba(212,166,74,0.25) !important;
    min-width: 300px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

.sb-header {
    background: linear-gradient(135deg, #2d3561, #232B4D);
    border-bottom: 1px solid rgba(212,166,74,0.3);
    padding: 28px 22px 22px;
    position: relative;
    overflow: hidden;
}
.sb-header::before {
    content: '';
    position: absolute;
    top: -30px; right: -30px;
    width: 120px; height: 120px;
    background: radial-gradient(circle, rgba(212,166,74,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.sb-logo-area {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}
.sb-icon {
    width: 42px; height: 42px;
    background: linear-gradient(135deg, #D4A64A, #e8c06a);
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2rem;
    flex-shrink: 0;
    box-shadow: 0 4px 15px rgba(212,166,74,0.4);
}
.sb-title {
    font-size: 1rem !important;
    font-weight: 800 !important;
    color: #F8F6F2 !important;
    letter-spacing: -0.02em;
    line-height: 1.1;
    font-family: 'Poppins', sans-serif !important;
}
.sb-sub {
    font-size: 0.67rem !important;
    color: #8fa0b5 !important;
    font-weight: 500 !important;
    margin-top: 2px !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}
.sb-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(76,175,80,0.15);
    border: 1px solid rgba(76,175,80,0.35);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.67rem;
    font-weight: 600;
    color: #7de07f;
    letter-spacing: 0.05em;
}
.sb-status-dot {
    width: 6px; height: 6px;
    background: #7de07f;
    border-radius: 50%;
    animation: blink 1.8s ease-in-out infinite;
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.sb-section-title {
    font-size: 0.64rem !important;
    font-weight: 700 !important;
    color: #8fa0b5 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.13em !important;
    padding: 20px 22px 8px !important;
}

[data-testid="stSidebar"] .stTextArea > label {
    font-size: 0.75rem !important;
    font-weight: 700 !important;
    color: #8fa0b5 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stSidebar"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(212,166,74,0.2) !important;
    border-radius: 12px !important;
    color: #F8F6F2 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.82rem !important;
    line-height: 1.65 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stSidebar"] textarea:focus {
    border-color: #D4A64A !important;
    box-shadow: 0 0 0 3px rgba(212,166,74,0.15) !important;
    outline: none !important;
}
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stMarkdown p {
    color: #8fa0b5 !important;
    font-size: 0.82rem !important;
}

/* ═══════════════════════════════════════════════════════════════
   HERO BANNER
═══════════════════════════════════════════════════════════════ */
.enterprise-hero {
    position: relative;
    border-radius: 20px;
    overflow: hidden;
    margin-bottom: 28px;
    min-height: 260px;
    background: linear-gradient(135deg, #B7C1B0 0%, #AFC6BE 40%, #c9b88a 100%);
    box-shadow: 0 8px 40px rgba(35,43,77,0.12);
}
.hero-bg-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(
        135deg,
        rgba(35,43,77,0.78) 0%,
        rgba(35,43,77,0.55) 45%,
        rgba(175,198,190,0.15) 100%
    );
}
.hero-sparkle {
    position: absolute;
    inset: 0;
    background-image:
        radial-gradient(circle 1.5px at 15% 20%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(circle 1px at 85% 15%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(circle 2px at 60% 75%, rgba(255,255,255,0.35) 0%, transparent 100%),
        radial-gradient(circle 1px at 30% 80%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(circle 1.5px at 90% 55%, rgba(255,255,255,0.4) 0%, transparent 100%);
}
.hero-content {
    position: relative;
    z-index: 2;
    padding: 44px 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 32px;
    min-height: 260px;
}
.hero-left { flex: 1; min-width: 0; }
.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(212,166,74,0.2);
    border: 1px solid rgba(212,166,74,0.5);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.69rem;
    font-weight: 700;
    color: #f5d78e;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 16px;
}
.hero-headline {
    font-size: 2.3rem !important;
    font-weight: 900 !important;
    color: #F8F6F2 !important;
    line-height: 1.1 !important;
    letter-spacing: -0.03em !important;
    margin-bottom: 14px !important;
    font-family: 'Poppins', sans-serif !important;
}
.hero-headline span {
    background: linear-gradient(135deg, #D4A64A, #f0ca7a, #D4A64A);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.hero-subline {
    font-size: 0.92rem !important;
    color: rgba(248,246,242,0.82) !important;
    line-height: 1.7 !important;
    max-width: 520px !important;
    font-weight: 400 !important;
}
.hero-actions {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 24px;
    flex-wrap: wrap;
}
.hero-btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: linear-gradient(135deg, #D4A64A, #c49235);
    color: #fff;
    font-size: 0.82rem;
    font-weight: 700;
    padding: 10px 22px;
    border-radius: 10px;
    border: none;
    cursor: pointer;
    box-shadow: 0 4px 20px rgba(212,166,74,0.45);
    letter-spacing: 0.02em;
    text-decoration: none;
    font-family: 'Poppins', sans-serif;
}
.hero-btn-secondary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(248,246,242,0.12);
    color: #F8F6F2;
    font-size: 0.82rem;
    font-weight: 600;
    padding: 10px 22px;
    border-radius: 10px;
    border: 1px solid rgba(248,246,242,0.25);
    cursor: pointer;
    letter-spacing: 0.02em;
    text-decoration: none;
    backdrop-filter: blur(8px);
}
.hero-right {
    display: flex;
    flex-direction: column;
    gap: 12px;
    flex-shrink: 0;
}
.hero-stat-card {
    background: rgba(248,246,242,0.15);
    border: 1px solid rgba(248,246,242,0.25);
    border-radius: 14px;
    padding: 16px 22px;
    text-align: center;
    backdrop-filter: blur(16px);
    min-width: 140px;
    position: relative;
    overflow: hidden;
}
.hero-stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #D4A64A, #f0ca7a);
}
.hero-stat-num {
    font-size: 1.8rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    line-height: 1;
    margin-bottom: 4px;
    font-family: 'Poppins', sans-serif;
}
.hero-stat-lbl {
    font-size: 0.65rem;
    font-weight: 600;
    color: rgba(248,246,242,0.65);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

/* ═══════════════════════════════════════════════════════════════
   FEATURE CARDS
═══════════════════════════════════════════════════════════════ */
.feature-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 32px;
}
.feature-card {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 16px;
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    cursor: default;
    box-shadow: 0 2px 12px rgba(35,43,77,0.06);
    transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
}
.feature-card:hover {
    transform: translateY(-4px);
    border-color: #D4A64A;
    box-shadow: 0 14px 40px rgba(35,43,77,0.12);
}
.feature-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent, linear-gradient(90deg, #D4A64A, #e8c06a));
    opacity: 0;
    transition: opacity 0.25s;
}
.feature-card:hover::after { opacity: 1; }
.feature-icon-wrap {
    width: 50px; height: 50px;
    border-radius: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    margin-bottom: 14px;
}
.fc-gold   .feature-icon-wrap { background: rgba(212,166,74,0.12); }
.fc-sage   .feature-icon-wrap { background: rgba(175,198,190,0.2); }
.fc-green  .feature-icon-wrap { background: rgba(76,175,80,0.1); }
.fc-navy   .feature-icon-wrap { background: rgba(35,43,77,0.08); }
.fc-gold   { --accent: linear-gradient(90deg, #D4A64A, #e8c06a); }
.fc-sage   { --accent: linear-gradient(90deg, #AFC6BE, #B7C1B0); }
.fc-green  { --accent: linear-gradient(90deg, #4CAF50, #81C784); }
.fc-navy   { --accent: linear-gradient(90deg, #232B4D, #3d4d8a); }
.feature-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #232B4D;
    margin-bottom: 6px;
    font-family: 'Poppins', sans-serif;
}
.feature-desc {
    font-size: 0.78rem;
    color: #6B7280;
    line-height: 1.55;
}

/* ═══════════════════════════════════════════════════════════════
   ANALYTICS DASHBOARD
═══════════════════════════════════════════════════════════════ */
.analytics-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}
.analytics-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #232B4D;
    letter-spacing: -0.02em;
    font-family: 'Poppins', sans-serif;
}
.analytics-subtitle {
    font-size: 0.74rem;
    color: #6B7280;
    margin-top: 2px;
}
.live-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(76,175,80,0.1);
    border: 1px solid rgba(76,175,80,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.64rem;
    font-weight: 700;
    color: #4CAF50;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.live-dot {
    width: 5px; height: 5px;
    background: #4CAF50;
    border-radius: 50%;
    animation: blink 1.5s infinite;
}

.analytics-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 32px;
}
.analytics-card {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 16px;
    padding: 22px 18px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(35,43,77,0.06);
    transition: transform 0.2s, box-shadow 0.2s;
}
.analytics-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(35,43,77,0.1);
}
.ac-icon { font-size: 1.3rem; margin-bottom: 12px; display: block; }
.ac-value {
    font-size: 1.9rem;
    font-weight: 900;
    letter-spacing: -0.04em;
    line-height: 1;
    margin-bottom: 5px;
    font-family: 'Poppins', sans-serif;
}
.ac-label {
    font-size: 0.67rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.ac-trend {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 0.65rem;
    font-weight: 600;
    margin-top: 8px;
    padding: 2px 7px;
    border-radius: 10px;
}
.ac-top-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 16px 16px 0 0;
}

/* ═══════════════════════════════════════════════════════════════
   SECTION DIVIDER
═══════════════════════════════════════════════════════════════ */
.section-divider {
    display: flex;
    align-items: center;
    gap: 14px;
    margin: 28px 0 18px;
}
.sd-label {
    font-size: 0.7rem;
    font-weight: 800;
    color: #D4A64A;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    white-space: nowrap;
    font-family: 'Poppins', sans-serif;
}
.sd-line {
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(212,166,74,0.4), transparent);
}

/* ═══════════════════════════════════════════════════════════════
   TABS — pill-style
═══════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: #F8F6F2 !important;
    border: 1px solid #D8D8D8 !important;
    border-radius: 14px !important;
    gap: 4px !important;
    padding: 5px !important;
    margin-bottom: 4px !important;
}
button[data-baseweb="tab"] {
    background: transparent !important;
    color: #6B7280 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    border-radius: 10px !important;
    padding: 9px 20px !important;
    border: none !important;
    transition: color 0.2s, background 0.2s !important;
    font-family: 'Inter', sans-serif !important;
}
button[data-baseweb="tab"]:hover {
    color: #232B4D !important;
    background: rgba(35,43,77,0.06) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #F8F6F2 !important;
    background: linear-gradient(135deg, #232B4D, #3a4580) !important;
    box-shadow: 0 3px 12px rgba(35,43,77,0.25) !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 24px !important;
}

/* ═══════════════════════════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: rgba(248,246,242,0.8) !important;
    border: 2px dashed rgba(212,166,74,0.4) !important;
    border-radius: 16px !important;
    transition: border-color 0.25s, background 0.25s !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #D4A64A !important;
    background: rgba(212,166,74,0.04) !important;
}
section[data-testid="stFileUploaderDropzone"] {
    background: transparent !important;
    padding: 8px !important;
}
section[data-testid="stFileUploaderDropzone"] button {
    background: rgba(212,166,74,0.12) !important;
    color: #c49235 !important;
    border: 1px solid rgba(212,166,74,0.35) !important;
    border-radius: 10px !important;
}
section[data-testid="stFileUploaderDropzone"] small {
    color: #6B7280 !important;
}

/* ═══════════════════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════════════════ */
.stButton > button {
    background: linear-gradient(135deg, #232B4D, #3a4580) !important;
    color: #F8F6F2 !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: 0 3px 14px rgba(35,43,77,0.25) !important;
    transition: transform 0.15s, box-shadow 0.15s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(35,43,77,0.3) !important;
}
.stDownloadButton > button {
    background: #F8F6F2 !important;
    color: #232B4D !important;
    border: 1px solid #D8D8D8 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover {
    border-color: #D4A64A !important;
    background: rgba(212,166,74,0.06) !important;
    box-shadow: none !important;
}

/* ═══════════════════════════════════════════════════════════════
   INPUTS
═══════════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #F8F6F2 !important;
    border: 1px solid #D8D8D8 !important;
    border-radius: 10px !important;
    color: #232B4D !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.85rem !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #D4A64A !important;
    box-shadow: 0 0 0 3px rgba(212,166,74,0.15) !important;
}
.stTextInput > label,
.stTextArea > label {
    color: #6B7280 !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════════════════
   SELECTBOX
═══════════════════════════════════════════════════════════════ */
.stSelectbox > div > div {
    background: #F8F6F2 !important;
    border: 1px solid #D8D8D8 !important;
    border-radius: 10px !important;
    color: #232B4D !important;
}
.stSelectbox label { color: #6B7280 !important; font-size: 0.78rem !important; font-weight: 600 !important; }

/* ═══════════════════════════════════════════════════════════════
   CHECKBOXES
═══════════════════════════════════════════════════════════════ */
.stCheckbox label,
div[data-testid="stCheckbox"] label p {
    color: #232B4D !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ═══════════════════════════════════════════════════════════════
   CANDIDATE PROFILE CARD
═══════════════════════════════════════════════════════════════ */
.candidate-profile-card {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 18px;
    padding: 0;
    margin-bottom: 14px;
    overflow: hidden;
    box-shadow: 0 2px 14px rgba(35,43,77,0.07);
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.25s;
    position: relative;
}
.candidate-profile-card:hover {
    border-color: #D4A64A;
    box-shadow: 0 10px 36px rgba(35,43,77,0.12);
    transform: translateY(-1px);
}
.cpc-accent-bar { height: 4px; width: 100%; }
.cpc-accent-shortlisted { background: linear-gradient(90deg, #4CAF50, #81C784); }
.cpc-accent-rejected    { background: linear-gradient(90deg, #E57373, #EF9A9A); }
.cpc-body {
    display: grid;
    grid-template-columns: 60px 1fr 140px 1fr 100px;
    align-items: center;
    gap: 20px;
    padding: 20px 24px;
}
.cpc-rank {
    width: 52px; height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
    flex-shrink: 0;
    font-family: 'Poppins', sans-serif;
}
.rank-1 { background: linear-gradient(135deg,#D4A64A,#f0ca7a); color: #fff; box-shadow: 0 4px 15px rgba(212,166,74,0.45); }
.rank-2 { background: linear-gradient(135deg,#B7C1B0,#d4dbd2); color: #232B4D; box-shadow: 0 4px 12px rgba(183,193,176,0.4); }
.rank-3 { background: linear-gradient(135deg,#AFC6BE,#c8dcd7); color: #232B4D; box-shadow: 0 4px 12px rgba(175,198,190,0.4); }
.rank-n { background: rgba(107,114,128,0.1); color: #6B7280; border: 1px solid rgba(107,114,128,0.2); }
.cpc-info { min-width: 0; }
.cpc-name {
    font-size: 0.97rem;
    font-weight: 700;
    color: #232B4D;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 4px;
    font-family: 'Poppins', sans-serif;
}
.cpc-email {
    font-size: 0.72rem;
    color: #D4A64A;
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 3px;
}
.cpc-file {
    font-size: 0.68rem;
    color: #6B7280;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.cpc-score-wrap { text-align: center; }
.cpc-score-circle {
    width: 72px; height: 72px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    margin: 0 auto 6px;
}
.cpc-score-num {
    font-size: 1.2rem;
    font-weight: 900;
    line-height: 1;
    font-family: 'Poppins', sans-serif;
}
.cpc-score-pct { font-size: 0.6rem; color: #6B7280; font-weight: 600; }
.score-high .cpc-score-circle { background: rgba(76,175,80,0.1);   border: 2px solid rgba(76,175,80,0.4); }
.score-mid  .cpc-score-circle { background: rgba(212,166,74,0.1);  border: 2px solid rgba(212,166,74,0.4); }
.score-low  .cpc-score-circle { background: rgba(229,115,115,0.1); border: 2px solid rgba(229,115,115,0.4); }
.score-high .cpc-score-num { color: #4CAF50; }
.score-mid  .cpc-score-num { color: #D4A64A; }
.score-low  .cpc-score-num { color: #E57373; }
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 3px 10px;
    border-radius: 20px;
}
.badge-shortlisted { background: rgba(76,175,80,0.1);   color: #4CAF50; border: 1px solid rgba(76,175,80,0.3); }
.badge-rejected    { background: rgba(229,115,115,0.1); color: #E57373; border: 1px solid rgba(229,115,115,0.3); }
.cpc-skills { min-width: 0; }
.skills-row-label {
    font-size: 0.6rem;
    font-weight: 700;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 5px;
}
.skill-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 20px;
    font-size: 0.67rem;
    font-weight: 600;
    margin: 2px 3px 2px 0;
    line-height: 1;
}
.pill-match { background: rgba(76,175,80,0.1);   color: #4CAF50; border: 1px solid rgba(76,175,80,0.25); }
.pill-miss  { background: rgba(229,115,115,0.08); color: #E57373; border: 1px solid rgba(229,115,115,0.2); }
.pill-none  { color: #6B7280; font-style: italic; font-size: 0.72rem; }
.cpc-actions { display: flex; flex-direction: column; gap: 7px; align-items: flex-end; }
.action-tag {
    font-size: 0.65rem;
    font-weight: 600;
    color: #6B7280;
    padding: 4px 10px;
    background: rgba(35,43,77,0.05);
    border: 1px solid rgba(35,43,77,0.12);
    border-radius: 8px;
    white-space: nowrap;
}

/* ═══════════════════════════════════════════════════════════════
   HR DECISION SECTION
═══════════════════════════════════════════════════════════════ */
.decision-panel {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 16px;
    overflow: hidden;
    margin-bottom: 10px;
    box-shadow: 0 2px 12px rgba(35,43,77,0.06);
}
.decision-panel-header {
    background: linear-gradient(90deg, rgba(35,43,77,0.05), rgba(212,166,74,0.06));
    border-bottom: 1px solid #D8D8D8;
    padding: 12px 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.dph-title {
    font-size: 0.72rem;
    font-weight: 700;
    color: #232B4D;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-family: 'Poppins', sans-serif;
}
.decision-row {
    display: flex;
    align-items: center;
    padding: 12px 20px;
    border-bottom: 1px solid rgba(216,216,216,0.6);
    gap: 14px;
    transition: background 0.15s;
}
.decision-row:last-child { border-bottom: none; }
.decision-row:hover { background: rgba(212,166,74,0.04); }
.dr-name {
    font-size: 0.88rem;
    font-weight: 600;
    color: #232B4D;
    flex: 1;
    min-width: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.dr-email { font-size: 0.72rem; color: #6B7280; }
.dr-score {
    font-size: 0.88rem;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 8px;
    white-space: nowrap;
    font-family: 'Poppins', sans-serif;
}

/* ═══════════════════════════════════════════════════════════════
   EMAIL COMPOSER
═══════════════════════════════════════════════════════════════ */
.email-composer {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 16px;
    overflow: hidden;
    margin-top: 16px;
    box-shadow: 0 2px 12px rgba(35,43,77,0.06);
}
.ec-header {
    background: #EEF2EE;
    border-bottom: 1px solid #D8D8D8;
    padding: 12px 18px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.ec-dot { width: 10px; height: 10px; border-radius: 50%; }
.ec-filename {
    font-size: 0.7rem;
    color: #6B7280;
    margin-left: 6px;
}
.ec-body {
    padding: 22px 24px;
    font-family: 'Inter', sans-serif;
    font-size: 0.84rem;
    color: #374151;
    line-height: 1.8;
    white-space: pre-wrap;
}

/* ═══════════════════════════════════════════════════════════════
   DATABASE TAB
═══════════════════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid #D8D8D8 !important;
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 12px rgba(35,43,77,0.06) !important;
}
[data-testid="stDataFrame"] th {
    background: #EEF2EE !important;
    color: #232B4D !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
}
[data-testid="stDataFrame"] td {
    color: #374151 !important;
    font-size: 0.82rem !important;
    background: #F8F6F2 !important;
}

/* ═══════════════════════════════════════════════════════════════
   REPORT TAB
═══════════════════════════════════════════════════════════════ */
.report-summary-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}
.report-card {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 14px;
    padding: 20px 22px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(35,43,77,0.06);
}
.rc-top { position: absolute; top: 0; left: 0; right: 0; height: 3px; }
.rc-num {
    font-size: 1.8rem;
    font-weight: 900;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
    font-family: 'Poppins', sans-serif;
}
.rc-label {
    font-size: 0.67rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
.report-preview-container {
    background: #F8F6F2;
    border: 1px solid #D8D8D8;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(35,43,77,0.06);
}
.rpc-header {
    background: #EEF2EE;
    border-bottom: 1px solid #D8D8D8;
    padding: 14px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.rpc-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #232B4D;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-family: 'Poppins', sans-serif;
}
.rpc-body {
    padding: 24px 26px;
    font-family: 'Inter', monospace;
    font-size: 0.75rem;
    color: #374151;
    white-space: pre;
    overflow-x: auto;
    max-height: 480px;
    overflow-y: auto;
    line-height: 1.75;
}
.rpc-body::-webkit-scrollbar { width: 6px; height: 6px; }
.rpc-body::-webkit-scrollbar-track { background: #EEF2EE; }
.rpc-body::-webkit-scrollbar-thumb { background: rgba(212,166,74,0.35); border-radius: 3px; }

/* ═══════════════════════════════════════════════════════════════
   EMPTY STATE
═══════════════════════════════════════════════════════════════ */
.empty-state {
    text-align: center;
    padding: 60px 40px;
    background: rgba(248,246,242,0.7);
    border: 1.5px dashed rgba(212,166,74,0.35);
    border-radius: 20px;
}
.empty-icon { font-size: 3rem; margin-bottom: 16px; display: block; }
.empty-title {
    font-size: 1rem;
    font-weight: 700;
    color: #232B4D;
    margin-bottom: 8px;
    font-family: 'Poppins', sans-serif;
}
.empty-desc { font-size: 0.83rem; color: #6B7280; line-height: 1.6; }

/* ═══════════════════════════════════════════════════════════════
   SUCCESS / ERROR / INFO OVERRIDES
═══════════════════════════════════════════════════════════════ */
.stSuccess { border-radius: 12px !important; background: rgba(76,175,80,0.08)  !important; border: 1px solid rgba(76,175,80,0.3)   !important; }
.stError   { border-radius: 12px !important; background: rgba(229,115,115,0.08)!important; border: 1px solid rgba(229,115,115,0.3) !important; }
.stWarning { border-radius: 12px !important; background: rgba(212,166,74,0.08) !important; border: 1px solid rgba(212,166,74,0.3)  !important; }
.stInfo    { border-radius: 12px !important; background: rgba(175,198,190,0.1) !important; border: 1px solid rgba(175,198,190,0.35)!important; }

/* ═══════════════════════════════════════════════════════════════
   TYPOGRAPHY & MISC
═══════════════════════════════════════════════════════════════ */
hr { border: none !important; border-top: 1px solid #D8D8D8 !important; margin: 24px 0 !important; }
h1,h2,h3,h4,h5,h6 { color: #232B4D !important; font-family: 'Poppins', sans-serif !important; }
.stMarkdown p, .stText { color: #374151 !important; }
[data-testid="stMetricLabel"] { color: #6B7280 !important; font-weight: 600 !important; }
[data-testid="stMetricValue"] { color: #232B4D !important; font-weight: 700 !important; }
details {
    background: #F8F6F2 !important;
    border: 1px solid #D8D8D8 !important;
    border-radius: 12px !important;
}
summary { color: #374151 !important; font-weight: 600 !important; font-size: 0.85rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sb-header">
        <div class="sb-logo-area">
            <div class="sb-icon">🎯</div>
            <div>
                <div class="sb-title">AI Recruitment Assistant</div>
                <div class="sb-sub">Eidiko Systems Integrators</div>
            </div>
        </div>
        <div class="sb-status-pill">
            <span class="sb-status-dot"></span>
            AI Engine Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        st.image("Eidiko_logo.png", use_container_width=True)
    except Exception:
        pass

    st.markdown('<div class="sb-section-title">Job Description</div>', unsafe_allow_html=True)
    jd = st.text_area(
        "Paste the full job description",
        height=290,
        placeholder="e.g. We are looking for a Python Developer with 2+ years of experience in FastAPI, PostgreSQL, and machine learning pipelines...\n\nRequired Skills:\n- Python, FastAPI\n- PostgreSQL, Redis\n- Scikit-learn, Transformers",
        label_visibility="collapsed"
    )

    if jd.strip():
        wc = len(jd.split())
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-top:8px;padding:8px 12px;background:rgba(212,166,74,0.08);
                    border-radius:8px;border:1px solid rgba(212,166,74,0.25)">
            <span style="font-size:0.68rem;color:#6B7280;font-weight:600">📝 Job Description</span>
            <span style="font-size:0.68rem;font-weight:700;color:#D4A64A">{wc} words</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="padding:0 4px">
        <div style="font-size:0.64rem;font-weight:700;color:#8fa0b5;
                    text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px">
            Platform Capabilities
        </div>
        <div style="display:flex;flex-direction:column;gap:8px">
            <div style="display:flex;align-items:center;gap:8px;font-size:0.74rem;color:#b0bdcc">
                <span style="color:#f5d78e">⚡</span> Semantic Similarity Scoring
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.74rem;color:#b0bdcc">
                <span style="color:#90ccc8">🧠</span> Groq LLaMA 3 · Skill Extraction
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.74rem;color:#b0bdcc">
                <span style="color:#7de07f">🗄️</span> PostgreSQL · Qdrant Vector DB
            </div>
            <div style="display:flex;align-items:center;gap:8px;font-size:0.74rem;color:#b0bdcc">
                <span style="color:#f5d78e">📊</span> Langfuse Observability
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────
_all_cands  = get_all_candidates()
_all_emails = get_all_emails()
_total_cands     = len(_all_cands)
_shortlisted     = len([c for c in _all_cands if len(c) > 4 and c[4] == "Similar"]) if _all_cands else 0
_emails_sent     = len(_all_emails)
_ai_accuracy     = "94.2%"

st.markdown(f"""
<div class="enterprise-hero">
    <div class="hero-bg-overlay"></div>
    <div class="hero-sparkle"></div>
    <div class="hero-content">
        <div class="hero-left">
            <div class="hero-eyebrow">
                ✦ &nbsp;Powered by Generative AI &amp; Semantic Matching
            </div>
            <div class="hero-headline">
                AI-Powered Recruitment<br>
                <span>Intelligence Platform</span>
            </div>
            <div class="hero-subline">
                Automate resume screening, identify top talent, and accelerate hiring decisions
                using Generative AI and Semantic Matching —
                built for enterprise teams at Eidiko Systems Integrators.
            </div>
            <div class="hero-actions">
                <span class="hero-btn-primary">🚀 &nbsp;Start Screening</span>
                <span class="hero-btn-secondary">📊 &nbsp;View Analytics</span>
            </div>
        </div>
        <div class="hero-right">
            <div class="hero-stat-card">
                <div class="hero-stat-num" style="color:#f5d78e">{_total_cands:,}</div>
                <div class="hero-stat-lbl">Candidates Processed</div>
            </div>
            <div class="hero-stat-card">
                <div class="hero-stat-num" style="color:#90ccc8">{_shortlisted:,}</div>
                <div class="hero-stat-lbl">Shortlisted</div>
            </div>
            <div class="hero-stat-card">
                <div class="hero-stat-num" style="color:#f5d78e">{_emails_sent:,}</div>
                <div class="hero-stat-lbl">Emails Sent</div>
            </div>
            <div class="hero-stat-card">
                <div class="hero-stat-num" style="color:#B7C1B0">{_ai_accuracy}</div>
                <div class="hero-stat-lbl">AI Accuracy</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FEATURE CARDS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="feature-grid">
    <div class="feature-card fc-gold">
        <div class="feature-icon-wrap">🤖</div>
        <div class="feature-title">AI Resume Screening</div>
        <div class="feature-desc">Semantic similarity-based ranking using all-MiniLM-L6-v2 embeddings and cosine distance scoring.</div>
    </div>
    <div class="feature-card fc-sage">
        <div class="feature-icon-wrap">🧠</div>
        <div class="feature-title">Skill Intelligence</div>
        <div class="feature-desc">AI-extracted matched and missing skills per candidate powered by Groq LLaMA 3 for precise gap analysis.</div>
    </div>
    <div class="feature-card fc-green">
        <div class="feature-icon-wrap">📧</div>
        <div class="feature-title">Automated Outreach</div>
        <div class="feature-desc">AI-generated personalised emails for shortlisted and rejected candidates with one-click delivery.</div>
    </div>
    <div class="feature-card fc-navy">
        <div class="feature-icon-wrap">📊</div>
        <div class="feature-title">Recruitment Analytics</div>
        <div class="feature-desc">Real-time hiring insights, scoring distributions, and comprehensive reports exportable as CSV and TXT.</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# ANALYTICS DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
_df_live     = st.session_state.get("df", pd.DataFrame())
_has_results = st.session_state.get("analysed", False)

_total_s   = len(_df_live) if _has_results else _total_cands
_short_s   = len(_df_live[_df_live["Status"] == "Similar"]) if _has_results and len(_df_live) else _shortlisted
_reject_s  = (_total_s - _short_s)
_avg_score = round(_df_live["Score"].mean(), 1) if _has_results and len(_df_live) else 0
_top_score = int(_df_live["Score"].max()) if _has_results and len(_df_live) else 0

st.markdown("""
<div class="analytics-header">
    <div>
        <div class="analytics-title">Recruitment Analytics</div>
        <div class="analytics-subtitle">Live metrics from current screening session</div>
    </div>
    <div class="live-badge"><span class="live-dot"></span>Live</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="analytics-grid">
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#232B4D,#3a4580)"></div>
        <span class="ac-icon">📄</span>
        <div class="ac-value" style="color:#232B4D">{_total_s}</div>
        <div class="ac-label">Total Screened</div>
        <div class="ac-trend" style="background:rgba(35,43,77,0.07);color:#232B4D">📂 This session</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#4CAF50,#81C784)"></div>
        <span class="ac-icon">✅</span>
        <div class="ac-value" style="color:#4CAF50">{_short_s}</div>
        <div class="ac-label">Shortlisted</div>
        <div class="ac-trend" style="background:rgba(76,175,80,0.1);color:#4CAF50">↑ Qualified</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#E57373,#EF9A9A)"></div>
        <span class="ac-icon">❌</span>
        <div class="ac-value" style="color:#E57373">{_reject_s}</div>
        <div class="ac-label">Not Matching</div>
        <div class="ac-trend" style="background:rgba(229,115,115,0.08);color:#E57373">↓ Below threshold</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#D4A64A,#e8c06a)"></div>
        <span class="ac-icon">📊</span>
        <div class="ac-value" style="color:#D4A64A">{_avg_score}%</div>
        <div class="ac-label">Avg Match Score</div>
        <div class="ac-trend" style="background:rgba(212,166,74,0.1);color:#D4A64A">◈ Semantic</div>
    </div>
    <div class="analytics-card">
        <div class="ac-top-bar" style="background:linear-gradient(90deg,#AFC6BE,#B7C1B0)"></div>
        <span class="ac-icon">🏆</span>
        <div class="ac-value" style="color:#5a8a7e">{_top_score}%</div>
        <div class="ac-label">Top Score</div>
        <div class="ac-trend" style="background:rgba(175,198,190,0.15);color:#5a8a7e">★ Best candidate</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs([
    "  🔍  Resume Screening  ",
    "  🗄️  Candidate Database  ",
    "  📋  Screening Reports  "
])


# ════════════════════════════════════════════════════════════════════════════
#  TAB 1 — RESUME SCREENING
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── Upload section ────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">📂 Upload Resumes</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    upload_col, info_col = st.columns([3, 1])
    with upload_col:
        uploaded_files = st.file_uploader(
            "Drag & drop PDF, DOCX, or TXT resumes here — or click Browse",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            label_visibility="visible"
        )

    with info_col:
        st.markdown("""
        <div style="background:#F8F6F2;border:1px solid #D8D8D8;
                    border-radius:14px;padding:18px 16px;height:100%;
                    box-shadow:0 2px 10px rgba(35,43,77,0.06)">
            <div style="font-size:0.64rem;font-weight:700;color:#6B7280;
                        text-transform:uppercase;letter-spacing:0.12em;margin-bottom:12px">
                Supported Formats
            </div>
            <div style="display:flex;flex-direction:column;gap:8px">
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:#374151">
                    <span style="color:#E57373;font-size:1rem">📕</span> PDF Documents
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:#374151">
                    <span style="color:#4a7ab5;font-size:1rem">📘</span> Word (.docx)
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:#374151">
                    <span style="color:#6B7280;font-size:1rem">📄</span> Plain Text
                </div>
                <div style="display:flex;align-items:center;gap:8px;font-size:0.78rem;color:#6B7280">
                    <span style="color:#4CAF50;font-size:1rem">✓</span> No size limit
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if uploaded_files:
        os.makedirs("resumes", exist_ok=True)
        for f in uploaded_files:
            with open(os.path.join("resumes", f.name), "wb") as out:
                out.write(f.getbuffer())

        st.success(f"✅  {len(uploaded_files)} resume(s) uploaded and ready for analysis")

        with st.expander(f"👁  Preview extracted resume text  ({len(uploaded_files)} files)"):
            for ufile in uploaded_files:
                st.markdown(f"""
                <div style="padding:8px 0;border-bottom:1px solid #D8D8D8;
                            margin-bottom:10px;display:flex;align-items:center;gap:10px">
                    <span style="font-size:0.9rem">📄</span>
                    <span style="font-size:0.85rem;font-weight:700;color:#232B4D">{ufile.name}</span>
                </div>
                """, unsafe_allow_html=True)
                resume_text = extract_resume_text(os.path.join("resumes", ufile.name))
                resume_embedding = model.encode(resume_text).tolist()
                st.markdown(
                    f'<span style="font-size:0.7rem;color:#6B7280">'
                    f'Embedding dim: {len(resume_embedding)} · Model: all-MiniLM-L6-v2</span>',
                    unsafe_allow_html=True
                )
                st.text_area("", resume_text, height=260, key=f"preview_{ufile.name}")

        st.markdown("---")

        if not jd.strip():
            st.markdown("""
            <div style="background:rgba(212,166,74,0.08);border:1px solid rgba(212,166,74,0.35);
                        border-radius:12px;padding:14px 18px;display:flex;align-items:center;gap:12px">
                <span style="font-size:1.2rem">⚠️</span>
                <span style="font-size:0.85rem;color:#c49235;font-weight:500">
                    Please paste a Job Description in the sidebar before starting analysis.
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("🔍  Analyse All Candidates", use_container_width=True):
                with st.spinner("🤖  Extracting required skills from Job Description…"):
                    jd_skills = extract_jd_skills(jd)

                results = []
                progress_bar = st.progress(0, text="Initialising AI pipeline…")

                for i, f in enumerate(uploaded_files):
                    progress_bar.progress(
                        i / len(uploaded_files),
                        text=f"🔄  Analysing {f.name}  ({i+1}/{len(uploaded_files)})"
                    )
                    result = recruitment_pipeline(os.path.join("resumes", f.name), jd)

                    text            = result["text"]
                    score           = result["score"]
                    resume_skills   = result["resume_skills"]
                    matched         = result["matched"]
                    missing         = result["missing"]
                    candidate_name  = result["candidate_name"]
                    candidate_email = result["candidate_email"]

                    resume_embedding = model.encode(text).tolist()
                    save_embedding(
                        candidate_id=i + 1,
                        candidate_name=candidate_name,
                        candidate_email=candidate_email,
                        score=score,
                        embedding=resume_embedding
                    )
                    matched, missing = compute_skill_match(resume_skills, jd_skills)
                    results.append({
                        "Candidate":      candidate_name,
                        "Email":          candidate_email,
                        "File":           f.name,
                        "Score":          score,
                        "Status":         get_status(score),
                        "Matched Skills": ", ".join(sorted(matched)) or "—",
                        "Missing Skills": ", ".join(sorted(missing)) or "—",
                        "Embedding":      resume_embedding,
                    })

                progress_bar.progress(1.0, text="✅  Analysis complete!")
                import time; time.sleep(0.6)
                progress_bar.empty()

                df = pd.DataFrame(results).sort_values("Score", ascending=False)
                df["Rank"] = range(1, len(df) + 1)
                df = df[["Rank", "Candidate", "Email", "File", "Score", "Status",
                          "Matched Skills", "Missing Skills"]]
                st.session_state["df"]       = df
                st.session_state["analysed"] = True
                save_candidates(results)
                st.success(f"✅  Screening complete — {len(df)} candidates ranked")
                st.rerun()

    # ── Results section ────────────────────────────────────────────────────
    if st.session_state.get("analysed"):
        df  = st.session_state["df"]
        sim = len(df[df["Status"] == "Similar"])

        st.markdown("""
        <div class="section-divider">
            <span class="sd-label">📊 Candidate Rankings</span>
            <div class="sd-line"></div>
        </div>
        """, unsafe_allow_html=True)

        # Candidate profile cards
        for _, row in df.iterrows():
            rank  = int(row["Rank"])
            score = row["Score"]
            is_match = row["Status"] == "Similar"

            sc_cls  = "score-high" if score >= 70 else "score-mid" if score >= 45 else "score-low"
            acc_cls = "cpc-accent-shortlisted" if is_match else "cpc-accent-rejected"
            rb_cls  = "rank-1" if rank == 1 else "rank-2" if rank == 2 else "rank-3" if rank == 3 else "rank-n"
            badge_cls = "badge-shortlisted" if is_match else "badge-rejected"
            badge_lbl = "✓  Shortlisted" if is_match else "✗  Not Matching"

            matched_pills = "".join(
                f'<span class="skill-pill pill-match">✓ {s.strip()}</span>'
                for s in row["Matched Skills"].split(",")
                if s.strip() and s.strip() != "—"
            )
            missing_pills = "".join(
                f'<span class="skill-pill pill-miss">✗ {s.strip()}</span>'
                for s in row["Missing Skills"].split(",")
                if s.strip() and s.strip() != "—"
            )
            skills_html = matched_pills + missing_pills or '<span class="pill-none">No skill data extracted</span>'
            email_disp  = row["Email"] if row["Email"] else "Email not found"

            st.markdown(f"""
            <div class="candidate-profile-card">
                <div class="cpc-accent-bar {acc_cls}"></div>
                <div class="cpc-body">
                    <div class="cpc-rank {rb_cls}">#{rank}</div>
                    <div class="cpc-info">
                        <div class="cpc-name">{row['Candidate']}</div>
                        <div class="cpc-email">{email_disp}</div>
                        <div class="cpc-file">📎 {row['File']}</div>
                    </div>
                    <div class="cpc-score-wrap {sc_cls}">
                        <div class="cpc-score-circle">
                            <div class="cpc-score-num">{score}</div>
                            <div class="cpc-score-pct">%</div>
                        </div>
                        <div class="status-badge {badge_cls}">{badge_lbl}</div>
                    </div>
                    <div class="cpc-skills">
                        <div class="skills-row-label">Skills Analysis</div>
                        {skills_html}
                    </div>
                    <div class="cpc-actions">
                        <div class="action-tag">Rank #{rank} of {len(df)}</div>
                        <div class="action-tag" style="color:{'#4CAF50' if score>=70 else '#D4A64A' if score>=45 else '#E57373'}">
                            {'Strong Match' if score>=70 else 'Partial Match' if score>=45 else 'Weak Match'}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        col_dl, _ = st.columns([1, 3])
        col_dl.download_button(
            "⬇️  Export Rankings CSV",
            df.to_csv(index=False).encode(),
            "candidate_ranking.csv",
            "text/csv"
        )

        # ── HR Final Decision ──────────────────────────────────────────────
        st.markdown("""
        <div class="section-divider" style="margin-top:36px">
            <span class="sd-label">👩‍💼 HR Final Decision</span>
            <div class="sd-line"></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <p style="font-size:0.82rem;color:#6B7280;margin-bottom:16px">
            Review AI recommendations below and override selections before sending outreach emails.
            Checked candidates will receive a shortlist email; unchecked will receive a rejection email.
        </p>
        """, unsafe_allow_html=True)

        final_selection = {}
        st.markdown('<div class="decision-panel"><div class="decision-panel-header"><div class="dph-title">✦ Candidate Selection — Override AI Decisions</div></div>', unsafe_allow_html=True)

        for idx, row in df.iterrows():
            default_val = row["Status"] == "Similar"
            email_disp  = row["Email"] if row["Email"] else "—"
            sc = row["Score"]
            score_color = "#4CAF50" if sc >= 70 else "#D4A64A" if sc >= 45 else "#E57373"

            chk_col, info_col = st.columns([0.05, 0.95])
            with chk_col:
                checked = st.checkbox("", value=default_val, key=f"select_{idx}")
            with info_col:
                st.markdown(f"""
                <div class="decision-row">
                    <div style="flex:1">
                        <div class="dr-name">{row['Candidate']}</div>
                        <div class="dr-email">{email_disp}</div>
                    </div>
                    <div class="dr-score" style="background:{'rgba(76,175,80,0.1)' if sc>=70 else 'rgba(212,166,74,0.1)' if sc>=45 else 'rgba(229,115,115,0.1)'};color:{score_color}">
                        {sc}%
                    </div>
                </div>
                """, unsafe_allow_html=True)
            final_selection[row["Candidate"]] = checked

        st.markdown('</div>', unsafe_allow_html=True)
        st.session_state["final_selection"] = final_selection

        selected_list = [n for n, v in final_selection.items() if v]
        rejected_list = [n for n, v in final_selection.items() if not v]

        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.markdown(f"""
            <div style="background:rgba(76,175,80,0.06);border:1px solid rgba(76,175,80,0.25);
                        border-radius:14px;padding:18px 20px;margin-top:14px">
                <div style="font-size:0.68rem;font-weight:800;color:#4CAF50;text-transform:uppercase;
                            letter-spacing:0.12em;margin-bottom:12px;font-family:Poppins,sans-serif">
                    ✅  Final Shortlist — {len(selected_list)} candidates
                </div>
                {"".join(f'<div style="font-size:0.84rem;color:#4CAF50;padding:4px 0;border-bottom:1px solid rgba(76,175,80,0.1)">✓ {c}</div>' for c in selected_list) or
                 '<div style="color:#6B7280;font-size:0.8rem;font-style:italic">No candidates selected</div>'}
            </div>
            """, unsafe_allow_html=True)
        with res_col2:
            st.markdown(f"""
            <div style="background:rgba(229,115,115,0.06);border:1px solid rgba(229,115,115,0.25);
                        border-radius:14px;padding:18px 20px;margin-top:14px">
                <div style="font-size:0.68rem;font-weight:800;color:#E57373;text-transform:uppercase;
                            letter-spacing:0.12em;margin-bottom:12px;font-family:Poppins,sans-serif">
                    ✗  Rejected — {len(rejected_list)} candidates
                </div>
                {"".join(f'<div style="font-size:0.84rem;color:#E57373;padding:4px 0;border-bottom:1px solid rgba(229,115,115,0.1)">✗ {c}</div>' for c in rejected_list) or
                 '<div style="color:#6B7280;font-size:0.8rem;font-style:italic">All candidates selected</div>'}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        if st.button("🚀  Send Emails to All Candidates", use_container_width=True):
            sent_count = 0
            with st.spinner("📧  Generating and sending emails…"):
                for _, row in df.iterrows():
                    cname  = row["Candidate"]
                    cemail = row["Email"]
                    if not cemail:
                        continue
                    flag = final_selection[cname]
                    body = generate_email(cname, "Similar" if flag else "Rejected")
                    ok   = send_email(cemail, "Application Update", body)
                    if ok:
                        save_email(cname, cemail, "Similar" if flag else "Rejected", body)
                        sent_count += 1
            st.success(f"✅  {sent_count} emails dispatched successfully.")

        # ── Email Generator ────────────────────────────────────────────────
        st.markdown("""
        <div class="section-divider" style="margin-top:36px">
            <span class="sd-label">✉️ Email Generator</span>
            <div class="sd-line"></div>
        </div>
        """, unsafe_allow_html=True)

        eg_col1, eg_col2 = st.columns([3, 1])
        sel_cand = eg_col1.selectbox(
            "Select candidate to generate email for",
            df["Candidate"].tolist(),
            label_visibility="visible"
        )
        row = df[df["Candidate"] == sel_cand].iloc[0]
        sc_color = "#4CAF50" if row["Status"] == "Similar" else "#E57373"

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:16px;padding:12px 18px;
                    background:#F8F6F2;border:1px solid #D8D8D8;
                    border-radius:12px;margin:12px 0 16px;box-shadow:0 2px 8px rgba(35,43,77,0.05)">
            <span style="font-weight:700;color:#232B4D;font-size:0.92rem;font-family:Poppins,sans-serif">{sel_cand}</span>
            <span style="color:#D8D8D8;font-size:0.9rem">·</span>
            <span style="font-size:0.82rem;color:#6B7280">{row['Score']}% semantic match</span>
            <span style="color:#D8D8D8">·</span>
            <span class="status-badge {'badge-shortlisted' if row['Status']=='Similar' else 'badge-rejected'}">
                {'✓ Shortlisted' if row['Status']=='Similar' else '✗ Not Matching'}
            </span>
        </div>
        """, unsafe_allow_html=True)

        if eg_col2.button("✨  Generate Email", use_container_width=True):
            with st.spinner("🤖  Crafting personalised email…"):
                st.session_state["email"]     = generate_email(sel_cand, row["Status"])
                st.session_state["email_for"] = sel_cand
            st.success("Email generated!")

        if st.session_state.get("email") and st.session_state.get("email_for") == sel_cand:
            email_text = st.session_state["email"]

            st.markdown(f"""
            <div class="email-composer">
                <div class="ec-header">
                    <div class="ec-dot" style="background:#E57373"></div>
                    <div class="ec-dot" style="background:#D4A64A"></div>
                    <div class="ec-dot" style="background:#4CAF50"></div>
                    <span class="ec-filename">
                        draft_email_{sel_cand.replace(' ','_').lower()}.txt
                        &nbsp;·&nbsp;
                        {'Shortlist' if row['Status']=='Similar' else 'Rejection'} Template
                    </span>
                </div>
                <div class="ec-body">{email_text}</div>
            </div>
            """, unsafe_allow_html=True)

            candidate_email = st.text_input(
                "Candidate Email Address",
                value=row["Email"],
                key="send_email_addr"
            )
            edited_email = st.text_area(
                "Edit Email Before Sending",
                value=email_text,
                height=320,
                key="email_edit_area"
            )
            send_col1, send_col2 = st.columns(2)
            if send_col1.button("✏️ Save Changes", use_container_width=True):
                st.session_state["email"] = edited_email
                st.success("Email updated successfully.")
            if send_col2.button("📧 Send Email", use_container_width=True):
                if not candidate_email:
                    st.error("Please enter candidate email address.")
                else:
                    success = send_email(candidate_email, "Application Update", edited_email)
                    if success:
                        st.success(f"Email sent successfully to {candidate_email}")
                    else:
                        st.error("Failed to send email.")


# ════════════════════════════════════════════════════════════════════════════
#  TAB 2 — CANDIDATE DATABASE
# ════════════════════════════════════════════════════════════════════════════
with tab2:

    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">🗄️ Candidate Database</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    candidates = get_all_candidates()
    if candidates:
        cdf = pd.DataFrame(candidates, columns=[
            "Name", "Email", "File", "Score", "Status",
            "Matched Skills", "Missing Skills", "Screened At"
        ])

        # Search & filter controls
        db_c1, db_c2 = st.columns([3, 1])
        with db_c1:
            search_q = st.text_input("🔍 Search candidates", placeholder="Name, email, or skill…", label_visibility="collapsed")
        with db_c2:
            status_f = st.selectbox("Status", ["All", "Similar", "Not Similar"], label_visibility="collapsed")

        filtered_df = cdf.copy()
        if search_q:
            q = search_q.lower()
            filtered_df = filtered_df[
                filtered_df["Name"].str.lower().str.contains(q, na=False) |
                filtered_df["Email"].str.lower().str.contains(q, na=False) |
                filtered_df["Matched Skills"].str.lower().str.contains(q, na=False)
            ]
        if status_f != "All":
            filtered_df = filtered_df[filtered_df["Status"] == status_f]

        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px">
            <div style="font-size:0.72rem;font-weight:700;color:#6B7280;text-transform:uppercase;letter-spacing:0.1em">
                Showing {len(filtered_df)} of {len(cdf)} records
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

        dl1, dl2 = st.columns(2)
        dl1.download_button(
            "⬇️  Export Full DB CSV",
            cdf.to_csv(index=False).encode(),
            "candidates_db.csv",
            "text/csv"
        )
        dl2.download_button(
            "⬇️  Export Filtered CSV",
            filtered_df.to_csv(index=False).encode(),
            "candidates_filtered.csv",
            "text/csv"
        )

    else:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">🗄️</span>
            <div class="empty-title">No Candidate Records Found</div>
            <div class="empty-desc">
                Your PostgreSQL database is empty. Run a resume screening session
                to populate it with candidate data.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Email Log ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class="section-divider" style="margin-top:36px">
        <span class="sd-label">📧 Sent Email Log</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    emails_log = get_all_emails()
    if emails_log:
        edf = pd.DataFrame(emails_log, columns=[
            "Candidate", "Email", "Status", "Email Body", "Sent At"
        ])
        for _, erow in edf.iterrows():
            is_ok = erow["Status"] == "Similar"
            icon = "✅" if is_ok else "✗"
            with st.expander(f"{icon}  {erow['Candidate']}  ·  {erow['Email']}  ·  {erow['Sent At']}"):
                st.markdown(f"""
                <div class="email-composer">
                    <div class="ec-header">
                        <div class="ec-dot" style="background:#E57373"></div>
                        <div class="ec-dot" style="background:#D4A64A"></div>
                        <div class="ec-dot" style="background:#4CAF50"></div>
                        <span class="ec-filename">
                            Sent to: {erow['Email']}
                            &nbsp;·&nbsp;
                            <span style="color:{'#4CAF50' if is_ok else '#E57373'}">
                                {'Shortlist' if is_ok else 'Rejection'} Email
                            </span>
                        </span>
                    </div>
                    <div class="ec-body">{erow['Email Body']}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state" style="padding:40px">
            <span class="empty-icon">📭</span>
            <div class="empty-title">No Emails Sent Yet</div>
            <div class="empty-desc">
                Use the Email Generator in the Resume Screening tab to send outreach.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Danger zone ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("""
    <div style="background:rgba(229,115,115,0.04);border:1px solid rgba(229,115,115,0.18);
                border-radius:12px;padding:16px 20px;display:flex;
                align-items:center;justify-content:space-between;gap:16px">
        <div>
            <div style="font-size:0.8rem;font-weight:700;color:#E57373;margin-bottom:3px">
                ⚠️  Danger Zone
            </div>
            <div style="font-size:0.75rem;color:#6B7280">
                Permanently delete all candidate records and email logs from PostgreSQL.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    danger_col, _ = st.columns([1, 4])
    if danger_col.button("🗑️  Clear All Database Records"):
        clear_db()
        st.success("Database cleared. All records removed.")
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
#  TAB 3 — SCREENING REPORTS
# ════════════════════════════════════════════════════════════════════════════
with tab3:

    st.markdown("""
    <div class="section-divider">
        <span class="sd-label">📋 Screening Report</span>
        <div class="sd-line"></div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.get("analysed"):
        df     = st.session_state["df"]
        report = generate_screening_report(df, jd)

        sim_r   = len(df[df["Status"] == "Similar"])
        rej_r   = len(df) - sim_r
        avg_r   = round(df["Score"].mean(), 1)
        top_r   = df.iloc[0]["Candidate"] if len(df) else "—"
        top_sc  = int(df["Score"].max()) if len(df) else 0
        rate_r  = round((sim_r / len(df)) * 100, 1) if len(df) else 0

        # Summary cards
        st.markdown(f"""
        <div class="report-summary-grid">
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#232B4D,#3a4580)"></div>
                <div class="rc-num" style="color:#232B4D">{len(df)}</div>
                <div class="rc-label">Total Candidates</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#4CAF50,#81C784)"></div>
                <div class="rc-num" style="color:#4CAF50">{sim_r}</div>
                <div class="rc-label">Shortlisted</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#E57373,#EF9A9A)"></div>
                <div class="rc-num" style="color:#E57373">{rej_r}</div>
                <div class="rc-label">Rejected</div>
            </div>
        </div>
        <div class="report-summary-grid">
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#D4A64A,#e8c06a)"></div>
                <div class="rc-num" style="color:#D4A64A">{avg_r}%</div>
                <div class="rc-label">Average Match Score</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#AFC6BE,#B7C1B0)"></div>
                <div class="rc-num" style="color:#5a8a7e">{rate_r}%</div>
                <div class="rc-label">Shortlist Rate</div>
            </div>
            <div class="report-card">
                <div class="rc-top" style="background:linear-gradient(90deg,#D7B37C,#e8c896)"></div>
                <div class="rc-num" style="color:#c49235;font-size:1.1rem">{top_r}</div>
                <div class="rc-label">Top Candidate ({top_sc}%)</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Report preview
        st.markdown(f"""
        <div class="report-preview-container">
            <div class="rpc-header">
                <div class="rpc-title">📄  Full Screening Report</div>
                <div style="font-size:0.68rem;color:#6B7280">screening_report.txt</div>
            </div>
            <div class="rpc-body">{report}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        rpt_col1, rpt_col2, _ = st.columns([1.2, 1.2, 2])
        rpt_col1.download_button(
            "⬇️  Download Report (.txt)",
            report.encode(),
            "screening_report.txt",
            "text/plain",
            use_container_width=True
        )
        rpt_col2.download_button(
            "⬇️  Export Rankings (.csv)",
            df.to_csv(index=False).encode(),
            "candidate_ranking.csv",
            "text/csv",
            use_container_width=True
        )

    else:
        st.markdown("""
        <div class="empty-state">
            <span class="empty-icon">📊</span>
            <div class="empty-title">No Report Available Yet</div>
            <div class="empty-desc">
                Reports are generated automatically after each screening run.<br>
                Go to the <strong>Resume Screening</strong> tab, upload resumes,
                add a Job Description in the sidebar, and run the analysis.
            </div>
        </div>
        """, unsafe_allow_html=True)