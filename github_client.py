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
    
    def enable_pages_with_actions(self, repo) -> str:
        """Enable GitHub Pages using GitHub Actions workflow (matches diagram)"""
        try:
            log_event("Creating GitHub Actions workflow for Pages deployment...", task_id=repo.name)
            
            # Step 1: Create the GitHub Actions workflow file
            workflow_content = self._get_pages_workflow()
            
            try:
                repo.create_file(
                    ".github/workflows/pages.yml",
                    "Add GitHub Pages deployment workflow",
                    workflow_content,
                    branch="main"
                )
                log_event("✅ GitHub Actions workflow created", task_id=repo.name)
            except GithubException as e:
                if "already exists" in str(e):
                    log_event("Workflow already exists", "INFO", task_id=repo.name)
                else:
                    raise
            
            # Step 2: Enable Pages via API (but workflow will handle deployment)
            api_url = f"https://api.github.com/repos/{repo.owner.login}/{repo.name}/pages"
            
            headers = {
                "Authorization": f"token {config.GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            }
            
            # Configure Pages to use GitHub Actions
            payload = {
                "source": {
                    "branch": "main",
                    "path": "/"
                },
                "build_type": "workflow"  # This tells GitHub to use Actions
            }
            
            response = requests.post(api_url, json=payload, headers=headers)
            
            if response.status_code == 201:
                log_event("✅ GitHub Pages configured to use Actions", task_id=repo.name)
            elif response.status_code == 409 or response.status_code == 422:
                # Pages might already be enabled, try to update
                log_event("Updating Pages configuration...", "INFO", task_id=repo.name)
                # Try PUT to update
                put_response = requests.put(
                    api_url,
                    json={"build_type": "workflow", "source": {"branch": "main", "path": "/"}},
                    headers=headers
                )
                if put_response.status_code in [200, 201, 204]:
                    log_event("✅ Pages configuration updated", task_id=repo.name)
                else:
                    log_event(f"Pages configuration: {put_response.status_code}", "WARNING", task_id=repo.name)
            else:
                log_event(f"Pages API response: {response.status_code}", "WARNING", task_id=repo.name)
            
            # Step 3: Trigger the workflow by making a small commit
            time.sleep(2)
            self._trigger_workflow(repo)
            
            pages_url = f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}"
            
            # Step 4: Wait for Actions to complete
            log_event("⏳ Waiting for GitHub Actions to deploy Pages...", task_id=repo.name)
            time.sleep(10)  # Give Actions time to start
            
            # Step 5: Monitor workflow status
            self._wait_for_workflow_completion(repo)
            
            log_event(f"✅ GitHub Pages URL: {pages_url}", task_id=repo.name)
            return pages_url
            
        except Exception as e:
            error_msg = f"Failed to enable GitHub Pages with Actions: {e}"
            log_event(error_msg, "ERROR", task_id=repo.name)
            # Return expected URL even if setup fails
            return f"https://{config.GITHUB_USERNAME}.github.io/{repo.name}"
    
    def _get_pages_workflow(self) -> str:
        """Generate GitHub Actions workflow for Pages deployment"""
        return """name: Deploy to GitHub Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: '.'
          
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
    
    def _trigger_workflow(self, repo):
        """Trigger workflow by making a small commit"""
        try:
            # Create or update a trigger file
            trigger_content = f"# Deployment triggered at {datetime.now().isoformat()}"
            
            try:
                # Try to get existing file
                trigger_file = repo.get_contents(".github/DEPLOYMENT_TRIGGER.md")
                repo.update_file(
                    ".github/DEPLOYMENT_TRIGGER.md",
                    "Trigger Pages deployment",
                    trigger_content,
                    trigger_file.sha,
                    branch="main"
                )
            except:
                # File doesn't exist, create it
                repo.create_file(
                    ".github/DEPLOYMENT_TRIGGER.md",
                    "Trigger Pages deployment",
                    trigger_content,
                    branch="main"
                )
            
            log_event("✅ Workflow triggered", task_id=repo.name)
        except Exception as e:
            log_event(f"Failed to trigger workflow: {e}", "WARNING", task_id=repo.name)
    
    def _wait_for_workflow_completion(self, repo, max_wait: int = 120):
        """Wait for GitHub Actions workflow to complete"""
        try:
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                # Get workflow runs
                workflows = repo.get_workflow_runs()
                
                if workflows.totalCount > 0:
                    latest_run = workflows[0]
                    status = latest_run.status
                    conclusion = latest_run.conclusion
                    
                    log_event(f"Workflow status: {status}, conclusion: {conclusion}", task_id=repo.name)
                    
                    if status == "completed":
                        if conclusion == "success":
                            log_event("✅ GitHub Actions workflow completed successfully", task_id=repo.name)
                            return True
                        else:
                            log_event(f"⚠️ Workflow completed with status: {conclusion}", "WARNING", task_id=repo.name)
                            return False
                
                time.sleep(10)  # Check every 10 seconds
            
            log_event("⏱️ Workflow still running after max wait time", "WARNING", task_id=repo.name)
            return False
            
        except Exception as e:
            log_event(f"Error monitoring workflow: {e}", "WARNING", task_id=repo.name)
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