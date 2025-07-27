import asyncio
import os
import json
from datetime import datetime
from typing import Dict, Any
from crew import MarketStrategyCrew

# Set up environment variables
def setup_environment():
    """Setup required environment variables"""
    required_env_vars = {
        'OPENAI_API_KEY': 'your-openai-api-key',
        'SERPER_API_KEY': 'your-serper-api-key'
    }
    
    for var, default in required_env_vars.items():
        if not os.getenv(var):
            print(f"⚠️  Warning: {var} not set. Using default: {default}")
            os.environ[var] = default

def create_config_directories():
    """Create necessary configuration directories"""
    os.makedirs('config', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

def save_results(result, inputs: Dict[str, Any], execution_time: float):
    """Save execution results to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/market_strategy_{inputs['product'].replace(' ', '_')}_{timestamp}.json"
    
    output_data = {
        "execution_info": {
            "timestamp": timestamp,
            "execution_time_seconds": execution_time,
            "product": inputs['product'],
            "target_audience": inputs['target_audance'],
            "competitors": inputs['compitators']
        },
        "results": {
            "raw_output": result.raw,
            "task_outputs": [
                {
                    "task_name": task.description[:50] + "...",
                    "agent": task.agent.role if hasattr(task, 'agent') else "Unknown",
                    "output": str(task.output) if hasattr(task, 'output') else "No output"
                }
                for task in result.tasks_output
            ] if hasattr(result, 'tasks_output') else [],
            "token_usage": result.token_usage if hasattr(result, 'token_usage') else {}
        }
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Results saved to: {filename}")
    return filename

async def run_async_analysis(inputs: Dict[str, Any]):
    """Run the market strategy analysis asynchronously"""
    print("🔄 Starting ASYNC market strategy analysis...")
    start_time = asyncio.get_event_loop().time()
    
    try:
        # Initialize crew
        market_crew = MarketStrategyCrew()
        
        # Execute analysis
        result = await market_crew.kickoff_async(inputs)
        
        # Calculate execution time
        execution_time = asyncio.get_event_loop().time() - start_time
        
        # Save results
        save_results(result, inputs, execution_time)
        
        print(f"✅ Async analysis completed in {execution_time:.2f} seconds")
        return result
        
    except Exception as e:
        print(f"❌ Error during async execution: {str(e)}")
        raise

def run_sync_analysis(inputs: Dict[str, Any]):
    """Run the market strategy analysis synchronously"""
    print("🔄 Starting SYNC market strategy analysis...")
    start_time = datetime.now()
    
    try:
        # Initialize crew
        market_crew = MarketStrategyCrew()
        
        # Execute analysis
        result = market_crew.kickoff_sync(inputs)
        
        # Calculate execution time
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # Save results
        save_results(result, inputs, execution_time)
        
        print(f"✅ Sync analysis completed in {execution_time:.2f} seconds")
        return result
        
    except Exception as e:
        print(f"❌ Error during sync execution: {str(e)}")
        raise

def get_user_inputs() -> Dict[str, Any]:
    """Get inputs from user or use defaults for testing"""
    print("📝 Enter your market strategy analysis parameters:")
    
    # You can modify these defaults or make them interactive
    default_inputs = {
        "product": "AI-powered project management software",
        "target_audance": "small to medium-sized tech companies and startups",
        "compitators": "Asana, Monday.com, Notion, ClickUp, Trello"
    }
    
    use_defaults = input(f"Use default inputs? (y/n): ").lower().strip() == 'y'
    
    if use_defaults:
        return default_inputs
    else:
        return {
            "product": input("Product name: ").strip() or default_inputs["product"],
            "target_audance": input("Target audience: ").strip() or default_inputs["target_audance"],
            "compitators": input("Competitors (comma-separated): ").strip() or default_inputs["compitators"]
        }

async def main():
    """Main execution function"""
    print("🚀 Market Strategy AI Crew - Starting Analysis")
    print("=" * 50)
    
    # Setup
    setup_environment()
    create_config_directories()
    
    # Get inputs
    inputs = get_user_inputs()
    
    print(f"\n📊 Analysis Parameters:")
    print(f"Product: {inputs['product']}")
    print(f"Target Audience: {inputs['target_audance']}")
    print(f"Competitors: {inputs['compitators']}")
    print("=" * 50)
    
    # Choose execution mode
    execution_mode = input("\nChoose execution mode (async/sync) [async]: ").lower().strip()
    execution_mode = execution_mode if execution_mode in ['async', 'sync'] else 'async'
    
    try:
        if execution_mode == 'async':
            result = await run_async_analysis(inputs)
        else:
            result = run_sync_analysis(inputs)
        
        # Display summary
        print("\n" + "=" * 50)
        print("📋 ANALYSIS SUMMARY")
        print("=" * 50)
        print(result.raw[:500] + "..." if len(result.raw) > 500 else result.raw)
        
        if hasattr(result, 'token_usage') and result.token_usage:
            print(f"\n💰 Token Usage: {result.token_usage}")
        
    except KeyboardInterrupt:
        print("\n⏹️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main())