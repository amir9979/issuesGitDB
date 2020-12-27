import operator
import javalang
from collections import Counter

# only full name
type_token = ['String', 'Identifier', 'DecimalFloatingPoint', 'DecimalInteger', 'HexInteger', 'OctalInteger',  ]


class SourceLine(object):
    def __init__(self, line, line_number, is_changed, ordinal, decls, tokens):
        self.line = line.strip()
        self.line_number = line_number
        self.is_changed = is_changed
        self.ordinal = ordinal
        self.decls = decls
        self.tokens = tokens

    def __repr__(self):
        start = "  "
        if self.is_changed:
            start = "* "
        return "{0}{1}: {2}".format(start, str(self.line_number), self.line)

    @staticmethod
    def get_source_lines(start_line, end_line, contents, changed_indices, method_used_lines, parsed_body, tokens=None):
        source_lines = []
        for line_number in range(start_line - 1, end_line):
            if line_number not in method_used_lines:
                continue
            decls = SourceLine.get_decl_at_line(parsed_body, line_number + 1)
            tokens_types = SourceLine.get_tokens_at_line(tokens, line_number + 1)
            line = contents[line_number]
            is_changed = line_number in changed_indices
            source_lines.append(
                SourceLine(line, line_number, is_changed, line_number - start_line, decls, tokens_types))
        return source_lines

    @staticmethod
    def get_decl_at_line(parsed_body, line_number):
        ans = []
        for e in parsed_body:
            for e2 in map(operator.itemgetter(1), e.filter(object)):
                if e2.position and e2.position.line == line_number:
                    ans.append(e2)
        return dict(Counter(map(lambda x: type(x).__name__, ans)))

    @staticmethod
    def get_tokens_at_line(tokens, line_number):
        ans = []
        for t in tokens:
            if t.position.line == line_number:
                ans.append(t)
        full_names = []
        for t in ans:
            if type(t).__name__ in type_token:
                full_names.append(type(t).__name__)
            else:
                full_names.append("{0}_{1}".format(type(t).__name__, t.value))
        return dict(Counter(full_names))


class MethodData(object):
    def __init__(self, method_name, start_line, end_line, contents, changed_indices, method_used_lines, parameters,
                 file_name, method_decl, analyze_source_lines=True, tokens=None):
        self.method_name = method_name
        self.start_line = int(start_line)
        self.end_line = int(end_line)
        self.implementation = contents[self.start_line - 1: self.end_line]
        self.method_used_lines = method_used_lines
        self.parameters = parameters
        self.file_name = file_name
        self.method_decl = method_decl
        self.source_lines = SourceLine.get_source_lines(start_line, end_line, contents, changed_indices,
                                                        method_used_lines, method_decl.body, tokens)
        self.method_name_parameters = self.method_name + "(" + ",".join(self.parameters) + ")"
        self.id = self.file_name + "@" + self.method_name_parameters
        self.changed = self._is_changed()

    def _is_changed(self):
        # return len(set(self.method_used_lines).intersection(set(indices))) > 0
        return any(filter(lambda line: line.is_changed, self.source_lines))
        # return any(filter(lambda ind: ind >= self.start_line and ind <= self.end_line, indices))

    def __eq__(self, other):
        assert isinstance(other, type(self))
        return self.method_name == other.method_name and self.parameters == other.parameters

    def __repr__(self):
        return self.id

    def get_changed_lines(self):
        return filter(lambda line: line.is_changed, self.source_lines)
