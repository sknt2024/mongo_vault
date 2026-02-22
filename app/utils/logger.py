from datetime import datetime

def format_log(message: str) -> str:
    timestamp = datetime.now().strftime("%H:%M:%S")
    return f"[{timestamp}] {message}"
