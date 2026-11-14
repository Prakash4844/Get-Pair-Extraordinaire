"""Contributor history and Markdown table helpers."""

import json
import os
import re
from datetime import datetime

from bs4 import BeautifulSoup


def _load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Served.json must contain a JSON object")
    return data


def record_contributor(
    served_path, username, display_name, served_date, request_id, initial_times=0
):
    """Record a unique issue request and return (usage_count, already_processed)."""
    username = username.strip().lstrip("@")
    if not username:
        raise ValueError("A GitHub username is required")

    data = _load_json(served_path)
    contributors = data.setdefault("Contributors", {})
    contributor = contributors.setdefault(
        username,
        {"Times": int(initial_times), "Requests": [], "History": []},
    )

    request_id = str(request_id)
    requests = contributor.setdefault("Requests", [])
    if request_id in requests:
        return int(contributor.get("Times", 0)), True

    current_date = datetime.strptime(served_date, "%Y-%m-%d")
    year = f"Year {current_date.year}"
    month = current_date.strftime("%B")
    week = f"Week {current_date.strftime('%U')}"
    daily_records = (
        data.setdefault(year, {})
        .setdefault(month, {})
        .setdefault(week, {})
        .setdefault(served_date, {})
    )
    account_record = daily_records.setdefault(
        username, {"Name": display_name, "Messages": []}
    )
    if isinstance(account_record.get("Messages"), str):
        account_record["Messages"] = [account_record["Messages"]]
    account_record.setdefault("Name", display_name)
    account_record.setdefault("Messages", []).append(
        f"served to {display_name} (@{username}) on {served_date}"
    )

    contributor["Times"] = int(contributor.get("Times", 0)) + 1
    contributor["Requests"] = requests + [request_id]
    contributor.setdefault("History", []).append(
        {"Date": served_date, "Issue": request_id, "Name": display_name}
    )
    contributor["Last served"] = served_date

    with open(served_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
        file.write("\n")

    return contributor["Times"], False


def update_contributor_table(markdown_path, username, avatar_url, github_link, times):
    """Update an account's existing cell or append one when it is new."""
    with open(markdown_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")

    table = soup.find("table", class_="contributors")
    if table is None:
        table = soup.new_tag("table", **{"class": "contributors"})
        soup.append(table)

    normalized_url = github_link.rstrip("/").casefold()
    matching_cells = []
    for cell in table.find_all("td"):
        link = cell.find("a", href=True)
        if link and link["href"].rstrip("/").casefold() == normalized_url:
            matching_cells.append(cell)

    if matching_cells:
        cell = matching_cells[0]
        for duplicate in matching_cells[1:]:
            duplicate.decompose()
    else:
        rows = table.find_all("tr")
        last_row = rows[-1] if rows else None
        if last_row is None or len(last_row.find_all("td")) >= 7:
            last_row = soup.new_tag("tr")
            table.append(last_row)
        cell = soup.new_tag("td", align="center")
        last_row.append(cell)

    cell.clear()
    link = soup.new_tag("a", href=github_link)
    cell.append(link)
    image = soup.new_tag("img", src=avatar_url, width="100", alt=username)
    link.append(image)
    link.append(soup.new_tag("br"))
    label = soup.new_tag("b")
    label.string = username
    link.append(label)
    link.append(soup.new_tag("br"))
    count = soup.new_tag("small")
    count.string = f"Times: {times}"
    link.append(count)

    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(soup.prettify())


def count_contributor_entries(markdown_path, github_link):
    """Return the number of existing table cells for a GitHub account."""
    if not os.path.exists(markdown_path):
        return 0
    with open(markdown_path, encoding="utf-8") as file:
        soup = BeautifulSoup(file.read(), "html.parser")
    normalized_url = github_link.rstrip("/").casefold()
    return sum(
        1
        for cell in soup.select("table.contributors td")
        for link in [cell.find("a", href=True)]
        if link and link["href"].rstrip("/").casefold() == normalized_url
    )


def parse_request_fields(issue_body):
    """Return a non-empty (name, email) pair, or None for malformed requests."""
    body = issue_body or ""
    name_match = re.search(
        r"(?im)^Name:[ \t]*(?P<name>\S(?:.*\S)?)[ \t]*\r?$",
        body,
    )
    email_match = re.search(
        r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,7}\b",
        body,
    )
    if not name_match or not email_match:
        return None
    return name_match.group("name"), email_match.group()


def find_request_pull_request(pull_requests, issue_number):
    """Find the PR linked to an issue, including merged PRs."""
    issue_pattern = re.compile(
        rf"\bIssue\s*#?\s*{int(issue_number)}\b", re.IGNORECASE
    )
    for pull_request in pull_requests:
        body = pull_request.get("body") or ""
        title = pull_request.get("title") or ""
        if issue_pattern.search(body) or issue_pattern.search(title):
            return pull_request
    return None
