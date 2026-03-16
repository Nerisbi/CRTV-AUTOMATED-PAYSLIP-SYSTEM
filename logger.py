import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/payslip_log.txt",
    level=logging.INFO,
    format="%(asctime)s| %(levelname)s | %(message)s"
)

def log_info(message):
    """Log info message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] INFO: {message}"
    
    # Print to console
    print(log_message)
    
    # Write to log file
    logging.info(message)

def log_error(message):
    """Log error message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] ERROR: {message}"
    
    # Print to console
    print(log_message)
    
    # Write to log file
    logging.error(message)

def log_warning(message):
    """Log warning message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] WARNING: {message}"
    
    # Print to console
    print(log_message)
    
    # Write to log file
    logging.warning(message)

def log_success(message):
    """Log success message to file and console"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] SUCCESS: {message}"
    
    # Print to console
    print(log_message)
    
    # Write to log file
    logging.info(f"SUCCESS: {message}")

def get_logs(log_type="payslip", lines=100):
    """Get recent log entries"""
    log_file = f"logs/{log_type}_log.txt"
    
    if not os.path.exists(log_file):
        return f"No {log_type} log file found."
    
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            # Return last N lines
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            return "".join(recent_lines)
    except Exception as e:
        return f"Error reading log file: {e}"

def clear_logs(log_type="payslip"):
    """Clear log files"""
    log_file = f"logs/{log_type}_log.txt"
    
    try:
        if os.path.exists(log_file):
            open(log_file, "w").close()
            return True
        return False
    except Exception as e:
        print(f"Failed to clear {log_file}: {e}")
        return False