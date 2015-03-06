from .statements import Statements


class OpusMarkup:
    def __init__(self, project):
        self.project = project

    def parse(self, line):
        return Statements.parse("comment", line, replacer=lambda m: "")
