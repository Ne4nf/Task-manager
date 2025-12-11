"""
Repomix Integration Utility
Runs repomix to pack Git repositories into a single file for AI analysis
"""
import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse


class RepomixRunner:
    """Handles execution of repomix on Git repositories"""
    
    ALLOWED_HOSTS = [
        "github.com",
        "gitlab.com",
        "bitbucket.org"
    ]
    
    def __init__(self):
        """Initialize Repomix runner"""
        self.temp_dir = None
    
    def validate_git_url(self, git_url: str) -> bool:
        """
        Validate Git URL is from allowed hosts
        
        Args:
            git_url: Git repository URL
        
        Returns:
            True if valid, raises ValueError otherwise
        """
        try:
            parsed = urlparse(git_url)
            hostname = parsed.netloc.lower()
            
            # Remove 'www.' prefix if exists
            if hostname.startswith('www.'):
                hostname = hostname[4:]
            
            if hostname not in self.ALLOWED_HOSTS:
                raise ValueError(
                    f"Repository host '{hostname}' is not allowed. "
                    f"Allowed hosts: {', '.join(self.ALLOWED_HOSTS)}"
                )
            
            return True
        except Exception as e:
            raise ValueError(f"Invalid Git URL: {str(e)}")
    
    def extract_repo_info(self, git_url: str) -> Tuple[str, str]:
        """
        Extract repository owner and name from Git URL
        
        Args:
            git_url: Git repository URL
        
        Returns:
            Tuple of (owner, repo_name)
        """
        # Parse URL: https://github.com/owner/repo.git
        parsed = urlparse(git_url)
        path = parsed.path.strip('/')
        
        # Remove .git suffix
        if path.endswith('.git'):
            path = path[:-4]
        
        parts = path.split('/')
        if len(parts) >= 2:
            owner = parts[0]
            repo_name = parts[1]
            return owner, repo_name
        else:
            raise ValueError(f"Cannot extract repo info from URL: {git_url}")
    
    def run_repomix_remote(
        self,
        git_url: str,
        branch: str = "main",
        access_token: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Run repomix on a remote Git repository
        
        Args:
            git_url: Git repository URL (https)
            branch: Branch to analyze
            access_token: GitHub access token for private repos
            output_dir: Custom output directory (optional)
        
        Returns:
            Tuple of (output_file_path, packed_content)
        
        Raises:
            RuntimeError: If repomix execution fails
            ValueError: If URL is invalid
        """
        # Validate URL
        self.validate_git_url(git_url)
        
        # Extract repo info
        owner, repo_name = self.extract_repo_info(git_url)
        
        # Create temp directory if not specified
        if output_dir is None:
            self.temp_dir = tempfile.mkdtemp(prefix="repomix_")
            output_dir = self.temp_dir
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Prepare Git URL with token if private
        repo_url = git_url
        if access_token:
            # Insert token into URL: https://token@github.com/owner/repo.git
            parsed = urlparse(git_url)
            repo_url = f"{parsed.scheme}://{access_token}@{parsed.netloc}{parsed.path}"
        
        # Build repomix command
        # repomix --remote https://github.com/owner/repo --output output.xml
        output_file = output_path / f"{repo_name}_{branch}.xml"
        
        cmd = [
            "npx",  # Use npx to run repomix without global install
            "repomix",
            "--remote", repo_url,
            "--output", str(output_file),
            "--style", "xml",  # XML format for better parsing
        ]
        
        # Add branch if specified
        if branch and branch != "main":
            cmd.extend(["--branch", branch])
        
        try:
            # Run repomix
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=output_dir
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                raise RuntimeError(f"Repomix failed: {error_msg}")
            
            # Check if output file exists
            if not output_file.exists():
                raise RuntimeError(f"Repomix did not create output file: {output_file}")
            
            # Read packed content
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(output_file, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            if not content or len(content) < 100:
                raise RuntimeError("Repomix output is empty or too small")
            
            return str(output_file), content
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("Repomix execution timed out after 5 minutes")
        except Exception as e:
            raise RuntimeError(f"Failed to run repomix: {str(e)}")
    
    def cleanup(self):
        """Clean up temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                print(f"Warning: Failed to cleanup temp directory: {e}")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.cleanup()


def run_repomix_on_repo(
    git_url: str,
    branch: str = "main",
    access_token: Optional[str] = None
) -> str:
    """
    Convenience function to run repomix and get packed content
    
    Args:
        git_url: Git repository URL
        branch: Branch to analyze
        access_token: GitHub access token for private repos
    
    Returns:
        Packed repository content as string
    """
    runner = RepomixRunner()
    try:
        _, content = runner.run_repomix_remote(git_url, branch, access_token)
        return content
    finally:
        runner.cleanup()
