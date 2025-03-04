class User:
    def __init__(self, name, search_query, spreadsheet_id):
        self.name = name
        self.search_query = search_query
        self.spreadsheet_id = spreadsheet_id

# Replace "YOUR_SPREADSHEET_ID" with the actual ID
Miguel = User(name="Miguel", search_query="nodejs", spreadsheet_id="1tRxmT2ZTvL5Zagh1hc44lFthQswrqNrh86uUVu636yw")
Javi = User(name="Javi", search_query="python", spreadsheet_id="YOUR_SPREADSHEET_ID")
