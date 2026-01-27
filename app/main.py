#!/usr/bin/env python
"""Simple wrapper to run the FastAPI app"""
import sys
import os

# Add the parent directory to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

if __name__ == "__main__":
    import uvicorn
    import app as app_module
    
    uvicorn.run(app_module.app, host="127.0.0.1", port=8001, log_level="info")
