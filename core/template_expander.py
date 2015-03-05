import re
import os.path
from .statements import Statements


TEMPLATE_DIR = "core/templates"


class TemplateExpander:
    @staticmethod
    def get_file_name(file_type, name):
        if file_type == "tex":
            return "%s.tex" % (name)
        elif file_type == "ref":
            return "%s_ref.bib" % (name)
        elif file_type == "tpl":
            return "%s.tex" % (name)
        else:
            return name

    def __init__(self, project):
        self.project = project
        self.tex_file_name = TemplateExpander.get_file_name(
            "tex", project["output_name"]
        )
        self.ref_file_name = TemplateExpander.get_file_name(
            "ref", project["output_name"]
        )
        self.tex_file = open(self.tex_file_name, "w", encoding="utf-8")
        self.ref_file = open(self.ref_file_name, "w", encoding="utf-8")

    def encode_thai(self, string):
        return re.sub("([^\\x00-\\xff]+)", "{\\\\thi \\1}", string)

    def parse_keyword(self, keyword):
        if ("type" in keyword
                and self.project["output_type"] != keyword["type"]):
            return ""
        non_string = ["name", "authors", "advisor", "abstract", "chapters"]
        keyword_name = keyword["name"]
        if keyword_name[0] == "[" and keyword_name[-1] == "]":
            return keyword_name[1:-1]
        if keyword_name in self.project and keyword_name not in non_string:
            return self.project[keyword_name]
        return keyword["matches"].group(0)

    def write(self, line, target="tex"):
        if target == "tex":
            self.tex_file.write(
                self.encode_thai(
                    Statements.parse(
                        "keyword_tag", line, replacer=self.parse_keyword
                    )
                )
            )
        elif target == "ref":
            self.ref_file.write(self.encode_thai(line))

    def parse_references(self):
        references_file = open(self.project["reference"], "r")
        for line in references_file.readlines():
            self.write(line, target="ref")

    def parse_template(self, template, templates):
        if ("type" in template
                and self.project["output_type"] != template["type"]):
            return ""
        if (template["name"] in templates or
                not self.expand(template["name"], templates)):
            return template["matches"].group(0)

    def expand(self, template="index", templates=None):
        if not templates:
            self.parse_references()
        templates = templates or []
        templates.append(template)
        template_path = os.path.join(
            TEMPLATE_DIR, TemplateExpander.get_file_name("tpl", template)
        )
        if not os.path.exists(template_path):
            return False
        template_file = open(template_path, "r")
        for line in template_file.readlines():
            line = Statements.parse(
                "template_include", line,
                replacer=lambda t: self.parse_template(t, templates)
            )
            if line is not None:
                self.write(line, target="tex")
        return True
