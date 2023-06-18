import datetime
import requests
import json
# from github import Github
import subprocess
import os

PATH = os.path.abspath(os.path.dirname(__file__))
os.chdir(PATH)
# subprocess.run(['git', 'pull', 'origin', 'main'])

# Set up GitHub repository details
repository_name = 'Get-Pair-Extraordinaire'
author_name = 'Prakash4844'

# Get today's date
today = datetime.date.today().isoformat()

# Get list of issues with label 'Request'
issues_url = f'https://api.github.com/repos/{author_name}/{repository_name}/issues?labels=Request&state=open'

issue_response = requests.get(issues_url)
issues = issue_response.json()

for issue in issues:
    issue_username = issue['user']['login']
    issue_username_avatar_url = issue['user']['avatar_url']
    issue_id = issue['id']
    issue_body = issue['body']

    # Find the position of the colon (:) to separate the label and the value
    name_start = issue_body.find(':') + 2
    email_start = issue_body.find('Email:') + 7

    # Extract the name and email using string slicing
    name = issue_body[name_start:issue_body.find('\r')]
    email = issue_body[email_start:]

    print("Name:", name)
    print("Email:", email)

print('test')
