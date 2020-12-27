
try:
    from FileDiff import FileDiff
except ImportError:
    from .FileDiff import FileDiff 


class CommitsDiff(object):
    def __init__(self, child, parent):
        self.diffs = list(CommitsDiff.diffs(child, parent))

    @staticmethod
    def diffs(child, parent):
        for d in parent.tree.diff(child.tree, ignore_blank_lines=True, ignore_space_at_eol=True):
            try:
                yield FileDiff(d, child.hexsha)
            except:
                pass
