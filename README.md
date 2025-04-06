# PyFixer

PyFixer is an educational tool designed to help people learn Python by analyzing their code, identifying errors, and providing intelligent suggestions for improvement.

## Features

- Paste Python code and get immediate analysis
- See detailed error information and counts
- Receive intelligent suggestions for code improvement
- Learn from beginner-friendly explanations and tips

## Project Structure

- `backend/`: Flask server that performs code analysis and provides improvement suggestions
- `frontend/`: React application for the user interface

## Getting Started

### Prerequisites

- Python 3.8 or newer
- Node.js 14 or newer
- (Optional) Ollama or LocalAI for enhanced code suggestions

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Start the backend server:
   ```
   python app.py
   ```
   The server will run on http://localhost:5000

### (Optional) Enhanced Code Suggestions

PyFixer can use locally running LLM services for more advanced code suggestions if available:

#### Option 1: Ollama
1. Install [Ollama](https://ollama.ai/) following their website instructions
2. Pull the CodeLlama model:
   ```
   ollama pull codellama:7b
   ```
3. Run Ollama before starting PyFixer

#### Option 2: LocalAI
1. Install [LocalAI](https://github.com/go-skynet/LocalAI) following their instructions
2. Configure it to use a code-specialized model like CodeLlama
3. Run LocalAI before starting PyFixer

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm run dev
   ```
   The frontend will run on http://localhost:3000

## How to Use

1. Write or paste Python code in the editor
2. Click "Analyze Code"
3. View errors and warnings
4. Read the suggestions and explanations
5. Learn from the improvement tips
6. Apply the suggested changes

## Development

This project is intended as an educational tool. Feel free to extend it with new features or improve the existing ones.

## License

MIT License