from crewai import Agent, LLM
from src.tools import MedicalTools
from src.prompt import SYSTEM_DESCRIPTION
import os

class MedicalAgents:
    def __init__(self):
        self.llm = LLM(
            model="gemini/gemini-1.5-flash",
            verbose=True,
            temperature=0.2,
            api_key=os.getenv("GOOGLE_API_KEY"),
            safety_settings={
                "HARASSMENT": "BLOCK_NONE",
                "HATE": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE"
            }
        )
        self.tools = MedicalTools()


    def researcher(self):
        return Agent(
            role='Medical Researcher',
            goal='Find accurate medical information for queries, or identify general conversation.',
            backstory='Assistant specialized in searching medical databases. You distinguish between medical questions and casual greetings.',
            tools=[self.tools.medical_search],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def analyst(self):
        return Agent(
            role='Medical Analyst',
            goal='Analyze clinical data and provide structured consultation responses.',
            backstory=SYSTEM_DESCRIPTION,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

