<!--suppress HtmlDeprecatedAttribute -->

<div align="center">
  <h1>Flowchart using Mermaid</h1>
  <img src="title.png" alt="Pair Extraordinaire"/>
</div>

---

## Flowchart

### 1. [main.py](../main.py)

<details>
<summary>Click to expand</summary>

```mermaid
graph TD
    A[Start] --> B(Define Constants)
    B --> C(Change Working Directory)
    C --> D(Get GitHub Token)
    D --> E(Get Today's Date)
    E --> F[Fetch Issues]
    F --> G{Issues Exist?}
    G -- Yes --> H(Process Each Issue)
    G -- No --> Z(End)
    H --> I(Parse Issue Details)
    I --> J(Update served.json)
    J --> K(Git Operations)
    K --> L(Comment on Issue)
    L --> M(Create Pull Request)
    M --> N(Get Pull Requests)
    N --> O(Merge Pull Request)
    O --> P(Close Issue with Comment)
    P --> Q(Cleanup Git)
    Q --> F
    H --> H
    Q --> Z
    Z --> R(End)

```

![main.py_flowchart](main.svg)
</details>

### 2. Fetch Issues

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[fetch_issues] --> B(Set up GitHub API URL)
    B --> C(Set API Parameters)
    C --> D[issue_response = requests.get]
    D --> E{Response Status Code}
    E -- 200 --> F(Return issue_response.json)
    E -- Others --> G(Print Error Message)
    G --> H(Return None)

```

![fetch_issues_flowchart](fetch_issue().svg)
</details>

### 3. Update served.json

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[update_served_json] --> B(Try Block)
    B --> C[Open served_file]
    C --> D{File Exists?}
    D -- Yes --> E[Load JSON data]
    D -- No --> F[Pass]
    E --> G(Get Current Year, Month, Week, and Date)
    G --> H{JSON Structure Exists?}
    H -- No --> I[Create JSON Structure]
    H -- Yes --> J[Update JSON Data]
    J --> K[Write JSON data to file]
    K --> L[End]
    I --> L
    F --> L

```

![update_served_json_flowchart](Update_json().svg)

</details>

### 4. Git Config_Commit_Push

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[git_config_commit_push] --> B(Config git user email)
    B --> C(Config git user name)
    C --> D(Create new branch)
    D --> E(Add changes)
    E --> F(Commit changes)
    F --> G(Push branch to remote repository)

```

![git_config_commit_push_flowchart](git_config_commit_push().svg)

</details>

### 5. Comment on Issue

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[comment_on_issue] --> B(Set up URL, Data, and Headers)
    B --> C(Make API POST request)
    C --> D{Response Status Code}
    D -- 201 --> E(Print "Comment added successfully.")
    D -- Others --> F(Print Error Message)

```

![comment_on_issue_flowchart](comment_on_issue().svg)

</details>

### 6. Create Pull Request

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[create_pull_request] --> B(Set up URL, Headers, and Data)
    B --> C(Make API POST request)
    C --> D{Response Status Code}
    D -- 201 --> E(Print "Pull request created successfully.")
    D -- Others --> F(Print Error Message)

```

![create_pull_request_flowchart](create_pull_request().svg)

</details>

### 7. Get Pull Request

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[get_pull_requests] --> B(Set up URL, Headers, and Parameters)
    B --> C(Make API GET request)
    C --> D{Response Status Code}
    D -- 200 --> E(Get Pull Requests)
    D -- Others --> F(Print Error Message)

```

![get_pull_requests_flowchart](get_pull_requests().svg)

</details>

### 8. Merge Pull Request

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[merge_pull_request] --> B(Set up URL, Headers, and Data)
    B --> C(Make API PUT request)
    C --> D{Response Status Code}
    D -- 200 --> E(Print "Pull request merged successfully.")
    D -- Others --> F(Print Error Message)

```

![merge_pull_request_flowchart](merge_pull_request().svg)

</details>

### 9. Close Issue with Comment

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[close_issue_with_comment] --> B(Set up URLs and Headers)
    B --> C(Add comment to closed issue)
    C --> D{Response Status Code}
    D -- 201 --> E(Print "Comment added successfully.")
    D -- Others --> F(Print Error Message)
    F --> G(Close the issue)
    G --> H{Response Status Code}
    H -- 200 --> I(Print "Issue closed successfully.")
    H -- Others --> J(Print Error Message)

```

![close_issue_with_comment_flowchart](close_issue_with_comment().svg)

</details>

### 10. Cleanup Git

<details>
<summary>Click to expand</summary>

```mermaid
graph LR
    A[git_cleanup] --> B(Checkout main branch)
    B --> C(Delete local branch)
    C --> D(Delete remote branch)
    D --> E(Fetch with prune)
    E --> F(Pull main branch)

```

![git_cleanup_flowchart](git_cleanup().svg)

</details>

## References

- [Mermaid JS](https://mermaid-js.github.io/mermaid/#/)
- [Mermaid Live Editor](https://mermaid-js.github.io/mermaid-live-editor)

## License

![GitHub](https://img.shields.io/github/license/prakash4844/get-pair-extraordinaire?style=for-the-badge)