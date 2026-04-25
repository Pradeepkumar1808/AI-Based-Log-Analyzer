import re
from datetime import datetime
from typing import List, Dict

def parse_logs(log_text: str, chunk_size: int = 5000) -> List[Dict[str, str]]:
    """
    Parse log file into structured entries and chunks for processing
    
    Args:
        log_text: Raw log file content
        chunk_size: Number of characters per chunk for LLM processing
        
    Returns:
        List of log entries/chunks with metadata
    """
    
    # Split by common log patterns (timestamps, log levels)
    log_pattern = r'(\d{4}-\d{2}-\d{2}|\d{2}:\d{2}:\d{2}|ERROR|WARN|INFO|DEBUG)'
    
    entries = []
    chunks = []
    
    # Split into manageable chunks for LLM
    for i in range(0, len(log_text), chunk_size):
        chunk = log_text[i:i + chunk_size]
        chunks.append({
            "chunk_id": i // chunk_size,
            "content": chunk,
            "start_pos": i,
            "end_pos": min(i + chunk_size, len(log_text))
        })
    
    # Also extract individual error lines
    lines = log_text.split('\n')
    for line in lines:
        if any(keyword in line.upper() for keyword in ['ERROR', 'FAIL', 'CRITICAL', 'EXCEPTION']):
            entries.append({
                "type": "error",
                "content": line,
                "severity": determine_severity(line)
            })
    
    return chunks if chunks else entries

def determine_severity(log_line: str) -> str:
    """
    Determine severity level from log line
    
    Args:
        log_line: A single log line
        
    Returns:
        Severity level: 'critical', 'high', 'medium', or 'low'
    """
    line_upper = log_line.upper()
    
    if any(keyword in line_upper for keyword in ['CRITICAL', 'FATAL', 'PANIC']):
        return 'critical'
    elif any(keyword in line_upper for keyword in ['ERROR', 'EXCEPTION']):
        return 'high'
    elif any(keyword in line_upper for keyword in ['WARN', 'WARNING']):
        return 'medium'
    else:
        return 'low'
