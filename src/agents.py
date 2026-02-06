from crewai import Agent
from src.tools import PDFSearchTool

class MedicalAgents:
    def researcher(self):
        return Agent(
            role='Medical Researcher',
            goal='Find precise information from medical documents.',
            backstory="""You are an expert researcher. Your job is to dig through 
            medical PDFs to find relevant clinical trials, treatments, and protocols.""",
            verbose=True,
            allow_delegation=False,
            tools=[PDFSearchTool()]
        )

    def analyst(self):
        return Agent(
            role='Medical Analyst',
            goal='Analyze and synthesize medical research into clear answers.',
            backstory="""You are a senior medical analyst. You take raw data from 
            researchers and turn it into actionable, easy-to-understand advice.""",
            verbose=True,
            allow_delegation=False
        )
