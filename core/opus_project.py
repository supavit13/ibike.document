from .logger import Logger
from .statements import Statements
from .template_expander import TemplateExpander


"""
Generation sequences
 - xelatex -output-directory=output -interaction=nonstopmode -halt-on-error -no-pdf <project>
 - bibtex output/<project>
 - xelatex -output-directory=output -interaction=nonstopmode -halt-on-error <project>
"""


class OpusProject:
    def __init__(self, filename):
        self.project_file = open(filename, "r")

    def validate_project(self, project):
        missing = []
        properties = {
            "output_name": "Output File Name",
            "output_type": "Output Type",
            "name": "Project Name (TH & EN)",
            "authors": "Project Authors (TH & EN)",
            "advisor": "Project Advisor (TH & EN)",
            "committee1": "Project Committee #1",
            "committee2": "Project Committee #2",
            "headdepartment": "Head of Department",
            "abstract": "Abstract (TH & EN)",
            "acknowledgement": "Acknowledgement",
            "reference": "Reference",
            "chapters": "Project Contents (Chapters)"
        }
        for prop in properties:
            if prop not in project:
                missing.append(properties[prop])
        if len(missing) == 0:
            if len(project["authors"]) == 0:
                missing.append(
                    "Authors must have at least 1 person"
                )
            else:
                for author in project["authors"]:
                    if len(author) < 2:
                        missing.append(
                            "Authors must have both Thai and English name" +
                            " for every person"
                        )
                        break
            if len(properties["chapters"]) == 0:
                missing.append(
                    "Chapters must have at least 1 chapter"
                )
            if len(properties["name"]) < 2:
                missing.append(
                    "Project Name must have both Thai and English name"
                )
            if len(properties["advisor"]) < 2:
                missing.append(
                    "Project Advisor must have both Thai and English name"
                )
            else:
                for lang in ["th", "en"]:
                    language = "Thai" if lang == "th" else "English"
                    if lang not in project["advisor"]:
                        missing.append(
                            "Project Advisor must have %s name" % (language)
                        )
                        continue
                    if len(project["advisor"][lang]) < 2:
                        missing.append(
                            "Project Advisor must have" +
                            " both name and degree in %s" % (language)
                        )
            if len(properties["abstract"]) < 2:
                missing.append(
                    "Abstract must have both Thai and English version"
                )
        missing.sort()
        return missing

    def set_property(self, project, prop):
        if prop["name"] == "document":
            if "property" in prop:
                project["output_name"] = prop["property"]
            project["output_type"] = prop["value"].lower()
        elif prop["name"] == "chapter" or prop["name"] == "appendix":
            for field in ["chapters", "appendices"]:
                if field not in project:
                    project[field] = []
                data = {}
                if "property" in prop:
                    data["name"] = prop["property"]
                data["file"] = prop["value"]
                project[field].append(data)
        elif (prop["name"].startswith("name-") or
                prop["name"].startswith("abstract")):
            for field in ["name", "abstract"]:
                if field not in project:
                    project[field] = {}
                for lang in ["en", "th"]:
                    if prop["name"].endswith(lang):
                        project[field][lang] = prop["value"]
        elif prop["name"].startswith("advisor-"):
            if "advisor" not in project:
                project["advisor"] = {}
            for lang in ["en", "th"]:
                if not prop["name"].endswith(lang):
                    continue
                if lang not in project["advisor"]:
                    project["advisor"][lang] = {}
                project["advisor"][lang]["name"] = prop["value"]
                if "support_value" in prop:
                    project["advisor"][lang]["degree"] = prop["support_value"]
        elif prop["name"].startswith("author-"):
            if "authors" not in project:
                project["authors"] = []
            for lang in ["en", "th"]:
                if not prop["name"].endswith(lang):
                    continue
                add = False
                for author in project["authors"]:
                    if lang not in author:
                        author[lang] = prop["value"]
                        add = True
                        break
                if not add:
                    project["authors"].append({
                        lang: prop["value"]
                    })
        else:
            fields = [
                "committee1", "committee2", "headdepartment",
                "acknowledgement", "reference"
            ]
            for field in fields:
                if not prop["name"].startswith(field):
                    continue
                project[field] = prop["value"]

    def parse_project(self, args):
        lines = self.project_file.readlines()
        project_info = {}
        line_no = 0
        for line in lines:
            line = Statements.get("comment")["pattern"].sub("", line)
            line_no += 1
            if Statements.parse("empty", line):
                # Skip empty line
                continue
            prop = Statements.parse("property", line)
            prop_end = Statements.parse("property_end", line)
            if not prop and not prop_end:
                Logger.error(
                    self.project_file, line_no,
                    "InvalidProperty", "Invalid property"
                )
                return
            if prop_end:
                break
            if prop:
                if "name" not in prop or "value" not in prop:
                    Logger.error(
                        self.project_file, line_no,
                        "InvalidProperty", "Property did not have name or value"
                    )
                    return
                self.set_property(project_info, prop)
        if len(args) > 0:
            project_info["output_type"] = args[0].lower()
        validation = self.validate_project(project_info)
        if len(validation) > 0:
            print("Error! Following project properties are missing...")
            for miss in validation:
                print("  - %s" % (miss))
            return
        expander = TemplateExpander(project_info)
        return expander.expand()

    def compile(self, args):
        self.parse_project(args)
