import os
import inspect
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

LOGS_DIR = os.getenv("LOGS_DIR", "logs")
session_files = {}

def get_session_log_file(session_name: str) -> str:
    # If a specific log file is configured in the environment, use it directly
    env_log_file = os.getenv("SESSION_LOG_FILE")
    if env_log_file:
        return env_log_file

    # Normalize session_name to prevent directory traversal or malformed paths
    normalized_name = "".join(c for c in session_name if c.isalnum() or c in "_-").strip()
    if not normalized_name:
        normalized_name = "default"
        
    if normalized_name not in session_files:
        os.makedirs(LOGS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{normalized_name}.log"
        session_files[normalized_name] = os.path.join(LOGS_DIR, filename)
        
    return session_files[normalized_name]

def log_message(session_name: str, level: str, message: str):
    filepath = get_session_log_file(session_name)
    time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    # Trace the caller script name and function name
    caller_file = "unknown"
    caller_func = "unknown"
    caller_line = 0
    
    try:
        stack = inspect.stack()
        for frame_info in stack:
            frame_file = os.path.basename(frame_info.filename)
            if frame_file != "logger.py":
                caller_file = frame_file
                caller_func = frame_info.function
                caller_line = frame_info.lineno
                break
    except Exception:
        pass

    log_line = f"[{time_str}] [{level}] [{caller_file}:{caller_func}:{caller_line}] {message}\n"
    
    # Print to stdout in addition to writing to the file
    print(f"[{level}] [{caller_file}:{caller_func}:{caller_line}] {message}")
    
    with open(filepath, "a", encoding="utf-8") as f:
        f.write(log_line)

def log_info(session_name: str, message: str):
    log_message(session_name, "INFO", message)

def log_error(session_name: str, message: str):
    log_message(session_name, "ERROR", message)

