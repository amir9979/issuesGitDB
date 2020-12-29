import MatrixDB as db
import GitCommits as g
import JiraIssues as j
import Debug
import Matrix
import pathlib

if __name__ == '__main__':
    # Set variables according to the project

    DB_PATH = r"C:\Users\User\Documents\GitHub\issuesGitDB\CommitIssueDB.db"
    PROJECT_NAME = "commons-math"
    GIT_REPO_PATH = r"https://github.com/apache/commons-math"
    GIT_REPO_PATH_LOCAL = r"C:\temp\commons-math"
    JIRA_PATH = r"http://issues.apache.org/jira"
    JIRA_PROJECT_ID = "MATH"

    # Get DB connection
    db_connection = db.get_connection(DB_PATH)
    if Debug.mode:
        print("connection established")

    # Project Handling
    db_connection.insert_project(PROJECT_NAME, JIRA_PROJECT_ID, GIT_REPO_PATH)

    # Issues Handling
    if Debug.mode:
        print("creating issue lists")
    j.set_jira(JIRA_PATH)
    jql_features = 'project = {0} AND issuetype = "New Feature" AND statusCategory = Done'.format(JIRA_PROJECT_ID)
    jql_bugs_improvements = 'project = {0} AND issuetype in (Bug, Improvement) AND statusCategory = Done'.format(JIRA_PROJECT_ID)

    issues_features = j.get_issues_list(jql_features)
    if Debug.mode:
        print("number of features: {0}".format(len(issues_features)))
    for issue in issues_features:
        db_connection.insert_issue(issue, PROJECT_NAME)

    issues_bugs_improvements = j.get_issues_list(jql_bugs_improvements)
    if Debug.mode:
        print("number of bugs & improvements: {0}".format(len(issues_bugs_improvements)))
    for issue in issues_bugs_improvements:
        db_connection.insert_issue(issue, PROJECT_NAME)

    all_issues = issues_bugs_improvements + issues_features  # union both issue lists to one

    # Commits Handling
    g.set_repo_path(GIT_REPO_PATH_LOCAL)
    comms = g.get_commits_files(GIT_REPO_PATH_LOCAL)
    commits = list(filter(lambda c: c.is_java, comms))
    if Debug.mode:
        # len(commits) - 4546
        print("number of commits: {0}".format(len(commits)))

    for commit in commits[:300]:
        db.insert_commit(db_connection, commit, PROJECT_NAME)

    # Matrix Handling
    m = Matrix.create_matrix(all_issues, commits)
    if Debug.mode:
        print("number of matching found: {0}".format(len(m)))

    for issue, commit in m:
        db_connection.insert_linkage(commit, issue)

    # DONE
    db.close_connection(db_connection)
    if Debug.mode:
        print("connection is closed")
