import os
import asyncio
from typing import List, Dict, Any
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff
from crewai_tools import SerperDevTool
from crewai.agents.agent_builder.base_agent import BaseAgent
import yaml

@CrewBase
class MarketStrategyCrew:
    """Market Strategy AI Crew for comprehensive market analysis and strategy development"""
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    # Configuration file paths
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        # Initialize tools
        self.serper_tool = SerperDevTool()
        
    @before_kickoff
    def prepare_inputs(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and validate inputs before crew execution"""
        # Validate required inputs
        required_fields = ['product', 'target_audance', 'compitators']
        for field in required_fields:
            if field not in inputs:
                raise ValueError(f"Missing required input: {field}")
        
        # Add timestamp for tracking
        inputs['execution_timestamp'] = asyncio.get_event_loop().time()
        print(f"🚀 Starting market strategy analysis for: {inputs['product']}")
        return inputs
    
    @after_kickoff
    def process_output(self, output):
        """Process and enhance output after crew completion"""
        print("✅ Market strategy analysis completed successfully!")
        output.raw += "\n\n--- Analysis completed by CrewAI Market Strategy Team ---"
        return output

    @agent
    def market_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['market_researcher'],
            tools=[self.serper_tool],
            verbose=True,
            max_rpm=10,
            memory=True
        )

    @agent
    def competitor_intelligence(self) -> Agent:
        return Agent(
            config=self.agents_config['competitor_intelligence'],
            tools=[self.serper_tool],
            verbose=True,
            max_rpm=10,
            memory=True
        )

    @agent
    def data_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['data_extractor'],
            verbose=True,
            max_rpm=15,
            memory=True
        )

    @agent
    def customer_profiler(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_profiler'],
            verbose=True,
            max_rpm=10,
            memory=True
        )

    @agent
    def customer_insights(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_insights'],
            verbose=True,
            max_rpm=10,
            memory=True
        )

    @agent
    def strategy_maker(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_maker'],
            verbose=True,
            max_rpm=8,
            memory=True
        )

    @task
    def market_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['market_research_task'],
            agent=self.market_researcher(),
            async_execution=False  # This runs first
        )

    @task
    def competitor_intelligence_task(self) -> Task:
        return Task(
            config=self.tasks_config['competitor_intelligence_task'],
            agent=self.competitor_intelligence(),
            async_execution=False  # This runs in parallel with market research
        )

    @task
    def data_structuring_task(self) -> Task:
        return Task(
            config=self.tasks_config['data_structuring_task'],
            agent=self.data_extractor(),
            context=[self.market_research_task(), self.competitor_intelligence_task()],
            async_execution=False
        )

    @task
    def customer_profiling_task(self) -> Task:
        return Task(
            config=self.tasks_config['customer_profiling_task'],
            agent=self.customer_profiler(),
            context=[self.data_structuring_task()],
            async_execution=False
        )

    @task
    def customer_insights_task(self) -> Task:
        return Task(
            config=self.tasks_config['customer_insights_task'],
            agent=self.customer_insights(),
            context=[self.customer_profiling_task()],
            async_execution=False
        )

    @task
    def strategy_maker_task(self) -> Task:
        return Task(
            config=self.tasks_config['strategy_maker_task'],
            agent=self.strategy_maker(),
            context=[
                self.data_structuring_task(),
                self.customer_profiling_task(),
                self.customer_insights_task()
            ],
            async_execution=False
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            cache=True,
            max_rpm=50,  # Overall crew rate limit
            output_log_file="market_strategy_logs.json",
            planning=True,  # Enable planning for better coordination
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        )

    async def kickoff_async(self, inputs: Dict[str, Any]):
        """Async execution method"""
        return await self.crew().kickoff_async(inputs=inputs)

    def kickoff_sync(self, inputs: Dict[str, Any]):
        """Synchronous execution method"""
        return self.crew().kickoff(inputs=inputs)