import requests
import time
import json
from typing import Dict, Any, Optional
from config import config
from utils import log_event

class EvaluationClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'LLM-Code-Deployment/1.0'
        })
    
    def submit_evaluation(self, evaluation_url: str, data: Dict[str, Any], task_id: str) -> bool:
        """Submit evaluation data with retry logic"""
        
        log_event(f"Submitting evaluation to {evaluation_url}", task_id=task_id)
        
        for retry in range(config.MAX_RETRIES):
            try:
                log_event(f"Evaluation attempt {retry + 1}/{config.MAX_RETRIES}", task_id=task_id)
                
                response = self.session.post(
                    evaluation_url,
                    json=data,
                    headers={'Content-Type': 'application/json'},
                    timeout=config.EVALUATION_TIMEOUT
                )
                
                if response.status_code == 200:
                    log_event("✅ Evaluation submitted successfully", task_id=task_id)
                    return True
                else:
                    log_event(f"❌ Evaluation submission failed: HTTP {response.status_code}", 
                             "WARNING", task_id=task_id)
                    if response.content:
                        log_event(f"Response: {response.text[:500]}", "DEBUG", task_id=task_id)
                    
            except requests.exceptions.Timeout:
                log_event(f"❌ Evaluation submission timeout (attempt {retry + 1})", "WARNING", task_id=task_id)
            except requests.exceptions.ConnectionError:
                log_event(f"❌ Evaluation connection error (attempt {retry + 1})", "WARNING", task_id=task_id)
            except Exception as e:
                log_event(f"❌ Evaluation submission error: {e} (attempt {retry + 1})", "WARNING", task_id=task_id)
            
            # Exponential backoff
            if retry < config.MAX_RETRIES - 1:
                delay = config.RETRY_DELAYS[retry]
                log_event(f"⏳ Retrying in {delay} seconds...", task_id=task_id)
                time.sleep(delay)
        
        log_event("❌ All evaluation submission attempts failed", "ERROR", task_id=task_id)
        return False
    
    def build_evaluation_data(self, request_data: Dict[str, Any], repo_url: str, 
                            commit_sha: str, pages_url: str) -> Dict[str, Any]:
        """Build evaluation payload"""
        return {
            "email": request_data["email"],
            "task": request_data["task"],
            "round": request_data["round"],
            "nonce": request_data["nonce"],
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url
        }
    
    def validate_evaluation_url(self, evaluation_url: str) -> bool:
        """Validate evaluation URL format"""
        if not evaluation_url:
            return False
        
        # Basic URL validation
        if not (evaluation_url.startswith('http://') or evaluation_url.startswith('https://')):
            return False
        
        return True
