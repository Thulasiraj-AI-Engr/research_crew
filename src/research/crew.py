from crewai import Crew, Process, Agent, Task, LLM, Flow
from crewai.flow.flow import listen, start
from pathlib import Path
import yaml
from dotenv import load_dotenv
import os

load_dotenv()

def load_yaml(file_path):
    """Load YAML configuration files"""
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

def create_llm():
    """Create DeepSeek LLM instance"""
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is required")
    
    return LLM(
        provider="deepseek",
        model="deepseek-chat",
        api_key=deepseek_api_key,
        temperature=0.2,
        stream=True
    )

class MarketStrategyFlow(Flow):
    """Market Strategy Flow using CrewAI Flow"""
    
    def __init__(self, inputs):
        super().__init__()
        self.inputs = inputs
        self.results = {}
        
        # Load configurations
        base_path = Path(__file__).resolve().parent
        config_path = base_path / "config"
        self.agents_data = load_yaml(config_path / "agents.yaml")
        self.tasks_data = load_yaml(config_path / "tasks.yaml")
        self.llm = create_llm()
        
        # Map inputs to context
        self.context = {
            "product": inputs.get("product_description", ""),
            "compitators": inputs.get("competitors", ""),
            "target_audance": inputs.get("target_audience", ""),
            "industry": inputs.get("industry", ""),
            "region": inputs.get("region", "")
        }

    def create_single_crew(self, agent_key, task_key):
        """Create a crew with single agent and task"""
        # Create agent
        agent_data = self.agents_data[agent_key]
        agent = Agent(
            role=agent_data.get("role", "").format(**self.context),
            goal=agent_data.get("goal", "").format(**self.context),
            backstory=agent_data.get("backstory", "").format(**self.context),
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
        
        # Create task
        task_data = self.tasks_data[task_key]
        task = Task(
            description=task_data.get("description", "").format(**self.context),
            expected_output=task_data.get("expected_output", "").format(**self.context),
            agent=agent
        )
        
        # Create and return crew
        return Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=True
        )

    @start()
    def start_research(self):
        """Start the flow"""
        print("🚀 Starting Market Strategy Flow...")
        return "Flow started"

    @listen("start_research")
    def market_research(self, context):
        """Execute market research"""
        print("📊 Running Market Research...")
        crew = self.create_single_crew("market_researcher", "market_research_task")
        result = crew.kickoff()
        self.results["market_research"] = result
        return "Market research completed"

    @listen("market_research")
    def competitor_analysis(self, context):
        """Execute competitor analysis"""
        print("🏢 Running Competitor Analysis...")
        crew = self.create_single_crew("competitor_intelligence", "competitor_intelligence_task")
        result = crew.kickoff()
        self.results["competitor_analysis"] = result
        return "Competitor analysis completed"

    @listen("competitor_analysis")
    def data_structuring(self, context):
        """Structure the data"""
        print("📋 Structuring Data...")
        crew = self.create_single_crew("data_extractor", "data_structuring_task")
        result = crew.kickoff()
        self.results["structured_data"] = result
        return "Data structuring completed"

    @listen("data_structuring")
    def customer_profiling(self, context):
        """Profile customers"""
        print("👥 Customer Profiling...")
        crew = self.create_single_crew("customer_profiler", "customer_profiling_task")
        result = crew.kickoff()
        self.results["customer_profiles"] = result
        return "Customer profiling completed"

    @listen("customer_profiling")
    def customer_insights(self, context):
        """Gather customer insights"""
        print("💡 Customer Insights...")
        crew = self.create_single_crew("customer_insights", "customer_insights_task")
        result = crew.kickoff()
        self.results["customer_insights"] = result
        return "Customer insights completed"

    @listen("customer_insights")
    def final_strategy(self, context):
        """Create final strategy"""
        print("🎯 Creating Final Strategy...")
        crew = self.create_single_crew("strategy_maker", "strategy_maker_task")
        result = crew.kickoff()
        self.results["final_strategy"] = result
        
        # Save report
        self.save_report()
        
        return result

    def save_report(self):
        """Save comprehensive report"""
        report = f"""# 🚀 Market Strategy Analysis Report

**Product:** {self.context.get('product', 'N/A')}
**Industry:** {self.context.get('industry', 'N/A')}
**Region:** {self.context.get('region', 'N/A')}
**Competitors:** {self.context.get('compitators', 'N/A')}
**Target Audience:** {self.context.get('target_audance', 'N/A')}

---

## 📊 Market Research
{self.results.get('market_research', 'No data')}

---

## 🏢 Competitor Analysis
{self.results.get('competitor_analysis', 'No data')}

---

## 📋 Structured Data
{self.results.get('structured_data', 'No data')}

---

## 👥 Customer Profiling
{self.results.get('customer_profiles', 'No data')}

---

## 💡 Customer Insights
{self.results.get('customer_insights', 'No data')}

---

## 🎯 Final Strategy
{self.results.get('final_strategy', 'No data')}

---
*Generated by Market Strategy AI Flow*
"""
        
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        print("📄 Report saved to report.md")

def create_crew():
    """Create and return crew instance"""
    
    class MarketStrategyCrew:
        def __init__(self):
            self.flow = None
            
        def kickoff(self, inputs):
            """Execute the flow"""
            # Create and run flow
            self.flow = MarketStrategyFlow(inputs)
            result = self.flow.kickoff()
            
            # Return final strategy
            final_strategy = self.flow.results.get("final_strategy", "Strategy completed")
            return str(final_strategy)
    
    return MarketStrategyCrew()
