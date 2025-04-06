import { highlight, languages } from 'prismjs';
import 'prismjs/components/prism-python';

function Suggestions({ suggestions }) {
  if (!suggestions) {
    return null;
  }

  // Format code with syntax highlighting
  const highlightedCode = highlight(
    suggestions.improved_code || '',
    languages.python,
    'python'
  );

  return (
    <div className="suggestions-container">
      <div className="suggestion-explanation">
        <h3>What Was Wrong?</h3>
        <p>{suggestions.explanation}</p>
        
        <h3>Learning Tip</h3>
        <div className="learning-tip">
          <p>{suggestions.learning_tip}</p>
        </div>
      </div>
      
      <div className="suggestion-code">
        <h3>Improved Code</h3>
        <pre 
          className="code-block"
          dangerouslySetInnerHTML={{ __html: highlightedCode }}
        />
      </div>
      
      <div className="suggestion-improvements">
        <h3>Key Improvements</h3>
        <ul className="improvements-list">
          {suggestions.improvements && suggestions.improvements.map((improvement, index) => (
            <li key={index} className="improvement-item">
              <div className="improvement-issue">
                <strong>Issue:</strong> {improvement.issue}
              </div>
              <div className="improvement-solution">
                <strong>Solution:</strong> {improvement.solution}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default Suggestions;