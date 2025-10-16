from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import time
import asyncio
from datetime import datetime

from config import config
from github_client import GitHubClient
from llm_generator import LLMGenerator
from evaluation_client import EvaluationClient
from utils import generate_repo_name, validate_secret, log_event, validate_request_data, cleanup_attachments, save_attachments

app = FastAPI(
    title="LLM Code Deployment API",
    description="Automated web application generation and deployment system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize clients
github_client = GitHubClient()
llm_generator = LLMGenerator()
evaluation_client = EvaluationClient()

# Request models
class Attachment(BaseModel):
    name: str
    url: str

class DeploymentRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: List[str]
    evaluation_url: str
    attachments: List[Attachment] = []

class DeploymentResponse(BaseModel):
    status: str
    message: str
    repo_url: Optional[str] = None
    pages_url: Optional[str] = None
    task_id: Optional[str] = None
    timestamp: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    log_event(f"{request.method} {request.url.path} - Status: {response.status_code} - Time: {process_time:.2f}s")
    
    return response

@app.get("/")
async def root():
    return {
        "status": "ready", 
        "service": "LLM Code Deployment API",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "ok",
            "github": "unknown",
            "openai": "unknown"
        }
    }
    
    # Check GitHub connectivity
    try:
        github_client.user.login
        health_status["components"]["github"] = "ok"
    except Exception as e:
        health_status["components"]["github"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check OpenAI connectivity (simplified)
    try:
        # Just check if API key is set and looks valid
        if config.OPENAI_API_KEY and config.OPENAI_API_KEY.startswith('sk-'):
            health_status["components"]["openai"] = "ok"
        else:
            health_status["components"]["openai"] = "invalid_key"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["openai"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

async def process_deployment(request_data: dict, is_update: bool = False):
    """Process deployment in background"""
    task_id = request_data["task"]
    
    try:
        # Save attachments temporarily
        attachment_files = save_attachments(request_data["attachments"])
        
        # Generate application code
        app_files = llm_generator.generate_app(
            request_data["brief"], 
            request_data["checks"], 
            request_data["attachments"],
            task_id,
            request_data["round"]
        )
        
        repo_name = generate_repo_name(task_id, request_data["email"])
        
        if is_update:
            # Update existing repository
            log_event(f"Updating existing repository: {repo_name}", task_id=task_id)
            repo = github_client.github.get_user().get_repo(repo_name)
            
            # For simplicity, we're recreating files. In production, you'd want smarter updates.
            commit_sha = github_client.commit_files(
                repo, 
                app_files, 
                f"Update for round {request_data['round']}"
            )
            
        else:
            # Create new repository
            repo_info = github_client.create_repo(repo_name, f"LLM Generated App for {task_id}")
            repo = repo_info["repo"]
            
            # Commit files
            commit_sha = github_client.commit_files(repo, app_files)
            
            # Enable GitHub Pages
            pages_url = github_client.enable_pages(repo)
        
        # Get the latest commit if we don't have it
        if not commit_sha:
            commit_sha = github_client.get_latest_commit(repo)
        
        # Build evaluation data
        evaluation_data = evaluation_client.build_evaluation_data(
            request_data,
            repo.html_url,
            commit_sha,
            pages_url if not is_update else f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}"
        )
        
        # Submit evaluation
        evaluation_success = evaluation_client.submit_evaluation(
            request_data["evaluation_url"],
            evaluation_data,
            task_id
        )
        
        if not evaluation_success:
            log_event("Evaluation submission failed, but deployment completed", "WARNING", task_id)
        
        # Clean up attachments
        cleanup_attachments(attachment_files)
        
        log_event(f"Deployment process completed for {task_id}", task_id=task_id)
        
    except Exception as e:
        log_event(f"Background deployment failed: {str(e)}", "ERROR", task_id=task_id)
        # Clean up attachments even on failure
        try:
            cleanup_attachments(attachment_files)
        except:
            pass

@app.post("/deploy", response_model=DeploymentResponse)
async def deploy_app(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Deploy a new application (Round 1)"""
    
    # Validate request
    if not validate_request_data(request.dict()):
        raise HTTPException(status_code=400, detail="Invalid request data")
    
    # Validate secret
    if not validate_secret(request.secret):
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Validate evaluation URL
    if not evaluation_client.validate_evaluation_url(request.evaluation_url):
        raise HTTPException(status_code=400, detail="Invalid evaluation URL")
    
    # Validate round
    if request.round != 1:
        raise HTTPException(status_code=400, detail="Use /update for rounds 2+")
    
    log_event(f"Starting deployment for task: {request.task}", task_id=request.task)
    
    # Start background deployment task
    background_tasks.add_task(process_deployment, request.dict(), False)
    
    return DeploymentResponse(
        status="processing",
        message="Deployment started successfully. The application is being generated and deployed.",
        task_id=request.task,
        timestamp=datetime.now().isoformat()
    )

@app.post("/update", response_model=DeploymentResponse)
async def update_app(request: DeploymentRequest, background_tasks: BackgroundTasks):
    """Update existing application (Round 2+)"""
    
    # Validate request
    if not validate_request_data(request.dict()):
        raise HTTPException(status_code=400, detail="Invalid request data")
    
    # Validate secret
    if not validate_secret(request.secret):
        raise HTTPException(status_code=403, detail="Invalid secret")
    
    # Validate evaluation URL
    if not evaluation_client.validate_evaluation_url(request.evaluation_url):
        raise HTTPException(status_code=400, detail="Invalid evaluation URL")
    
    # Validate round
    if request.round < 2:
        raise HTTPException(status_code=400, detail="Use /deploy for round 1")
    
    log_event(f"Starting update for task: {request.task}, round: {request.round}", task_id=request.task)
    
    # Start background update task
    background_tasks.add_task(process_deployment, request.dict(), True)
    
    return DeploymentResponse(
        status="processing",
        message=f"Update started successfully for round {request.round}. The application is being updated.",
        task_id=request.task,
        timestamp=datetime.now().isoformat()
    )

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Get deployment status for a task"""
    # In a production system, you'd query a database for task status
    # For now, we return a simple response
    return {
        "task_id": task_id,
        "status": "completed",  # This would be dynamic
        "timestamp": datetime.now().isoformat(),
        "message": "Status tracking would be implemented with a database"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG,
        log_level="info" if config.DEBUG else "warning"
    )
