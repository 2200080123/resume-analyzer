from src.matcher import compare_resume_job
from src.reporter import generate_report

resume_path = "data/sample_resume.pdf"
job_path = "data/sample_job.txt"

result = compare_resume_job(resume_path, job_path)
generate_report(result)
