import streamlit as st
import tempfile
from src.extractors import extract_text
from src.matcher import compare_resume_job
from src.ai_analysis import analyze_resume_with_ai

st.set_page_config(page_title="AI Resume Analyzer", page_icon="🤖", layout="wide")
st.title("🤖 AI Resume Analyzer")
st.write("Upload your Resume and provide a Job Description (file or text).")

# ---------------- Resume Upload ----------------
resume_file = st.file_uploader("📄 Upload Resume (PDF/DOCX)", type=["pdf", "docx"])

# ---------------- Job Description Input ----------------
st.subheader("📑 Job Description Input")
job_mode = st.radio("How would you like to provide the Job Description?", ["Upload File", "Paste Text"])
job_text, job_file = None, None
if job_mode == "Upload File":
    job_file = st.file_uploader("📂 Upload Job Description", type=["pdf", "docx", "txt"])
else:
    job_text = st.text_area("Paste Job Description Here")

# ---------------- Run Analysis ----------------
if resume_file and (job_file or job_text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=resume_file.name) as tmp_resume:
        tmp_resume.write(resume_file.read())
        resume_path = tmp_resume.name

    if job_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=job_file.name) as tmp_job:
            tmp_job.write(job_file.read())
            job_path = tmp_job.name
        result = compare_resume_job(resume_path, job_path, is_text=False)
        job_text_plain = extract_text(job_path)
    else:
        result = compare_resume_job(resume_path, job_text, is_text=True)
        job_text_plain = job_text

    resume_text_plain = extract_text(resume_path)

    # ---------------- Match Percentage ----------------
    st.subheader("📌 Match Percentage")
    match_score = result.get("match_percentage", 0)
    st.progress(int(match_score))
    if match_score >= 75:
        st.success(f"✅ Strong Match: {match_score}%")
    elif match_score >= 50:
        st.warning(f"⚠️ Moderate Match: {match_score}%")
    else:
        st.error(f"❌ Weak Match: {match_score}%")

    # ---------------- Summary Report ----------------
    st.subheader("📝 Summary Report")
    st.markdown(result.get("summary", "No summary available."))

    # ---------------- Feedback ----------------
    st.subheader("⭐ Feedback")
    st.info(result.get("feedback", "No feedback available."))

    # ---------------- Extra AI-Powered Analysis (Optional Button) ----------------
    if st.button("🚀 Generate Detailed AI Report"):
        with st.spinner("Analyzing resume with advanced AI..."):
            ai_feedback = analyze_resume_with_ai(resume_path, job_text_plain)
            st.subheader("🤖 AI-Powered Report")
            st.markdown(ai_feedback)
else:
    st.info("Please upload the resume and provide the job description (file or text) to run analysis.")
