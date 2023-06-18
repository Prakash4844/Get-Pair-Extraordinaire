import requests
import json
from github import Github
import subprocess
import os

PATH = os.path.abspath(os.path.dirname(__file__))
os.chdir(PATH)
subprocess.run(['git', 'pull', 'origin', 'main'])

# GitHub Personal Access Token PATH
PAT_PATH = "/home/zaphkiel/Documents/Github/PAT"

# Set up GitHub repository details
repository_name = 'Get-Pair-Extraordinaire'
author_name = 'Prakash4844'

# Set up GitHub Personal Access Token
with open(PAT_PATH, 'r') as f:
    personal_access_token = f.read().strip()

# Create a GitHub instance using Personal Access Token
github_instance = Github(base_url="https://api.github.com", login_or_token=personal_access_token)

# Get the repository issues
issues = github_instance.get_user().get_repo(repository_name).get_issues(labels="Request")
