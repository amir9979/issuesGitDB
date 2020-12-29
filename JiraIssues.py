from jira import JIRA
from jira.exceptions import JIRAError

from datetime import datetime

import Debug

jira = JIRA(r"http://issues.apache.org/jira")

def set_jira(path):
    global jira
    jira = JIRA(path)

def get_issues_list(jql):
    # get issues relevant issues by jql
    block_size = 100
    block_num = 0
    issues = []

    try:
        while True:
            start_idx = block_num * block_size
            more_issue = jira.search_issues(jql, start_idx, block_size) 
            if len(more_issue) > 0:
                for issue in more_issue:
                    issues.append(issue)
            else:
                break
            block_num += 1
        if Debug.mode(): print("**issue list done")
        return issues

    except JIRAError:
        if Debug.mode(): print("JIRA Connection ERROR!!!")
        return []

def get_issue_id(issue):
    return issue.key

def get_issue_summary(issue):
    return issue.fields.summary

def get_issue_description(issue):
    return issue.fields.description

def get_issue_status(issue):
    return issue.fields.status.name

def get_issue_type(issue):
    return issue.fields.issuetype.name

def get_issue_creation_date(issue):
    long_time = str(issue.fields.created).replace('T', ' ')
    return long_time[:19]
