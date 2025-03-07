import os
import openai
import re

# Ensure your OpenRouter API key is set in your environment.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ Missing OpenRouter API key! Set it in a .env file.")

def ask_openrouter(prompt):
    fallback_models = [
        "google/gemini-2.0-pro-exp-02-05:free",
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "qwen/qwen2.5-vl-72b-instruct:free"
    ]
    
    def _try_models(models):
        if not models:
            raise Exception(f"All models failed for prompt: {prompt}")
        current_model = models[0]
        try:
            client = openai.OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
            )
            response = client.chat.completions.create(
                model=current_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Model {current_model} failed with error: {e}. Trying next model...")
            return _try_models(models[1:])
    
    return _try_models(fallback_models)

MATCH_AND_RATE_QUERY = (
    "1. Input to AI: “Here is the developer profile above. Below is a job description. "
    "Compare the job description’s requirements with the developer’s experience. "
    "Rate the match on a scale from 0 to 100 and provide a concise explanation for why you assigned that score.”\n"
    "2. Output from AI (you should directly write this as follows without any style):\n"
    "   - Match Rating (0–100): Numeric value\n"
    "   - Comment: Short concret bullet points on compatibility and gaps\n"
)

import re

def evaluate_job_match(user, job, query=MATCH_AND_RATE_QUERY):
    prompt = (
        f"{query}\n\n"
        f"Developer Profile:\n{user.work_preferences}\n\n"
        f"Job Description:\n{job.get('description', '')}\n\n"
        "Evaluate:"
    )
    response = ask_openrouter(prompt)
    rating = 0
    comment = ""
    if response:
        response = re.sub(r"\*+", "", response)
        rating_match = re.search(r"Match Rating\s*\(0[–-]100\):\s*(\d+)", response)
        comment_match = re.search(r"Comment:\s*(.+)", response, re.DOTALL)
        if rating_match:
            rating = int(rating_match.group(1))
        if comment_match:
            comment = comment_match.group(1).strip()
    return rating, comment

def evaluate_all_jobs(user, jobs, query=MATCH_AND_RATE_QUERY):
    evaluated_jobs = []
    for job in jobs:
        if job.get("company") != 'Hostaway':
            continue
        rating, comment = evaluate_job_match(user, job, query)
        job["match_rating"] = rating
        job["match_comment"] = comment
        evaluated_jobs.append(job)
    return sorted(evaluated_jobs, key=lambda j: j["match_rating"], reverse=True)
