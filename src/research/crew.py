from crewai import Crew, Process, Agent, Task, LLM, Flow
from crewai.flow.flow import listen, start
from pathlib import Path
import yaml
from dotenv import load_dotenv
import os
from datetime import datetime

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
    """Dynamic Market Strategy Flow with parallel execution"""
    
    def __init__(self, inputs, max_retries=3):
        super().__init__()
        self.inputs = inputs
        self.max_retries = max_retries
        self.results = {}
        
        # Dynamic mapping of main.py inputs to agent variables
        self.context = {
            "product": inputs.get("product_description", ""),
            "compitators": inputs.get("competitors", ""),  # Keep original YAML key
            "target_audance": inputs.get("target_audience", ""),  # Keep original YAML key
            "industry": inputs.get("industry", ""),
            "region": inputs.get("region", "")
        }

    def retry_task(self, task_name, crew_func, task_inputs=None):
        """Execute task with retry mechanism"""
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"🔄 {task_name} - Attempt {attempt}")
                crew = crew_func()
                
                # Use custom inputs if provided, otherwise use default context
                inputs_to_use = task_inputs if task_inputs else self.context
                result = crew.kickoff(inputs=inputs_to_use)
                
                if result and str(result).strip():
                    print(f"✅ {task_name} - Completed")
                    return result
                    
            except Exception as e:
                print(f"❌ {task_name} - Attempt {attempt} failed: {str(e)}")
                if attempt == self.max_retries:
                    return f"{task_name} failed after {self.max_retries} attempts. Using available data for strategy."
        
        return f"{task_name} - No valid result"

    @start()
    def start_parallel_research(self):
        """Start parallel research phase"""
        print("🚀 Starting parallel market research and competitor analysis...")
        return {"phase": "parallel_research"}

    @listen(start_parallel_research)
    def market_research(self, context):
        """Execute market research in parallel"""
        result = self.retry_task("Market Research", 
                                lambda: create_single_agent_crew("market_researcher", "market_research_task"))
        self.results["market_research"] = result
        return {"task": "market_research", "status": "completed"}

    @listen(start_parallel_research)
    def competitor_analysis(self, context):
        """Execute competitor analysis in parallel"""
        result = self.retry_task("Competitor Analysis", 
                                lambda: create_single_agent_crew("competitor_intelligence", "competitor_intelligence_task"))
        self.results["competitor_analysis"] = result
        return {"task": "competitor_analysis", "status": "completed"}

    @listen((market_research, competitor_analysis))  # ✅ FIXED: Added tuple syntax
    def data_structuring(self, contexts):
        """Structure all research data"""
        print("📊 Structuring research data...")
        
        # Prepare enhanced context with research results
        structure_context = self.context.copy()
        structure_context.update({
            "market_research_data": self.results.get("market_research", "Limited market research data"),
            "competitor_data": self.results.get("competitor_analysis", "Limited competitor data")
        })
        
        result = self.retry_task("Data Structuring", 
                                lambda: create_single_agent_crew("data_extractor", "data_structuring_task"),
                                structure_context)
        self.results["structured_data"] = result
        return {"task": "data_structuring", "status": "completed"}

    @listen(data_structuring)
    def start_parallel_customer_analysis(self, context):
        """Start parallel customer analysis phase"""
        print("👥 Starting parallel customer profiling and insights analysis...")
        return {"phase": "parallel_customer_analysis"}

    @listen(start_parallel_customer_analysis)
    def customer_profiling(self, context):
        """Find ICP customers - runs in parallel with insights"""
        customer_context = self.context.copy()
        customer_context["structured_data"] = self.results.get("structured_data", "")
        
        result = self.retry_task("Customer Profiling", 
                                lambda: create_single_agent_crew("customer_profiler", "customer_profiling_task"),
                                customer_context)
        self.results["customer_profiles"] = result
        return {"task": "customer_profiling", "status": "completed"}

    @listen(start_parallel_customer_analysis)
    def customer_insights(self, context):
        """Analyze pain points - runs in parallel with profiling"""
        insights_context = self.context.copy()
        insights_context["structured_data"] = self.results.get("structured_data", "")
        
        result = self.retry_task("Customer Insights", 
                                lambda: create_single_agent_crew("customer_insights", "customer_insights_task"),
                                insights_context)
        self.results["customer_insights"] = result
        return {"task": "customer_insights", "status": "completed"}

    @listen((customer_profiling, customer_insights))  # ✅ FIXED: Added tuple syntax
    def final_strategy(self, contexts):
        """Create final marketing strategy"""
        print("🎯 Creating final marketing strategy...")
        
        # Prepare comprehensive context with all results
        strategy_context = self.context.copy()
        strategy_context.update({
            "market_research_data": self.results.get("market_research", ""),
            "competitor_data": self.results.get("competitor_analysis", ""),
            "structured_data": self.results.get("structured_data", ""),
            "customer_profiles": self.results.get("customer_profiles", ""),
            "customer_insights": self.results.get("customer_insights", "")
        })
        
        result = self.retry_task("Strategy Creation", 
                                lambda: create_single_agent_crew("strategy_maker", "strategy_maker_task"),
                                strategy_context)
        self.results["final_strategy"] = result
        
        # Generate comprehensive report
        self.save_report()
        
        return {"task": "final_strategy", "status": "completed", "result": result}

    def save_report(self):
        """Save comprehensive report to report.md"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# 🚀 Market Strategy Analysis Report

**Generated:** {timestamp}
**Product:** {self.context.get('product', 'N/A')}
**Industry:** {self.context.get('industry', 'N/A')}
**Region:** {self.context.get('region', 'N/A')}
**Competitors:** {self.context.get('compitators', 'N/A')}
**Target Audience:** {self.context.get('target_audance', 'N/A')}

---

## 📊 Market Research Analysis
{self.results.get('market_research', 'No data available')}

---

## 🏢 Competitor Intelligence  
{self.results.get('competitor_analysis', 'No data available')}

---

## 📋 Structured Data Insights
{self.results.get('structured_data', 'No data available')}

---

## 👥 Customer Profiling (ICP)
{self.results.get('customer_profiles', 'No data available')}

---

## 💡 Customer Insights & Pain Points
{self.results.get('customer_insights', 'No data available')}

---

## 🎯 Final Marketing Strategy
{self.results.get('final_strategy', 'No data available')}

---

*Report generated by Market Strategy AI Flow*
"""
        
        with open("report.md", "w", encoding="utf-8") as f:
            f.write(report)
        
        print("📄 Detailed report saved to report.md")

