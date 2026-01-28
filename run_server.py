#!/usr/bin/env python
"""Run the FastAPI server"""
import sys
import os

# Add app directory to path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

if __name__ == "__main__":
    import uvicorn
    from __init__ import app
    
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")
