import os
import openai
import re
import json

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
            return response.choices[0].message.content, current_model
        except Exception as e:
            print(f"Model {current_model} failed with error: {e}. Trying next model...")
            return _try_models(models[1:])
    
    return _try_models(fallback_models)

MATCH_AND_RATE_QUERY = (
   "Analyze the developer profile and job description below. Perform the following tasks systematically:\n\n1. REQUIREMENT ANALYSIS:\n   - List all explicit requirements from the job description\n   - Identify preferred/bonus qualifications separately\n\n2. EXPERIENCE MAPPING:\n   - Match developer's skills/experience to required qualifications\n   - Map developer's skills to bonus qualifications\n   - Identify clear gaps\n\n3. SCORING (1-10 scale):\n   10 = All required + all bonus qualifications\n    7-9 = All required + some bonus\n    5-6 = All required qualifications\n    3-4 = Some required qualifications\n    1-2 = No relevant qualifications\n    (Adjust ±1 for years of experience relevance)\n\n4. Generate JSON output with:\n   - Numerical score based on above rubric\n   - 3-5 strictly concise bullet points\n   - Use format: [±] [Category] [Details] (e.g., [-] Cloud: Missing AWS experience)\n   - Prioritize most impactful factors\n\nJSON Output Format:\n{\n  \"rating\": [1-10],\n  \"comment\": [\n    \"✅ [Category] [Brief Detail]\",\n    \"❌ [Category] [Missing Requirement]\",\n    \"🤔 [Category] [Partial Match]\"\n  ]\n}\n\nMaintain absolute brevity - maximum 15 words per bullet. Focus on factual matches/gaps without commentary."
)

import re

def evaluate_job_match(user, job, query=MATCH_AND_RATE_QUERY):
    prompt = (
        f"{query}\n\n"
        f"Developer Profile:\n{user.work_preferences}\n\n"
        f"Job Description:\n{job.get('description', '')}\n\n"
        "Evaluate:"
    )
    response_content, model_used = ask_openrouter(prompt)
    response = clean_json_response(response_content)
    rating = response.get("rating", 0)
    comment = response.get("comment", [])
    comment = "\n".join(comment)
    return rating, comment, model_used

def evaluate_all_jobs(user, jobs, query=MATCH_AND_RATE_QUERY):
    evaluated_jobs = []
    for job in jobs:
        rating, comment, model_used = evaluate_job_match(user, job, query)
        job["match_rating"] = rating
        job["match_comment"] = comment
        job["ai_model"] = model_used
        evaluated_jobs.append(job)
    return sorted(evaluated_jobs, key=lambda j: j["match_rating"], reverse=True)

def clean_json_response(raw_response):
    # Remove Markdown code blocks and whitespace
    cleaned = re.sub(r'^.*?{', '{', raw_response, flags=re.DOTALL)
    cleaned = re.sub(r'}\s*`*$', '}', cleaned)
    return json.loads(cleaned)