import os
import sys
import uvicorn

if __name__ == "__main__":
    # Ensure current directory is in PYTHONPATH
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        
    print(f"Starting CareerMind AI Web Server from: {project_root}")
    uvicorn.run("web_app.app:app", host="127.0.0.1", port=8000, reload=True)
