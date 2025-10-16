#!/usr/bin/env python3
"""
Main entry point for LLM Code Deployment API
"""

import uvicorn
from config import config

if __name__ == "__main__":
    print("🚀 Starting LLM Code Deployment API")
    print(f"📡 Server: {config.API_HOST}:{config.API_PORT}")
    print(f"🔧 Debug: {config.DEBUG}")
    print("📚 API Docs: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stopn")
    
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level="info" if config.DEBUG else "warning",
        access_log=True
    )
