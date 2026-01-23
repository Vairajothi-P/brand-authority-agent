#!/usr/bin/env python
"""Simple wrapper to run the FastAPI app"""
import sys
import os

# Add the app directory to sys.path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

if __name__ == "__main__":
    import uvicorn
    from app import app
    
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
