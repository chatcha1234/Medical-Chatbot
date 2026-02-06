from crewai import Crew, Process
from src.agents import MedicalAgents
from src.tasks import MedicalTasks
import os

def create_crew(inputs):
    agents = MedicalAgents()
    tasks = MedicalTasks()

    # 1. Triage
    triage_specialist = agents.triage_specialist()
    t_task = tasks.triage_task(triage_specialist, inputs['topic'])

    # 2. Research
    researcher = agents.medical_researcher()
    r_task = tasks.research_task(researcher, inputs['topic'], t_task)

    # 3. Clinical Interaction
    consultant = agents.clinical_consultant()
    d_task = tasks.dialogue_task(
        consultant, 
        inputs['topic'], 
        t_task, 
        r_task, 
        inputs.get('history', ""), 
        inputs.get('user_profile', "{}")
    )

    # 4. Final Formatting
    formatter = agents.format_specialist()
    f_task = tasks.formatting_task(formatter, d_task)

    # Crew Assembly
    crew = Crew(
        agents=[triage_specialist, researcher, consultant, formatter],
        tasks=[t_task, r_task, d_task, f_task],
        verbose=True,
        process=Process.hierarchical,
        manager_llm=agents.manager_llm,
        memory=True,
        embedder={
            "provider": "google-generativeai",
            "config": {
                "model": "models/gemini-embedding-001",
            }
        }
    )

    return crew

if __name__ == "__main__":
    test_crew = create_crew({'topic': 'ปวดหัวครับ', 'history': '', 'user_profile': '{}'})
    test_crew.kickoff()
