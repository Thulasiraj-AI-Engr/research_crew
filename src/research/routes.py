from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.research.crew import create_crew
import uvicorn

app = FastAPI()

class UserInput(BaseModel):
    product_description: str
    industry: str
    region: str
    competitors: str
    target_audience: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
    <html>
        <head>
            <title>Market Strategy Crew</title>
            <style>
                body { font-family: Arial, sans-serif; background: #f7f7f7; }
                .container { max-width: 500px; margin: 40px auto; background: #fff; padding: 32px 24px 24px 24px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
                h2 { text-align: center; margin-bottom: 24px; }
                .form-group { margin-bottom: 18px; }
                label { display: block; margin-bottom: 6px; font-weight: 500; }
                input[type="text"] { width: 100%; padding: 8px 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 1rem; }
                input[type="submit"] { width: 100%; padding: 10px; background: #0078d4; color: #fff; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; margin-top: 10px; }
                input[type="submit"]:hover { background: #005fa3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Enter Market Strategy Inputs</h2>
                <form action="/run" method="post">
                    <div class="form-group">
                        <label for="product_description">Product Description:</label>
                        <input name="product_description" id="product_description" type="text" required />
                    </div>
                    <div class="form-group">
                        <label for="industry">Industry or Category:</label>
                        <input name="industry" id="industry" type="text" required />
                    </div>
                    <div class="form-group">
                        <label for="region">Target Region:</label>
                        <input name="region" id="region" type="text" required />
                    </div>
                    <div class="form-group">
                        <label for="competitors">Key Competitors (comma-separated):</label>
                        <input name="competitors" id="competitors" type="text" required />
                    </div>
                    <div class="form-group">
                        <label for="target_audience">Target Audience (demographics, ICP):</label>
                        <input name="target_audience" id="target_audience" type="text" required />
                    </div>
                    <input type="submit" value="Run Crew" />
                </form>
            </div>
        </body>
    </html>
    """

@app.post("/run", response_class=HTMLResponse)
def run_crew(
    product_description: str = Form(...),
    industry: str = Form(...),
    region: str = Form(...),
    competitors: str = Form(...),
    target_audience: str = Form(...)
):
    crew = create_crew()
    inputs = {
        "product_description": product_description,
        "industry": industry,
        "region": region,
        "competitors": competitors,
        "target_audience": target_audience
    }
    result = crew.kickoff(inputs=inputs)
    return f"""
    <html>
        <head><title>Market Strategy Result</title></head>
        <body>
            <h2>Raw Output</h2>
            <pre>{result}</pre>
            <a href="/">Back</a>
        </body>
    </html>
    """

# To run: uvicorn src.research.routes:app --reload
if __name__ == "__main__":
    uvicorn.run("src.research.routes:app", host="127.0.0.1", port=8000, reload=True)
