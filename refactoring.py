from dataclasses import dataclass, asdict
from typing import List
import jsons
import os

@dataclass
class RefactoringMinerLocation:
    filePath: str
    startLine: int = 0
    endLine: int = 0
    startColumn: int = 0
    endColumn: int = 0
    codeElementType: str = ''
    description: str = ''
    codeElement: str = ''
    repository: str = ''
    sha1: str = ''
    refactor_ind: int = 0
    side: str = ''

    def set(self, repo, sha1, refactor_ind, side):
        self.filePath = os.path.normpath(self.filePath)
        self.startLine = self.startLine - 1 # start from 0
        self.endLine = self.endLine - 1
        self.repository = repo
        self.sha1 = sha1
        self.refactor_ind = refactor_ind
        self.side = side

    def get(self, **kargs):
        d = asdict(self)
        d.update(kargs)
        return d


@dataclass
class RefactoringMinerRefactor:
    refactor_type: str
    description: str
    leftSideLocations: List[RefactoringMinerLocation]
    rightSideLocations: List[RefactoringMinerLocation]
    repository: str = ''
    sha1: str = ''

    def set(self, repo, sha1):
        self.repository = repo
        self.sha1 = sha1
        for ind, l in enumerate(self.leftSideLocations):
            l.set(repo, sha1, ind, 'left')
        for ind, r in enumerate(self.rightSideLocations):
            r.set(repo, sha1, ind, 'right')

    def get(self):
        return list(map(lambda x: x.get(refactor_type=self.refactor_type, refactor_description=self.description), self.leftSideLocations + self.rightSideLocations)) #{'refactor_type': self.refactor_type, 'description': self.description, 'repository': self.repository, 'sha1': self.sha1}


@dataclass
class RefactoringMinerCommit:
    repository: str
    sha1: str
    url: str
    refactorings: List[RefactoringMinerRefactor]

    def set(self):
        for r in self.refactorings:
            r.set(self.repository, self.sha1)

    def get(self):
        ans = []
        for r in self.refactorings:
            ans.extend(r.get())
        return ans


@dataclass
class RefactoringMinerOutput:
    commits: List[RefactoringMinerCommit]

    def set(self):
        for c in self.commits:
            c.set()
w
    def get(self):
        ans = []
        for r in self.commits:
            ans.extend(r.get())
        return ans


def load(s):
    ans = jsons.loads(s, cls=RefactoringMinerOutput)
    ans.set()
    return ans


if __name__ == "__main__":
    data = load(open(r"C:\Users\User\Downloads\11.json (1)\out.json").read())
    pass
