import { useEffect } from 'react';
import Editor from 'react-simple-code-editor';
import { highlight, languages } from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism.css';

function CodeEditor({ code, onChange }) {
  useEffect(() => {
    // Load Prism.js syntax highlighting
    if (window.Prism) {
      window.Prism.highlightAll();
    }
  }, [code]);

  const handleChange = (newCode) => {
    onChange(newCode);
  };

  return (
    <div className="code-editor-container">
      <Editor
        value={code}
        onValueChange={handleChange}
        highlight={code => highlight(code, languages.python, 'python')}
        padding={10}
        style={{
          fontFamily: '"Fira code", "Fira Mono", monospace',
          fontSize: 14,
          backgroundColor: '#f5f5f5',
          borderRadius: '4px',
          minHeight: '300px',
        }}
        className="code-editor"
      />
    </div>
  );
}

export default CodeEditor;