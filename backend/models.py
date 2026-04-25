from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class LogEntry(BaseModel):
    """Model for individual log entry"""
    timestamp: Optional[str] = None
    level: str
    message: str
    source: Optional[str] = None

class ErrorDetail(BaseModel):
    """Model for error details in analysis"""
    error_id: int = Field(..., description="Unique error identifier")
    message: str = Field(..., description="Error message")
    severity: str = Field(..., description="Severity level: critical, high, medium, low")
    count: int = Field(default=1, description="Number of occurrences")
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    suggested_fix: Optional[str] = None

class SummaryStats(BaseModel):
    """Model for summary statistics"""
    total_errors: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    analysis_timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class LogAnalysisResponse(BaseModel):
    """Model for complete analysis response"""
    summary: SummaryStats
    errors: List[ErrorDetail]
    recommendations: List[str] = Field(default_factory=list)
    file_info: dict = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "summary": {
                    "total_errors": 5,
                    "critical_count": 1,
                    "high_count": 2,
                    "medium_count": 2,
                    "low_count": 0,
                    "analysis_timestamp": "2024-01-01T12:00:00"
                },
                "errors": [
                    {
                        "error_id": 1,
                        "message": "Database connection timeout",
                        "severity": "critical",
                        "count": 3,
                        "suggested_fix": "Increase database connection timeout"
                    }
                ],
                "recommendations": [
                    "Check database server status",
                    "Review connection pool settings"
                ],
                "file_info": {
                    "filename": "app.log",
                    "size_bytes": 15234,
                    "lines": 342
                }
            }
        }
