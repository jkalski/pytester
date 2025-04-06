import re
import ast
import subprocess
import os
import json
import requests
from typing import Dict, List, Optional, Tuple, Any

# Dictionary of common Python error patterns and their explanations/fixes
ERROR_PATTERNS = {
    'SyntaxError: invalid syntax': {
        'explanation': 'Your code has a syntax error, which means Python cannot understand the structure.',
        'typical_fixes': ['Check for missing colons after if/for/while statements', 
                         'Make sure all parentheses, brackets, and braces are properly closed',
                         'Verify indentation is consistent']
    },
    "SyntaxError: expected ':'": {
        'explanation': 'You\'re missing a colon at the end of a line with a control statement.',
        'typical_fixes': ['Add a colon at the end of if, elif, else, for, while, def, or class statements']
    },
    'IndentationError: expected an indented block': {
        'explanation': 'After a line ending with a colon, the next line must be indented.',
        'typical_fixes': ['Add 4 spaces or a tab before the line that should be indented']
    },
    'IndentationError: unexpected indent': {
        'explanation': 'A line is indented when it shouldn\'t be.',
        'typical_fixes': ['Remove extra spaces at the beginning of the line',
                         'Make sure all lines at the same level have the same indentation']
    },
    'NameError: name .* is not defined': {
        'explanation': 'You\'re using a variable that hasn\'t been defined yet.',
        'typical_fixes': ['Check for typos in variable names',
                         'Make sure to assign a value to the variable before using it',
                         'Verify the variable is defined in the current scope']
    },
    'TypeError: .* takes \\d+ positional arguments but \\d+ were given': {
        'explanation': 'You\'re calling a function with the wrong number of arguments.',
        'typical_fixes': ['Check the function definition to see how many arguments it needs',
                         'Verify that you\'re calling the function with the correct number of arguments']
    },
    'ImportError: No module named .*': {
        'explanation': 'Python can\'t find the module you\'re trying to import.',
        'typical_fixes': ['Make sure the module name is spelled correctly',
                         'Install the module using pip: pip install module_name',
                         'Check that the module file is in the correct directory']
    },
    'ZeroDivisionError: division by zero': {
        'explanation': 'You\'re trying to divide a number by zero, which is not allowed in mathematics.',
        'typical_fixes': ['Add a condition to check if the denominator is zero before performing division',
                         'Provide an alternative value when division by zero would occur']
    },
    'IndexError: list index out of range': {
        'explanation': 'You\'re trying to access an element at an index that doesn\'t exist in the list.',
        'typical_fixes': ['Make sure the index is within the valid range (0 to len(list)-1)',
                         'Check the length of the list before accessing elements',
                         'Use a condition to verify the index exists before accessing it']
    },
    'KeyError: .*': {
        'explanation': 'You\'re trying to access a dictionary key that doesn\'t exist.',
        'typical_fixes': ['Use dict.get(key) which returns None instead of raising an error',
                         'Check if the key exists with "if key in dict:" before accessing it',
                         'Make sure the key name is spelled correctly']
    },
    'AttributeError: .* has no attribute .*': {
        'explanation': 'You\'re trying to access an attribute or method that doesn\'t exist for this object.',
        'typical_fixes': ['Check the spelling of the attribute name',
                         'Make sure you\'re using the correct object type',
                         'Verify that the attribute exists for the object you\'re using']
    },
    'E0602: Undefined variable': {
        'explanation': 'Pylint detected you\'re using a variable that hasn\'t been defined.',
        'typical_fixes': ['Define the variable before using it',
                         'Check for typos in the variable name',
                         'Make sure the variable is accessible in the current scope']
    },
    'W0611: Unused import': {
        'explanation': 'You\'ve imported a module that isn\'t used in your code.',
        'typical_fixes': ['Remove the unused import to keep your code clean',
                         'If you need the import, make sure you\'re using it somewhere in your code']
    },
    'C0103: Invalid name': {
        'explanation': 'The variable or function name doesn\'t follow Python naming conventions.',
        'typical_fixes': ['Use snake_case for variables and functions (lowercase with underscores)',
                         'Use CamelCase for class names',
                         'Use UPPERCASE for constants']
    },
    'C0111: Missing docstring': {
        'explanation': 'Your function, class, or module is missing a documentation string.',
        'typical_fixes': ['Add a descriptive docstring enclosed in triple quotes at the beginning of your function, class, or module']
    },
    'W0612: Unused variable': {
        'explanation': 'You\'ve defined a variable that isn\'t used anywhere in your code.',
        'typical_fixes': ['Remove the unused variable',
                        'If you need the variable, make sure you\'re using it somewhere in your code']
    }
}

