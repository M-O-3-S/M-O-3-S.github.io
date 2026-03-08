import subprocess
import logging
import os
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - DEPLOY - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def run_git_cmd(command):
    """Executes a git command using subprocess."""
    try:
        result = subprocess.run(
            ['git'] + command,
            cwd=REPO_DIR,
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: git {' '.join(command)}")
        logger.error(f"Error output: {e.stderr.strip()}")
        return None

def deploy_to_github():
    """Automates Git Add, Commit, and Push for updated JSON files."""
    logger.info("Starting automated Git deployment...")
    
    # Check if we are in a git repository
    status = run_git_cmd(['status', '--short'])
    if status is None:
        logger.error("Not a git repository, or Git is not installed.")
        return False
        
    if not status:
        logger.info("No changes to deploy. Directory is clean.")
        return True
        
    logger.info("Changes detected. Proceeding with deployment.")
    
    # Optional: fetch and pull safely before pushing to avoid conflicts
    # However, since this script is the single source of truth for /data, 
    # we can pull with strategy ours or just stick to safe adding.
    # We will just commit and push.
    
    date_str = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Add files 
    # We specifically want to track changes in the frontend/data directory
    run_git_cmd(['add', 'frontend/data/'])
    
    # Also add backend src/config changes if any, or general 'all'
    run_git_cmd(['add', '.'])
    
    # Commit
    commit_msg = f"Auto-Deploy: Daily DB & JSON update ({date_str})"
    run_git_cmd(['commit', '-m', commit_msg])
    logger.info(f"Committed changes: '{commit_msg}'")
    
    # Push
    logger.info("Pushing to remote origin...")
    
    # Get current branch
    current_branch = run_git_cmd(['rev-parse', '--abbrev-ref', 'HEAD'])
    if not current_branch:
        current_branch = 'main'
        
    push_result = run_git_cmd(['push', 'origin', current_branch])
    
    if push_result is not None:
        logger.info("Successfully pushed to GitHub. Deployment complete!")
        return True
    else:
        logger.error("Failed to push to GitHub.")
        return False

if __name__ == "__main__":
    deploy_to_github()
