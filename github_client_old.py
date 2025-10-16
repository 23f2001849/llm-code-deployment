import base64
import time
import requests
from github import Github, GithubException, InputGitTreeElement
from config import config
from utils import log_event
from datetime import datetime

class GitHubClient:
    def __init__(self):
        self.github = Github(config.GITHUB_TOKEN)
        self.user = self.github.get_user()
    
    def create_repo(self, repo_name: str, description: str = "LLM Generated App") -> dict:
        """Create a new GitHub repository with initial commit"""
        try:
            log_event(f"Creating repository: {repo_name}", task_id=repo_name)
            
            # Create repo WITH readme to avoid empty repo issue
            repo = self.user.create_repo(
                repo_name,
                description=description,
                private=False,
                auto_init=True,  # This creates initial commit with README
                license_template="mit"
            )
            
            # Wait for repo to be fully initialized
            time.sleep(2)
            
            log_event(f"Repository created: {repo.html_url}", task_id=repo_name)
            return {
                "repo": repo,
                "url": repo.html_url,
                "name": repo.name
            }
            
        except GithubException as e:
            error_msg = f"Failed to create repository: {e}"
            log_event(error_msg, "ERROR", task_id=repo_name)
            raise Exception(error_msg)
    
    def commit_files(self, repo, files: dict, commit_message: str = "Update application") -> str:
        """Commit multiple files to repository"""
        try:
            log_event(f"Committing {len(files)} files to repository", task_id=repo.name)
            
            # Ensure index.html exists and is valid
            if 'index.html' not in files:
                raise Exception("index.html is required but not found in generated files")
            
            # Verify index.html has minimum content
            if len(files['index.html'].strip()) < 100:
                raise Exception("index.html appears to be invalid or too small")
            
            for file_path, content in files.items():
                # Skip empty files
                if not content or not content.strip():
                    log_event(f"Skipping empty file: {file_path}", "WARNING", task_id=repo.name)
                    continue
                
                try:
                    existing_file = repo.get_contents(file_path)
                    # Update existing file
                    repo.update_file(
                        file_path,
                        commit_message,
                        content,
                        existing_file.sha,
                        branch="main"
                    )
                    log_event(f"Updated file: {file_path}", task_id=repo.name)
                except:
                    # File doesn't exist, create it
                    try:
                        repo.create_file(
                            file_path,
                            commit_message,
                            content,
                            branch="main"
                        )
                        log_event(f"Created file: {file_path}", task_id=repo.name)
                    except GithubException as e:
                        log_event(f"Failed to create {file_path}: {e}", "WARNING", task_id=repo.name)
            
            # Get the latest commit SHA
            time.sleep(1)  # Brief wait for Git to sync
            latest_commit = repo.get_branch("main").commit
            log_event(f"Files committed successfully, SHA: {latest_commit.sha}", task_id=repo.name)
            return latest_commit.sha
            
        except GithubException as e:
            error_msg = f"Failed to commit files: {e}"
            log_event(error_msg, "ERROR", task_id=repo.name)
            raise Exception(error_msg)
    
    def enable_pages(self, repo) -> str:
        """Enable GitHub Pages for the repository using REST API"""
        try:
            log_event("Enabling GitHub Pages via REST API...", task_id=repo.name)
            
            # Use GitHub REST API to enable Pages
            api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/pages"
            
            headers = {
                "Authorization": f"token {config.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            # First, check if Pages is already enabled
            get_response = requests.get(api_url, headers=headers)
            
            if get_response.status_code == 200:
                log_event("GitHub Pages already enabled", "INFO", task_id=repo.name)
                pages_data = get_response.json()
                pages_url = pages_data.get('html_url', f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}")
                log_event(f"Existing GitHub Pages URL: {pages_url}", task_id=repo.name)
                return pages_url
            
            # Enable Pages from main branch at root
            payload = {
                "source": {
                    "branch": "main",
                    "path": "/"
                }
            }
            
            # Try to enable Pages
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 201:
                log_event("GitHub Pages enabled successfully via API", task_id=repo.name)
                pages_data = response.json()
                pages_url = pages_data.get('html_url', f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}")
            elif response.status_code == 409:
                # Pages might already be enabled
                log_event("GitHub Pages may already be enabled (409 conflict)", "INFO", task_id=repo.name)
                pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}"
            else:
                log_event(f"GitHub Pages API response: {response.status_code} - {response.text}", "WARNING", task_id=repo.name)
                pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}"
            
            # Wait for Pages to initialize (GitHub takes a moment)
            log_event("Waiting for GitHub Pages to initialize...", task_id=repo.name)
            time.sleep(5)
            
            # Verify Pages is accessible
            self._verify_pages_deployment(pages_url, repo.name)
            
            log_event(f"GitHub Pages URL: {pages_url}", task_id=repo.name)
            return pages_url
            
        except Exception as e:
            error_msg = f"Failed to enable GitHub Pages: {e}"
            log_event(error_msg, "ERROR", task_id=repo.name)
            # Return expected URL even if API call fails - user can enable manually
            return f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}"
    
    def _verify_pages_deployment(self, pages_url: str, repo_name: str, max_retries: int = 3):
        """Verify that Pages deployment is accessible"""
        for i in range(max_retries):
            try:
                response = requests.get(pages_url, timeout=10)
                if response.status_code == 200:
                    log_event(f"✅ GitHub Pages is live and accessible", task_id=repo_name)
                    return True
                else:
                    log_event(f"Pages check attempt {i+1}: Status {response.status_code}", "INFO", task_id=repo_name)
            except Exception as e:
                log_event(f"Pages check attempt {i+1}: {e}", "INFO", task_id=repo_name)
            
            if i < max_retries - 1:
                time.sleep(10)  # Wait before retry
        
        log_event("⚠️ Could not verify Pages deployment, but it may take a few minutes to go live", "WARNING", task_id=repo_name)
        return False
    
    def get_latest_commit(self, repo) -> str:
        """Get the latest commit SHA from repository"""
        try:
            branch = repo.get_branch("main")
            return branch.commit.sha
        except GithubException as e:
            error_msg = f"Failed to get latest commit: {e}"
            log_event(error_msg, "ERROR", task_id=repo.name)
            raise Exception(error_msg)