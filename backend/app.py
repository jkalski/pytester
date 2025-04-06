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
    pylint_result = run_pylint_analysis(code)
    result['output'] = pylint_result['output']
    
    # Count different types of issues from pylint output
    result['error_count'] = pylint_result['error_count']
    result['warning_count'] = pylint_result['warning_count']
    result['error_types'] = pylint_result['error_types']
    
    # Step 3: Check for logical errors and other issues
    logical_issues = check_logical_issues(code)
    if logical_issues['output']:
        result['output'] += "\n" + logical_issues['output']
        result['error_count'] += logical_issues['error_count']
        result['warning_count'] += logical_issues['warning_count']
        
        # Merge error types
        for error_type, count in logical_issues['error_types'].items():
            result['error_types'][error_type] = result['error_types'].get(error_type, 0) + count
    
    return result

def run_pylint_analysis(code: str) -> Dict[str, Any]:
    """Run pylint on the provided code and return the results."""
    result = {
        'error_count': 0,
        'warning_count': 0,
        'error_types': {},
        'output': '',
    }
    
    with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
        temp_file.write(code.encode())
        temp_file_path = temp_file.name
    
    try:
        # Run pylint with customized options
        process = subprocess.Popen(
            [
                'pylint',
                '--output-format=text',
                temp_file_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()
        
        pylint_output = stdout.decode()
        result['output'] = pylint_output
        
        # Count and categorize issues
        error_count = 0
        warning_count = 0
        error_types = {}
        
        for line in pylint_output.split('\n'):
            # Check for message codes like E0602 (undefined variable)
            if ':' in line:
                # Extract code like E0602, C0103, etc.
                match = re.search(r'([EWRFC]\d{4})', line)
                if match:
                    code = match.group(1)
                    category = code[0]
                    
                    # Categorize by first letter
                    if category == 'E' or category == 'F':  # Error or Fatal
                        error_count += 1
                        category_name = 'error'
                    elif category == 'W':  # Warning
                        warning_count += 1
                        category_name = 'warning'
                    else:  # Convention or Refactor
                        warning_count += 1
                        category_name = 'style'
                    
                    # Add to error types dictionary
                    error_types[category_name] = error_types.get(category_name, 0) + 1
        
        result['error_count'] = error_count
        result['warning_count'] = warning_count
        result['error_types'] = error_types
    
    except Exception as e:
        result['output'] = f"Error running pylint: {str(e)}"
        result['error_count'] = 1
        result['error_types']['system'] = 1
    
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)
    
    return result

def check_logical_issues(code: str) -> Dict[str, Any]:
    """
    Check for logical errors and other issues that pylint might miss.
    This is a simpler check to supplement pylint.
    """
    result = {
        'error_count': 0,
        'warning_count': 0,
        'error_types': {},
        'output': '',
    }
    
    issues = []
    
    # Parse the AST for deeper analysis
    try:
        tree = ast.parse(code)
        
        # Check for division by zero risks
        division_by_zero = check_division_by_zero(tree)
        if division_by_zero:
            issues.append("Potential division by zero detected. Always check if divisor is zero before division.")
            result['warning_count'] += 1
            result['error_types']['logic'] = result['error_types'].get('logic', 0) + 1
        
        # Check for unreachable code
        unreachable = check_unreachable_code(tree)
        if unreachable:
            issues.append("Unreachable code detected. Code after return/break/continue statements will never execute.")
            result['warning_count'] += 1
            result['error_types']['logic'] = result['error_types'].get('logic', 0) + 1
        
        # Check for mutable default arguments
        mutable_defaults = check_mutable_default_args(tree)
        if mutable_defaults:
            issues.append("Mutable default argument detected. Using mutable objects as default arguments can lead to unexpected behavior.")
            result['warning_count'] += 1
            result['error_types']['logic'] = result['error_types'].get('logic', 0) + 1
            
    except Exception as e:
        # If AST parsing fails (which should be rare since we already checked syntax)
        # we'll just skip these additional checks
        pass
    
    # Build output
    if issues:
        result['output'] = "Additional logical checks:\n" + "\n".join(f"- {issue}" for issue in issues)
    
    return result

def check_division_by_zero(tree: ast.AST) -> bool:
    """Check for potential division by zero."""
    class DivisionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_risky_division = False
        
        def visit_BinOp(self, node):
            # Check for division operations
            if isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
                # Check if right operand is a constant zero
                if isinstance(node.right, ast.Constant) and node.right.value == 0:
                    self.has_risky_division = True
                # Check for more complex cases would require data flow analysis
            
            # Continue visiting
            self.generic_visit(node)
    
    visitor = DivisionVisitor()
    visitor.visit(tree)
    return visitor.has_risky_division

def check_unreachable_code(tree: ast.AST) -> bool:
    """Check for unreachable code after return/break/continue."""
    class UnreachableVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_unreachable = False
        
        def visit_FunctionDef(self, node):
            # Check function body for unreachable code
            has_return = False
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, ast.Return):
                    has_return = True
                elif has_return and i < len(node.body) - 1:
                    self.has_unreachable = True
                    break
            
            # Continue visiting
            self.generic_visit(node)
    
    visitor = UnreachableVisitor()
    visitor.visit(tree)
    return visitor.has_unreachable

def check_mutable_default_args(tree: ast.AST) -> bool:
    """Check for mutable default arguments in function definitions."""
    class MutableDefaultVisitor(ast.NodeVisitor):
        def __init__(self):
            self.has_mutable_default = False
        
        def visit_FunctionDef(self, node):
            for arg in node.args.defaults:
                # Check if default is a list, dict, or set literal
                if isinstance(arg, (ast.List, ast.Dict, ast.Set)):
                    self.has_mutable_default = True
                    break
            
            # Continue visiting
            self.generic_visit(node)
    
    visitor = MutableDefaultVisitor()
    visitor.visit(tree)
    return visitor.has_mutable_default