import git
import os
from javadiff import diff as d
import Debug
import JavaAnalyzer as a
import time

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = r"C:\Program Files\Gl'it\bin\git.exe"
REPO_PATH =  r"C:\Users\shir0\commons-math"

repo_path = REPO_PATH


def set_repo_path(path):
    global repo_path
    repo_path = path


def get_commit_by_id(commit_id):
    repo = git.Repo(repo_path)
    return repo.commit(commit_id)


def get_all_commits():
    repo = git.Repo(repo_path)
    all_commits = []
    if not repo.bare:  # check that the repository loaded correctly
        all_commits = list(repo.iter_commits())
        if Debug.mode():
            print("commit list done")
    return all_commits


def _get_commits_files(repo):
    data = repo.git.log('--numstat','--pretty=format:"sha: %H"').split("sha: ")
    comms = {}
    for d in data[1:]:
        d = d.replace('"', '').replace('\n\n', '\n').split('\n')
        commit_sha = d[0]
        comms[commit_sha] = []
        for x in d[1:-1]:
            insertions, deletions, name = x.split('\t')
            names = fix_renamed_files([name])
            comms[commit_sha].extend(list(map(lambda n: CommittedFile(commit_sha, n, insertions, deletions), names)))
    return dict(map(lambda x: (repo.commit(x), comms[x]), filter(lambda x: comms[x], comms)))


def fix_renamed_files(files):
    """
    fix the paths of renamed files.
    before : u'tika-core/src/test/resources/{org/apache/tika/fork => test-documents}/embedded_with_npe.xml'
    after:
    u'tika-core/src/test/resources/org/apache/tika/fork/embedded_with_npe.xml'
    u'tika-core/src/test/resources/test-documents/embedded_with_npe.xml'
    :param files: self._files
    :return: list of modified files in commit
    """
    new_files = []
    for file in files:
        if "=>" in file:
            if "{" and "}" in file:
                # file moved
                src, dst = file.split("{")[1].split("}")[0].split("=>")
                fix = lambda repl: re.sub(r"{[\.a-zA-Z_/\-0-9]* => [\.a-zA-Z_/\-0-9]*}", repl.strip(), file)
                new_files.extend(map(fix, [src, dst]))
            else:
                # full path changed
                new_files.extend(map(lambda x: x.strip(), file.split("=>")))
                pass
        else:
            new_files.append(file)
    return new_files


def filter_commits(commits_list):  # return a list with commits that has java files
    commits = []
    for commit in commits_list:
        files = get_code_file(commit)
        if (len(files[0]) > 0) | (len(files[1]) > 0):  # contain java files (code or test)
            commits.append(commit)
    return commits


def get_code_file(commit):
    file_paths = commit.stats.files.keys()
    code = list()
    test = list()
    for path in file_paths:
        if path.endswith(".java"):
            if "test" in path.lower():
                test.append(path)
            else:
                code.append(path)
    return code, test


def get_commit_name(commit):
    return commit.summary


def get_commit_id(commit):
    return commit.hexsha


def get_commit_message(commit):
    return commit.message


def get_commit_date(commit):
    unix = commit.committed_date
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix))


def get_commit_parent_id(commit):
    return get_commit_id(commit.parents[0])


def get_commit_changes(commit):
    repo = git.Repo(repo_path)
    if isinstance(commit, str):
        commit = repo.commit(commit)
    relevant_data = []
    try:
        commit_diff = d.get_commit_diff(
            repo_path, commit)
        methods_dict = commit_diff.get_methods_dict()
        before_methods = methods_dict['before_changed'] + methods_dict['before_unchanged']
        changed_methods_before = methods_dict['before_changed']
        changed_methods_after = methods_dict['after_changed']
    except Exception as e:
        print(e)
        return None
    # [before_methods, changed_methods_before, after_methods, changed_methods_after]= d.get_changed_methods(repo_path, commit)  # amir's - return all methods relevant to the commit
    print("BEFORE:")
    print(changed_methods_before)
    print("AFTER:")
    print(changed_methods_after)
    changed_before_dict = {m.method_name_parameters: (m.file_name, m.source_lines) for m in changed_methods_before}
    before_dict = {m.method_name_parameters: (m.file_name, m.source_lines) for m in before_methods}
    for new_method in changed_methods_after:
        to_add = True
        new_path = new_method.file_name
        method_name = new_method.method_name_parameters
        new_content = a.get_content(new_method.source_lines)

        old_path, old_lines = changed_before_dict.get(method_name, (None, None))
        if (old_lines is None) | (old_path is None):  # new method \ only added
            old_path, old_lines = before_dict.get(method_name, (None, None))
            if old_lines is None:
                to_add = True
            else:
                old_content = a.get_content(old_lines)
                if (old_content != new_content) | (old_path != new_path):  # something has changed
                    to_add = True

        else:
            changed_before_dict.pop(method_name)
            old_content = a.get_content(old_lines)
            if (old_content != new_content) | (old_path != new_path):  # something has changed
                to_add = True

        if to_add:
            relevant_data.append((method_name, new_path, new_method.source_lines, old_path, old_lines))

    for method_name, (old_path, old_lines) in changed_before_dict.items():  # deleted methods
        relevant_data.append((method_name, old_path, None, old_path, old_lines))

    return relevant_data


"""
def test_diff(commit):
    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    parent = commit.parents[0] if commit.parents else EMPTY_TREE_SHA
    diffs = commit.diff(parent)
    relevant_data = []
    for diff_item in diffs.iter_change_type('M'):
        if diff_item.a_path.endswith(".java"):
            # read before and after commit to files
            before_code = diff_item.a_blob.data_stream.read().decode('utf-8')
            with open("before.txt", "w", encoding="utf-8") as f:
                f.write(before_code)
                f.close()
            after_code = diff_item.b_blob.data_stream.read().decode('utf-8')
            with open("after.txt", "w", encoding="utf-8") as f:
                f.write(after_code)
                f.close()

            # create changes file
            text1 = open("before.txt").readlines()
            text2 = open("after.txt").readlines()
            with open("compare.txt", "w", encoding="utf-8") as f:
                f.writelines(difflib.unified_diff(text2, text1))
                f.close()

            # separate diffs to functions
            functions = []
            with open('compare.txt') as fp:
                contents = fp.read()
                funcs = contents.split("public")  # TODO: split also private and protected
                for func in funcs[1:]:
                    func = "".join(["public ", func])
                    functions.append(func)
                f.close()
            relevant_data.append((diff_item.a_path, functions))
    return relevant_data
"""

if __name__ == '__main__':
    commit = get_commit_by_id("9cbf1d184442063ec5ab833e954009b7f18c2781")
    changes = get_commit_changes(commit)
    print(len(changes))
    print(changes)
