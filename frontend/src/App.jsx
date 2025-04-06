import { useState } from 'react';
import CodeEditor from './components/CodeEditor';
import ErrorDisplay from './components/ErrorDisplay';
import Suggestions from './components/Suggestions';
import './styles.css';

function App() {
  const [code, setCode] = useState('# Write your Python code here\ndef hello():\n    print("Hello, World!")\n\nhello()');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleCodeChange = (newCode) => {
    setCode(newCode);
  };

  const handleAnalyze = async () => {
    if (!code.trim()) {
      setError('Please enter some code to analyze');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const response = await fetch('http://localhost:5000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code }),
      });

      if (!response.ok) {
        throw new Error('Server error: ' + response.statusText);
      }

      const data = await response.json();
      setAnalysisResult(data);
    } catch (err) {
      console.error('Error analyzing code:', err);
      setError('Error analyzing code: ' + err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>PyFixer</h1>
        <p className="tagline">Learn Python by fixing errors and improving your code</p>
      </header>

      <main className="main-content">
        <section className="code-section">
          <h2>Your Python Code</h2>
          <CodeEditor 
            code={code} 
            onChange={handleCodeChange} 
          />
          <div className="controls">
            <button 
              className="analyze-button" 
              onClick={handleAnalyze}
              disabled={isLoading}
            >
              {isLoading ? 'Analyzing...' : 'Analyze Code'}
            </button>
          </div>
          {error && <div className="error-message">{error}</div>}
        </section>

        {analysisResult && (
          <>
            <section className="results-section">
              <h2>Analysis Results</h2>
              <div className="metrics">
                <div className="metric">
                  <span className="metric-value">{analysisResult.error_count}</span>
                  <span className="metric-label">Errors</span>
                </div>
                <div className="metric">
                  <span className="metric-value">{analysisResult.warning_count}</span>
                  <span className="metric-label">Warnings</span>
                </div>
              </div>
              
              <ErrorDisplay output={analysisResult.output} />
            </section>

            {analysisResult.suggestions && (
              <section className="suggestions-section">
                <h2>Improvements</h2>
                <Suggestions suggestions={analysisResult.suggestions} />
              </section>
            )}
          </>
        )}
      </main>
      
      <footer className="app-footer">
        <p>PyFixer - Learn Python by fixing errors and improving your code</p>
      </footer>
    </div>
  );
}

export default App;