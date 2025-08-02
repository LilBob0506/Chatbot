import threading
import uvicorn
from main import app

def run_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

def start_fastapi_server():
    # Start FastAPI in a daemon thread
    server_thread = threading.Thread(target=run_fastapi, daemon=True)
    server_thread.start()
