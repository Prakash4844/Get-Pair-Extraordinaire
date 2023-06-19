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


def update_extraordinary_md():
    """
    Updates the Extraordinary.md file with the details of the issue creator
    :return: none
    """
    boilerplate_text = f"""
    <tc>
        <td align="center"><a href="https://github.com/{issue_username}"><img
            src={issue_username_avatar_url}
            width="100px;"
            alt=""/><br/><sub><b>{name}</b></sub></a><br/></td>
    </tc>
    """
    with open('Extraordinary.md', 'r') as f:
        lines = f.readlines()

    # Find the index of the last occurrence of "</tc>"
    last_tc_index = None
    for i in range(len(lines) - 1, -1, -1):
        if "</tc>" in lines[i]:
            last_tc_index = i
            break

    # Check if "</tc>" was found
    if last_tc_index is not None:
        # Append text in the next line
        lines.insert(last_tc_index + 1, f"{boilerplate_text}\n")

        # Open the file in write mode and overwrite its contents
        with open('Extraordinary.md', "w") as file:
            file.writelines(lines)
            print("Text appended successfully.")
    else:
        print("'</tc>' not found in the file.")


def get_issue_details():
    """
    Extracts the details of the issue creator from the issue object and stores them in global variables
    :return: none
    """
    for issue in issues:
        global issue_username, issue_username_avatar_url, issue_id, issue_body, name, email
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


issues = fetch_issues()
get_issue_details()
update_extraordinary_md()

print('test')
