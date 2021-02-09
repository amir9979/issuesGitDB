import JiraIssues as j


def create_matrix(jira_issues, git_commits):
    # TODO: check if we match by other commit fields other than commit's name
    matrix = []
    for commit in git_commits:
        for issue in jira_issues:
            issue_id = j.get_issue_id(issue)
            index = commit.summary.find(issue_id)
            if index != -1:
                if len(commit.summary) == index + len(issue_id):  # last word in commit's name
                    matrix.append((issue, commit))
                else:  # check if this is the issue or shorter ID
                    next_char = commit.summary[index + len(issue_id)]
                    if not next_char.isdigit():
                        matrix.append((issue, commit))  # add to Matrix
    return matrix
