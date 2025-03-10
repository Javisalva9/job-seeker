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
    MATCH_AND_RATE = """1. Input to AI: “Here is the developer profile above. Below is a job description. Compare the job description’s requirements with the developer’s experience. Rate the match on a scale from 0 to 100 and provide a concise explanation for why you assigned that score.”
2. Output from AI:
   - Match Rating (0–100): Numeric value
   - Comment: Brief rationale describing which skills align well and any gaps identified
"""