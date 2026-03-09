"""
FastAPI application entry point.
Запуск: python main.py
"""
import sys
from pathlib import Path

# Добавляем src/ в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

import uvicorn
from src.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

