import MatrixDB as db
import GitCommits as g
import JiraIssues as j
import Matrix
import sys

if __name__ == '__main__':
    # Set variables according to the project

    PROJECT_NAME = sys.argv[1] # "commons-math"
    JIRA_PROJECT_ID = sys.argv[2] # "MATH"
    commits_start = None
    commits_end = None
    if len(sys.argv) > 3:
        commits_start = int(sys.argv[3])
        commits_end = commits_start + 1000

    DB_PATH = r"CommitIssueDB.db"
    GIT_REPO_PATH_LOCAL = r"C:\Users\User\Documents\GitHub\issuesGitDB\local_repo"
    JIRA_PATH = r"http://issues.apache.org/jira"

    # Get DB connection
    db_connection = db.get_connection(DB_PATH)

    # Project Handling
    db_connection.insert_project(PROJECT_NAME, JIRA_PROJECT_ID)

    # Commits Handling
    g.set_repo_path(GIT_REPO_PATH_LOCAL)
    comms = g.get_commits_files(GIT_REPO_PATH_LOCAL)
    commits = list(filter(lambda c: c.is_java, comms))
    if commits_start:
        commits_num = commits[commits_start: commits_end]

    for commit in commits:
        db.insert_commit(db_connection, commit, PROJECT_NAME)

    # Issues Handling
    j.set_jira(JIRA_PATH)
    jql_features = 'project = {0} AND issuetype = "New Feature" AND statusCategory = Done'.format(JIRA_PROJECT_ID)
    jql_bugs_improvements = 'project = {0} AND issuetype in (Bug, Improvement) AND statusCategory = Done'.format(JIRA_PROJECT_ID)

    issues_features = j.get_issues_list(jql_features)
    for issue in issues_features:
        db_connection.insert_issue(issue, PROJECT_NAME)

    issues_bugs_improvements = j.get_issues_list(jql_bugs_improvements)
    for issue in issues_bugs_improvements:
        db_connection.insert_issue(issue, PROJECT_NAME)

    all_issues = issues_bugs_improvements + issues_features  # union both issue lists to one


    # Matrix Handling
    m = Matrix.create_matrix(all_issues, commits)
    for issue, commit in m:
        db_connection.insert_linkage(commit, issue)

    # DONE
    db.close_connection(db_connection)
