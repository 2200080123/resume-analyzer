# src/reporter.py
def generate_summary(resume_sections, jd_sections):
    """
    Create a high-level summary comparing resume vs job description.
    """
    missing_sections = [
        section for section, content in resume_sections.items()
        if not content.strip()
    ]

    summary = "📝 **Summary Report**\n\n"
    if missing_sections:
        summary += f"The resume is missing these important sections: {', '.join(missing_sections)}.\n"
    else:
        summary += "The resume covers all major sections required for a typical job description.\n"

    return summary


def generate_feedback(resume_text, job_text, rating=7.5):
    """
    Provide a structured feedback rating & comments.
    """
    feedback = "⭐ **Feedback**\n\n"
    feedback += f"**Rating:** {rating}/10\n\n"
    feedback += "- The resume demonstrates relevant strengths but could be improved with quantified achievements, better formatting, and clarity.\n"
    feedback += "- Ensure alignment of projects and experiences with the job description.\n"

    return feedback
