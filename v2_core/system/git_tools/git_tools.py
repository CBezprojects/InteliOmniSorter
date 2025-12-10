# InteliOmniSorter V2 - Git tools wrapper

import os
import subprocess

def run_git_guardian():
    repo_root = os.getcwd()
    guardian = os.path.join(repo_root, "InteliGitGuardian.ps1")
    if os.path.exists(guardian):
        print("GitTools: running Git Guardian...")
        subprocess.call(["powershell", "-ExecutionPolicy", "Bypass", "-File", guardian])
    else:
        print("GitTools: InteliGitGuardian.ps1 not found.")