def create_single_agent_crew(agent_key, task_key):
    """Create a single-agent crew for specific task with enhanced prompts"""
    base_path = Path(__file__).resolve().parent
    config_path = base_path / "config"
    
    # Load configurations
    agents_data = load_yaml(config_path / "agents.yaml")
    tasks_data = load_yaml(config_path / "tasks.yaml")
    llm = create_llm()
    
    # Create agent with enhanced structured output capability
    agent_data = agents_data[agent_key]
    
    # Enhanced backstory for structured output
    enhanced_backstory = agent_data.get("backstory", "") + """

IMPORTANT OUTPUT REQUIREMENTS:
- Always provide structured, detailed responses in markdown format
- Use clear headings, bullet points, and organized sections
- Include specific examples and actionable insights
- Ensure all data is properly formatted and easy to read
- When analyzing data, provide clear categorization and prioritization
"""
    
    agent = Agent(
        role=agent_data.get("role", ""),
        goal=agent_data.get("goal", ""),
        backstory=enhanced_backstory,
        allow_delegation=False,
        llm=llm,
        verbose=True,
        memory=True
    )
    
    # Create task with enhanced output requirements
    task_data = tasks_data[task_key]
    
    # Enhanced description for better structured output
    enhanced_description = task_data.get("description", "") + """

OUTPUT FORMAT REQUIREMENTS:
- Structure your response with clear markdown headings
- Use bullet points for lists and key findings
- Include specific examples and data points
- Organize information in logical sections
- Provide actionable insights and recommendations
"""
    
    task = Task(
        description=enhanced_description,
        expected_output=task_data.get("expected_output", "") + "\n\nEnsure the output is well-structured with clear markdown formatting, specific examples, and actionable insights.",
        agent=agent,
        output_format="markdown"
    )
    
    # Create crew
    return Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential,
        verbose=True
    )

def create_crew():
    """Main function to create the market strategy crew"""
    
    class MarketStrategyCrew:
        def __init__(self):
            self.flow = None
            
        def kickoff(self, inputs):
            """Execute the market strategy flow with dynamic inputs"""
            print(f"🚀 Starting Market Strategy Analysis for: {inputs.get('product_description', 'Unknown Product')}")
            print(f"🎯 Industry: {inputs.get('industry', 'Not specified')}")
            print(f"🌍 Region: {inputs.get('region', 'Not specified')}")
            print(f"🏢 Competitors: {inputs.get('competitors', 'Not specified')}")
            print(f"👥 Target Audience: {inputs.get('target_audience', 'Not specified')}")
            print("-" * 60)
            
            # Create and execute flow with dynamic inputs
            self.flow = MarketStrategyFlow(inputs, max_retries=3)
            result = self.flow.kickoff()
            
            # Return final strategy for main.py
            final_strategy = self.flow.results.get("final_strategy", "Strategy generation completed with available data")
            return self.process_output(final_strategy)
            
        def process_output(self, output):
            """Process and enhance output after crew completion"""
            print("✅ Market strategy analysis completed successfully!")
            enhanced_output = f"{output}\n\n--- Analysis completed by CrewAI Market Strategy Team ---"
            return enhanced_output
    
    return MarketStrategyCrew()