def get_improvement_suggestions(code: str, analysis_output: str, error_count: int, warning_count: int) -> Dict[str, Any]:
    """
    Generate improvement suggestions for Python code based on the analysis output.
    Uses rule-based suggestions rather than external API calls.
    """
    # Try to parse the code to identify syntax and logical issues
    syntax_errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        syntax_errors.append({
            'line': e.lineno,
            'column': e.offset,
            'message': str(e)
        })

    # Extract error codes from the analysis output
    error_matches = []
    for line in analysis_output.split('\n'):
        # Look for various error code patterns
        pylint_match = re.search(r'([EWRFC]\d{4})', line)
        line_match = re.search(r'line (\d+)', line)
        
        if pylint_match:
            error_code = pylint_match.group(1)
            line_num = int(line_match.group(1)) if line_match else 0
            error_matches.append({
                'code': error_code,
                'line_num': line_num,
                'message': line
            })
        # Also check for standard Python error patterns
        elif any(pattern in line for pattern in ['SyntaxError', 'IndentationError', 'NameError', 'TypeError']):
            if line_match:
                line_num = int(line_match.group(1))
                error_matches.append({
                    'code': 'E9999',  # Generic error code
                    'line_num': line_num,
                    'message': line
                })

    # Apply fixes based on the identified issues
    improved_code = code
    improvements = []
    explanation = ""
    learning_tip = ""

    # Fix syntax errors first
    if syntax_errors:
        improved_code, new_improvements = fix_syntax_errors(code, syntax_errors)
        improvements.extend(new_improvements)
        explanation = "Your code has syntax errors that need to be fixed before it can run."
        learning_tip = "Always check for syntax errors first. Python won't run your code until all syntax errors are fixed."

    # Then apply fixes for pylint errors
    elif error_matches:
        improved_code, new_improvements = fix_pylint_errors(code, error_matches)
        improvements.extend(new_improvements)
        explanation = "Your code has some style and potential logical issues that should be addressed."
        learning_tip = "Following Python style guidelines makes your code more readable and less prone to errors."

    # If we didn't find specific errors but analysis reports errors
    if not improvements and (error_count > 0 or warning_count > 0):
        explanation = "The analysis found some issues in your code. Review the error messages for details."
        learning_tip = "Read error messages carefully - they often tell you exactly what's wrong and where to look."
        
        # Look for common error patterns in the raw output
        for pattern, info in ERROR_PATTERNS.items():
            if re.search(pattern, analysis_output):
                improvements.append({
                    'issue': f"Potential issue: {pattern.split(':')[0]}",
                    'solution': info['explanation'] + " " + info['typical_fixes'][0]
                })
    
    # If we still don't have improvements, give some general best practices
    if not improvements:
        if "def" in code and not re.search(r'def \w+\([^)]*\):\s*[\'"]', code):
            improvements.append({
                'issue': "Missing docstrings",
                'solution': "Add descriptive docstrings to your functions to explain what they do"
            })
        
        if re.search(r'except:', code) and not re.search(r'except [A-Za-z]+:', code):
            improvements.append({
                'issue': "Bare except clause",
                'solution': "Specify the exceptions you want to catch instead of catching all exceptions"
            })
            
        explanation = "Your code has no major issues, but here are some best practices to consider."
        learning_tip = "Even working code can be improved for readability, maintainability, and efficiency."

    # Create the response dictionary
    return {
        "improved_code": improved_code,
        "explanation": explanation or "I've analyzed your code and made some improvements.",
        "improvements": improvements or [{"issue": "No specific issues found", "solution": "Your code looks good!"}],
        "learning_tip": learning_tip or "Always test your code thoroughly, even when it looks correct."
    }

