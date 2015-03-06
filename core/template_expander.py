import re
import os.path
from .statements import Statements
from .opus_markup import OpusMarkup


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

    def parse_object(self, keyword):
        keyword_name = keyword["name"]
        keyword_sel = None
        if "selector" in keyword:
            keyword_sel = keyword["selector"]
        if keyword_name == "name" and keyword_sel:
            return self.project["name"][keyword_sel[0]]
        elif keyword_name == "advisor" and keyword_sel:
            advisor = self.project["advisor"][keyword_sel[0]]
            keyword_sel = keyword_sel[1:]
            if keyword_sel:
                return "%s" % (advisor[keyword_sel[0]])
            else:
                return "%s, %s" % (advisor["name"], advisor["degree"])
        if keyword_name == "authors" and keyword_sel:
            output = []
            for author in self.project["authors"]:
                output.append(author[keyword_sel[0]])
            return "\\\\\n".join(output)
        return keyword["matches"].group(0)

    def parse_keyword(self, keyword):
        if ("type" in keyword
                and self.project["output_type"] != keyword["type"]):
            return ""
        non_string = ["name", "authors", "advisor", "abstract", "chapters"]
        keyword_name = keyword["name"]
        if keyword_name[0] == "[" and keyword_name[-1] == "]":
            return keyword_name[1:-1]
        if keyword_name in non_string:
            return self.parse_object(keyword)
        if keyword_name in self.project:
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

    def parse_include(self, template_name, template):
        include_path = None
        if template_name == "abstract" and template["selector"]:
            include_path = self.project["abstract"][template["selector"][0]]
        elif template_name == "acknowledgement":
            include_path = self.project["acknowledgement"]

        if not os.path.exists(include_path):
            print("%s is not found" % (include_path))
            return ""
        markup = OpusMarkup(self.project)
        include_file = open(include_path, "r")
        output = "".join([
            markup.parse(line) for line
            in include_file.readlines()
        ])
        include_file.close()
        return output

    def parse_template(self, template, templates):
        if ("type" in template
                and self.project["output_type"] != template["type"]):
            return ""
        if template["name"][0] == "[" and template["name"][-1] == "]":
            return self.parse_include(template["name"][1:-1], template)
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
        template_file.close()
        return True
