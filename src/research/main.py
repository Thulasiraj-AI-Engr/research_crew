import os
from dotenv import load_dotenv
from src.research.crew import create_crew

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

    result = crew.kickoff(inputs=inputs)
    
    with open("final_marketing_strategy.md", "w") as file:
        file.write(result)

    print("\n✅ Marketing strategy saved to final_marketing_strategy.md")
    print("📄 Detailed analysis saved to report.md")

if __name__ == "__main__":
    main()
