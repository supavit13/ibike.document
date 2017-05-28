# -*- coding: utf-8 -*-
import re
import os.path
from datetime import datetime
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
        self.project["expander"] = {
            "citations": False,
            "figures": False,
            "tables": False
        }
        self.markup = OpusMarkup(self.project)
        self.success = True
        self.tex_file_name = TemplateExpander.get_file_name(
            "tex", project["output_name"]
        )
        self.ref_file_name = TemplateExpander.get_file_name(
            "ref", project["output_name"]
        )
        self.tex_lines = []
        self.tex_file = open(self.tex_file_name, "w", encoding="utf8")
        self.ref_file = open(self.ref_file_name, "w", encoding="utf8")

    def encode_thai(self, string):
        def replacer(matches):
            if matches.group(1):
                return matches.group(2)
            return "{\\thi %s}" % (matches.group(2))
        return re.sub("(\\\\)?([^\\x00-\\xff]+)", replacer, string)

    def parse_chapter_keyword(self, chapter, keyword):
        if keyword["name"] in ["chapter_name", "appendix_name"]:
            return chapter["name"]
        elif keyword["name"] in ["chapter_file", "appendix_file"]:
            return chapter["file"]
        print("Warning! Chapter keyword %s cannot be parsed." % (
            keyword["matches"].group(0)
        ))
        return keyword["matches"].group(0)

    def parse_chapter_template(self, chapter, template):
        if template["name"] == "[chapter_file]":
            return self.parse_include("chapter", chapter)
        elif template["name"] == "[appendix_file]":
            return self.parse_include("appendix", chapter)
        print("Warning! Chapter template \"%s\" cannot be parsed." % (
            template["matches"].group(0)
        ))
        return template["matches"].group(0)

    def parse_chapter(self, template, chapter):
        template_path = os.path.join(
            TEMPLATE_DIR, TemplateExpander.get_file_name("tpl", template)
        )
        if not os.path.exists(template_path):
            print("Warning! Chapter template \"%s\" is not found." % (
                template_path
            ))
            return None
        template_file = open(template_path, "r", encoding="utf8")
        output = []
        for line in template_file.readlines():
            if line is not None:
                line = Statements.parse(
                    "template_include", line,
                    replacer=lambda t: self.parse_chapter_template(chapter, t)
                )
                output.append(Statements.parse(
                    "keyword_tag", line,
                    replacer=lambda m: self.parse_chapter_keyword(chapter, m)
                ))
        template_file.close()
        return "".join(output)

    def parse_object(self, keyword):
        keyword_name = keyword["name"]
        keyword_sel = None
        one_line = False
        if "selector" in keyword:
            keyword_sel = keyword["selector"]
        if keyword_sel:
            index = 0
            for sel in keyword_sel:
                if sel[-1] == "!":
                    one_line = True
                    keyword_sel[index] = keyword_sel[index][:-1]
                index += 1
        if keyword_name == "name" and keyword_sel:
            return self.project["name"][keyword_sel[0]]
        elif keyword_name == "advisor" and keyword_sel:
            advisor = self.project["advisor"][keyword_sel[0]]
            keyword_sel = keyword_sel[1:]
            if keyword_sel:
                if keyword_sel[0] == "name":
                    return "%s%s" % (
                        advisor["prefix"],
                        advisor["name"]
                    )
                else:
                    return "%s" % (advisor[keyword_sel[0]])
            elif "degree" not in advisor:
                return "%s%s" % (
                    advisor["prefix"],
                    advisor["name"]
                )
            else:
                return "%s%s, %s" % (
                    advisor["prefix"],
                    advisor["name"],
                    advisor["degree"]
                )
        elif keyword_name in ["committee1", "committee2", "headdepartment"]:
            professor = self.project[keyword_name]
            return "%s%s" % (professor["prefix"], professor["name"])
        elif keyword_name == "current_month" and keyword_sel:
            current_month = datetime.now().month-1
            abbr = 0
            lang = keyword_sel[0]
            keyword_sel = keyword_sel[1:]
            if keyword_sel and keyword_sel[0] == "abbr":
                keyword_sel = keyword_sel[1:]
                abbr = 1
            if lang == "en":
                lower = False
                if keyword_sel and keyword_sel[0] == "lower":
                    keyword_sel = keyword_sel[1:]
                    lower = True
                month_name = [
                    ["January", "Jan"], ["February", "Feb"], ["March", "Mar"],
                    ["April", "Apr"], ["May", "May"], ["June", "Jun"],
                    ["July", "Jul"], ["August", "Aug"], ["September", "Sep"],
                    ["October", "Oct"], ["November", "Nov"], ["December", "Dec"]
                ][current_month][abbr]
                if lower:
                    month_name = month_name.lower()
                return month_name
            elif lang == "th":
                return [
                    ["มกราคม", "ม.ค."], ["กุมภาพันธ์", "ก.พ."],
                    ["มีนาคม", "มี.ค."], ["เมษายน", "เม.ย."],
                    ["พฤษภาคม", "พ.ค."], ["มิถุนายน", "มิ.ย."],
                    ["กรกฎาคม", "ก.ค."], ["สิงหาคม", "ส.ค."],
                    ["กันยายน", "ก.ย."], ["ตุลาคม", "ต.ค."],
                    ["พฤศจิกายน", "พ.ย."], ["ธันวาคม", "ธ.ค."]
                ][current_month][abbr]
            print("Warning! Keyword \"%s\" cannot required language" % (
                keyword["matches"].group(0)
            ))
            return ""
        elif keyword_name == "authors" and keyword_sel:
            prefix = ""
            suffix = ""
            if "prefix" in keyword:
                prefix = keyword["prefix"]
            if "suffix" in keyword:
                suffix = keyword["suffix"]
            output = []
            for author in self.project["authors"]:
                output.append(author[keyword_sel[0]])
            joiner = prefix
            if not one_line:
                joiner += "\n"
            joiner += suffix
            return joiner.join(output)
        elif keyword_name in ["chapters", "appendices"]:
            field = "chapter" if keyword_name == "chapters" else "appendix"
            chapters_output = []
            if keyword_name not in self.project:
                return ""
            for chapter in self.project[keyword_name]:
                chapter_output = self.parse_chapter(field, chapter)
                if chapter_output is not None:
                    chapters_output.append(chapter_output)
            return "".join(chapters_output)
        print(
            "Warning! Multi-values keyword \"%s\" cannot be parsed." % (
                keyword["matches"].group(0)
            )
        )
        return keyword["matches"].group(0)

    def parse_keyword(self, keyword):
        if (
            "type" in keyword and self.project["output_type"] != keyword["type"]
        ):
            return ""
        non_string = [
            "name", "authors", "advisor",
            "abstract", "chapters", "appendices",
            "current_month", "committee1", "committee2",
            "headdepartment"
        ]
        keyword_name = keyword["name"]
        if keyword_name[0] == "[" and keyword_name[-1] == "]":
            return keyword_name[1:-1]
        elif keyword_name in non_string:
            return self.parse_object(keyword)
        elif keyword_name == "reference":
            return os.path.splitext(self.ref_file_name)[0]
        elif keyword_name in self.project:
            return self.project[keyword_name]
        print("Warning! Keyword \"%s\" cannot be parsed." % (
            keyword["matches"].group(0)
        ))
        return keyword["matches"].group(0)

    def write(self, line, target="tex"):
        if target == "tex":
            self.tex_lines.append(
                self.encode_thai(
                    Statements.parse(
                        "keyword_tag", line, replacer=self.parse_keyword
                    )
                )
            )
        elif target == "ref":
            self.ref_file.write(self.encode_thai(line))

    def parse_references(self):
        references_file = open(self.project["reference"], "r", encoding="utf8")
        for line in references_file.readlines():
            self.write(line, target="ref")

    def parse_include(self, template_name, template):
        include_path = None
        if template_name == "abstract" and template["selector"]:
            include_path = self.project["abstract"][template["selector"][0]]
        elif template_name == "acknowledgement":
            include_path = self.project["acknowledgement"]
        elif template_name == "proposal":
            include_path = self.project["proposal"]
        elif template_name in ["chapter", "appendix"]:
            include_path = template["file"]
        elif template_name in ["listoftables", "listoffigures"]:
            return template["matches"].group(0)

        if include_path is None:
            print("Warning! Template \"%s\" is not found." % (template_name))
            return ""
        if not os.path.exists(include_path):
            print("Warning! Include file \"%s\" is not found." % (include_path))
            return ""
        include_file = open(include_path, "r", encoding="utf8")
        output = []
        line_no = 0
        empty_line = 0
        for line in include_file.readlines():
            line_no += 1
            parsed_line = self.markup.parse(line, line_no, include_path)
            if parsed_line.strip() == "":
                empty_line += 1
            else:
                empty_line = 0
            if empty_line < 2:
                output.append(parsed_line)
            else:
                empty_line = 0
            self.success = self.success and self.markup.success
        include_file.close()
        return "".join(output)

    def parse_template(self, template, templates):
        if (
            "type" in template and
            self.project["output_type"] != template["type"] and
            self.project["output_language"] != template["type"]
        ):
            return ""
        if template["name"][0] == "[" and template["name"][-1] == "]":
            return self.parse_include(template["name"][1:-1], template)
        if (template["name"] in templates or
                not self.expand(template["name"], templates)):
            print("Warning! Template \"%s\" cannot be expanded." % (
                template["name"]
            ))
            return template["matches"].group(0)

    def expand(self, template="index", templates=None, as_string=False):
        if not templates:
            self.parse_references()
        templates = templates or []
        templates.append(template)
        template_path = os.path.join(
            TEMPLATE_DIR, TemplateExpander.get_file_name("tpl", template)
        )
        if not os.path.exists(template_path):
            print("Warning! Template \"%s\" not found." % (template))
            if as_string:
                return None
            else:
                return False
        template_file = open(template_path, "r", encoding="utf8")
        output = []
        for line in template_file.readlines():
            line = Statements.parse(
                "template_include", line,
                replacer=lambda t: self.parse_template(t, templates)
            )
            if line is not None:
                if as_string:
                    output.append(line)
                else:
                    self.write(line, target="tex")
        template_file.close()
        if as_string:
            return "".join(output)
        else:
            return True

    def parse_post_template(self, template):
        if (
            "type" in template and
            self.project["output_type"] != template["type"] and
            self.project["output_language"] != template["type"]
        ):
            return ""
        if template["name"][0] == "[" and template["name"][-1] == "]":
            template_name = template["name"][1:-1]
            expander = self.project["expander"]
            if (template_name == "listoftables" and expander["tables"] or
                    template_name == "listoffigures" and expander["figures"]):
                return "\\%s" % (template_name)
            else:
                return ""
        print("Warning! Template \"%s\" cannot be expanded." % (
            template["name"]
        ))
        return ""

    def post_process(self):
        for line in self.tex_lines:
            line = Statements.parse(
                "template_include", line,
                replacer=lambda t: self.parse_post_template(t)
            )
            self.tex_file.write(line)

    def close(self):
        self.post_process()
        self.tex_file.close()
        self.ref_file.close()
        if not self.success:
            os.remove(self.tex_file_name)
            os.remove(self.ref_file_name)
            return (self.project, None, None)
        return (self.project, self.tex_file_name, self.ref_file_name)
