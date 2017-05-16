# -*- coding: utf-8 -*-
import re
import os.path
from datetime import datetime
from .logger import Logger
from .statements import Statements

"""
Validation
- References not exists
"""


class OpusMarkup:
    def __init__(self, project):
        self.project = project
        self.success = True
        self.inside = []

    def markup_attrs(self, markup):
        attrs = {}
        if "attributes" in markup:
            for attr in markup["attributes"]:
                comp = attr.split("=")
                if len(comp) > 1:
                    attrs[comp[0]] = comp[1]
                else:
                    attrs[comp[0]] = True
        return attrs

    def parse_keyword(self, keyword, line_no, file_path):
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
        Logger.warning(
            file_path, line_no,
            "InvalidMarkupKeyword",
            "Markup keyword \"%s\" cannot be parsed" % (
                keyword["matches"].group(0)
            )
        )
        return keyword["matches"].group(0)

    def parse_special_keyword(self, keyword, line_no, file_path):
        keyword_name = keyword["name"]
        keyword_sel = None
        if "selector" in keyword:
            keyword_sel = keyword["selector"]
        if keyword_name == "current_month" and keyword_sel:
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
                    ["October", "Oct"], ["November", "Nov"],
                    ["December", "Dec"]
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
            print("Warning! Markup \"%s\" cannot required language" % (
                keyword["matches"].group(0)
            ))
            return ""
        elif keyword_name == "current_file":
            file_name = os.path.basename(file_path)
            if keyword_sel and keyword_sel[0] == "escaped":
                keyword_sel = keyword_sel[1:]
                file_name = file_name.replace("_", "\\_")
            if keyword_sel and keyword_sel[0] == "name":
                return os.path.splitext(file_name)[0]
            elif keyword_sel and keyword_sel[0] == "ext":
                return os.path.splitext(file_name)[1][1:]
            return file_name
        Logger.warning(
            file_path, line_no,
            "InvalidMarkupKeyword",
            "Markup special keyword \"%s\" cannot be parsed" % (
                keyword["matches"].group(0)
            )
        )
        return keyword["matches"].group(0)

    def parse_escaped(self, escaped, line_no, file_path):
        if "character" in escaped:
            return escaped["character"]
        elif "return" in escaped:
            return escaped["return"]
        Logger.warning(
            file_path, line_no,
            "InvalidEscaped",
            "Escaped character \"%s\" cannot be parsed" % (
                escaped["matches"].group(0)
            )
        )
        return escaped["matches"].group(0)

    def parse_style(self, style, line_no, file_path):
        if "bold" in style:
            line = "\\textbf{%s}" % (Statements.parse(
                "basic_style",
                style["bold"],
                replacer=lambda m: self.parse_style(m, line_no, file_path)
            ))
            return "%s" % (Statements.parse(
                "escaped_character",
                line,
                replacer=lambda m: self.parse_escaped(m, line_no, file_path)
            ))
        elif "italic" in style:
            line = "\\emph{%s}" % (Statements.parse(
                "basic_style",
                style["italic"],
                replacer=lambda m: self.parse_style(m, line_no, file_path)
            ))
            return "%s" % (Statements.parse(
                "escaped_character",
                line,
                replacer=lambda m: self.parse_escaped(m, line_no, file_path)
            ))
        elif "underline" in style:
            line = "\\underline{%s}" % (Statements.parse(
                "basic_style",
                style["underline"],
                replacer=lambda m: self.parse_style(m, line_no, file_path)
            ))
            return "%s" % (Statements.parse(
                "escaped_character",
                line,
                replacer=lambda m: self.parse_escaped(m, line_no, file_path)
            ))
        elif "code" in style:
            return "{\\ttfamily\\verb`%s`}" % (style["code"])
        Logger.warning(
            file_path, line_no,
            "InvalidMarkupStyle",
            "Markup style \"%s\" cannot be parsed" % (
                style["matches"].group(0)
            )
        )
        return style["matches"].group(0)

    def parse_list_item(self, item, line_no, file_path):
        if "text" in item:
            return "\\item{%s}" % (item["text"])
        elif "list_command" in item:
            return item["matches"].group(0)
        Logger.warning(
            file_path, line_no,
            "InvalidListItem",
            "List item \"%s\" cannot be parsed" % (
                item["matches"].group(0)
            )
        )
        return item["matches"].group(0)

    def parse_markup(self, markup, line_no, file_path):
        attrs = self.markup_attrs(markup)
        keyword = Statements.parse("markup_keyword", markup["tag"])
        inside = None if len(self.inside) == 0 else self.inside[-1]

        if not inside and markup["tag"] in [
            "section", "subsection", "subsubsection"
        ]:
            settings = {
                "caption": "",
                "reference": ""
            }

            if "value" in markup:
                settings["caption"] = markup["value"]
            if "expression" in markup:
                settings["reference"] = markup["expression"]

            output = "\\%s{%s}" % (markup["tag"], settings["caption"])
            if settings["reference"] != "":
                output += "\n\\label{%s}" % (settings["reference"])

            return output
        elif markup["tag"] in ["ref", "cite"]:
            if "expression" not in markup or markup["expression"] == "":
                self.success = False
                Logger.error(
                    file_path, line_no,
                    "InvalidReference",
                    "Reference must contains a reference name"
                )
                return ""
            if markup["tag"] == "cite":
                self.project["expander"]["citations"] = True
            return "\\%s{%s}" % (markup["tag"], markup["expression"])
        elif not inside and markup["tag"] == "image":
            settings = {
                "path": "",
                "caption": "",
                "width": 1,
                "float": "h",
                "reference": ""
            }

            if "value" in markup:
                settings["path"] = markup["value"]
            if "expression" in markup:
                settings["reference"] = markup["expression"]
            if "caption" in attrs:
                settings["caption"] = attrs["caption"]
            if "width" in attrs:
                settings["width"] = attrs["width"]
            if "float" in attrs:
                settings["float"] = attrs["float"]

            if not os.path.exists("images/%s" % (settings["path"])):
                Logger.warning(
                    file_path, line_no,
                    "InvalidImage",
                    "Image path \"%s\" is not exists" % (settings["path"])
                )
                return ""

            output = ""
            if settings["caption"] != "":
                output += "\\begin{figure}%s\n\\centering\n" % (
                    "[%s]" % (settings["float"])
                    if settings["float"] != "" else ""
                )
            output += "\\includegraphics[width=%s\\textwidth]{%s}" % (
                settings["width"], settings["path"]
            )
            if settings["caption"] != "":
                output += "\n\\caption{%s}" % (settings["caption"])
            if settings["reference"] != "":
                output += "\n\\label{%s}" % (settings["reference"])
            if settings["caption"] != "":
                output += "\n\\end{figure}"
            self.project["expander"]["figures"] = True
            return output
        elif markup["tag"] in ["list", "ulist"]:
            self.inside.append(markup["tag"])
            return "\\begin{%s}" % (
                "enumerate" if markup["tag"] == "list" else "itemize"
            )
        elif markup["tag"] == "eq":
            settings = {
                "reference": ""
            }

            if "expression" in markup:
                settings["reference"] = markup["expression"]

            self.inside.append(markup["tag"])
            output = "\\begin{equation}"
            if settings["reference"] != "":
                output += "\n\\label{%s}" % (settings["reference"])
            return output
        elif markup["tag"] == "math":
            self.inside.append(markup["tag"])
            return "\\["
        elif markup["tag"] == "code":
            settings = {
                "frame": True,
                "language": ""
            }

            options = []

            if "value" in markup:
                settings["language"] = markup["value"]
            if "frame" in attrs:
                if attrs["frame"].lower() in ["true", "false"]:
                    settings["frame"] = bool(attrs["frame"].lower())
                else:
                    Logger.warning(
                        file_path, line_no,
                        "InvalidAttribute",
                        "Attribute \"frame\" must be" +
                        " either \"true\" or \"false\""
                    )

            self.inside.append(markup["tag"])
            if settings["frame"]:
                options.append("frame=single")
            if settings["language"]:
                options.append("language=%s" % (settings["language"]))

            return (
                "\\lstset{basicstyle=\\footnotesize\\ttfamily," +
                "breaklines=true}\\begin{lstlisting}[%s]" % (",".join(options))
            )
        elif markup["tag"] == "mathcode":
            settings = {
                "frame": True,
                "math": False
            }

            options = ["fontfamily=tt"]

            if "math" in attrs:
                if attrs["math"].lower() in ["true", "false"]:
                    settings["math"] = bool(attrs["math"].lower())
                else:
                    Logger.warning(
                        file_path, line_no,
                        "InvalidAttribute",
                        "Attribute \"math\" must be" +
                        " either \"true\" or \"false\""
                    )
            if "frame" in attrs:
                if attrs["frame"].lower() in ["true", "false"]:
                    settings["frame"] = bool(attrs["frame"].lower())
                else:
                    Logger.warning(
                        file_path, line_no,
                        "InvalidAttribute",
                        "Attribute \"frame\" must be" +
                        " either \"true\" or \"false\""
                    )

            self.inside.append(markup["tag"])
            if settings["frame"]:
                options.append("frame=single")
            if settings["math"]:
                options.append("commandchars=\\\\\\{\\}")
                options.append("codes={\\catcode`$=3\\catcode`^=7}")

            return "\\begin{Verbatim}[%s]" % (",".join(options))
        elif markup["tag"] == "table":
            if "format" not in markup:
                self.success = False
                Logger.error(
                    file_path, line_no,
                    "InvalidFormat",
                    "Table must contains a format"
                )
                return ""

            settings = {
                "reference": "",
                "format": "",
                "caption": "",
                "float": "h",
                "size": "",
                "unit": "pt"
            }

            if "format" in markup:
                settings["format"] = markup["format"]
            if "expression" in markup:
                settings["reference"] = markup["expression"]
            if "value" in markup:
                settings["caption"] = markup["value"]
            if "float" in attrs:
                settings["float"] = attrs["float"]
            if "size" in attrs:
                settings["size"] = attrs["size"]
            if "unit" in attrs:
                settings["unit"] = attrs["unit"]

            output = ""
            if settings["caption"] != "":
                self.project["expander"]["tables"] = True
                self.inside.append("table_labeled")
                caption = settings["caption"]
                if settings["size"] != "":
                    caption = "\\fontsize{%s%s}{16pt}\\selectfont %s" % (
                        settings["size"],
                        settings["unit"],
                        settings["caption"]
                    )
                output += "\\begin{table}%s\n\\centering\n\\caption{%s}\n" % (
                    "[%s]" % (settings["float"])
                    if settings["float"] != "" else "",
                    caption
                )
            else:
                self.inside.append("table")
            if settings["reference"] != "":
                output += "\\label{%s}" % (settings["reference"])
            output += "\\begin{tabular}{%s}" % (settings["format"])
            return output
        elif markup["tag"] == "end" and len(self.inside) > 0:
            ending_type = self.inside.pop()
            if ending_type == "list":
                return "\\end{enumerate}"
            elif ending_type == "ulist":
                return "\\end{itemize}"
            elif ending_type == "eq":
                return "\\end{equation}"
            elif ending_type in ["table", "table_labeled"]:
                output = "\\end{tabular}"
                if ending_type == "table_labeled":
                    output += "\n\\end{table}"
                return output
            elif ending_type == "math":
                return "\\]"
            elif ending_type == "code":
                return "\\end{lstlisting}"
            elif ending_type == "mathcode":
                return "\\end{Verbatim}"
        elif keyword and keyword["name"] in self.project:
            return self.parse_keyword(keyword, line_no, file_path)
        elif keyword and keyword["name"] in ["current_month", "current_file"]:
            return self.parse_special_keyword(keyword, line_no, file_path)
        Logger.warning(
            file_path, line_no,
            "InvalidMarkup",
            "Markup \"%s\" cannot be parsed" % (markup["matches"].group(0))
        )
        return markup["matches"].group(0)

    def parse(self, line, line_no, file_path):
        self.success = True
        line = Statements.parse(
            "comment",
            line,
            replacer=lambda m: ""
        )
        if line.replace(" ", "").replace("\t", "") == "":
            return ""
        match = re.search("^\\$[^$]+\\$$", line)
        if match:
            return match.group(0)
        line = Statements.parse(
            "basic_style",
            line,
            replacer=lambda m: self.parse_style(m, line_no, file_path)
        )
        line = "%s" % (Statements.parse(
            "escaped_character",
            line,
            replacer=lambda m: self.parse_escaped(m, line_no, file_path)
        ))
        if len(self.inside) > 0 and self.inside[-1] in ["list", "ulist"]:
            if Statements.parse("list_item", line):
                line = Statements.parse(
                    "list_item",
                    line,
                    replacer=lambda m: self.parse_list_item(
                        m, line_no, file_path
                    )
                )
            else:
                Logger.warning(
                    file_path, line_no,
                    "InvalidListItem",
                    "List item \"%s\" cannot be parsed" % (
                        line.strip()
                    )
                )
        return Statements.parse(
            "markup",
            line,
            replacer=lambda m: self.parse_markup(m, line_no, file_path)
        )
