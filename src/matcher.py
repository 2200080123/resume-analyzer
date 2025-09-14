# src/matcher.py
from src.extractors import extract_text
import re
from difflib import SequenceMatcher

# ---------------- Section Headers ----------------
SECTION_HEADERS = [
    "summary", "objective", "skills", "projects", "experience", "work experience",
    "professional experience", "education", "certification", "awards"
]

# A simple skill dictionary (extend this with technologies you care about)
SKILL_KEYWORDS = [
    "python","java","c++","c#","javascript","react","angular","node","express",
    "django","flask","sql","postgres","mysql","mongodb","aws","azure","gcp",
    "docker","kubernetes","rest","api","nlp","tensorflow","pytorch","git","ci/cd",
    "linux","bash","html","css","tensorflow","keras","spark","hadoop"
]

# ---------------- Extract Resume Sections ----------------
def extract_sections(text):
    lines = text.splitlines()
    sections = {}
    current_section = None
    buffer = []

    def get_header(line):
        for h in SECTION_HEADERS:
            if re.match(rf"^{h}\b", line.strip().lower()):
                return h.title()
        return None

    for line in lines:
        header = get_header(line)
        if header:
            if current_section and buffer:
                sections[current_section] = "\n".join(buffer).strip()
            current_section = header
            buffer = []
        else:
            if current_section:
                buffer.append(line)
    if current_section and buffer:
        sections[current_section] = "\n".join(buffer).strip()
    return sections

# ---------------- Utilities ----------------
def normalize_text(text: str) -> str:
    return re.sub(r'[^a-z0-9\s/+-]', ' ', (text or "").lower())

def extract_skills_from_text(text: str):
    t = normalize_text(text)
    found = set()
    for kw in SKILL_KEYWORDS:
        if re.search(rf"\b{re.escape(kw)}\b", t):
            found.add(kw)
    return found

def similarity_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()

# ---------------- Generate Feedback ----------------
def generate_feedback_and_rating(resume_sections, jd_sections, resume_skills_set, jd_skills_set):
    feedback_lines = []
    rating = 5

    # Skills check
    missing_skills = sorted(list(jd_skills_set - resume_skills_set))
    if missing_skills:
        feedback_lines.append(f"Add missing skills: {', '.join(missing_skills)}")
        rating -= min(len(missing_skills), 2)

    # Projects check
    if "Projects" in jd_sections and (("Projects" not in resume_sections) or not resume_sections.get("Projects")):
        feedback_lines.append("Add projects relevant to the job description")
        rating -= 1

    # Education check
    if "Education" in jd_sections and (("Education" not in resume_sections) or not resume_sections.get("Education")):
        feedback_lines.append("Educational background does not match JD or is missing")
        rating -= 1

    # Experience check
    jd_wants_experience = bool(jd_sections.get("Experience") or "experience" in " ".join(jd_sections.values()).lower())
    resume_has_experience = bool(resume_sections.get("Experience") or resume_sections.get("Work Experience") or resume_sections.get("Professional Experience"))
    if jd_wants_experience and not resume_has_experience:
        feedback_lines.append("Work experience not aligned with job requirements")
        rating -= 1

    # Soft skills
    resume_text_all = " ".join(resume_sections.values()).lower()
    if not any(x in resume_text_all for x in ("communication", "team", "leadership", "collaborat")):
        feedback_lines.append("Consider highlighting soft skills (communication, teamwork, leadership) with brief examples")

    if rating < 1:
        rating = 1

    # Format feedback as point-wise
    if feedback_lines:
        feedback_text = "\n".join([f"- {line}" for line in feedback_lines])
    else:
        feedback_text = "- Good fit for the job requirements"

    final_feedback = f"⭐ Rating: {rating}/5\n{feedback_text}"
    return final_feedback

