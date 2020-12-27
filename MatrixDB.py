import json
import pathlib
import sqlite3
import GitCommits as g
import JiraIssues as j
import JavaAnalyzer as a
import Debug


def get_connection(path):
    return sqlite3.connect(path)

def close_connection(conn):
    if conn: conn.close()


def init(conn):
    with open("table creation.sql") as f:
        cursor = conn.cursor()
        sql_as_string = f.read()
        cursor.executescript(sql_as_string)


def insert_project(conn, projectName, JiraProjectId, GitRepositoryPath):
    if Debug.mode:
        print("**insert project {0} the DB".format(projectName))
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO Projects (ProjectName, JiraProjectId, GitRepositoryPath) VALUES (?,?,?)"
            cur.execute(SQL, (projectName, JiraProjectId, GitRepositoryPath))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

def insert_issue(conn, issue, projectName):
    issue_id = j.get_issue_id(issue)
    issue_type = j.get_issue_type(issue)
    summary = j.get_issue_summary(issue)
    desc = j.get_issue_description(issue)
    status = j.get_issue_status(issue)
    time = j.get_issue_creation_date(issue)

    if Debug.mode:
        print("**insert issue #{0} to DB".format(issue_id))
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO JiraIssues (IssueID, IssueType, ProjectName, Summary, Description, Status, Date) VALUES (?,?,?,?,?,?,?)"
            cur.execute(SQL, (issue_id, issue_type, projectName, summary, desc, status, time))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])


def insert_commit(conn, commit, projectName):
    commit_id = g.get_commit_id(commit)
    summary = g.get_commit_name(commit)
    message = g.get_commit_message(commit)
    date = g.get_commit_date(commit)
    parent_id = g.get_commit_parent_id(commit)

    if Debug.mode:
        print("**insert commit {0} to DB".format(commit_id))
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO Commits (CommitID, ProjectName, Summary, Message, Date, ParentID) VALUES (?,?,?,?,?,?)"
            cur.execute(SQL, (commit_id, projectName, summary, message, date, parent_id))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

    files = g.get_code_file(commit)
    for code_file in files[0]:
        insert_file(conn, commit, code_file, "CODE")
    for test_file in files[1]:
        insert_file(conn, commit, test_file, "TEST")

    changes = g.get_commit_changes(commit)
    if changes is not None:
        for diff in changes:
            insert_changes(conn, commit, diff)


def insert_linkage(conn, commit, issue):
    issue_id = j.get_issue_id(issue)
    commit_id = g.get_commit_id(commit)
    if Debug.mode:
        print("**insert matching: commit {0} & issue {1} to DB".format(commit_id, issue_id))
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO CommitsIssuesLinkage (IssueID, CommitID) VALUES (?,?)"
            cur.execute(SQL, (issue_id, commit_id))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])


def insert_file(conn, commit, file_path, file_type):
    commit_id = g.get_commit_id(commit)
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO CommitFiles (CommitID, Path, FileType) VALUES (?,?,?)"
            cur.execute(SQL, (commit_id, file_path, file_type))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

def insert_changes(conn, commit, diff):
    commit_id = g.get_commit_id(commit)
    method_name = diff[0]
    new_path = diff[1]
    old_path = diff[3]

    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO CommitChanges (CommitID, MethodName, NewPath, OldPath) VALUES (?,?,?,?)"
            cur.execute(SQL, (commit_id, method_name, new_path, old_path))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])

    new_lines = diff[2]
    old_lines = diff[4]
    changed_lines = a.analyze_changes(old_lines, new_lines)

    for line in changed_lines:
        insert_line(conn, commit, method_name, line, new_path)

def insert_line(conn, commit, method_name, line, new_path):
    commit_id = g.get_commit_id(commit)
    line_type = line.line_type
    line_number = line.line_number
    content = line.content
    changed = line.is_changed
    if line.meaning == '{}':
        meaning = ""
    else:
        meaning = json.dumps(line.meaning)
    if line.tokens == '{}':
        token = ""
    else:
        token = json.dumps(line.tokens)
    try:
        with conn:
            cur = conn.cursor()
            SQL = "INSERT INTO MethodData (CommitID, MethodName, OldNew, LineNumber, Content, Changed, Meaning, Tokens, NewPath) VALUES (?,?,?,?,?,?,?, ?, ?)"
            cur.execute(SQL, (commit_id, method_name, line_type, line_number, content, changed, meaning, token, new_path))

    except sqlite3.Error as e:
        print("Error %s:" % e.args[0])
        e = None


if __name__ == '__main__':
    try:
        import json
        db_path =  str(pathlib.Path().absolute()) + "\..\Test_shir.db"
        # issue1 = j.get_issues_list("key = 'LANG-1606'")[0]
        con = get_connection(db_path)
        insert_project(con, "TEST_project", "T_jiraId", "T_repositoryPath")
        # insert_issue(con, issue1, "TEST_project")
        commit1 = g.get_commit_by_id("c7c85ee39892df3ca007c6596c41654865be7e43")
        insert_commit(con, commit1, "TEST_project")
        close_connection(con)
    except ValueError:
        print("Commit not found")
