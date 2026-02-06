from crewai import Task
from src.prompt import RESEARCH_DESCRIPTION, ANALYSIS_DESCRIPTION

class MedicalTasks:
    def search_task(self, agent, topic, history="", user_profile="{}"):
        return Task(
            description=RESEARCH_DESCRIPTION.format(
                topic=topic, 
                history=history, 
                user_profile=user_profile
            ),
            expected_output="Detailed findings with citations or a follow-up response.",
            agent=agent
        )

    def analysis_task(self, agent, topic, findings, user_profile="{}", history=""):
        return Task(
            description=ANALYSIS_DESCRIPTION.format(
                topic=topic,
                user_profile=user_profile,
                history=history
            ),
            expected_output="Direct response/advice in Thai with [SUGGESTIONS] and [MODE] at the end.",
            agent=agent,
            context=[findings]
        )
