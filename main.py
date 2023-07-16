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
branch_name = None
AUTHOR_NAME = 'Prakash4844'
AUTHOR_EMAIL = os.environ.get('GIT_EMAIL', '81550376+Prakash4844@users.noreply.github.com')

# Get GITHUB_TOKEN from GitHub secrets
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Get GitHub token from GitHub secrets
GITHUB_PAT = os.environ.get('EXTRAORDINAIREPAT', f'{GITHUB_TOKEN}')

# Get today's date
today = date.today().isoformat()


def fetch_issues():
    """
    Fetches issues from GitHub API, given the parameters above
    :param: none
    :return: list of issues with the given label and state or None if the request fails
    """
    # Set up GitHub API URL
    ISSUE_API_URL = f'https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/issues'

    # API Parameters for filtering issues by label and state
    API_PARAM = {
        "labels": "Request",
        "state": "open",
    }

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
    finally:
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
    subprocess.run(['git', 'checkout', '-b', f'{branch_name}'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'Add {issue_creator} to the list of served users on {today}'])
    subprocess.run(['git', 'push', '-u',
                    f'https://{GITHUB_PAT}@github.com/{AUTHOR_NAME}/{repository_name}.git',
                    f'{branch_name}'])


def git_cleanup():
    """
    Performs git operations to checkout the main branch, delete the local and remote branches.
    :param: none
    :return:
    """
    subprocess.run(['git', 'checkout', 'main'])
    subprocess.run(['git', 'branch', '-D', f'{issue_creator}-request-{today}'])
    subprocess.run(['git', 'push', 'origin', '--delete', f'{issue_creator}-request-{today}'])
    subprocess.run(['git', 'fetch', '--prune'])
    subprocess.run(['git', 'pull', f'https://{GITHUB_PAT}@github.com/{AUTHOR_NAME}/{repository_name}.git',
                    'main'])


def comment_on_issue(comment_text, issue_no):
    """
    Adds a comment to the issue with the given Issue_number
    :param comment_text:
    :param issue_no: (This is the issue number to which the comment should be added)
    :return:
    """
    # Set up the URL, Data and headers for the API request
    url = f"https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/issues/{issue_no}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "body": comment_text
    }

    # Make the API POST request to add the comment and get the response
    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print("Comment added successfully.")
    else:
        print(f"Failed to add comment. Response: {response.text}")


def create_pull_request(title, body, head_branch, base_branch="main"):
    """
    Creates a pull request in the given repository
    :param base_branch:
    :param head_branch:
    :param title:
    :param body:
    :return:
    """
    url = f"https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/pulls"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,  # Title of the pull request
        "body": body,  # Body of the pull request
        "head": head_branch,  # Branch where your changes are implemented (feature branch)
        "base": base_branch  # Branch you want your changes pulled into (default: main)
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print("Pull request created successfully.")
    else:
        print(f"Failed to create pull request. Response: {response.text}")


def get_pull_requests():
    """
    Get a list of Open pull requests
    :return:
    """
    url = f"https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/pulls"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "state": "open"  # possible values: open, closed, all
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        prs = response.json()
        return prs
    else:
        print(f"Failed to fetch pull requests. Response: {response.text}")
        return None


def merge_pull_request(pull_number):
    """
    merge the pull request identified by pull number to main branch
    :param pull_number:
    :return:
    """
    url = f"https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/pulls/{pull_number}/merge"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "merge_method": "merge",  # possible values: merge, squash, rebase
        "commit_message": f"merged PR for issue {issue_number}"  # custom merged commit message
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Pull request merged successfully.")
    else:
        print(f"Failed to merge pull request. Response: {response.text}")


# Get the list of issues
issue_list = fetch_issues()

# Loop through the list of issues and process each one
for issue in issue_list:
    issue_body = issue['body']
    # Find the position of the colon (:) to separate the label and the value
    name_start = issue_body.find(':') + 2
    email_start = issue_body.find('Email:') + 7
    issue_creator = issue['user']['login']
    issue_number = issue['number']

    # Extract the name and email using string slicing
    NAME = issue_body[name_start:issue_body.find('\r')]
    EMAIL = issue_body[email_start:]

    # Set branch name for issue
    branch_name = f'{issue_creator}-request-{today}'

    # Update served.json
    update_served_json()

    # Perform git operations to create a new branch,
    # add the changes, commit them, and push the branch to the remote repository with tracking enabled
    git_process()

    # Comment on Current Issue
    Issue_comment = f"Hi @{issue_creator},\n\nProcess has been started for your request." \
                    "\n\nThank you for using Get Pair Extraordinaire! :smile:\n" \
                    "You will be kept updated."

    comment_on_issue(Issue_comment, issue_number)

    # Create Pull Request
    pr_title = f"Serving Pair-Extraordinaire, Add {issue_creator} to the list of served users on {today}"
    pr_body = f"Committed with, co-author, {issue_creator} for providing Pair Extraordinaire badge " \
              f"Committed with, coauthor {issue_creator} for providing Pair Extraordinaire badge This PR is" \
              f" in Relation to Issue #{issue_number}"

    create_pull_request(pr_title, pr_body, head_branch=f"{branch_name}")

    # Get the list of pull requests
    pr_list = get_pull_requests()

    for pr in pr_list:
        if pr['title'] == pr_title:
            pr_number = pr['number']
            break
    else:
        pr_number = 0

    # Merge Pull Request with pr_number
    merge_pull_request(pr_number)

    git_cleanup()

print('Done!')
