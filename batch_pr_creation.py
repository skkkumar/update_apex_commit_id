#!/usr/bin/env python3
"""
Batch PR Creation Script
This script automates PR creation for multiple PyTorch and Apex branch pairs.

Usage:
    python3 batch_pr_creation.py --pytorch-repo-url https://github.com/skkkumar/pytorch
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from typing import List, Dict, Tuple


class BatchPRCreation:
    def __init__(self):
        self.workspace_root = Path("/home/sriram/Documents/Workspace")
        self.pytorch_repo = self.workspace_root / "office" / "sriram-pytorch" / "pytorch"
        self.apex_repo = self.workspace_root / "office" / "apex"
        
        # Compatible branch pairs: (apex_branch, pytorch_branch)
        self.branch_pairs = [
            ("release/1.8.0", "release/2.8"),
            ("release/1.7.0", "release/2.7"),
            ("release/1.6.0", "release/2.6"),
            ("release/1.5.0", "release/2.5"),
            ("release/1.4.0", "release/2.4"),
        ]
        
        self.results = []
        self.pytorch_repo_url = None
    
    def set_pytorch_repo_url(self, url: str):
        """Set the PyTorch repository URL"""
        self.pytorch_repo_url = url
    
    def run_git_command(self, repo_path: Path, command: List[str], description: str = "") -> bool:
        """Run a git command in the specified repository"""
        try:
            print(f"Running: git {' '.join(command)} in {repo_path}")
            if description:
                print(f"Description: {description}")
                
            result = subprocess.run(
                ["git"] + command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Error running git command: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            return False
    
    def verify_repo_exists(self, repo_path: Path, repo_name: str) -> bool:
        """Verify that the repository exists and is a git repository"""
        if not repo_path.exists():
            print(f"Error: {repo_name} repository not found at {repo_path}")
            return False
            
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            print(f"Error: {repo_path} is not a git repository")
            return False
            
        print(f"✓ {repo_name} repository found at {repo_path}")
        return True
    
    def get_current_branch(self, repo_path: Path) -> str:
        """Get the current branch name"""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "unknown"
    
    def get_primary_remote(self, repo_path: Path) -> str:
        """Get the primary remote name (upstream if exists, otherwise origin)"""
        try:
            result = subprocess.run(
                ["git", "remote"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            remotes = result.stdout.strip().split('\n')
            
            # Prefer upstream if it exists (for forked repos), otherwise use origin
            if 'upstream' in remotes:
                return 'upstream'
            elif 'origin' in remotes:
                return 'origin'
            else:
                return remotes[0] if remotes else 'origin'
        except subprocess.CalledProcessError:
            return 'origin'
    
    def has_uncommitted_changes(self, repo_path: Path) -> bool:
        """Check if there are uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            return False
    
    def checkout_branch(self, repo_path: Path, branch_name: str, repo_name: str) -> bool:
        """Checkout a specific branch"""
        print(f"\n--- Checking out {repo_name} to branch: {branch_name} ---")
        
        current_branch = self.get_current_branch(repo_path)
        print(f"Current branch: {current_branch}")
        
        # Get primary remote
        primary_remote = self.get_primary_remote(repo_path)
        print(f"Using remote: {primary_remote}")
        
        # First, pull latest changes on current branch before switching
        print(f"Pulling latest changes on current branch {current_branch}...")
        if not self.run_git_command(repo_path, ["pull"], f"Pulling latest changes on {current_branch}"):
            print(f"Warning: Failed to pull latest changes on {current_branch}, but continuing...")
        
        # Fetch latest changes
        if not self.run_git_command(repo_path, ["fetch", primary_remote], f"Fetching latest changes from {primary_remote}"):
            return False
        
        # Check if branch exists locally
        try:
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            branch_exists = bool(result.stdout.strip())
        except subprocess.CalledProcessError:
            branch_exists = False
        
        if branch_exists:
            print(f"Branch {branch_name} exists locally, checking out...")
        else:
            print(f"Branch {branch_name} doesn't exist locally, creating from {primary_remote}/{branch_name}...")
        
        # Stash any uncommitted changes
        if self.has_uncommitted_changes(repo_path):
            print("Stashing uncommitted changes...")
            if not self.run_git_command(repo_path, ["stash", "push"], "Stashing uncommitted changes"):
                return False
        
        # Checkout the branch
        if not self.run_git_command(repo_path, ["checkout", branch_name], f"Switching to {branch_name}"):
            return False
        
        # Pop stashed changes if any
        if self.has_uncommitted_changes(repo_path):
            print("Popping stashed changes...")
            if not self.run_git_command(repo_path, ["stash", "pop"], "Restoring stashed changes"):
                return False
        
        # Pull latest changes on the target branch
        print(f"Pulling latest changes on target branch {branch_name}...")
        if not self.run_git_command(repo_path, ["pull"], f"Pulling latest changes on {branch_name}"):
            return False
        
        print(f"✓ Successfully checked out {repo_name} to {branch_name}")
        return True
    
    def run_single_pr_creation(self, apex_branch: str, pytorch_branch: str) -> Dict:
        """Run PR creation for a single branch pair"""
        print(f"\n{'='*80}")
        print(f"🚀 PROCESSING: Apex {apex_branch} → PyTorch {pytorch_branch}")
        print(f"{'='*80}")
        
        result = {
            "apex_branch": apex_branch,
            "pytorch_branch": pytorch_branch,
            "success": False,
            "error": None,
            "pr_url": None,
            "branch_name": None
        }
        
        try:
            # Step 1: Checkout branches
            if not self.checkout_branch(self.pytorch_repo, pytorch_branch, "PyTorch"):
                result["error"] = f"Failed to checkout PyTorch branch {pytorch_branch}"
                return result
            
            if not self.checkout_branch(self.apex_repo, apex_branch, "Apex"):
                result["error"] = f"Failed to checkout Apex branch {apex_branch}"
                return result
            
            # Step 2: Run the PR creation script
            branch_name = f"updated_related_commit_{pytorch_branch.replace('/', '_')}"
            result["branch_name"] = branch_name
            
            # Construct the command
            cmd = [
                sys.executable, "pr_creation_script.py",
                "--pytorch-branch", pytorch_branch,
                "--apex-branch", apex_branch,
                "--pytorch-repo-url", self.pytorch_repo_url,
                "--push-and-create-pr",
                "--open-browser"
            ]
            
            print(f"\n🔧 Running PR creation script...")
            print(f"Command: {' '.join(cmd)}")
            
            # Run the script
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path.cwd()
            )
            
            # Check if script ran successfully
            if process.returncode == 0:
                result["success"] = True
                print(f"✅ Successfully created PR for {apex_branch} → {pytorch_branch}")
                
                # Extract PR URL from output
                output_lines = process.stdout.split('\n')
                for line in output_lines:
                    if "PR URL:" in line and self.pytorch_repo_url in line:
                        result["pr_url"] = line.split("PR URL:")[1].strip()
                        break
                
                if not result["pr_url"]:
                    # Try to construct the URL
                    result["pr_url"] = f"{self.pytorch_repo_url}/compare/{pytorch_branch}...{branch_name}?expand=1"
                
            else:
                result["error"] = f"Script failed with return code {process.returncode}"
                print(f"❌ Script failed: {process.stderr}")
                
        except Exception as e:
            result["error"] = f"Exception occurred: {str(e)}"
            print(f"❌ Exception: {e}")
        
        return result
    
    def open_pr_urls(self, results: List[Dict]):
        """Open all successful PR URLs in browser"""
        successful_results = [r for r in results if r["success"] and r["pr_url"]]
        
        if not successful_results:
            print("\n❌ No successful PRs to open in browser")
            return
        
        print(f"\n🌐 Opening {len(successful_results)} PR URLs in browser...")
        
        for result in successful_results:
            try:
                print(f"Opening: {result['pr_url']}")
                webbrowser.open(result['pr_url'])
                time.sleep(1)  # Small delay between opening tabs
            except Exception as e:
                print(f"❌ Failed to open {result['pr_url']}: {e}")
    
    def print_summary(self, results: List[Dict]):
        """Print a summary of all results"""
        print(f"\n{'='*80}")
        print(f"📊 BATCH PR CREATION SUMMARY")
        print(f"{'='*80}")
        
        total = len(results)
        successful = len([r for r in results if r["success"]])
        failed = total - successful
        
        print(f"Total branch pairs processed: {total}")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        print(f"Success rate: {(successful/total)*100:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        print(f"{'='*60}")
        
        for i, result in enumerate(results, 1):
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            print(f"{i}. {result['apex_branch']} → {result['pytorch_branch']}: {status}")
            
            if result["success"]:
                print(f"   Branch: {result['branch_name']}")
                print(f"   PR URL: {result['pr_url']}")
            else:
                print(f"   Error: {result['error']}")
            print()
    
    def run_batch_creation(self) -> List[Dict]:
        """Run PR creation for all branch pairs"""
        print(f"🚀 Starting Batch PR Creation")
        print(f"PyTorch Repository: {self.pytorch_repo_url}")
        print(f"Branch pairs to process: {len(self.branch_pairs)}")
        
        # Verify repositories exist
        if not self.verify_repo_exists(self.pytorch_repo, "PyTorch"):
            print("❌ PyTorch repository not found!")
            return []
        
        if not self.verify_repo_exists(self.apex_repo, "Apex"):
            print("❌ Apex repository not found!")
            return []
        
        results = []
        
        # Process each branch pair
        for apex_branch, pytorch_branch in self.branch_pairs:
            result = self.run_single_pr_creation(apex_branch, pytorch_branch)
            results.append(result)
            
            # Add a delay between processing to avoid overwhelming the system
            if apex_branch != self.branch_pairs[-1][0]:  # Not the last one
                print(f"\n⏳ Waiting 5 seconds before next branch pair...")
                time.sleep(5)
        
        return results


def main():
    parser = argparse.ArgumentParser(
        description="Batch PR Creation Script - Create PRs for multiple PyTorch and Apex branch pairs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create PRs for all branch pairs using default repository
  python3 batch_pr_creation.py

  # Create PRs for all branch pairs using custom repository
  python3 batch_pr_creation.py --pytorch-repo-url https://github.com/skkkumar/pytorch

  # Create PRs for specific branch pairs only
  python3 batch_pr_creation.py --apex-branches release/1.8.0 release/1.7.0 --pytorch-branches release/2.8 release/2.7
        """
    )
    
    parser.add_argument(
        "--pytorch-repo-url", 
        default="https://github.com/ROCm/pytorch",
        help="PyTorch repository URL (default: https://github.com/ROCm/pytorch)"
    )
    
    parser.add_argument(
        "--apex-branches",
        nargs="+",
        help="Specific Apex branches to process (if not specified, all compatible branches will be used)"
    )
    
    parser.add_argument(
        "--pytorch-branches", 
        nargs="+",
        help="Specific PyTorch branches to process (if not specified, all compatible branches will be used)"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open PR URLs in browser automatically"
    )
    
    args = parser.parse_args()
    
    # Initialize the batch PR creation
    batch_creator = BatchPRCreation()
    batch_creator.set_pytorch_repo_url(args.pytorch_repo_url)
    
    # Handle custom branch pairs if specified
    if args.apex_branches and args.pytorch_branches:
        if len(args.apex_branches) != len(args.pytorch_branches):
            print("❌ Error: Number of Apex branches must match number of PyTorch branches")
            sys.exit(1)
        
        batch_creator.branch_pairs = list(zip(args.apex_branches, args.pytorch_branches))
        print(f"Using custom branch pairs: {batch_creator.branch_pairs}")
    
    # Run batch creation
    results = batch_creator.run_batch_creation()
    
    # Print summary
    batch_creator.print_summary(results)
    
    # Open PR URLs in browser if requested
    # if not args.no_browser:
        # batch_creator.open_pr_urls(results)
    
    # Exit with appropriate code
    successful = len([r for r in results if r["success"]])
    if successful == len(results):
        print(f"\n🎉 All {len(results)} PRs created successfully!")
        sys.exit(0)
    elif successful > 0:
        print(f"\n⚠️  {successful}/{len(results)} PRs created successfully. Some failed.")
        sys.exit(1)
    else:
        print(f"\n❌ All {len(results)} PRs failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 