def fix_syntax_errors(code: str, errors: List[Dict]) -> Tuple[str, List[Dict]]:
    """Apply fixes to syntax errors in the code."""
    lines = code.split('\n')
    improvements = []
    
    for error in errors:
        line_num = error['line'] - 1  # 0-indexed
        message = error['message']
        
        if line_num >= len(lines):
            continue  # Skip if line number is out of range
            
        current_line = lines[line_num]
        
        # Handle missing colon
        if "expected ':'" in message:
            # More robust check for missing colon
            if not current_line.rstrip().endswith(':'):
                # Check if this is a statement that requires a colon
                if re.search(r'(if|elif|else|for|while|def|class)\b.*\S', current_line):
                    lines[line_num] = current_line.rstrip() + ':'
                    improvements.append({
                        'issue': f"Missing colon at line {error['line']}",
                        'solution': "Added missing colon after statement"
                    })
        
        # Handle unbalanced parentheses/brackets
        elif "unmatched" in message or "unclosed" in message:
            # Simple fix for common cases - not comprehensive
            if '(' in current_line and ')' not in current_line:
                lines[line_num] = current_line + ')'
                improvements.append({
                    'issue': f"Unbalanced parentheses at line {error['line']}",
                    'solution': "Added closing parenthesis"
                })
            elif '[' in current_line and ']' not in current_line:
                lines[line_num] = current_line + ']'
                improvements.append({
                    'issue': f"Unbalanced brackets at line {error['line']}",
                    'solution': "Added closing bracket"
                })
            elif '{' in current_line and '}' not in current_line:
                lines[line_num] = current_line + '}'
                improvements.append({
                    'issue': f"Unbalanced braces at line {error['line']}",
                    'solution': "Added closing brace"
                })
        
        # Handle unexpected indentation
        elif "unexpected indent" in message:
            lines[line_num] = current_line.lstrip()
            improvements.append({
                'issue': f"Incorrect indentation at line {error['line']}",
                'solution': "Removed extra indentation"
            })
        
        # Handle expected indentation
        elif "expected an indented block" in message:
            lines[line_num] = "    " + current_line
            improvements.append({
                'issue': f"Missing indentation at line {error['line']}",
                'solution': "Added required indentation"
            })
    
    return '\n'.join(lines), improvements

