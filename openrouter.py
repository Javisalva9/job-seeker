import os
from dotenv import load_dotenv
import openai
import re
import json
from config.config import AIQueries

# Load environment variables first
load_dotenv("config/.env")

# Ensure your OpenRouter API key is set in your environment.
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MATCH_AND_RATE_QUERY = AIQueries.MATCH_AND_RATE
if not OPENROUTER_API_KEY:
    raise ValueError("❌ Missing OpenRouter API key! Set it in a .env file.")


def ask_openrouter(prompt):
    fallback_models = [
        "google/gemini-2.0-pro-exp-02-05:free",
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "qwen/qwen2.5-vl-72b-instruct:free" "nvidia/llama-3.1-nemotron-70b-instruct:free",
        "google/gemini-2.0-flash-thinking-exp:free",
        "nousresearch/deephermes-3-llama-3-8b-preview:free",
        "nvidia/llama-3.1-nemotron-70b-instruct:free",
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
                messages=[{"role": "user", "content": prompt}],
            )

            error_message = response.model_extra.get("error", {}).get("message", "No error message found")

            if error_message == "Rate limit exceeded: free-models-per-day":
                raise ValueError(error_message)

            content = response.choices[0].message.content
            parsed_response = clean_json_response(content)
            # Validate required fields exist
            if not all(key in parsed_response for key in ("rating", "comment")):
                raise ValueError("Missing required fields in JSON response")
            return parsed_response, current_model
        except Exception as e:
            error_type = "API call" if isinstance(e, openai.APIError) else "JSON validation"
            print(f"Model {current_model} failed ({error_type} error): {str(e)[:100]}")
            return _try_models(models[1:])

    return _try_models(fallback_models)


def evaluate_job_match(user, job):
    work_preferences_str = json.dumps(user.work_preferences, indent=2)

    prompt = (
        f"{MATCH_AND_RATE_QUERY}\n\n"
        f"Developer Profile:\n{work_preferences_str}\n\n"
        f"Job title:\n{job.get('title', '')}\n\n"
        f"Job Description:\n{job.get('description', '')}\n\n"
    )
    try:
        response, model_used = ask_openrouter(prompt)
        rating = response.get("rating", 0)
        comment = response.get("comment", [])
    except (ValueError, Exception):
        print("Failed to get valid response")
        rating = 0
        comment = ["AI evaluation failed"]
        model_used = "error"
    comment = "\n".join(comment)
    return rating, comment, model_used


def evaluate_all_jobs(user, jobs):
    evaluated_jobs = []
    for job in jobs:
        rating, comment, model_used = evaluate_job_match(user, job)
        job["score"] = rating
        job["comment"] = comment
        job["ai_model"] = model_used
        evaluated_jobs.append(job)
    return sorted(evaluated_jobs, key=lambda j: j["score"], reverse=False)


def clean_json_response(raw_response):
    # Remove Markdown code blocks and whitespace
    cleaned = re.sub(r"^.*?{", "{", raw_response, flags=re.DOTALL)
    cleaned = re.sub(r"}\s*`*$", "}", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        raise ValueError("Failed to parse JSON response")
