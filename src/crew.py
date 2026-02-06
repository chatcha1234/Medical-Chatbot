from crewai import Crew, Process
from src.agents import MedicalAgents
from src.tasks import MedicalTasks
import os

def create_crew():
    agents = MedicalAgents()
    tasks = MedicalTasks()

    # Instantiate Agents
    researcher = agents.researcher()
    analyst = agents.analyst()

    # Instantiate Tasks
    # Note: In CrewAI, tasks are usually instantiated with the agents. 
    # But for dynamic inputs like 'topic', we often define them in a way that can accept inputs.
    # However, CrewAI kickof(inputs={...}) interpolates {variables} in descriptions.
    
    # Redefine tasks to be static but use interpolation
    # Or keep it simple as before but organized.
    
    # Correct approach for interpolation with kickoff inputs:
    # We create the task objects. The description string should have {topic} placeholders.
    
    task1 = tasks.search_task(researcher, "{topic}")
    task2 = tasks.analysis_task(analyst, "{topic}", task1)

    # Crew
    crew = Crew(
        agents=[researcher, analyst],
        tasks=[task1, task2],
        verbose=True,
        process=Process.sequential
    )

    return crew

if __name__ == "__main__":
    # Example usage
    # os.environ["GOOGLE_API_KEY"] = "YOUR_API_KEY_HERE" 
    try:
        my_crew = create_crew()
        result = my_crew.kickoff(inputs={'topic': 'input your query here'})
        print(result)
    except Exception as e:
        print(f"Error: {e}")
