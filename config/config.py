class AIQueries:
    MATCH_AND_RATE = """Analyze the developer profile and job description
and generate a direct match score and summary:

1. DIRECT SCORING (0-10 scale):
   0 = Location mismatch (candidate ineligible for job location)
   1-2 = Title contains technology that user does not use
   3-4 = Partial match (some required qualifications)
   5-6 = Adequate match (all required qualifications)
   7-9 = Strong match (all required + some bonus)
   10 = Perfect match (all required + all bonus qualifications)
   (Adjust ±1 based on experience level fit)

2. Generate JSON output with:
   - Numerical score based on above rubric
   - 3-5 strictly concise bullet points highlighting:
     * Most significant matches
     * Most critical gaps
     * Key partial matches

JSON Output Format:
{
  \"rating\": [0-10],
  \"comment\": [
    \"✅ [Category] [Brief Detail]\",
    \"❌ [Category] [Missing Requirement]\",
    \"🤔 [Category] [Partial Match]\"
  ]
}

Maintain absolute brevity - maximum 15 words per bullet.
Focus on factual matches/gaps without commentary."""
