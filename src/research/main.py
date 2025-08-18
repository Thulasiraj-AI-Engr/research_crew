import os
from dotenv import load_dotenv
from crew import create_crew

<<<<<<< Updated upstream
load_dotenv()

def main():
    crew = create_crew()

    inputs = {
        "product_description": input("Describe your product: "),
        "industry": input("Industry or category: "),
        "region": input("Target region: "),
        "competitors": input("List key competitors (comma-separated): "),
        "target_audience": input("Who is your target audience (demographics, ICP): ")
    }
=======
# Set up environment variables
def setup_environment():
    """Setup required environment variables"""
    required_env_vars = {
        'DEEPSEEK_API_KEY': 'your-deepseek-api-key',
        'SERPER_API_KEY' : 'your-serper-api-key'
    }
    for var, default in required_env_vars.items():
        if not os.getenv(var):
            print(f"⚠️  Warning: {var} not set. Using default: {default}")
            os.environ[var] = default
>>>>>>> Stashed changes

    result = crew.kickoff(inputs=inputs)
    
    with open("final_marketing_strategy.md", "w") as file:
        file.write(result)

    print("\n✅ Marketing strategy saved to final_marketing_strategy.md")
    print("📄 Detailed analysis saved to report.md")

if __name__ == "__main__":
    main()
