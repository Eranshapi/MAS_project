from store_db import vector_db  # Ensure database is populated
from crewai_integration import crew

if __name__ == "__main__":
    print("Starting Multi-Agent System...")
    crew.kickoff()
