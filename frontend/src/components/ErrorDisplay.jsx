function ErrorDisplay({ output }) {
    const getLineClass = (line) => {
      if (line.includes('error') || line.includes('Error') || line.includes('E:')) return 'error-line';
      if (line.includes('warning') || line.includes('Warning') || line.includes('W:')) return 'warning-line';
      if (line.includes('convention') || line.includes('C:')) return 'convention-line';
      if (line.includes('refactor') || line.includes('R:')) return 'refactor-line';
      return '';
    };
  
    const formatLine = (line) => {
      // Extract line numbers and highlight message portions
      if (line.includes(':')) {
        const parts = line.split(':');
        if (parts.length >= 3) {
          // This is likely a line with file:line:col: message format
          const lineNumber = parts[1];
          const message = parts.slice(2).join(':');
          
          return (
            <>
              <span className="error-location">Line {lineNumber}:</span>
              <span className="error-message">{message}</span>
            </>
          );
        }
      }
      return line;
    };
  
    if (!output || output.trim() === '') {
      return (
        <div className="no-errors">
          <p>No issues found in your code. Great job!</p>
        </div>
      );
    }
  
    return (
      <div className="error-display">
        <h3>Details</h3>
        <div className="error-lines">
          {output.split('\n').map((line, index) => (
            <div key={index} className={`error-line ${getLineClass(line)}`}>
              {formatLine(line)}
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  export default ErrorDisplay;