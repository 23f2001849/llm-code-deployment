import hashlib
import uuid
import os
import base64
from datetime import datetime
from typing import List, Dict, Any
import json
from config import config

# Add this to your utils.py file, or replace the existing generate_repo_name function:

def generate_repo_name(task_id: str, email: str) -> str:
    """Generate unique repository name with timestamp"""
    import time
    email_hash = hashlib.md5(email.encode()).hexdigest()[:6]
    task_hash = hashlib.md5(task_id.encode()).hexdigest()[:6]
    timestamp = str(int(time.time()))[-6:]  # Last 6 digits of timestamp
    return f"llm-app-{task_hash}-{email_hash}-{timestamp}"

def validate_secret(secret: str) -> bool:
    """Validate the provided secret"""
    return secret in config.ALLOWED_SECRETS

def log_event(message: str, level: str = "INFO", task_id: str = None):
    """Log events with timestamp"""
    timestamp = datetime.now().isoformat()
    log_message = f"[{timestamp}] [{level}]"
    if task_id:
        log_message += f" [task:{task_id}]"
    log_message += f" {message}"
    
    print(log_message)
    
    # Also write to log file
    log_file = os.path.join(config.LOG_DIR, f"deployment_{datetime.now().strftime('%Y%m%d')}.log")
    with open(log_file, "a", encoding='utf-8') as f:
        f.write(log_message + "n")

def save_attachments(attachments: List[Dict[str, Any]]) -> List[str]:
    """Save attachments to disk and return file paths"""
    os.makedirs(config.ATTACHMENTS_DIR, exist_ok=True)
    saved_files = []
    
    for attachment in attachments:
        try:
            if attachment['url'].startswith('data:'):
                # Extract and decode base64 data
                base64_data = attachment['url'].split('base64,')[1]
                file_content = base64.b64decode(base64_data)
                
                file_path = os.path.join(config.ATTACHMENTS_DIR, attachment['name'])
                with open(file_path, 'wb') as f:
                    f.write(file_content)
                
                saved_files.append(file_path)
                log_event(f"Saved attachment: {attachment['name']}")
            else:
                log_event(f"Skipping non-data URL attachment: {attachment['name']}", "WARNING")
        except Exception as e:
            log_event(f"Failed to save attachment {attachment['name']}: {str(e)}", "ERROR")
    
    return saved_files

def cleanup_attachments(file_paths: List[str]):
    """Clean up saved attachment files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                log_event(f"Cleaned up attachment: {file_path}")
        except Exception as e:
            log_event(f"Failed to clean up {file_path}: {str(e)}", "WARNING")

def validate_request_data(data: Dict[str, Any]) -> bool:
    """Validate incoming request data"""
    required_fields = ['email', 'secret', 'task', 'round', 'nonce', 'brief', 'checks', 'evaluation_url']
    
    for field in required_fields:
        if field not in data:
            return False
    
    if not isinstance(data['checks'], list):
        return False
    
    if not isinstance(data['attachments'], list):
        return False
    
    return True

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_text_file(filename: str) -> bool:
    """Check if file is likely a text file"""
    text_extensions = {'.txt', '.md', '.json', '.csv', '.html', '.css', '.js', '.py', '.xml', '.yaml', '.yml'}
    return get_file_extension(filename) in text_extensions
