from crewai import Task

class MedicalTasks:
    def triage_task(self, agent, topic):
        return Task(
            description=f"Analyze user input: '{topic}'. Identify if it is a GREETING, a MEDICAL_QUERY, or an EMERGENCY. Assess severity (Low, Medium, High).",
            expected_output="A classification report including category and severity.",
            agent=agent
        )

    def research_task(self, agent, topic, triage_report):
        return Task(
            description=f"If the triage report for '{topic}' indicates a medical query, perform a focused search for clinical facts using your tools. If it is just a greeting, skip research and return 'No research needed'.",
            expected_output="Relevant clinical snippets or a note that research was skipped.",
            agent=agent,
            context=[triage_report]
        )

    def dialogue_task(self, agent, topic, triage_report, research_report, history, user_profile):
        return Task(
            description=f"""Conduct a clinical consultation for '{topic}'.
            HISTORY: {history}
            PROFILE: {user_profile}
            
            GUIDELINES:
            1. Review the triage report and research findings provided in your context.
            2. If history taking is incomplete (less than 4 turns), ask EXACTLY ONE follow-up question.
            3. If an emergency or history is sufficient, provide a summary and advice.
            4. Use the research data to improve advice quality.
            5. Language: Thai only.""",
            expected_output="A professional clinical response in Thai.",
            agent=agent,
            context=[triage_report, research_report]
        )

    def formatting_task(self, agent, dialogue_result):
        return Task(
            description="""Format the clinical response into the final template.
            REQUIRED STRUCTURE:
            [THINKING: Phase, Status]
            
            (Blank Line)
            
            * Point 1
            * Point 2
            
            (Blank Line)
            
            [SUGGESTIONS: "...", "..."]
            [MODE: RAG/BRAIN]
            
            RULES:
            - Thai Language only.
            - Bullet points only for the main body.
            - Mandatory blank lines around the bullet points.""",
            expected_output="A perfectly formatted medical response in Thai.",
            agent=agent,
            context=[dialogue_result]
        )
