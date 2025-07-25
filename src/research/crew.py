from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv

load_dotenv()

import os

# Update the environment variable name to match DeepSeek
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
if deepseek_key:
    print("DeepSeek API Key is Loaded")
else:
    print("DEEPSEEK_API_KEY not found")

@CrewBase
class ResearchCrew():
    """Research crew for comprehensive topic analysis and reporting"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['researcher'],
            tools=[SerperDevTool()],
            llm=LLM(
                model="openrouter/deepseek/deepseek-r1",
                base_url="https://openrouter.ai/api/v1",
                api_key=deepseek_key,
                temperature=0.7
            )
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'],
            verbose=True,
            llm=LLM(
                model="openrouter/deepseek/deepseek-r1",
                base_url="https://openrouter.ai/api/v1",
                api_key=deepseek_key,
                temperature=0.7
            )
        )

    @task
    def research_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_task'] 
        )

    @task
    def analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['analysis_task'],
            output_file='output/report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            llm=LLM(
                model="openrouter/deepseek/deepseek-r1",
                base_url="https://openrouter.ai/api/v1",
                api_key=deepseek_key,
                temperature=0.7
            )
        )