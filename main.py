from datetime import date
import subprocess
import os
import requests
import json
import re
from contributor_tracking import (
    count_contributor_entries,
    record_contributor,
    update_contributor_table,
)

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


def add_entry_to_table(username, avatar_url, github_link, times):
    """Add or update one contributor cell without creating duplicate accounts."""
    update_contributor_table(
        markdown_path='Extraordinary.md',
        username=username,
        avatar_url=avatar_url,
        github_link=github_link,
        times=times,
    )


def update_served_json(username, request_id, initial_times=0):
    """Record a request under a stable GitHub account key."""
    return record_contributor(
        served_path=served_file,
        username=username,
        display_name=NAME,
        served_date=today,
        request_id=request_id,
        initial_times=initial_times,
    )


def git_config_commit_push():
    """
    Performs git operations to configure the git user, create a new branch,
    add the changes, commit them, and push/publish the branch to the remote repository with tracking enabled.
    :param: none
    :return:
    """
    subprocess.run(['git', 'config', 'user.email', AUTHOR_EMAIL])
    subprocess.run(['git', 'config', 'user.name', AUTHOR_NAME])
    subprocess.run(['git', 'checkout', '-b', f'{branch_name}'])
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', f'''Add {issue_creator} to the list of served users on {today}
                    \n\n\nCo-authored-by: {NAME} <{EMAIL}>'''])

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
    subprocess.run(['git', 'branch', '-D', f'{branch_name}'])
    subprocess.run(
        ['git', 'push', f'https://{GITHUB_PAT}@github.com/{AUTHOR_NAME}/{repository_name}.git', '--delete',
         f'{branch_name}'])
    subprocess.run(['git', 'fetch', '--prune'])
    subprocess.run(['git', 'pull', f'https://{GITHUB_PAT}@github.com/{AUTHOR_NAME}/{repository_name}.git',
                    'main'])


def comment_on_issue(comment_text, issue_no):
    """
    Adds a comment_text to the issue with the given Issue_number
    :param comment_text:
    :param issue_no: (This is the issue number to which the comment should be added on)
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
    Creates a pull request in the given repository from the head_branch to the base_branch
    With the given title and body
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
        print("Aborting the process.\nPlease check the logs and try again.")
        exit(1)


def get_pull_requests():
    """
    Get a list of Open pull requests from the repository
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
        print("Aborting the process.\nPlease check the logs and try again.")
        exit(1)


def merge_pull_request(pull_number):
    """
    merge the pull request identified by pull number to main branch in the repository
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
        "commit_message": f"merged PR for issue #{issue_number}, Created by {NAME} "  # custom merged commit
        # message
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Pull request merged successfully.")
    else:
        print(f"Failed to merge pull request. Response: {response.text}")
        print("Aborting the process.\nPlease check the logs and try again.")
        exit(1)


def close_issue_with_comment(issue_no):
    """
    Close the issue with the given issue number in the repository along with a comment
    :param issue_no:
    :return:
    """
    issue_url = f"https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/issues/{issue_no}"
    comment_url = f"https://api.github.com/repos/{AUTHOR_NAME}/{repository_name}/issues/{issue_no}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Add a comment to the closed issue
    data = {
        "body": f"Your Request has been processed in PR #{pr_number}\nThank you for your contribution."
                "\n\nPlease star the repository if you liked it.\n"
    }

    response = requests.post(comment_url, headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print("Comment added successfully.")
    else:
        print(f"Failed to add comment. Response: {response.text}")

    # Close the issue
    data = {
        "state": "closed"
    }
    response = requests.patch(issue_url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print("Issue closed successfully.")
    else:
        print(f"Failed to close issue. Response: {response.text}")
        print(f"close manually issue #{issue_no}.")


# Get the list of issues
issue_list = fetch_issues()

if not issue_list:
    print('No issue with "Request" Label found. Exiting...')
    exit(0)

# Loop through the list of issues and process each one
for issue in issue_list:
    issue_body = issue['body'] or ''
    issue_creator = issue['user']['login']
    issue_number = issue['number']

    # Parse fields by label so both LF and CRLF issue bodies are supported.
    name_match = re.search(r'(?im)^Name:\s*(.+?)\s*
    email_match = re.search(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        issue_body,
    )
    if not name_match or not email_match:
        print(f"Skipping issue #{issue_number}: missing name or email.")
        continue
    NAME = name_match.group(1).strip()
    EMAIL = email_match.group()


    # Set branch name for issue
    branch_name = f'{issue_creator}-request-{today}'

    # Record this request once, keyed by the GitHub account rather than display name.
    legacy_times = count_contributor_entries(
        'Extraordinary.md', issue['user']['html_url']
    )
    times, already_processed = update_served_json(
        issue_creator, issue_number, legacy_times
    )
    if already_processed:
        print(f"Issue #{issue_number} has already been recorded. Skipping.")
        continue

    # Keep one Markdown entry per GitHub account and refresh its usage count.
    add_entry_to_table(
        username=issue_creator,
        avatar_url=issue['user']['avatar_url'],
        github_link=issue['user']['html_url'],
        times=times,
    )

    # Perform git operations to create a new branch,
    # add the changes, commit them, and push the branch to the remote repository with tracking enabled
    git_config_commit_push()

    # Comment on Current Issue
    Issue_comment = f"Hi @{issue_creator},\n\nProcess has been started for your request." \
                    "\n\nThank you for using Get Pair Extraordinaire! :smile:\n"

    comment_on_issue(Issue_comment, issue_number)

    # Create Pull Request
    pr_title = f"Serving Pair-Extraordinaire, Add {issue_creator} to the list of served users on {today}"
    pr_body = f"Committed with, co-author, @{issue_creator} for providing Pair Extraordinaire badge. " \
              f"This PR is in Relation to Issue #{issue_number}"

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

    # Close Issue with issue_number
    close_issue_with_comment(issue_number)

    # Clean up local and remote git repository
    git_cleanup()

print('Served everyone on the list! ;)')
, issue_body)
    email_match = re.search(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        issue_body,
    )
    if not name_match or not email_match:
        print(f"Skipping issue #{issue_number}: missing name or email.")
        continue
    NAME = name_match.group(1).strip()
    EMAIL = email_match.group()


    # Set branch name for issue
    branch_name = f'{issue_creator}-request-{today}'

    # Record this request once, keyed by the GitHub account rather than display name.
    legacy_times = count_contributor_entries(
        'Extraordinary.md', issue['user']['html_url']
    )
    times, already_processed = update_served_json(
        issue_creator, issue_number, legacy_times
    )
    if already_processed:
        print(f"Issue #{issue_number} has already been recorded. Skipping.")
        continue

    # Keep one Markdown entry per GitHub account and refresh its usage count.
    add_entry_to_table(
        username=issue_creator,
        avatar_url=issue['user']['avatar_url'],
        github_link=issue['user']['html_url'],
        times=times,
    )

    # Perform git operations to create a new branch,
    # add the changes, commit them, and push the branch to the remote repository with tracking enabled
    git_config_commit_push()

    # Comment on Current Issue
    Issue_comment = f"Hi @{issue_creator},\n\nProcess has been started for your request." \
                    "\n\nThank you for using Get Pair Extraordinaire! :smile:\n"

    comment_on_issue(Issue_comment, issue_number)

    # Create Pull Request
    pr_title = f"Serving Pair-Extraordinaire, Add {issue_creator} to the list of served users on {today}"
    pr_body = f"Committed with, co-author, @{issue_creator} for providing Pair Extraordinaire badge. " \
              f"This PR is in Relation to Issue #{issue_number}"

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

    # Close Issue with issue_number
    close_issue_with_comment(issue_number)

    # Clean up local and remote git repository
    git_cleanup()

print('Served everyone on the list! ;)')
