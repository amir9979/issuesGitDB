import GitCommits as g
import JiraIssues as j
import Matrix as m


def main():
    # get jira issues
    jql_features = 'project = LANG AND issuetype = "New Feature" AND status in (Resolved, Closed)'
    jql_bugs_improvements = 'project = LANG AND issuetype in (Bug, Improvement) AND status in (Resolved, Closed)'
    jira_features = j.get_issues_list(jql_features)
    jira_bugs_improvements = j.get_issues_list(jql_bugs_improvements)

    # get commits
    repo_path =  r"C:\Users\shir0\commons-lang"
    commits = g.get_all_commits(repo_path)

    # create matrix
    matrix_features = m.create_matrix(jira_features, commits)
    matrix_bugs_improvements = m.create_matrix(jira_bugs_improvements, commits)

    # copy data to csv
    csv_features = "Commit-Features Matrix.csv"
    csv_bugs_improvements = "Commit-BugsImprovements Matrix.csv"
    m.matrix_to_csv(matrix_features, csv_features)
    m.matrix_to_csv((matrix_bugs_improvements, csv_bugs_improvements))


if __name__ == '__main__':
    main()
