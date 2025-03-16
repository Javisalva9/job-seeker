class User:
    def __init__(self, name, search_query, spreadsheet_id, work_preferences):
        self.name = name
        self.search_query = search_query
        self.spreadsheet_id = spreadsheet_id
        self.work_preferences = work_preferences

# Replace "YOUR_SPREADSHEET_ID" with the actual ID
Miguel = User(name="Miguel", search_query="nodejs", spreadsheet_id="1tRxmT2ZTvL5Zagh1hc44lFthQswrqNrh86uUVu636yw", 
              work_preferences= "Node.js backend developer with over 5 years of experience creating scalable APIs in Node, TypeScript, and Nest.js. I've used mongodb mainly but I've also used MYSQL. I've got some experience with: AWS, Logly, opensearch and integrating IA APIs. Jenkins, GIT and scrum. I prefer to focus on backend development rather than full-stack and definetly not Front end."
)
Javi = User(name="Javi", search_query="python", spreadsheet_id="1VmlhE-AThc2QAaTTgqRMSxm87fXs4a_ysa0ihveK1V0", work_preferences= "I want to work with cats")

class AIQueries:
    MATCH_AND_RATE = """Analyze the developer profile and job description and generate a direct match score and summary:

1. DIRECT SCORING (0-10 scale):
   0 = Location mismatch (candidate ineligible for job location)
   1-2 = Poor match (few or no relevant qualifications)
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
   - Use format: [±] [Category] [Details]

JSON Output Format:
{
  \"rating\": [0-10],
  \"comment\": [
    \"✅ [Category] [Brief Detail]\",
    \"❌ [Category] [Missing Requirement]\",
    \"🤔 [Category] [Partial Match]\"
  ]
}

Maintain absolute brevity - maximum 15 words per bullet. Focus on factual matches/gaps without commentary."""