import datetime
import requests
import json
from github import Github
import subprocess
import os

PATH = os.path.abspath(os.path.dirname(__file__))
os.chdir(PATH)
subprocess.run(['git', 'pull', 'origin', 'main'])

# Set up GitHub repository details
repository_name = 'Get-Pair-Extraordinaire'
author_name = 'Prakash4844'


# Get today's date
today = datetime.date.today().isoformat()

# Get list of issues with label 'Request'
issues_url = f'https://api.github.com/repos/{author_name}/{repository_name}/issues?labels=Request&state=open'

issue_response = requests.get(issues_url)
issues = issue_response.json()

print('test')
