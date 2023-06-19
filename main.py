import datetime
# from github import Github
# import subprocess
import os

import requests

# Global variables
issue_username = None
issue_username_avatar_url = None
issue_id = None
issue_body = None
name = None
email = None


# Change the working directory to the path of this file
PATH = os.path.abspath(os.path.dirname(__file__))
os.chdir(PATH)
# subprocess.run(['git', 'pull', 'origin', 'main'])

# Set up GitHub repository details
repository_name = 'Get-Pair-Extraordinaire'
author_name = 'Prakash4844'

# Get today's date
today = datetime.date.today().isoformat()

# Issues API URL
issues_url = f'https://api.github.com/repos/{author_name}/{repository_name}/issues'

# Issue Parameters
label_name = "Request"
issue_state = "open"

# Parameters for filtering issues by label
params = {
    "labels": label_name,
    "state": issue_state,
}


def fetch_issues():
    """
    Fetches issues from GitHub API, given the parameters above
    :return: list of issues with the given label
    """
    issue_response = requests.get(issues_url, params=params)
    if issue_response.status_code == 200:
        return issue_response.json()
    else:
        print("Failed to fetch issues. Status code:", issue_response.status_code)


def get_issue_details(issue_id_par):
    """
    Extracts the details of the issue creator from the issue object and stores them in global variables
    :return: none
    """
    for issue in issues_list:
        global issue_username, issue_username_avatar_url, issue_body, name, email
        if issue['id'] == issue_id_par:
            issue_username = issue['user']['login']
            issue_username_avatar_url = issue['user']['avatar_url']
            issue_body = issue['body']

            # Find the position of the colon (:) to separate the label and the value
            name_start = issue_body.find(':') + 2
            email_start = issue_body.find('Email:') + 7

            # Extract the name and email using string slicing
            name = issue_body[name_start:issue_body.find('\r')]
            email = issue_body[email_start:]


issues_list = fetch_issues()

for iss in issues_list:
    issue_id = iss['id']
    get_issue_details(issue_id)

print('Done!')
