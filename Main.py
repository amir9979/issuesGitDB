import MatrixDB as db
import GitCommits as g
import JiraIssues as j
import Debug
import Matrix
import pathlib

if __name__ == '__main__':
    # Set variables according to the project

    DB_PATH = str(pathlib.Path().absolute()) + "\..\CommitIssueDB.db"
    PROJECT_NAME = "commons-math"
    GIT_REPO_PATH = r"https://github.com/apache/commons-math"
    GIT_REPO_PATH_LOCAL = r"C:\Users\shir0\commons-math"
    JIRA_PATH = r"http://issues.apache.org/jira"
    JIRA_PROJECT_ID = "MATH"

    # Get DB connection
    db_connection = db.get_connection(DB_PATH)
    if Debug.mode:
        print("connection established")

    # Project Handling
    db.insert_project(db_connection, PROJECT_NAME, JIRA_PROJECT_ID, GIT_REPO_PATH)

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
        db.insert_issue(db_connection, issue, PROJECT_NAME)

    issues_bugs_improvements = j.get_issues_list(jql_bugs_improvements)
    if Debug.mode:
        print("number of bugs & improvements: {0}".format(len(issues_bugs_improvements)))
    for issue in issues_bugs_improvements:
        db.insert_issue(db_connection, issue, PROJECT_NAME)

    all_issues = issues_bugs_improvements + issues_features  # union both issue lists to one

    # Commits Handling
    g.set_repo_path(GIT_REPO_PATH_LOCAL)
    # len(g.get_all_commits()) = 6024
    commits = g.filter_commits(g.get_all_commits())
    if Debug.mode:
        # len(commits) - 4546
        print("number of commits: {0}".format(len(commits)))

    for commit in commits:
        db.insert_commit(db_connection, commit, PROJECT_NAME)

    # Matrix Handling
    m = Matrix.create_matrix(all_issues, commits)
    if Debug.mode:
        print("number of matching found: {0}".format(len(m)))

    for issue, commit in m:
        db.insert_linkage(db_connection, commit, issue)

    # DONE
    db.close_connection(db_connection)
    if Debug.mode:
        print("connection is closed")
