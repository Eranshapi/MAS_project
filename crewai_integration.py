from crewai import Agent, Task, Crew
from query_db import query_database

# Define Retrieval Agent
retrieval_agent = Agent(
    role="Knowledge Expert",
    goal="Retrieve relevant knowledge from the database",
    backstory="Has access to a vast library of documents and answers questions based on them.",
    tools=[query_database],  # Attach ChromaDB retrieval function
)

# Define Task for the Agent
retrieval_task = Task(
    description="Search for information about machine learning and provide a summary.",
    agent=retrieval_agent,
)

# Create CrewAI System
crew = Crew(
    agents=[retrieval_agent],
    tasks=[retrieval_task],
    process="sequential",  # Can be 'parallel' if needed
)

# Start CrewAI Execution
if __name__ == "__main__":
    crew.kickoff()
