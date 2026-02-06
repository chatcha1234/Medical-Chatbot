from crewai import Crew, Process
from src.agents import MedicalAgents
from src.tasks import MedicalTasks
import os

def create_crew(inputs):
    agents = MedicalAgents()
    tasks = MedicalTasks()

    # Instantiate Agents
    researcher = agents.researcher()
    analyst = agents.analyst()

    # Tasks
    task1 = tasks.search_task(researcher, inputs['topic'], inputs.get('history', ""), inputs.get('user_profile', "{}"))
    task2 = tasks.analysis_task(analyst, inputs['topic'], task1, inputs.get('user_profile', "{}"), inputs.get('history', ""))

    # Crew
    crew = Crew(
        agents=[researcher, analyst],
        tasks=[task1, task2],
        verbose=True,
        process=Process.sequential,
        memory=False
    )

    return crew

if __name__ == "__main__":
    try:
        my_crew = create_crew({'topic': 'test', 'history': '', 'user_profile': '{}'})
        result = my_crew.kickoff()
        print(f"Test Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

