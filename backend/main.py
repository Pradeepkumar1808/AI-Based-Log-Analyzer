from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

from log_parser import parse_logs
from llm_prompt import analyze_logs_with_llm
from models import LogAnalysisResponse

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Log Analyser",
    description="Analyze log files using AI to identify errors and patterns",
    version="1.0.0"
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {"message": "AI Log Analyser API is running"}

@app.post("/analyze", response_model=LogAnalysisResponse)
async def analyze_logs(file: UploadFile = File(...)):
    """
    Analyze uploaded log file using AI
    
    Args:
        file: The log file to analyze
        
    Returns:
        LogAnalysisResponse with error table, summary stats, and recommendations
    """
    try:
        # Read file content
        content = await file.read()
        log_text = content.decode('utf-8', errors='ignore')
        
        # Parse logs into chunks
        log_entries = parse_logs(log_text)
        
        # Analyze with LLM
        analysis = await analyze_logs_with_llm(log_entries)
        
        return analysis
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"detail": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
