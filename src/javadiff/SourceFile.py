import operator

import javalang
from javalang.tree import ClassDeclaration

try: from methodData import MethodData
except: from .methodData import MethodData
import os


def extract_classes_names(parsed_data, package):
    classes = list(parsed_data.filter(javalang.tree.ClassDeclaration))  # tuple (position,class itself)
    names = list()
    for full_class in classes:
        class_declaration = full_class[1]
        position = full_class[0]
        if len(position) > 2:  # has parent class
            index = class_name.find('.')
            if index != -1:
                class_name = class_name[0:index]
            class_name = class_name + "." + class_declaration.name
        else:
            class_name = class_declaration.name
        names.append(package + "." + class_name)
    return names

class SourceFile(object):
    def __init__(self, contents, file_name, indices=()):
        self.contents = contents
        self.changed_indices = indices
        self.file_name = file_name
        self.methods = dict()
        try:
            if file_name.endswith(".java"):
                tokens = list(javalang.tokenizer.tokenize("".join(self.contents)))
                parser = javalang.parser.Parser(tokens)
                parsed_data = parser.parse()
                packages = list(map(operator.itemgetter(1), parsed_data.filter(javalang.tree.PackageDeclaration)))
                classes = list(map(operator.itemgetter(1), parsed_data.filter(javalang.tree.ClassDeclaration)))
                self.package_name = ''
                if packages:
                    self.package_name = packages[0].name
                    # self.modified_names = extract_classes_names(parsed_data)
                    self.modified_names = map(lambda c: self.package_name + "." + c.name, classes)
                self.methods = self.get_methods_by_javalang(tokens, parsed_data)
        except:
            raise

    def get_methods_by_javalang(self, tokens, parsed_data):
        def get_method_end_position(method, seperators):
            method_seperators = seperators[list(map(id, sorted(seperators + [method],
                                                          key=lambda x: (x.position.line, x.position.column)))).index(
                id(method)):]
            assert method_seperators[0].value == "{"
            counter = 1
            for seperator in method_seperators[1:]:
                if seperator.value == "{":
                    counter += 1
                elif seperator.value == "}":
                    counter -= 1
                if counter == 0:
                    return seperator.position

        used_lines = set(map(lambda t: t.position.line-1, tokens))
        seperators = list(filter(lambda token: isinstance(token, javalang.tokenizer.Separator) and token.value in "{}",
                            tokens))
        methods_dict = dict()

        classes_full = list(parsed_data.filter(javalang.tree.ClassDeclaration))  # tuple (position,class itself)
        for full_class in classes_full:
            class_path = full_class[0]
            class_declaration = full_class[1]
            if len(class_path) > 2:  # has parent class
                index = class_name.find('.')
                if index != -1:
                    class_name = class_name[0:index]
                class_name = class_name + "." + class_declaration.name
            else:
                class_name = class_declaration.name

            methods = list(map(operator.itemgetter(1), class_declaration.filter(javalang.tree.MethodDeclaration)))
            constructors = list(map(operator.itemgetter(1), class_declaration.filter(javalang.tree.ConstructorDeclaration)))
            for method in methods + constructors:
                if not method.body:
                    # skip abstract methods
                    continue
                method_start_position = method.position
                method_end_position = get_method_end_position(method, seperators)
                method_used_lines = list(filter(lambda line: method_start_position.line <= line <= method_end_position.line, used_lines))
                parameters = list(map(lambda parameter: parameter.type.name + ('[]' if parameter.varargs else ''), method.parameters))
                method_data = MethodData(".".join([self.package_name, class_name, method.name]),
                                         method_start_position.line, method_end_position.line,
                                         self.contents, self.changed_indices, method_used_lines, parameters, self.file_name, method)
                methods_dict[method_data.id] = method_data
        return methods_dict

    def get_changed_methods(self):
        return list(filter(lambda method: method.changed, self.methods.values()))

    def replace_method(self, method_data):
        assert method_data.method_name in self.methods
        old_method = self.methods[method_data.method_name]
        self.contents = self.contents[:old_method.start_line] + \
                        self.contents[method_data.start_line:method_data.end_line] + \
                        self.contents[old_method.end_line:]
        self.methods = self.get_methods_by_javalang()

    def __repr__(self):
        return self.file_name
