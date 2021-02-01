import git
import os
try:
    from javadiff.javadiff import diff as d
except:
    from javadiff import diff as d
import JavaAnalyzer as a
import time
import re

os.environ["GIT_PYTHON_REFRESH"] = "quiet"
os.environ["GIT_PYTHON_GIT_EXECUTABLE"] = r"C:\Program Files\Gl'it\bin\git.exe"
REPO_PATH =  r"C:\Users\shir0\commons-math"

repo_path = REPO_PATH


def set_repo_path(path):
    global repo_path
    repo_path = path


class Commit():
    def __init__(self, commit_object, committed_files):
        self.commit_object = commit_object
        self.id = self.commit_object.hexsha
        self.parent_id = self.commit_object.parents[0].hexsha
        self.summary = self.commit_object.summary
        unix = self.commit_object.committed_date
        self.date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix))
        self.message = self.commit_object.message
        self.committed_files = committed_files
        self.is_java = self.has_java()
        if self.is_java:
            self.code_files = []
            self.test_files = []
            for f in committed_files:
                if f[1].endswith('java'):
                    if 'test' in f[1].lower():
                        self.test_files.append(f)
                    else:
                        self.code_files.append(f)

    def has_java(self):
        return any(list(map(lambda f: f[1].endswith('java'), self.committed_files)))


def get_commits_files(repo):
    if type(repo) == type(''):
        repo = git.Repo(repo)
    data = repo.git.log('--numstat','--pretty=format:"sha: %H"').split("sha: ")
    comms = {}
    for d_ in data[1:]:
        d_ = d_.replace('"', '').replace('\n\n', '\n').split('\n')
        commit_sha = d_[0]
        comms[commit_sha] = []
        for x in d_[1:-1]:
            insertions, deletions, name = x.split('\t')
            names = fix_renamed_files([name])
            comms[commit_sha].extend(list(map(lambda file_name: (commit_sha, file_name, insertions, deletions), names)))
    ans = []
    for c in comms:
        if comms[c]:
            try:
                ans.append(Commit(repo.commit(c), comms[c]))
            except Exception as e:
                pass
    return ans #list(map(lambda x: Commit(repo.commit(x), comms[x]), filter(lambda x: comms[x], comms)))


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


def get_commit_changes(commit):
    relevant_data = []
    try:
        commit_diff = d.get_commit_diff(
            repo_path, commit.commit_object)
        methods_dict = commit_diff.get_methods_dict()
        before_methods = methods_dict['before_changed'] + methods_dict['before_unchanged']
        changed_methods_before = methods_dict['before_changed']
        changed_methods_after = methods_dict['after_changed']
    except Exception as e:
        print(e)
        return None
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
