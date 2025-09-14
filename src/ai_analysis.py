# src/ai_analysis.py
import os
import google.generativeai as genai
from src.extractors import extract_text
from src.matcher import extract_sections

# Configure Gemini with your API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "AIzaSyBazWyBTLK5jmxW43hF96havYmAUrO4-cs"))

def analyze_resume_with_ai(resume_file_or_text, job_description):
    """
    Uses Google Gemini AI to generate a detailed, section-wise improvement report 
    that tells the user exactly what changes to make in their resume to fit the JD.
    """

    try:
        # Step 1: Load Resume Text
        try:
            resume_text = extract_text(resume_file_or_text)  # if file is passed
        except Exception:
            resume_text = resume_file_or_text  # assume raw text

        # Step 2: Extract sections for structured input
        resume_sections = extract_sections(resume_text)
        jd_sections = extract_sections(job_description or "")

        # Step 3: Create structured prompt
        prompt = f"""
        You are a professional career coach and resume reviewer.

        Candidate Resume (sections extracted):
        {resume_sections}

        Job Description (sections extracted):
        {jd_sections}

        Task:
        - Compare the resume against the JD.
        - Identify **missing or weak points** in the resume.
        - Suggest **specific modifications** the candidate should make to improve alignment.
        - Write section-wise feedback in **clear bullet points** (no emojis, no fluff).
        - Focus on: Skills, Projects, Experience, Education, Certifications, and Soft Skills.
        - End with a short actionable summary.

        Format strictly like this:
        

        ### Skills
        - What to keep
        - What to add / change

        ### Projects
        - What to keep
        - What to add / change

        ### Experience
        - What to keep
        - What to add / change

        ### Education
        - What to keep
        - What to add / change

        ### Certifications
        - What to keep
        - What to add / change

        ### Soft Skills
        - What to keep
        - What to add / change

        ### Final Summary
        - 3 to 4 crisp, actionable lines for the user to improve their resume.
        """

        # Step 4: Call Gemini model
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text

    except Exception as e:
        return f"❌ Could not analyze resume with AI.\n\nError: {str(e)}"