# ---------------- Main Resume Analysis ----------------
def analyze_resume(resume_text, jd_text):
    resume_sections = extract_sections(resume_text)
    jd_sections = extract_sections(jd_text)

    jd_skills_raw = jd_sections.get("Skills", "") if jd_sections.get("Skills") else jd_text
    resume_skills_raw = resume_sections.get("Skills", "") if resume_sections.get("Skills") else resume_text

    jd_skills_set = extract_skills_from_text(jd_skills_raw)
    resume_skills_set = extract_skills_from_text(resume_skills_raw)

    # --- Summary (point-wise) ---
    summary_lines = []

    # Projects
    resume_projects = resume_sections.get("Projects", "")
    jd_projects = jd_sections.get("Projects", "")
    if resume_projects and jd_projects:
        proj_sim = similarity_ratio(resume_projects, jd_projects)
        if proj_sim > 0.35:
            summary_lines.append("• Projects: Matches JD-relevant work (good match)\n")
        elif proj_sim > 0.1:
            summary_lines.append("• Projects: Partial match to JD projects\n")
        else:
            summary_lines.append("• Projects: Present but not aligned to JD specifics\n")
    elif resume_projects:
        summary_lines.append("• Projects: Listed (add more JD-relevant details)\n")
    else:
        summary_lines.append("• Projects: Not listed\n")

    # Education
    resume_edu = resume_sections.get("Education", "")
    jd_edu = jd_sections.get("Education", "")
    if resume_edu and jd_edu:
        summary_lines.append(f"• Education: {resume_edu.splitlines()[0][:80]} (matches JD expectation)\n")
    elif resume_edu:
        summary_lines.append("• Education: Listed (confirm it meets JD requirement)\n")
    else:
        summary_lines.append("• Education: Not listed\n")

    # Skills
    if jd_skills_set:
        matched_skills = sorted(list(jd_skills_set & resume_skills_set))
        missing_skills = sorted(list(jd_skills_set - resume_skills_set))
        summary_lines.append(f"• Skills: Matched {len(matched_skills)}/{len(jd_skills_set)} JD skills\n")
        if missing_skills:
            summary_lines.append("• Skills - Missing: " + ", ".join(missing_skills[:6]))
    else:
        if resume_skills_set:
            summary_lines.append("• Skills: Found " + ", ".join(sorted(list(resume_skills_set))[:6]))
        else:
            summary_lines.append("• Skills: Not listed")

    # Experience
    resume_exp = resume_sections.get("Experience", "") or resume_sections.get("Work Experience", "") or resume_sections.get("Professional Experience", "")
    if resume_exp:
        yrs = re.findall(r'(\d{1,2})\+?\s+years', resume_exp.lower())
        if yrs:
            summary_lines.append(f"\n• Experience: {yrs[0]} years (mentioned)\n")
        else:
            summary_lines.append("\n• Experience: Listed (years not explicitly mentioned)\n")
    else:
        summary_lines.append("\n• Experience: Not listed\n")

    # Soft skills
    resume_text_all = " ".join(resume_sections.values()).lower()
    if any(x in resume_text_all for x in ("communication", "team", "leadership", "collaborat")):
        summary_lines.append("• Soft skills: Mentioned (communication / teamwork)\n")
    else:
        summary_lines.append("• Soft skills: Not clearly highlighted\n")

    # --- Feedback ---
    feedback = generate_feedback_and_rating(resume_sections, jd_sections, resume_skills_set, jd_skills_set)

    # --- Detailed AI Report ---
    strengths, weaknesses, suggestions = [], [], []

    if resume_skills_set & jd_skills_set:
        strengths.append("Has job-relevant technical skills: " + ", ".join(sorted(list(resume_skills_set & jd_skills_set))[:8]))
    if resume_sections.get("Projects"):
        strengths.append("Includes projects that demonstrate applied skills.")

    if jd_skills_set and not (resume_skills_set & jd_skills_set):
        weaknesses.append("Does not include key technical skills required by the JD: " + ", ".join(sorted(list(jd_skills_set))[:8]))
    if not resume_sections.get("Projects"):
        weaknesses.append("Missing project descriptions demonstrating impact and tools used.")
    if not resume_sections.get("Experience"):
        weaknesses.append("Limited or no work experience described.")

    if weaknesses:
        suggestions.append("Add/expand skills and include specific technologies from the job description.")
        suggestions.append("Add measurable outcomes to projects/experience (e.g., reduced X by Y%).")
    else:
        suggestions.append("Good match — polish formatting and quantify achievements for stronger impact.")

    detailed_ai_report = "### 🤖 AI Detailed Analysis\n\n"
    if strengths:
        detailed_ai_report += "**Strengths:**\n" + "\n".join([f"- {s}" for s in strengths]) + "\n\n"
    if weaknesses:
        detailed_ai_report += "**Weaknesses:**\n" + "\n".join([f"- {w}" for w in weaknesses]) + "\n\n"
    if suggestions:
        detailed_ai_report += "**Suggestions:**\n" + "\n".join([f"- {s}" for s in suggestions]) + "\n\n"

    # --- Match Percentage ---
    if jd_skills_set:
        match_percentage = round((len(jd_skills_set & resume_skills_set) / len(jd_skills_set)) * 100, 2)
    else:
        resume_words = set(re.findall(r'\b\w+\b', normalize_text(resume_text)))
        jd_words = set(re.findall(r'\b\w+\b', normalize_text(jd_text)))
        total_keywords = len(jd_words) if jd_words else 1
        match_percentage = round((len(resume_words.intersection(jd_words)) / total_keywords) * 100, 2)

    # Final summary markdown
    summary_markdown =  "\n".join(summary_lines)

    return {
        "match_percentage": match_percentage,
        "summary": summary_markdown,
        "feedback": feedback,
        "detailed_ai_report": detailed_ai_report,
        "resume_text": resume_text,
        "job_text": jd_text,
        "resume_sections": resume_sections,
        "jd_sections": jd_sections,
    }

# ---------------- Compare Resume vs JD ----------------
def compare_resume_job(resume_input, jd_input, is_text=False):
    if is_text:
        resume_text = resume_input
        jd_text = jd_input
    else:
        resume_text = extract_text(resume_input)
        jd_text = extract_text(jd_input)
    return analyze_resume(resume_text, jd_text)
