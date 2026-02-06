from crewai import Agent, LLM
from src.tools import MedicalTools
import os

class MedicalAgents:
    def __init__(self):
        self.tools = MedicalTools()

    @property
    def manager_llm(self):
        return LLM(
            model="gemini/gemini-2.0-flash",
            verbose=True,
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    @property
    def llm(self):
        return LLM(
            model="gemini/gemini-2.0-flash",
            verbose=True,
            api_key=os.getenv("GOOGLE_API_KEY")
        )

    def triage_specialist(self):
        return Agent(
            role='Triage Specialist',
            goal='Accurately classify patient intent: Greeting, Symptom, or Emergency.',
            backstory='You are the first point of contact in a digital clinic. Your job is to identify what the patient needs and flag any red flags immediately.',
            llm=self.llm,
            verbose=True
        )

    def medical_researcher(self):
        return Agent(
            role='Medical Research Specialist',
            goal='Find high-quality clinical information from the database to support diagnosis.',
            backstory='A data-driven scientist who searches through medical literature to provide facts. You handle tool errors gracefully by suggesting general guidelines if data is missing.',
            tools=[self.tools.medical_search],
            llm=self.llm,
            verbose=True
        )

    def clinical_consultant(self):
        return Agent(
            role='Clinical Consultant',
            goal='Conduct patient interviews and provide empathetic, fact-based advice.',
            backstory='A board-certified physician known for clear communication. You ask ONE question at a time during history taking and provide clear summaries when ready.',
            llm=self.llm,
            verbose=True
        )

    def format_specialist(self):
        return Agent(
            role='Output Format Specialist',
            goal='Ensure every response is clean, formatted in bullet points, and free of meta-talk.',
            backstory='A strict editor who enforces the delivery of information in Thai, using bullet points only, and ensuring all required tags ([THINKING], [SUGGESTIONS], etc.) are present.',
            llm=self.llm,
            verbose=True
        )
