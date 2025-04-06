import tempfile
import subprocess
import os
import re
import ast
from typing import Dict, List, Any

def analyze_python_code(code: str) -> Dict[str, Any]:
    """
    Analyze Python code for errors and quality issues.
    Returns dict with error count, error types, and raw output.
    """
    result = {
        'error_count': 0,
        'warning_count': 0,
        'error_types': {},
        'output': '',
    }
    
    # Step 1: Check for syntax errors with ast
    syntax_errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        line_num = e.lineno or 1
        col_num = e.offset or 0
        error_msg = f"Line {line_num}, Col {col_num}: SyntaxError: {e.msg}"
        result['output'] += error_msg + "\n"
        result['error_count'] = 1
        result['error_types']['syntax'] = 1
        return result  # Return early for syntax errors
    
    # Step 2: Run pylint analysis
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp:
        temp.write(code.encode())
        temp_path = temp.name
    
    try:
        pylint_output = subprocess.run(
            ['pylint', temp_path],
            capture_output=True,
            text=True
        )
        
        # Parse pylint output
        for line in pylint_output.stdout.split('\n'):
            if ':' in line:
                parts = line.split(':')
                if len(parts) >= 3:
                    error_type = parts[2].strip().split()[0]
                    if error_type.startswith('E'):
                        result['error_count'] += 1
                        result['error_types'][error_type] = result['error_types'].get(error_type, 0) + 1
                    elif error_type.startswith('W'):
                        result['warning_count'] += 1
                        result['error_types'][error_type] = result['error_types'].get(error_type, 0) + 1
                    result['output'] += line + '\n'
    
    finally:
        os.unlink(temp_path)
    
    return result
