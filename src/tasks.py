from crewai import Task

class MedicalTasks:
    def search_task(self, agent, topic):
        return Task(
            description=f"""Search for information about '{topic}' in the available medical documents.
            Be specific and cite sources if possible.""",
            expected_output="A list of relevant findings from the documents.",
            agent=agent
        )

    def analysis_task(self, agent, topic, findings):
        return Task(
            description=f"""Analyze the findings about '{topic}'. 
            Provide a clear, concise answer to the user's query based on the findings.""",
            expected_output="A summarized answer to the user's question.",
            agent=agent,
            context=[findings]
        )
