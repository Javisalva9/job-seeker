import os
import openai
import re

# Ensure your OpenRouter API key is set in your environment.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("❌ Missing OpenRouter API key! Set it in a .env file.")

def ask_openrouter(prompt, model="Qwen2.5 VL 72B Instruct"):
    """
    Sends a request to OpenRouter's API using the specified model.

    :param prompt: The text prompt to send.
    :param model: The AI model to use (default: Qwen2.5 VL 72B Instruct).
    :return: The AI response as a string.
    """
    try:
        client = openai.OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
        )
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenRouter Error: {e}")
        return None

MATCH_AND_RATE_QUERY = (
    "1. Input to AI: “Here is the developer profile above. Below is a job description. "
    "Compare the job description’s requirements with the developer’s experience. "
    "Rate the match on a scale from 0 to 100 and provide a concise explanation for why you assigned that score.”\n"
    "2. Output from AI:\n"
    "   - Match Rating (0–100): Numeric value\n"
    "   - Comment: Brief rationale describing which skills align well and any gaps identified\n"
)

def evaluate_job_match(user, job, query=MATCH_AND_RATE_QUERY):
    """
    Uses the AI to evaluate how well a job matches the developer's profile.

    :param user: Developer profile object containing work_preferences.
    :param job: Job dict, expects a 'description' key.
    :param query: The instruction prompt for matching.
    :return: Tuple (rating, comment).
    """
    prompt = (
        f"{query}\n\n"
        f"Developer Profile:\n{user.work_preferences}\n\n"
        f"Job Description:\n{job.get('description', '')}\n\n"
        "Evaluate:"
    )
    response = ask_openrouter(prompt, model="qwen/qwen2.5-vl-72b-instruct:free")
    rating = 0
    comment = ""
    if response:
        rating_match = re.search(r"Match Rating\s*\(0–100\):\s*(\d+)", response)
        comment_match = re.search(r"Comment:\s*(.+)", response)
        if rating_match:
            rating = int(rating_match.group(1))
        if comment_match:
            comment = comment_match.group(1).strip()
    return rating, comment

def evaluate_all_jobs(user, jobs, query=MATCH_AND_RATE_QUERY):
    evaluated_jobs = []
    for job in jobs:
        rating, comment = evaluate_job_match(user, job, query)
        job["match_rating"] = rating
        job["match_comment"] = comment
        evaluated_jobs.append(job)
    return sorted(evaluated_jobs, key=lambda j: j["match_rating"], reverse=True)
