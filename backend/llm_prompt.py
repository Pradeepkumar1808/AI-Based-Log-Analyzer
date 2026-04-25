import os
from openai import AsyncOpenAI
from typing import List, Dict
from models import LogAnalysisResponse, ErrorDetail, SummaryStats
import json

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def analyze_logs_with_llm(log_chunks: List[Dict]) -> LogAnalysisResponse:
    """
    Send log chunks to OpenAI API for analysis
    
    Args:
        log_chunks: List of log chunks from parser
        
    Returns:
        LogAnalysisResponse with AI-generated analysis
    """
    
    # Combine chunks for analysis (limit to reasonable size)
    combined_logs = "\n".join([chunk.get("content", "") for chunk in log_chunks[:10]])
    
    prompt = build_analysis_prompt(combined_logs)
    
    try:
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert system administrator and log analyzer. Analyze the provided logs and identify errors, their severity, and recommend fixes. Return a JSON response."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        # Parse LLM response
        response_text = response.choices[0].message.content
        analysis = parse_llm_response(response_text)
        
        return analysis
    
    except Exception as e:
        # Fallback response on API error
        return create_fallback_response(str(e))

def build_analysis_prompt(log_content: str) -> str:
    """
    Build the prompt for log analysis
    
    Args:
        log_content: The log text to analyze
        
    Returns:
        Formatted prompt string
    """
    
    return f"""Analyze the following logs and provide a comprehensive error analysis. 
Return a JSON response with this exact structure:
{{
    "summary": {{
        "total_errors": number,
        "critical_count": number,
        "high_count": number,
        "medium_count": number,
        "low_count": number
    }},
    "errors": [
        {{
            "error_id": number,
            "message": "error message",
            "severity": "critical|high|medium|low",
            "count": number,
            "suggested_fix": "suggested solution"
        }}
    ],
    "recommendations": ["recommendation 1", "recommendation 2"]
}}

LOGS TO ANALYZE:
{log_content}

Provide only the JSON response, no other text."""

def parse_llm_response(response_text: str) -> LogAnalysisResponse:
    """
    Parse LLM response into LogAnalysisResponse object
    
    Args:
        response_text: Raw response from LLM
        
    Returns:
        Parsed LogAnalysisResponse
    """
    try:
        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            data = json.loads(json_str)
            
            # Create response objects
            summary = SummaryStats(**data.get("summary", {}))
            errors = [ErrorDetail(**error) for error in data.get("errors", [])]
            recommendations = data.get("recommendations", [])
            
            return LogAnalysisResponse(
                summary=summary,
                errors=errors,
                recommendations=recommendations
            )
    except Exception as e:
        print(f"Error parsing LLM response: {e}")
    
    return create_fallback_response("Failed to parse analysis")

def create_fallback_response(error_msg: str) -> LogAnalysisResponse:
    """
    Create a fallback response when analysis fails
    
    Args:
        error_msg: Error message to include
        
    Returns:
        Empty LogAnalysisResponse with error info
    """
    return LogAnalysisResponse(
        summary=SummaryStats(
            total_errors=0,
            critical_count=0,
            high_count=0,
            medium_count=0,
            low_count=0
        ),
        errors=[],
        recommendations=[f"Error during analysis: {error_msg}"]
    )
