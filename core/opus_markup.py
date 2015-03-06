from .statements import Statements


class OpusMarkup:
    def __init__(self, project):
        self.project = project

    def parse(self, line):
        if Statements.parse("comment", line):
            return ""
        else:
            return line