def fix_pylint_errors(code: str, errors: List[Dict]) -> Tuple[str, List[Dict]]:
    """Apply fixes to pylint errors in the code."""
    lines = code.split('\n')
    improvements = []
    
    for error in errors:
        error_code = error.get('code', '')
        line_num = error.get('line_num', 0) - 1  # 0-indexed
        
        if line_num >= len(lines) or line_num < 0:
            continue  # Skip if line number is out of range
            
        current_line = lines[line_num]
        
        # Handle undefined variable
        if error_code == 'E0602':
            var_match = re.search(r"Undefined variable '(\w+)'", error['message'])
            if var_match:
                var_name = var_match.group(1)
                # Add a definition above
                lines.insert(line_num, f"{var_name} = None  # TODO: Initialize with a proper value")
                # Update line numbers since we inserted a line
                line_num += 1
                improvements.append({
                    'issue': f"Undefined variable '{var_name}'",
                    'solution': f"Added a placeholder initialization. Replace 'None' with an appropriate value."
                })
        
        # Handle unused import
        elif error_code == 'W0611':
            import_match = re.search(r"Unused import (\w+)", error['message'])
            if import_match:
                import_name = import_match.group(1)
                # Comment out the import
                if f"import {import_name}" in current_line:
                    lines[line_num] = f"# {current_line}  # Unused import"
                    improvements.append({
                        'issue': f"Unused import '{import_name}'",
                        'solution': "Commented out the unused import. Remove it if not needed."
                    })
        
        # Handle invalid names
        elif error_code == 'C0103':
            name_match = re.search(r"Invalid name \"(\w+)\"", error['message'])
            if name_match:
                invalid_name = name_match.group(1)
                # Suggest snake_case for variables/functions or CamelCase for classes
                if invalid_name[0].isupper():  # Likely a class name
                    suggestion = invalid_name  # Class names should be CamelCase already
                else:
                    # Convert to snake_case
                    suggestion = re.sub(r'([A-Z])', r'_\1', invalid_name).lower()
                    suggestion = suggestion.lstrip('_')
                
                # Don't replace if already in correct format
                if suggestion != invalid_name:
                    lines[line_num] = current_line.replace(invalid_name, suggestion)
                    improvements.append({
                        'issue': f"Invalid name '{invalid_name}'",
                        'solution': f"Renamed to '{suggestion}' following Python naming conventions"
                    })
                    
        # Handle unused variable
        elif error_code == 'W0612':
            var_match = re.search(r"Unused variable '(\w+)'", error['message'])
            if var_match:
                var_name = var_match.group(1)
                # Comment out the variable assignment
                pattern = rf'\b{re.escape(var_name)}\s*='
                if re.search(pattern, current_line):
                    lines[line_num] = f"# {current_line}  # Unused variable"
                    improvements.append({
                        'issue': f"Unused variable '{var_name}'",
                        'solution': "Commented out the unused variable. Remove it if not needed."
                    })
    
    return '\n'.join(lines), improvements

def try_local_ai_suggestion(code: str, errors: str) -> Optional[Dict[str, Any]]:
    """
    Try to get suggestions from a locally running LLM service (if available).
    Returns None if the service is not available or fails.
    """
    # First try Ollama
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "codellama:7b",
                "prompt": f"""
You are PyFixer, an AI coding assistant that helps Python beginners improve their code.
Analyze this Python code and provide suggestions for improvement:

```python
{code}
```

Error analysis:
{errors}

Provide your response as JSON with:
- improved_code: A fixed version of the code
- explanation: A simple explanation of what was wrong
- improvements: A list of issues and their solutions
- learning_tip: A helpful tip related to the main error
""",
                "stream": False
            },
            timeout=5  # Short timeout in case it's not running
        )
        
        if response.status_code == 200:
            result = response.json()
            # Parse the response from the LLM to extract the JSON
            try:
                # Extract JSON from the response text
                json_str = re.search(r'\{.*\}', result['response'], re.DOTALL)
                if json_str:
                    return json.loads(json_str.group(0))
            except Exception as e:
                print(f"Error parsing Ollama JSON response: {str(e)}")
                # Fall back to rule-based
                
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama: {str(e)}")
    
    # If Ollama fails, try LocalAI
    try:
        response = requests.post(
            "http://localhost:8080/v1/chat/completions",
            json={
                "model": "codellama",
                "messages": [
                    {"role": "system", "content": "You are PyFixer, an AI coding assistant that helps Python beginners improve their code."},
                    {"role": "user", "content": f"""
Analyze this Python code and provide suggestions for improvement:

```python
{code}
```

Error analysis:
{errors}

Provide your response as JSON with:
- improved_code: A fixed version of the code
- explanation: A simple explanation of what was wrong
- improvements: A list of issues and their solutions
- learning_tip: A helpful tip related to the main error
"""}
                ],
                "temperature": 0.3
            },
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            try:
                json_str = re.search(r'\{.*\}', result['choices'][0]['message']['content'], re.DOTALL)
                if json_str:
                    return json.loads(json_str.group(0))
            except Exception as e:
                print(f"Error parsing LocalAI JSON response: {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to LocalAI: {str(e)}")
        
    # Return None if all methods fail
    return None