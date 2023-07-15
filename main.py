from datetime import date, datetime
# from github import Github
import subprocess
import os
import requests
import json

NAME = None
EMAIL = None
served_file = 'Served.json'

# Change the working directory to the path of this file
PATH = os.path.abspath(os.path.dirname(__file__))
os.chdir(PATH)

# Set up GitHub repository details
repository_name = 'Get-Pair-Extraordinaire'
AUTHOR_NAME = 'Prakash4844'
AUTHOR_EMAIL = os.environ.get('EMAIL')

# Get today's date
today = date.today().isoformat()

# Set up GitHub API URL
ISSUE_API_URL = f'https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/issues'

# API Parameters for filtering issues by label and state
API_PARAM = {
    "labels": "Request",
    "state": "open",
}


def fetch_issues():
    """
    Fetches issues from GitHub API, given the parameters above
    :param: none
    :return: list of issues with the given label and state or None if the request fails
    """
    issue_response = requests.get(url=ISSUE_API_URL, params=API_PARAM)
    if issue_response.status_code == 200:
        return issue_response.json()
    else:
        print("Failed to fetch issues. Status code:", issue_response.status_code)
        return None


def update_served_json():
    """
    Updates the JSON file with the name and email of the user who has been served
    :return:
    """
    try:
        with open(served_file) as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    except json.decoder.JSONDecodeError:
        data = {}

        # Get current year, month, and week
        current_year = 'Year ' + str(datetime.now().year)
        current_month = datetime.now().strftime('%B')
        current_week = 'Week ' + datetime.now().strftime('%U')
        current_date = today

        # Create JSON structure if it doesn't exist
        if current_year not in data:
            data[current_year] = {}
        if current_month not in data[current_year]:
            data[current_year][current_month] = {}
        if current_week not in data[current_year][current_month]:
            data[current_year][current_month][current_week] = {}
        if current_date not in data[current_year][current_month][current_week]:
            data[current_year][current_month][current_week][current_date] = {}

        # Update JSON data
        data[current_year][current_month][current_week][current_date].update({
            'Messages': "served to " + NAME + " (" + EMAIL + ") on " + today,
        })

        # Write updated JSON data back to file
        with open(served_file, 'w') as file:
            json.dump(data, file, indent=4)


def git_process():
    """
    Performs git operations to create a new branch,
    add the changes, commit them, and push the branch to the remote repository with tracking enabled
    :param: none
    :return: none
    """
    # subprocess.run(['git', 'config', 'user.email', AUTHOR_EMAIL])
    # subprocess.run(['git', 'config', 'user.name', AUTHOR_NAME])
    subprocess.run(['git', 'checkout', '-b', f'{issue_creator}-request-{today}'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'Add {issue_creator} to the list of served users on {today}'])
    subprocess.run(['git', 'push', '-u', 'origin', f'{issue_creator}-request-{today}'])


def git_cleanup():
    subprocess.run(['git', 'checkout', 'main'])
    subprocess.run(['git', 'branch', '-D', f'{issue_creator}-request-{today}'])
    subprocess.run(['git', 'push', 'origin', '--delete', f'{issue_creator}-request-{today}'])
    subprocess.run(['git', 'fetch', '--prune'])
    subprocess.run(['git', 'pull', 'origin', 'main'])


# Get the list of issues
issue_list = fetch_issues()

# Loop through the list of issues and process each one
for issue in issue_list:
    issue_body = issue['body']
    # Find the position of the colon (:) to separate the label and the value
    name_start = issue_body.find(':') + 2
    email_start = issue_body.find('Email:') + 7
    issue_creator = issue['user']['login']
    issue_ID = issue['id']

    # Extract the name and email using string slicing
    NAME = issue_body[name_start:issue_body.find('\r')]
    EMAIL = issue_body[email_start:]
    subprocess.run(['git', 'pull', 'origin', 'main'])
    update_served_json()
    git_process()
    git_cleanup()
#
#
# for issue in issues_list:
#     issue_id = issue['id']
#     current_selected_issue_details = get_issue_details(issue_id)
#     print(current_selected_issue_details)
#     git_process(current_selected_issue_details)
print('Done!')
