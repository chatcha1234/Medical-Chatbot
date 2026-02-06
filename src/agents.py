from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools import MedicalTools
from src.prompt import SYSTEM_DESCRIPTION
import os

class MedicalAgents:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            verbose=True,
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            safety_settings={
                "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_NONE",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_NONE"
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

