import GitCommits as g
import JiraIssues as j
import Debug

JQL = 'project = LANG AND issuetype = "New Feature" AND status = Closed'

def create_matrix(jira_issues, git_commits):
    # TODO: check if we match by other commit fields other than commit's name
    matrix = []
    for commit in git_commits:
        code = g.get_code_file(commit)
        if len(code[0]) == 0 & len(code[1]) == 0:  # no java code files - not relevant
            continue
        commit_name = g.get_commit_name(commit)
        for issue in jira_issues:
            issue_id = j.get_issue_id(issue)
            index = commit_name.find(issue_id)
            if index != -1:
                if len(commit_name) == index + len(issue_id):  # last word in commit's name
                    matrix.append((issue, commit))
                else:  # check if this is the issue or shorter ID
                    next_char = commit_name[index + len(issue_id)]
                    if not next_char.isdigit():
                        matrix.append((issue, commit))  # add to Matrix
    if Debug.mode():
        print("matching done")
    return matrix


"""
def matrix_to_csv(matrix, f_name):
    with open(f_name, "w", encoding="utf-8") as f:
        f.write("#, issue id, issue summary, issue description, commit summary, code files, test files\n")
        count = 1

        for (issue, commit) in matrix:
            f.write(str(count))
            f.write(", ")
            f.write(issue.key)
            f.write(", ")
            f.write(issue.fields.summary)
            f.write(", ")
            # f.write(issue.fields.description)
            f.write(", ")
            f.write(commit.summary)
            f.write(", ")    
            files = g.get_code_file(commit)
            f.write("CODE:[")
            for path in files[0]:
                f.write(path)
            f.write("], TEST:[")
            for path in files[1]:
                f.write(path)
            f.write("]")

            f.write("\n")
            code = g.test_diff(commit)
            f.write(", CODE: [")
            for file, funcs in code:
                f.write("file:")
                f.write(file)
                f.write(",funcs:")
                for func in funcs:
                    f.write("\n--------new func-------\n")
                    f.write(func)

            f.write("\n\n")
            # print(count)
            count += 1
            
        f.close
"""

